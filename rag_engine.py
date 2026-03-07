"""
RAG ENGINE — Forensic Report Retrieval-Augmented Generation
Chunks forensic JSON reports, vectorizes with sentence-transformers,
stores in ChromaDB, and answers user queries via context retrieval.
The retrieved context is formatted for a local Llama 3 model.
"""

import json
import os
import re
import uuid
import hashlib
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

# Graceful imports with fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None  # type: ignore

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    HAS_RAG_DEPS = True
except ImportError:
    HAS_RAG_DEPS = False
    chromadb = None  # type: ignore
    Settings = None  # type: ignore
    SentenceTransformer = None  # type: ignore

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chromadb_store")
os.makedirs(CHROMA_DIR, exist_ok=True)

# ── Embedding model (runs locally — no API key needed) ────────────────────────
_EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # fast, 384-dim
_embed_model: Any = None


def _get_embed_model():
    """Lazy-load the embedding model so import time stays fast."""
    if not HAS_RAG_DEPS:
        raise ImportError("RAG dependencies not installed. Run: pip install numpy sentence-transformers chromadb")
    global _embed_model
    if _embed_model is None:
        print(f"[RAG] Loading embedding model: {_EMBED_MODEL_NAME} …")
        _embed_model = SentenceTransformer(_EMBED_MODEL_NAME)  # type: ignore
        print("[RAG] Embedding model ready.")
    return _embed_model


# ── ChromaDB client ───────────────────────────────────────────────────────────
_chroma_client = None


def _get_chroma():
    if not HAS_RAG_DEPS:
        raise ImportError("ChromaDB not installed. Run: pip install chromadb")
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)  # type: ignore
    return _chroma_client


# ── Helper: deterministic ID from text ────────────────────────────────────────
def _text_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ══════════════════════════════════════════════════════════════════════════════
#  ARTIFACT CLASSIFICATION (Step 1 & 2: metadata + query detection)
# ══════════════════════════════════════════════════════════════════════════════

# Maps text patterns → artifact_type for both chunk classification and query detection
_ARTIFACT_RULES: List[Dict[str, Any]] = [
    {
        "type": "browser_history",
        "keywords": ["browser", "chrome", "firefox", "edge", "safari", "opera",
                     "bookmark", "cookie", "cache", "website", "url", "http",
                     "web history", "browsing", "internet"],
        "paths":   ["/appdata/local/google", "/appdata/local/microsoft/edge",
                    "/mozilla/firefox", "history", "places.sqlite"],
    },
    {
        "type": "usb_logs",
        "keywords": ["usb", "removable", "thumb drive", "flash drive",
                     "mass storage", "setupapi", "usbstor"],
        "paths":   ["setupapi", "usbstor", "/inf/"],
    },
    {
        "type": "login_events",
        "keywords": ["login", "logon", "logoff", "authentication", "credential",
                     "password", "sam", "ntlm", "kerberos", "sign in",
                     "user account", "security log", "failed login"],
        "paths":   ["sam", "security", "ntuser.dat", "/config/"],
    },
    {
        "type": "installed_programs",
        "keywords": ["program", "install", "software", "application", "uninstall",
                     "app", ".exe", ".msi", "program files", "registry"],
        "paths":   ["/program files", "/program files (x86)", "uninstall",
                    ".exe", ".msi", ".dll"],
    },
    {
        "type": "network_connections",
        "keywords": ["network", "ip", "dns", "hosts", "tcp", "udp", "port",
                     "connection", "socket", "firewall", "arp", "routing",
                     "interface", "ethernet", "wifi"],
        "paths":   ["hosts", "dns", "etc/", "network"],
    },
    {
        "type": "filesystem",
        "keywords": ["file", "directory", "folder", "inode", "partition",
                     "sector", "cluster", "ntfs", "fat", "ext4", "volume",
                     "block", "filesystem", "deleted", "carved", "recovered"],
        "paths":   [],
    },
]


def _classify_artifact_type(text: str, source: str = "") -> str:
    """
    Classify a chunk's artifact_type based on its text content and source label.
    Returns one of the artifact categories, or 'general' if undetermined.
    """
    combined = (text + " " + source).lower()

    # Special source-label shortcuts
    if source == "overview" or source == "extension_stats":
        return "general"
    if source == "encrypted_items":
        return "filesystem"
    if source == "network_artifacts":
        return "network_connections"
    if source.startswith("timeline_batch"):
        return "general"  # timelines span multiple categories

    best_type = "general"
    best_score = 0

    for rule in _ARTIFACT_RULES:
        score = 0
        for kw in rule["keywords"]:
            if kw in combined:
                score += 1
        for p in rule["paths"]:
            if p in combined:
                score += 2  # path matches are stronger signals
        if score > best_score:
            best_score = score
            best_type = rule["type"]

    return best_type


def _detect_query_artifact(query: str) -> Optional[str]:
    """
    Lightweight rule-based classifier: detect which artifact category
    a user query relates to. Returns None if no category is detected.
    """
    q = query.lower().strip()

    # Ordered by specificity (most specific first)
    _QUERY_RULES = [
        ("usb_logs",            ["usb", "removable", "thumb drive", "flash drive",
                                 "mass storage", "usbstor"]),
        ("browser_history",     ["browser", "chrome", "firefox", "edge", "safari",
                                 "bookmark", "cookie", "web history", "browsing",
                                 "website", "visited"]),
        ("login_events",        ["login", "logon", "logoff", "authentication",
                                 "credential", "sign in", "sign-in", "failed login",
                                 "password", "user account"]),
        ("installed_programs",  ["installed", "program", "software", "application",
                                 "uninstall", ".msi", "app installed"]),
        ("network_connections", ["network", "ip address", "dns", "hosts file",
                                 "tcp", "udp", "port", "connection", "firewall",
                                 "arp", "routing", "ethernet", "wifi"]),
        ("filesystem",          ["deleted file", "recovered file", "carved",
                                 "inode", "partition", "sector", "cluster",
                                 "ntfs", "fat32", "ext4", "volume"]),
    ]

    for artifact_type, keywords in _QUERY_RULES:
        for kw in keywords:
            if kw in q:
                return artifact_type

    return None  # no specific category detected → use normal search


# ══════════════════════════════════════════════════════════════════════════════
#  1. CHUNKING
# ══════════════════════════════════════════════════════════════════════════════

def chunk_forensic_report(report_json: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Break a forensic JSON report into meaningful, self-contained text chunks.
    Each chunk carries a `text` field (for embedding) and a `source` label.
    """
    chunks: List[Dict[str, str]] = []
    report = report_json.get("forensic_report", report_json)

    # ── Chunk 1: overview / metadata ──────────────────────────────────────
    overview_lines = [
        "=== FORENSIC REPORT OVERVIEW ===",
        f"Image analysed: {report.get('image_path', 'N/A')}",
        f"Scan timestamp: {report.get('scan_timestamp', 'N/A')}",
    ]
    part_info = report.get("partition_info", {})
    overview_lines.append(
        f"Filesystem: {part_info.get('filesystem_type', 'N/A')} | "
        f"Block size: {part_info.get('block_size', 'N/A')} | "
        f"Block count: {part_info.get('block_count', 'N/A')}"
    )
    summary = report.get("summary", {})
    for k, v in summary.items():
        label = k.replace("_", " ").title()
        overview_lines.append(f"{label}: {v}")

    chunks.append({"text": "\n".join(overview_lines), "source": "overview"})

    # ── Chunk 2: file extension statistics ────────────────────────────────
    ext_stats = report.get("file_extension_statistics", {})
    if ext_stats:
        ext_lines = ["=== FILE EXTENSION STATISTICS ==="]
        for ext, count in sorted(ext_stats.items(), key=lambda x: x[1], reverse=True):
            ext_lines.append(f"{ext}: {count} file(s)")
        chunks.append({"text": "\n".join(ext_lines), "source": "extension_stats"})

    # ── Chunk 3+: one chunk per file ──────────────────────────────────────
    files: Dict[str, Any] = report.get("files", {})
    hashes: Dict[str, str] = report.get("file_hashes", {})

    for key, fmeta in files.items():
        lines = [
            f"=== FILE: {fmeta['name']} ===",
            f"Path: {fmeta.get('path', 'N/A')}",
            f"Size: {_human_size(fmeta.get('size', 0))}",
            f"Inode: {fmeta.get('inode', 'N/A')}",
            f"Created: {fmeta.get('creation_time', 'N/A')}",
            f"Modified: {fmeta.get('modification_time', 'N/A')}",
            f"Accessed: {fmeta.get('access_time', 'N/A')}",
            f"Deleted: {'Yes' if fmeta.get('is_deleted') else 'No'}",
            f"Directory: {'Yes' if fmeta.get('is_directory') else 'No'}",
        ]
        if key in hashes:
            lines.append(f"SHA-256 (partial): {hashes[key]}")

        # flag suspicious
        name_lower = fmeta["name"].lower()
        suspicious_exts = {".exe", ".dll", ".bat", ".ps1", ".scr", ".vbs"}
        if any(name_lower.endswith(ext) for ext in suspicious_exts):
            lines.append("⚠ FLAGGED AS SUSPICIOUS")

        chunks.append({"text": "\n".join(lines), "source": f"file:{fmeta['name']}"})

    # ── Chunk: encrypted items ────────────────────────────────────────────
    encrypted = report.get("encrypted_items", [])
    if encrypted:
        enc_lines = ["=== ENCRYPTED ITEMS ==="]
        for item in encrypted:
            enc_lines.append(
                f"• {item['name']}  Path: {item['path']}  "
                f"Type: {item.get('type', 'N/A')}  "
                f"Size: {_human_size(item.get('size', 0))}  "
                f"Modified: {item.get('modified', 'N/A')}"
            )
        chunks.append({"text": "\n".join(enc_lines), "source": "encrypted_items"})

    # ── Chunk: network artifacts ──────────────────────────────────────────
    network = report.get("network_artifacts", [])
    if network:
        net_lines = ["=== NETWORK ARTIFACTS ==="]
        for item in network:
            net_lines.append(
                f"• {item['name']}  Path: {item['path']}  "
                f"Type: {item.get('type', 'N/A')}  "
                f"Size: {_human_size(item.get('size', 0))}  "
                f"Modified: {item.get('modified', 'N/A')}"
            )
        chunks.append({"text": "\n".join(net_lines), "source": "network_artifacts"})

    # ── Chunk: timeline events (batches of 5) ─────────────────────────────
    timeline = report.get("timeline_events", [])
    for i in range(0, len(timeline), 5):
        batch = timeline[i : i + 5]
        tl_lines = [f"=== TIMELINE EVENTS (batch {i // 5 + 1}) ==="]
        for evt in batch:
            tl_lines.append(
                f"[{evt['timestamp']}] {evt['event_type'].upper()} — "
                f"{evt['file']}  ({_human_size(evt.get('size', 0))})"
            )
        chunks.append({"text": "\n".join(tl_lines), "source": f"timeline_batch_{i // 5 + 1}"})

    return chunks


def _human_size(nbytes: int) -> str:
    size = float(nbytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


# ══════════════════════════════════════════════════════════════════════════════
#  2. VECTORISE & STORE
# ══════════════════════════════════════════════════════════════════════════════

def vectorize_and_store(
    analysis_id: str,
    report_json: Dict[str, Any],
) -> str:
    """
    Chunk the report, embed each chunk, upsert into a ChromaDB collection
    named after the analysis_id.  Returns the collection name.
    """
    collection_name = f"forensic_{analysis_id}"
    # ChromaDB collection names: 3-63 chars, alphanumeric + _/-
    collection_name = re.sub(r"[^a-zA-Z0-9_-]", "_", collection_name)[:63]

    chroma = _get_chroma()
    # Delete existing collection with same name to avoid stale data
    try:
        chroma.delete_collection(collection_name)
    except Exception:
        pass

    collection = chroma.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    chunks = chunk_forensic_report(report_json)
    if not chunks:
        raise ValueError("Chunking produced zero chunks — report may be empty")

    model = _get_embed_model()
    texts = [c["text"] for c in chunks]
    sources = [c["source"] for c in chunks]

    print(f"[RAG] Embedding {len(texts)} chunks for collection '{collection_name}' …")
    embeddings = model.encode(texts, show_progress_bar=False).tolist()

    ids = [f"{collection_name}_{i}_{_text_id(t)}" for i, t in enumerate(texts)]

    # ── Build enriched metadata with artifact_type (Step 1) ───────────────
    metadatas = []
    source_file = report_json.get("forensic_report", report_json).get("image_path", "unknown")
    for i, (text, src) in enumerate(zip(texts, sources)):
        metadatas.append({
            "source":        src,
            "analysis_id":   analysis_id,
            "artifact_type": _classify_artifact_type(text, src),
            "source_file":   os.path.basename(source_file),
            "page_id":       i,
        })

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    # Log artifact distribution
    from collections import Counter
    dist = Counter(m["artifact_type"] for m in metadatas)
    print(f"[RAG] Stored {len(ids)} chunks in '{collection_name}'. Artifact distribution: {dict(dist)}")
    return collection_name


# ══════════════════════════════════════════════════════════════════════════════
#  3. RETRIEVAL  (hybrid + hierarchical + context compression)
# ══════════════════════════════════════════════════════════════════════════════

DISTANCE_THRESHOLD = 0.75  # cosine distance: 0 = identical, 2 = opposite


def _raw_query(
    collection,
    query_embedding: List[List[float]],
    n: int,
    where: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    """
    Low-level ChromaDB query. Returns list of {text, source, distance, artifact_type}.
    Applies distance threshold filtering.
    """
    count = collection.count()
    if count == 0:
        return []
    n = min(n, count)
    kwargs: Dict[str, Any] = {
        "query_embeddings": query_embedding,
        "n_results": n,
        "include": ["documents", "metadatas", "distances"],
    }
    if where is not None:
        kwargs["where"] = where
    try:
        results = collection.query(**kwargs)
    except Exception:
        # Metadata filter may fail on old collections without artifact_type
        # → fall back to unfiltered search
        kwargs.pop("where", None)
        results = collection.query(**kwargs)

    hits: List[Dict[str, Any]] = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist <= DISTANCE_THRESHOLD:
            hits.append({
                "text": doc,
                "source": meta.get("source", ""),
                "distance": dist,
                "artifact_type": meta.get("artifact_type", "general"),
            })
    return hits


def _merge_and_deduplicate(
    semantic_hits: List[Dict[str, Any]],
    filtered_hits: List[Dict[str, Any]],
    top_k: int,
) -> List[Dict[str, Any]]:
    """
    Hybrid merge: interleave 50 % semantic + 50 % filtered results,
    remove duplicates by text content, return top_k.
    """
    seen_texts: set = set()
    merged: List[Dict[str, Any]] = []

    # Round-robin interleave for balanced mixing
    max_len = max(len(semantic_hits), len(filtered_hits))
    for i in range(max_len):
        for pool in (filtered_hits, semantic_hits):  # filtered first for priority
            if i < len(pool):
                key = pool[i]["text"][:200]  # first 200 chars as dedup key
                if key not in seen_texts:
                    seen_texts.add(key)
                    merged.append(pool[i])

    # Sort by distance (best first) and trim
    merged.sort(key=lambda h: h["distance"])
    return merged[:top_k]


def _compress_context(
    query: str,
    chunks: List[Dict[str, Any]],
    top_n_sentences: int = 8,
    similarity_threshold: float = 0.25,
    query_vec = None,
) -> List[Dict[str, Any]]:
    """
    Context Compression (Step 5).
    Splits retrieved chunks into sentences, keeps only the most relevant
    sentences above a similarity threshold, and returns compressed chunks.

    Accepts an optional pre-computed query_vec to avoid re-encoding the query
    (saves one embedding call per request).
    """
    if not chunks:
        return chunks

    # Skip compression if numpy is not available
    if not HAS_NUMPY:
        return chunks

    # Skip compression for very small result sets — not worth the overhead
    total_text_len = sum(len(c["text"]) for c in chunks)
    if total_text_len < 500:
        return chunks

    model = _get_embed_model()
    if query_vec is None:
        query_vec = model.encode([query], show_progress_bar=False)[0]

    # Collect all sentences with their origin
    sentence_pool: List[Dict[str, Any]] = []
    for chunk in chunks:
        # Split on sentence boundaries (., !, ?, newline)
        raw_sentences = re.split(r'(?<=[.!?\n])\s+', chunk["text"])
        for sent in raw_sentences:
            sent = sent.strip()
            if len(sent) > 15:  # skip very short fragments
                sentence_pool.append({
                    "sentence": sent,
                    "source": chunk["source"],
                    "artifact_type": chunk.get("artifact_type", "general"),
                })

    if not sentence_pool:
        return chunks  # nothing to compress → return originals

    # Embed all sentences at once
    sent_texts = [s["sentence"] for s in sentence_pool]
    sent_vecs = model.encode(sent_texts, show_progress_bar=False)

    # Vectorised cosine similarity using numpy (much faster than a Python loop)
    query_norm = np.linalg.norm(query_vec)  # type: ignore
    if query_norm == 0:
        return chunks

    sent_norms = np.linalg.norm(sent_vecs, axis=1) + 1e-9  # type: ignore
    similarities = np.dot(sent_vecs, query_vec) / (sent_norms * query_norm)  # type: ignore

    # Filter + sort in one pass using numpy
    mask = similarities >= similarity_threshold
    if not np.any(mask):  # type: ignore
        return chunks  # threshold too strict → return originals

    indices = np.where(mask)[0]  # type: ignore
    top_indices = indices[np.argsort(similarities[indices])[::-1]][:top_n_sentences]  # type: ignore

    # Repack into a single compressed chunk per unique source
    source_groups: Dict[str, List[str]] = {}
    source_types: Dict[str, str] = {}
    for idx in top_indices:
        sp = sentence_pool[idx]
        src = sp["source"]
        source_groups.setdefault(src, []).append(sp["sentence"])
        source_types[src] = sp.get("artifact_type", "general")

    compressed: List[Dict[str, Any]] = []
    for src, sents in source_groups.items():
        compressed.append({
            "text": "\n".join(sents),
            "source": src,
            "distance": 0.0,  # already filtered by similarity
            "artifact_type": source_types.get(src, "general"),
        })

    return compressed


def retrieve_context(
    collection_name: str,
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Full retrieval pipeline:
      1. Detect artifact category from query  (hierarchical)
      2. Semantic search (always)
      3. Metadata-filtered search (if category detected)  (hierarchical)
      4. Hybrid merge + dedup
      5. Context compression
    Falls back to plain semantic search if metadata is absent.
    Signature unchanged for backward compatibility.
    """
    chroma = _get_chroma()
    try:
        collection = chroma.get_collection(collection_name)
    except Exception as exc:
        raise ValueError(f"Collection '{collection_name}' not found: {exc}")

    model = _get_embed_model()
    query_vec = model.encode([query], show_progress_bar=False)  # shape (1, 384)
    query_embedding = query_vec.tolist()

    # ── Step A: always do semantic search ─────────────────────────────────
    semantic_hits = _raw_query(collection, query_embedding, n=top_k)

    # ── Step B: detect artifact category ─────────────────────────────────
    detected_category = _detect_query_artifact(query)

    if detected_category is not None:
        # ── Step C: hierarchical filtered search ─────────────────────────
        filtered_hits = _raw_query(
            collection, query_embedding, n=top_k,
            where={"artifact_type": detected_category},
        )
        # ── Step D: hybrid merge ─────────────────────────────────────────
        merged = _merge_and_deduplicate(semantic_hits, filtered_hits, top_k)
    else:
        merged = semantic_hits

    # ── Step E: context compression (reuse query_vec to avoid re-encoding) ──
    compressed = _compress_context(
        query, merged, top_n_sentences=8, similarity_threshold=0.25,
        query_vec=query_vec[0],
    )

    return compressed


# ══════════════════════════════════════════════════════════════════════════════
#  4. PROMPT BUILDER  (for Llama 3 / any local LLM)
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """\
You are a digital forensics assistant. You are STRICTLY LIMITED to answering \
questions about the forensic disk-image analysis report provided in the context below.

CRITICAL RULES — NEVER VIOLATE THESE:
1. ONLY use the context chunks provided below to form your answer. NEVER use \
   your own knowledge, training data, or any external information.
2. If the user's question is NOT about the forensic report, uploaded file, \
   disk image analysis, files, hashes, timeline, artifacts, or evidence, \
   you MUST respond EXACTLY with:
   "🚫 I can only answer questions related to the uploaded forensic evidence. \
Please ask about the analysis report, files, timeline, or artifacts."
3. NEVER answer general knowledge, coding, math, trivia, jokes, greetings, \
   or any question unrelated to the forensic data.
4. If the question IS relevant to forensics but the answer is not found in \
   the context, say: "I don't have enough data in the current report to answer that."
5. Be precise: cite file names, paths, timestamps, and hashes when available.
6. Use bullet points and keep answers concise.
7. If someone asks "who are you" or "what can you do", respond ONLY with:
   "I am a forensic evidence assistant. I can answer questions about the \
uploaded forensic disk image analysis — files, hashes, timeline, deleted items, \
encrypted data, network artifacts, and more."
"""

# ── Keywords that indicate a forensic-relevant query ──────────────────────────
_FORENSIC_KEYWORDS = {
    "file", "files", "deleted", "suspicious", "malware", "hash", "sha256",
    "md5", "encrypted", "encryption", "network", "artifact", "timeline",
    "partition", "filesystem", "disk", "image", "inode", "directory",
    "extension", "exe", "dll", "bat", "report", "summary", "overview",
    "evidence", "forensic", "analysis", "scan", "size", "path", "folder",
    "created", "modified", "accessed", "timestamp", "date", "time",
    "block", "volume", "sector", "cluster", "ntfs", "fat", "ext4",
    "threat", "dangerous", "trojan", "virus", "ransomware", "hidden",
    "recovered", "carved", "exfiltrat", "ip", "dns", "hosts", "url",
    "connection", "browser", "history", "registry", "log", "event",
    "count", "total", "how many", "list", "show", "what", "which",
    "tell me", "describe", "explain", "detail", "uploaded", "scanned",
}

_IRRELEVANT_RESPONSE = (
    "🚫 I can only answer questions related to the uploaded forensic evidence "
    "files. Please ask something about the analysis report — for example:\n\n"
    "• *What suspicious files were found?*\n"
    "• *Show me the timeline of events*\n"
    "• *Are there any deleted files?*\n"
    "• *List encrypted items*\n"
    "• *Give me a summary of the report*"
)

# ── Patterns that are clearly NOT forensic questions ──────────────────────────
_IRRELEVANT_PATTERNS = {
    "hello", "hi", "hey", "good morning", "good evening", "good night",
    "how are you", "what's up", "thank you", "thanks", "bye", "goodbye",
    "who made you", "who created you", "tell me a joke", "joke",
    "what is python", "write code", "write a program", "capital of",
    "president of", "weather", "recipe", "song", "movie", "play",
    "calculate", "solve", "math", "translate", "meaning of life",
    "what is ai", "what is machine learning", "write an essay",
    "poem", "story", "sing", "draw", "paint", "game",
}


def _is_relevant_query(query: str) -> bool:
    """
    Check whether a user query is related to the forensic report.
    Returns True if it looks forensic-relevant, False otherwise.
    Uses a two-pass approach: first reject obvious off-topic queries,
    then check for forensic keywords.
    """
    q = query.lower().strip()

    # Pass 1: reject obvious irrelevant / casual chat
    for pattern in _IRRELEVANT_PATTERNS:
        if q == pattern or q.startswith(pattern + " ") or q.startswith(pattern + "?") or q.startswith(pattern + ","):
            return False

    # Pass 2: direct forensic keyword match
    for kw in _FORENSIC_KEYWORDS:
        if kw in q:
            return True

    # Pass 3: very short queries (< 3 words) that don't match any keyword → irrelevant
    if len(q.split()) < 3:
        return False

    # Pass 4: if the query mentions data-like terms
    if any(w in q for w in ["the", "this", "report", "upload", "drive", "found", "detect"]):
        return True

    return False


def build_llm_prompt(query: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Format the retrieved chunks + user question into a prompt suitable for
    Llama 3 (or any instruct-tuned model).
    """
    context_block = "\n\n---\n\n".join(c["text"] for c in context_chunks)

    prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"### Forensic Report Context\n{context_block}\n\n"
        f"### Question\n{query}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    return prompt


def generate_fallback_answer(query: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Rule-based fallback that synthesises an answer from retrieved context
    without needing an LLM. Used when Llama 3 is not yet connected.
    """
    if not context_chunks:
        return "No relevant information was found in the forensic report for your query."

    query_lower = query.lower()

    # ── Specific intent handlers ──────────────────────────────────────────
    # How many files?
    if any(kw in query_lower for kw in ["how many files", "total files", "file count", "number of files"]):
        for c in context_chunks:
            if "total files" in c["text"].lower():
                for line in c["text"].split("\n"):
                    if "total files" in line.lower():
                        return f"Based on the forensic report:\n\n{line.strip()}"

    # Suspicious files
    if any(kw in query_lower for kw in ["suspicious", "malware", "threat", "dangerous"]):
        suspicious = [c for c in context_chunks if "SUSPICIOUS" in c["text"] or "suspicious" in c["text"].lower()]
        if suspicious:
            answer = "🔴 **Suspicious files detected in the report:**\n\n"
            for c in suspicious:
                answer += f"```\n{c['text']}\n```\n\n"
            return answer.strip()

    # Deleted files
    if any(kw in query_lower for kw in ["deleted", "removed", "erased"]):
        deleted = [c for c in context_chunks if "Deleted: Yes" in c["text"]]
        if deleted:
            answer = "🗑️ **Deleted files found:**\n\n"
            for c in deleted:
                answer += f"```\n{c['text']}\n```\n\n"
            return answer.strip()

    # Encrypted
    if any(kw in query_lower for kw in ["encrypt", "encrypted", "encryption", "locked"]):
        enc = [c for c in context_chunks if "ENCRYPTED" in c["text"] or "encrypt" in c["text"].lower()]
        if enc:
            answer = "🔐 **Encrypted items:**\n\n"
            for c in enc:
                answer += f"```\n{c['text']}\n```\n\n"
            return answer.strip()

    # Timeline
    if any(kw in query_lower for kw in ["timeline", "recent", "latest", "when", "chronolog"]):
        tl = [c for c in context_chunks if "TIMELINE" in c["text"]]
        if tl:
            answer = "🕒 **Timeline events:**\n\n"
            for c in tl:
                answer += f"```\n{c['text']}\n```\n\n"
            return answer.strip()

    # Network
    if any(kw in query_lower for kw in ["network", "hosts", "dns", "ip", "connection"]):
        net = [c for c in context_chunks if "NETWORK" in c["text"] or "network" in c["text"].lower()]
        if net:
            answer = "🌐 **Network artifacts:**\n\n"
            for c in net:
                answer += f"```\n{c['text']}\n```\n\n"
            return answer.strip()

    # Overview / summary
    if any(kw in query_lower for kw in ["summary", "overview", "report", "tell me about"]):
        overview = [c for c in context_chunks if c["source"] == "overview"]
        if overview:
            return f"📋 **Report Overview:**\n\n```\n{overview[0]['text']}\n```"

    # ── Generic: return top-3 relevant chunks ────────────────────────────
    answer = "Based on the forensic report, here is the most relevant information:\n\n"
    for i, c in enumerate(context_chunks[:3], 1):
        answer += f"**[{i}] Source: {c['source']}**\n```\n{c['text']}\n```\n\n"

    return answer.strip()


# ══════════════════════════════════════════════════════════════════════════════
#  5. PUBLIC API  — single-call convenience
# ══════════════════════════════════════════════════════════════════════════════

def _call_ollama(prompt: str, model: str = "llama3") -> Optional[str]:
    """
    Call a local Ollama instance running Llama 3.
    Returns the generated text, or None if Ollama is unreachable.
    """
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 300, "temperature": 0.3},
            },
            timeout=60,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
        print(f"[RAG] Ollama returned status {resp.status_code}")
        return None
    except requests.ConnectionError:
        print("[RAG] Ollama not reachable at localhost:11434 — using fallback")
        return None
    except Exception as exc:
        print(f"[RAG] Ollama error: {exc}")
        return None


def ask(
    collection_name: str,
    query: str,
    top_k: int = 5,
    use_llm: bool = True,
) -> Dict[str, Any]:
    """
    End-to-end: check relevance → retrieve context → build prompt → generate answer.
    Irrelevant queries are rejected before any retrieval happens.
    When use_llm=True (default), tries Ollama/Llama 3 first; falls back to rule-based.
    """
    # ── Step 0: relevance guard ───────────────────────────────────────────
    if not _is_relevant_query(query):
        return {
            "answer": _IRRELEVANT_RESPONSE,
            "prompt": "",
            "context": [],
            "collection": collection_name,
            "rejected": True,
        }

    # ── Step 1: retrieve context from ChromaDB ────────────────────────────
    context_chunks = retrieve_context(collection_name, query, top_k=top_k)

    # If no chunks survived the distance threshold, the query doesn't
    # match anything meaningful in the forensic report.
    if not context_chunks:
        return {
            "answer": (
                "I don't have enough relevant information in the forensic report "
                "to answer that question. Try asking about specific files, the "
                "timeline, deleted items, encrypted data, or network artifacts."
            ),
            "prompt": "",
            "context": [],
            "collection": collection_name,
            "rejected": True,
        }

    prompt = build_llm_prompt(query, context_chunks)

    # ── Step 2: generate answer ───────────────────────────────────────────
    answer = None
    if use_llm:
        answer = _call_ollama(prompt, model="llama3")

    # Fallback to rule-based if LLM is off or unreachable
    if answer is None:
        answer = generate_fallback_answer(query, context_chunks)

    return {
        "answer": answer,
        "prompt": prompt,
        "context": [{"text": c["text"], "source": c["source"]} for c in context_chunks],
        "collection": collection_name,
        "rejected": False,
    }
