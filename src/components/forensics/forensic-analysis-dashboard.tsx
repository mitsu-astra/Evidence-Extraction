import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import type { AnalysisResultData } from '../../App';

interface AnalysisResult {
  id: string;
  fileName: string;
  status: 'analyzing' | 'completed' | 'error';
  progress: number;
  message?: string;
  summary?: {
    totalFiles: number;
    recoveredFiles: number;
    deletedFiles: number;
    suspiciousFiles: number;
    encryptedItems: number;
    networkArtifacts: number;
    filesbyType: Record<string, number>;
  };
  error?: string;
  timestamp: string;
}

interface ForensicAnalysisDashboardProps {
  analysisResult?: AnalysisResultData | null;
}

/**
 * Forensic Analysis Dashboard Component
 * Displays real-time analysis progress and results
 */
export const ForensicAnalysisDashboard: React.FC<ForensicAnalysisDashboardProps> = ({ analysisResult }) => {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResult | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [detailedResults, setDetailedResults] = useState<any>(null);

  // When parent passes a completed analysis result, fetch full data from backend
  useEffect(() => {
    if (!analysisResult || analysisResult.status !== 'completed') return;
    (async () => {
      try {
        const res = await fetch('http://localhost:5000/api/results');
        if (!res.ok) return;
        const data = await res.json();
        setDetailedResults(data);
        // Build a display-friendly object
        const display: AnalysisResult = {
          id: analysisResult.analysisId,
          fileName: analysisResult.fileName,
          status: 'completed',
          progress: 100,
          timestamp: analysisResult.timestamp,
          summary: {
            totalFiles: data.summary?.total_files || 0,
            recoveredFiles: data.summary?.total_files || 0,
            deletedFiles: data.summary?.total_deleted_files || 0,
            suspiciousFiles: data.summary?.suspicious_files_count || 0,
            encryptedItems: data.summary?.encrypted_items_count || 0,
            networkArtifacts: data.summary?.network_artifacts_count || 0,
            filesbyType: data.extensions || {},
          },
        };
        setSelectedAnalysis(display);
        setAnalyses((prev) => {
          const exists = prev.find((a) => a.id === display.id);
          if (exists) return prev.map((a) => (a.id === display.id ? display : a));
          return [display, ...prev];
        });
      } catch { /* backend offline */ }
    })();
  }, [analysisResult]);

  useEffect(() => {
    // Listen for file upload events
    const handleFileUpload = (event: any) => {
      const newAnalysis: AnalysisResult = {
        id: event.detail.analysis_id || Date.now().toString(),
        fileName: event.detail.fileName || event.detail.filename || 'Unknown',
        status: 'analyzing',
        progress: 10,
        timestamp: new Date().toISOString(),
      };
      setAnalyses((prev) => [newAnalysis, ...prev]);
      setSelectedAnalysis(newAnalysis);
      setIsPolling(true);
    };

    window.addEventListener('fileUploaded', handleFileUpload);
    return () => window.removeEventListener('fileUploaded', handleFileUpload);
  }, []);

  // Polling mechanism for real-time updates
  useEffect(() => {
    if (!isPolling || !selectedAnalysis) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/analysis/${selectedAnalysis.id}/status`);
        if (!response.ok) throw new Error('Failed to fetch status');

        const data = await response.json();
        
        setSelectedAnalysis(data);
        setAnalyses((prev) =>
          prev.map((a) => (a.id === data.id ? data : a))
        );

        if (data.status === 'completed' || data.status === 'error') {
          setIsPolling(false);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isPolling, selectedAnalysis]);

  return (
    <div className={cn('w-full max-w-6xl mx-auto p-6 space-y-6')}>
      {/* Active Analysis */}
      {selectedAnalysis && (
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white">{selectedAnalysis.fileName}</h2>
              <p className="text-gray-400 text-sm">
                {new Date(selectedAnalysis.timestamp).toLocaleString()}
              </p>
            </div>
            <span
              className={cn(
                'px-3 py-1 rounded-full text-sm font-semibold',
                selectedAnalysis.status === 'analyzing' && 'bg-blue-900 text-blue-200',
                selectedAnalysis.status === 'completed' && 'bg-green-900 text-green-200',
                selectedAnalysis.status === 'error' && 'bg-red-900 text-red-200'
              )}
            >
              {selectedAnalysis.status.toUpperCase()}
            </span>
          </div>

          {selectedAnalysis.status === 'analyzing' && (
            <>
              <div className="mb-4">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-300">Analysis Progress</span>
                  <span className="text-orange-500 font-bold">{selectedAnalysis.progress}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-orange-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${selectedAnalysis.progress}%` }}
                  ></div>
                </div>
              </div>
              <p className="text-gray-400 text-sm italic">Processing evidence data...</p>
            </>
          )}

          {selectedAnalysis.status === 'completed' && selectedAnalysis.summary && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded">
                <p className="text-gray-400 text-sm">Total Files</p>
                <p className="text-2xl font-bold text-white">
                  {selectedAnalysis.summary.totalFiles}
                </p>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <p className="text-gray-400 text-sm">Deleted Files</p>
                <p className="text-2xl font-bold text-red-400">
                  {selectedAnalysis.summary.deletedFiles}
                </p>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <p className="text-gray-400 text-sm">Suspicious Files</p>
                <p className="text-2xl font-bold text-yellow-400">
                  {selectedAnalysis.summary.suspiciousFiles}
                </p>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <p className="text-gray-400 text-sm">Encrypted Items</p>
                <p className="text-2xl font-bold text-purple-400">
                  {selectedAnalysis.summary.encryptedItems}
                </p>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <p className="text-gray-400 text-sm">Network Artifacts</p>
                <p className="text-2xl font-bold text-blue-400">
                  {selectedAnalysis.summary.networkArtifacts}
                </p>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <p className="text-gray-400 text-sm">File Types</p>
                <p className="text-xl font-bold text-orange-400">
                  {Object.keys(selectedAnalysis.summary.filesbyType || {}).length}
                </p>
              </div>
            </div>
          )}

          {selectedAnalysis.status === 'error' && (
            <div className="bg-red-900 border border-red-700 p-4 rounded">
              <p className="text-red-200">{selectedAnalysis.error || 'Analysis failed'}</p>
            </div>
          )}
        </div>
      )}

      {/* Recent Analyses */}
      {analyses.length > 0 && (
        <div>
          <h3 className="text-lg font-bold text-white mb-4">Analysis History</h3>
          <div className="space-y-2">
            {analyses.map((analysis) => (
              <button
                key={analysis.id}
                onClick={() => setSelectedAnalysis(analysis)}
                className={cn(
                  'w-full p-3 rounded-lg text-left transition-colors',
                  selectedAnalysis?.id === analysis.id
                    ? 'bg-orange-900 border border-orange-500'
                    : 'bg-gray-800 border border-gray-700 hover:border-gray-600'
                )}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-white">{analysis.fileName}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(analysis.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <span className="text-sm font-bold text-orange-400">{analysis.progress}%</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {analyses.length === 0 && (
        <div className="text-center p-8 text-gray-400">
          <p>No analyses yet. Upload a forensic image to begin.</p>
        </div>
      )}
    </div>
  );
};

export default ForensicAnalysisDashboard;
