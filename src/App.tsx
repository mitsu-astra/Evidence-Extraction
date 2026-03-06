import { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Home, Upload, BarChart3, FileText } from 'lucide-react';
import './App.css';

// ── Hero page — eagerly loaded (first screen the user sees) ─────────────────
import ForensicAnalysisHero from './components/forensics/forensic-analysis-hero';

// ── Analysis page — lazy loaded (separate JS chunks, only downloaded when
//    the user navigates to /analysis — not needed on the hero page at all)
const ForensicFileUpload = lazy(
  () => import('./components/forensics/forensic-file-upload')
);
const ForensicAnalysisDashboard = lazy(
  () => import('./components/forensics/forensic-analysis-dashboard')
);
const ForensicRagChat = lazy(
  () => import('./components/forensics/forensic-rag-chat')
);
// LetterGlitch: canvas animation — only on /analysis, keep it out of the
// initial bundle so the hero page is not blocked by canvas setup code
const LetterGlitch = lazy(
  () => import('./components/ui/LetterGlitch')
);
// NavBar imports framer-motion — lazy-load to keep it out of the hero bundle
const NavBar = lazy(
  () => import('./components/ui/tubelight-navbar').then((m) => ({ default: m.NavBar }))
);

// ── CARD COLORS — edit these hex values to change card appearance ──────────
const CARD_COLORS = {
  bg:     'rgba(0, 0, 0, 0.4)',
  border: '#4a2020',
  text:   '#ffffff',
};

const navItems = [
  { name: 'Home', url: '/', icon: Home },
  { name: 'Upload', url: '/analysis', icon: Upload },
  { name: 'Analysis', url: '/analysis', icon: BarChart3 },
  { name: 'Report', url: '/analysis', icon: FileText },
];

// ── Shared analysis result type ──────────────────────────────────────────────
export interface AnalysisResultData {
  analysisId: string;
  fileName: string;
  timestamp: string;
  status: 'analyzing' | 'completed' | 'error';
  progress: number;
  message?: string;
  results?: any;
  error?: string;
}

// ── Hero / Landing Page ──────────────────────────────────────────────────────
function HeroPage() {
  const navigate = useNavigate();
  return <ForensicAnalysisHero onBeginAnalysis={() => navigate('/analysis')} />;
}

// ── Home tab placeholder ─────────────────────────────────────────────────────
function HomeTab() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center px-4">
      <div className="mb-6 text-red-500">
        <svg xmlns="http://www.w3.org/2000/svg" className="w-16 h-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-3-3v6M4.5 12a7.5 7.5 0 1115 0 7.5 7.5 0 01-15 0z" />
        </svg>
      </div>
      <h2 className="text-4xl font-bold tracking-widest text-gray-100 mb-3" style={{ fontFamily: 'Oswald, sans-serif' }}>FORENSIC CORE</h2>
      <p className="text-gray-500 text-sm tracking-widest uppercase mb-8">Digital Evidence Analysis Suite v2.1</p>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl">
        {[
          { label: 'Supported Formats', value: 'RAW · DD · E01 · IMG · ISO' },
          { label: 'Export Formats', value: 'PDF · DOCX' },
          { label: 'Status', value: 'READY' },
        ].map((card) => (
          <div
            key={card.label}
            className="p-5 text-center"
            style={{
              background: CARD_COLORS.bg,
              border: `1px solid ${CARD_COLORS.border}`,
              color: CARD_COLORS.text,
            }}
          >
            <p className="text-[10px] tracking-[0.2em] uppercase mb-3" style={{ color: 'rgba(255,255,255,0.5)' }}>{card.label}</p>
            <p className="text-sm font-bold tracking-widest uppercase">{card.value}</p>
          </div>
        ))}
      </div>
      <p className="mt-10 text-gray-600 text-xs tracking-widest uppercase">Select a tab above to get started</p>
    </div>
  );
}

// ── Coming Soon placeholder ───────────────────────────────────────────────────
function ComingSoon({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
      <p className="text-xs text-gray-600 tracking-widest uppercase mb-3">{label}</p>
      <p className="text-2xl font-bold text-gray-500">Coming Soon</p>
    </div>
  );
}

// ── Fallback shown while lazy analysis chunks are downloading ────────────────
function AnalysisLoadingFallback() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div className="w-7 h-7 border-2 border-red-800 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-600 text-[10px] tracking-[0.25em] uppercase">Loading…</p>
      </div>
    </div>
  );
}

// ── Analysis Page ────────────────────────────────────────────────────────────
function AnalysisPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Upload');
  // Lift analysis state so it persists across tab switches
  const [analysisResult, setAnalysisResult] = useState<AnalysisResultData | null>(null);

  // Callback: after upload + analysis finishes → store result & switch to Analysis tab
  const handleAnalysisComplete = useCallback((result: AnalysisResultData) => {
    setAnalysisResult(result);
    setActiveTab('Analysis');
  }, []);

  // Also try to load the latest result from the backend on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('http://localhost:5001/api/status');
        if (!res.ok) return;
        const data = await res.json();
        if (data.status === 'completed' && data.results) {
          setAnalysisResult({
            analysisId: data.current || '',
            fileName: data.results?.image_path?.split(/[\\/]/).pop() || 'Unknown',
            timestamp: data.results?.timestamp || new Date().toISOString(),
            status: 'completed',
            progress: 100,
            results: data.results,
          });
        }
      } catch { /* backend offline */ }
    })();
  }, []);

  return (
    <Suspense fallback={<AnalysisLoadingFallback />}>
    <div className="min-h-screen text-gray-100">
      {/* Navbar */}
      <NavBar items={navItems} activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Go Back Button */}
      <button
        onClick={() => navigate('/')}
        className="fixed top-6 left-6 z-50 flex items-center gap-2 px-4 py-2 bg-gray-900 border border-gray-700 hover:border-red-500 text-gray-300 hover:text-red-400 rounded-lg text-sm font-semibold transition-all duration-200 shadow-lg"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Go Back
      </button>

      {/* Background */}
      <div className="fixed inset-0 z-0">
        <LetterGlitch glitchSpeed={120} centerVignette={true} outerVignette={false} smooth={true} glitchColors={['#8b1515', '#d63838', '#6b0f0f']} />
      </div>

      {/* Tab Content */}
      <div className="relative z-10 min-h-screen pt-24 max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'Home' && <HomeTab />}

        {/* Upload tab uses display:none instead of unmounting so the polling
            loop and upload state survive tab switches */}
        <div style={{ display: activeTab === 'Upload' ? 'block' : 'none' }}>
          <div className="space-y-8">
            <section>
              <h2 className="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">Upload Evidence</h2>
              <ForensicFileUpload onAnalysisComplete={handleAnalysisComplete} />
            </section>

            {/* Download section — only visible after analysis completes */}
            {analysisResult?.status === 'completed' && (
              <section>
                <h2 className="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">Export Report</h2>
                <ReportDownloadButtons analysisId={analysisResult.analysisId} />
              </section>
            )}

            <section>
              <h2 className="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">Analysis Results</h2>
              <ForensicAnalysisDashboard analysisResult={analysisResult} />
            </section>
          </div>
        </div>

        <div style={{ display: activeTab === 'Analysis' ? 'block' : 'none' }}>
          <div className="space-y-6">
            <section>
              <h2 className="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">
                🤖 Forensic RAG Assistant
              </h2>
              <ForensicRagChat analysisReady={analysisResult?.status === 'completed'} />
            </section>
          </div>
        </div>

        {activeTab === 'Report' && (
          <div className="space-y-8">
            <section>
              <h2 className="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">📋 Forensic Report</h2>
              {analysisResult && analysisResult.status === 'completed' ? (
                <div className="space-y-6">
                  {/* Report summary card */}
                  <div className="bg-black/40 border border-gray-700 rounded-xl p-6">
                    <h3 className="text-lg font-bold text-gray-200 mb-4 tracking-wider uppercase">Report Summary</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                      <div><span className="text-gray-500">File:</span> <span className="text-gray-200 font-semibold">{analysisResult.fileName}</span></div>
                      <div><span className="text-gray-500">Analysis ID:</span> <span className="text-gray-200 font-mono">{analysisResult.analysisId}</span></div>
                      <div><span className="text-gray-500">Date:</span> <span className="text-gray-200">{analysisResult.timestamp}</span></div>
                      <div><span className="text-gray-500">Status:</span> <span className="text-green-400 font-bold">COMPLETED</span></div>
                    </div>
                  </div>
                  {/* Dashboard */}
                  <ForensicAnalysisDashboard analysisResult={analysisResult} />
                  {/* Download buttons */}
                  <ReportDownloadButtons analysisId={analysisResult.analysisId} />
                </div>
              ) : (
                <div className="text-center py-16 text-gray-500">
                  <p className="text-lg">No report available yet.</p>
                  <p className="text-sm mt-2">Upload and analyze a forensic image first.</p>
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
    </Suspense>
  );
}

// ── Report Download Buttons ──────────────────────────────────────────────────
function ReportDownloadButtons({ analysisId }: { analysisId?: string }) {
  const [downloading, setDownloading] = useState<'pdf' | 'docx' | null>(null);
  const [dlError, setDlError] = useState<string | null>(null);

  const handleDownload = async (format: 'pdf' | 'docx') => {
    setDownloading(format);
    setDlError(null);
    try {
      const response = await fetch(`http://localhost:5001/api/export/${format}`);
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.error || `Export failed (${response.status})`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `forensic_report_${analysisId || 'report'}.${format === 'pdf' ? 'pdf' : 'docx'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      setDlError(e instanceof Error ? e.message : 'Download failed');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="bg-black/40 border border-gray-700 rounded-xl p-6">
      <p className="text-xs text-gray-500 tracking-widest uppercase mb-5">Choose export format</p>
      <div className="flex flex-wrap gap-4">
        <button
          onClick={() => handleDownload('pdf')}
          disabled={downloading !== null}
          className="flex items-center gap-3 px-6 py-4 rounded-lg bg-red-900/50 hover:bg-red-800/70 border border-red-700/60 hover:border-red-500 text-white font-semibold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed min-w-[180px] justify-center"
        >
          {downloading === 'pdf' ? (
            <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Generating PDF…</span></>
          ) : (
            <><span className="text-xl">📄</span><span>Download PDF</span></>
          )}
        </button>
        <button
          onClick={() => handleDownload('docx')}
          disabled={downloading !== null}
          className="flex items-center gap-3 px-6 py-4 rounded-lg bg-gray-800/70 hover:bg-gray-700/70 border border-gray-600/60 hover:border-gray-400 text-white font-semibold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed min-w-[180px] justify-center"
        >
          {downloading === 'docx' ? (
            <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Generating DOCX…</span></>
          ) : (
            <><span className="text-xl">📝</span><span>Download DOCX</span></>
          )}
        </button>
      </div>
      {dlError && (
        <p className="mt-3 text-red-400 text-xs">⚠ {dlError}</p>
      )}
    </div>
  );
}

// ── Root App ─────────────────────────────────────────────────────────────────
function App() {
  return (
    <Routes>
      <Route path="/" element={<HeroPage />} />
      <Route path="/analysis" element={<AnalysisPage />} />
    </Routes>
  );
}

export default App;
