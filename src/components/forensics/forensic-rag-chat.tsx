import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

/* ── Types ─────────────────────────────────────────────────────────────────── */
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sources?: { text: string; source: string }[];
}

/* ── Component ─────────────────────────────────────────────────────────────── */
const ForensicRagChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'system',
      content:
        '🔍 **Forensic RAG Assistant** ready.\n\nAsk me anything about the uploaded evidence — files, timeline, suspicious items, encrypted data, network artifacts, etc.',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ragReady, setRagReady] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  /* auto-scroll — use rAF for smoother performance */
  useEffect(() => {
    requestAnimationFrame(() => {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    });
  }, [messages]);

  /* poll RAG readiness — stops polling once ready */
  useEffect(() => {
    let cancelled = false;
    let intervalId: ReturnType<typeof setInterval> | null = null;
    const check = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/rag/status');
        if (!res.ok) return;
        const data = await res.json();
        if (!cancelled) {
          setRagReady(data.ready);
          // Stop polling once RAG is ready — no need to keep hitting the server
          if (data.ready && intervalId) {
            clearInterval(intervalId);
            intervalId = null;
          }
        }
      } catch {
        /* backend offline */
      }
    };
    check();
    intervalId = setInterval(check, 3000);
    return () => {
      cancelled = true;
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  /* ── send message ──────────────────────────────────────────────────────── */
  const send = async () => {
    const query = input.trim();
    if (!query || isLoading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:5000/api/rag/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 5, use_llm: true }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || 'Request failed');
      }

      const data = await res.json();

      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: data.rejected ? 'system' : 'assistant',
        content: data.answer,
        timestamp: new Date(),
        sources: data.rejected ? undefined : data.context,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `⚠ ${err instanceof Error ? err.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  /* ── quick-prompt chips ────────────────────────────────────────────────── */
  const quickPrompts = [
    'Give me a summary of the report',
    'List all suspicious files',
    'Are there any deleted files?',
    'Show encrypted items',
    'What are the network artifacts?',
    'Show the timeline of events',
  ];

  /* ── render helpers ────────────────────────────────────────────────────── */
  const renderMarkdown = (text: string) => {
    // very lightweight: bold, code blocks, bullet lists
    let html = text
      .replace(/```([\s\S]*?)```/g, '<pre class="bg-black/50 rounded p-2 text-xs overflow-x-auto my-1 whitespace-pre-wrap">$1</pre>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^• /gm, '&bull; ')
      .replace(/\n/g, '<br/>');
    return <span dangerouslySetInnerHTML={{ __html: html }} />;
  };

  return (
    <div className="flex flex-col h-[75vh] rounded-xl overflow-hidden border border-gray-700/60 bg-black/40 backdrop-blur-md">
      {/* ── Header ───────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3 px-5 py-3 border-b border-gray-700/60 bg-black/30">
        <div className={cn('w-2.5 h-2.5 rounded-full', ragReady ? 'bg-green-500 animate-pulse' : 'bg-yellow-500')} />
        <h3 className="text-sm font-bold tracking-widest uppercase text-gray-200">
          Forensic RAG Assistant
        </h3>
        <span className="ml-auto text-[10px] tracking-wider text-gray-500 uppercase">
          {ragReady ? 'Ready — ChromaDB connected' : 'Waiting for analysis…'}
        </span>
      </div>

      {/* ── Messages ─────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4 scrollbar-thin scrollbar-thumb-gray-700">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={cn(
              'max-w-[85%] rounded-lg px-4 py-3 text-sm leading-relaxed',
              msg.role === 'user'
                ? 'ml-auto bg-red-900/40 border border-red-800/50 text-gray-100'
                : msg.role === 'system'
                ? 'mx-auto bg-gray-800/60 border border-gray-700/40 text-gray-300 text-center text-xs'
                : 'mr-auto bg-gray-800/60 border border-gray-700/40 text-gray-200'
            )}
          >
            {msg.role === 'assistant' || msg.role === 'system'
              ? renderMarkdown(msg.content)
              : msg.content}

            {/* sources accordion */}
            {msg.sources && msg.sources.length > 0 && (
              <details className="mt-2 text-[10px] text-gray-500">
                <summary className="cursor-pointer hover:text-gray-400 uppercase tracking-widest">
                  Sources ({msg.sources.length})
                </summary>
                <ul className="mt-1 space-y-1 pl-3">
                  {msg.sources.map((s, i) => (
                    <li key={i} className="text-gray-500">
                      <span className="text-gray-400 font-medium">{s.source}</span>
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="mr-auto bg-gray-800/60 border border-gray-700/40 rounded-lg px-4 py-3 text-sm text-gray-400 flex items-center gap-2">
            <span className="animate-pulse">●</span>
            <span className="animate-pulse delay-150">●</span>
            <span className="animate-pulse delay-300">●</span>
            <span className="ml-2 text-xs">Searching forensic data…</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── Quick prompts ────────────────────────────────────────────────── */}
      {messages.length <= 2 && (
        <div className="px-5 pb-2 flex flex-wrap gap-2">
          {quickPrompts.map((p) => (
            <button
              key={p}
              onClick={() => {
                setInput(p);
                setTimeout(() => {
                  setInput(p);
                  send();
                }, 50);
              }}
              disabled={!ragReady || isLoading}
              className="text-[10px] px-3 py-1.5 rounded-full border border-gray-700 bg-gray-800/60 text-gray-400 hover:border-red-700 hover:text-gray-200 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {p}
            </button>
          ))}
        </div>
      )}

      {/* ── Input ────────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-2 px-4 py-3 border-t border-gray-700/60 bg-black/30">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={ragReady ? 'Ask about the forensic report…' : 'Upload & analyze a file first…'}
          disabled={!ragReady || isLoading}
          className="flex-1 bg-gray-800/60 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-red-700 transition-colors disabled:opacity-40"
        />
        <button
          onClick={send}
          disabled={!ragReady || isLoading || !input.trim()}
          className="px-5 py-2.5 rounded-lg bg-red-800 hover:bg-red-700 text-white text-sm font-bold tracking-wider uppercase transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isLoading ? '…' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ForensicRagChat;
