import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface ForensicReport {
  id: string;
  fileName: string;
  analysisDate: string;
  summary: {
    totalFiles: number;
    recoveredFiles: number;
    deletedFiles: number;
  };
  filesByType: Record<string, number>;
  timeline?: Array<{
    timestamp: string;
    action: string;
    details: string;
  }>;
}

/**
 * Forensic Report Viewer Component
 * Displays and allows export of analysis results
 */
export const ForensicReportViewer: React.FC<{ analysisId?: string }> = ({ analysisId }) => {
  const [report, setReport] = useState<ForensicReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'summary' | 'timeline' | 'files'>('summary');

  useEffect(() => {
    if (!analysisId) return;

    const fetchReport = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5000/api/analysis/${analysisId}/report`);
        if (!response.ok) throw new Error('Failed to fetch report');
        const data = await response.json();
        setReport(data);
      } catch (error) {
        console.error('Report fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [analysisId]);

  const handleExportPDF = async () => {
    if (!analysisId) return;
    try {
      const response = await fetch(`http://localhost:5000/api/analysis/${analysisId}/export/pdf`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `forensic_report_${analysisId}.pdf`;
      a.click();
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const handleExportDOCX = async () => {
    if (!analysisId) return;
    try {
      const response = await fetch(`http://localhost:5000/api/analysis/${analysisId}/export/docx`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `forensic_report_${analysisId}.docx`;
      a.click();
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  if (loading) {
    return <div className="text-center p-8 text-gray-400">Loading report...</div>;
  }

  if (!report) {
    return <div className="text-center p-8 text-gray-400">No report available</div>;
  }

  return (
    <div className={cn('w-full max-w-4xl mx-auto p-6 space-y-6')}>
      {/* Header */}
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
        <h1 className="text-3xl font-bold text-white mb-2">{report.fileName}</h1>
        <p className="text-gray-400">
          Analysis Date: {new Date(report.analysisDate).toLocaleString()}
        </p>
        <div className="flex gap-4 mt-4">
          <button
            onClick={handleExportPDF}
            className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 transition-colors"
          >
            Export as PDF
          </button>
          <button
            onClick={handleExportDOCX}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Export as DOCX
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {['summary', 'timeline', 'files'].map((tab) => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab as any)}
            className={cn(
              'px-4 py-2 font-semibold transition-colors',
              selectedTab === tab
                ? 'text-orange-500 border-b-2 border-orange-500'
                : 'text-gray-400 hover:text-gray-300'
            )}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div>
        {selectedTab === 'summary' && (
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <p className="text-gray-400 text-sm mb-2">Total Files</p>
              <p className="text-3xl font-bold text-white">{report.summary.totalFiles}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <p className="text-gray-400 text-sm mb-2">Recovered Files</p>
              <p className="text-3xl font-bold text-green-400">{report.summary.recoveredFiles}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <p className="text-gray-400 text-sm mb-2">Deleted Files</p>
              <p className="text-3xl font-bold text-red-400">{report.summary.deletedFiles}</p>
            </div>
          </div>
        )}

        {selectedTab === 'files' && (
          <div className="space-y-2">
            {Object.entries(report.filesByType).map(([type, count]) => (
              <div
                key={type}
                className="flex justify-between items-center bg-gray-800 p-3 rounded border border-gray-700"
              >
                <span className="text-white font-semibold">{type || 'Unknown'}</span>
                <span className="text-orange-400">{count} files</span>
              </div>
            ))}
          </div>
        )}

        {selectedTab === 'timeline' && report.timeline && (
          <div className="space-y-3">
            {report.timeline.map((event, index) => (
              <div key={index} className="bg-gray-800 p-4 rounded border-l-4 border-orange-500">
                <p className="text-sm text-gray-400">{event.timestamp}</p>
                <p className="text-white font-semibold">{event.action}</p>
                <p className="text-gray-400 text-sm mt-1">{event.details}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ForensicReportViewer;
