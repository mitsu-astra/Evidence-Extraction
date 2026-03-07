"""
SUPABASE CLIENT — Database Integration for Forensic Analysis
Handles storing analysis results, user data, and report history in Supabase
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Graceful import with fallback
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    create_client = None  # type: ignore
    Client = None  # type: ignore

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_supabase_client: Any = None


def get_supabase_client() -> Any:
    """Get or create Supabase client instance."""
    if not HAS_SUPABASE:
        raise ImportError("Supabase not installed. Run: pip install supabase")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase credentials not configured. "
            "Please add SUPABASE_URL and SUPABASE_KEY to .env file"
        )
    
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)  # type: ignore
        print("[Supabase] Connected successfully")
    
    return _supabase_client


def is_configured() -> bool:
    """Check if Supabase is properly configured."""
    return HAS_SUPABASE and bool(SUPABASE_URL) and bool(SUPABASE_KEY)


# ═══════════════════════════════════════════════════════════════════════════
#  DATABASE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

def save_analysis_report(
    analysis_id: str,
    image_name: str,
    report_data: Dict[str, Any],
    summary: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Save forensic analysis report to Supabase.
    
    Args:
        analysis_id: Unique identifier for the analysis
        image_name: Name of the disk image analyzed
        report_data: Complete forensic report JSON
        summary: Text summary of findings
        user_id: Optional user identifier
    
    Returns:
        Response from Supabase insert operation
    """
    if not is_configured():
        raise RuntimeError("Supabase not configured")
    
    supabase = get_supabase_client()
    
    data = {
        "analysis_id": analysis_id,
        "image_name": image_name,
        "report_data": report_data,
        "summary": summary,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "file_count": report_data.get("file_count", 0),
        "total_size": report_data.get("total_size", 0),
    }
    
    try:
        response = supabase.table("forensic_reports").insert(data).execute()
        print(f"[Supabase] Saved analysis report: {analysis_id}")
        return response.data  # type: ignore
    except Exception as e:
        print(f"[Supabase] Error saving report: {e}")
        raise


def get_analysis_report(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific analysis report by ID.
    
    Args:
        analysis_id: Unique identifier for the analysis
    
    Returns:
        Report data or None if not found
    """
    if not is_configured():
        raise RuntimeError("Supabase not configured")
    
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("forensic_reports").select("*").eq("analysis_id", analysis_id).execute()
        return response.data[0] if response.data else None  # type: ignore
    except Exception as e:
        print(f"[Supabase] Error retrieving report: {e}")
        return None


def list_analysis_reports(
    limit: int = 50,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all analysis reports, optionally filtered by user.
    
    Args:
        limit: Maximum number of reports to return
        user_id: Optional user filter
    
    Returns:
        List of report summaries
    """
    if not is_configured():
        raise RuntimeError("Supabase not configured")
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table("forensic_reports").select("analysis_id, image_name, created_at, file_count, total_size")
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        response = query.order("created_at", desc=True).limit(limit).execute()
        return response.data  # type: ignore
    except Exception as e:
        print(f"[Supabase] Error listing reports: {e}")
        return []


def delete_analysis_report(analysis_id: str) -> bool:
    """
    Delete an analysis report from Supabase.
    
    Args:
        analysis_id: Unique identifier for the analysis
    
    Returns:
        True if successful, False otherwise
    """
    if not is_configured():
        raise RuntimeError("Supabase not configured")
    
    supabase = get_supabase_client()
    
    try:
        supabase.table("forensic_reports").delete().eq("analysis_id", analysis_id).execute()
        print(f"[Supabase] Deleted analysis report: {analysis_id}")
        return True
    except Exception as e:
        print(f"[Supabase] Error deleting report: {e}")
        return False


def save_rag_query(
    analysis_id: str,
    query: str,
    response: str,
    chunks_used: int
) -> Dict[str, Any]:
    """
    Save RAG query history to Supabase for analytics.
    
    Args:
        analysis_id: Associated analysis ID
        query: User's question
        response: RAG system's answer
        chunks_used: Number of context chunks retrieved
    
    Returns:
        Response from Supabase insert operation
    """
    if not is_configured():
        raise RuntimeError("Supabase not configured")
    
    supabase = get_supabase_client()
    
    data = {
        "analysis_id": analysis_id,
        "query": query,
        "response": response,
        "chunks_used": chunks_used,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    try:
        result = supabase.table("rag_queries").insert(data).execute()
        return result.data  # type: ignore
    except Exception as e:
        print(f"[Supabase] Error saving RAG query: {e}")
        raise


# ═══════════════════════════════════════════════════════════════════════════
#  DATABASE SCHEMA SETUP (Run once to create tables)
# ═══════════════════════════════════════════════════════════════════════════

def get_schema_sql() -> str:
    """
    Returns SQL schema for creating required Supabase tables.
    Copy and run this in your Supabase SQL Editor.
    """
    return """
-- Forensic Reports Table
CREATE TABLE IF NOT EXISTS forensic_reports (
    id BIGSERIAL PRIMARY KEY,
    analysis_id TEXT UNIQUE NOT NULL,
    image_name TEXT NOT NULL,
    report_data JSONB NOT NULL,
    summary TEXT,
    user_id TEXT,
    file_count INTEGER DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RAG Queries Table
CREATE TABLE IF NOT EXISTS rag_queries (
    id BIGSERIAL PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    chunks_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (analysis_id) REFERENCES forensic_reports(analysis_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_forensic_reports_analysis_id ON forensic_reports(analysis_id);
CREATE INDEX IF NOT EXISTS idx_forensic_reports_user_id ON forensic_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_forensic_reports_created_at ON forensic_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rag_queries_analysis_id ON rag_queries(analysis_id);

-- Enable Row Level Security (optional, for multi-user)
ALTER TABLE forensic_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_queries ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for now - customize based on your needs)
CREATE POLICY "Enable all access for forensic_reports" ON forensic_reports FOR ALL USING (true);
CREATE POLICY "Enable all access for rag_queries" ON rag_queries FOR ALL USING (true);
"""


if __name__ == "__main__":
    print("═" * 80)
    print(" SUPABASE CLIENT - SETUP INSTRUCTIONS")
    print("═" * 80)
    print("\n1. Go to https://app.supabase.com and create a project")
    print("2. Copy your project URL and anon key from Settings > API")
    print("3. Add them to the .env file in this directory")
    print("\n4. Run this SQL in your Supabase SQL Editor:\n")
    print(get_schema_sql())
    print("\n" + "═" * 80)
    
    if is_configured():
        print("\n✓ Supabase is configured!")
        print(f"URL: {SUPABASE_URL}")
        try:
            client = get_supabase_client()
            print("✓ Connection successful!")
        except Exception as e:
            print(f"✗ Connection failed: {e}")
    else:
        print("\n✗ Supabase not configured yet. Please update .env file.")
