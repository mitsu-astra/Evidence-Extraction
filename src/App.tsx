import React from 'react';
import ForensicAnalysisHero from './components/forensics/forensic-analysis-hero';
import ForensicFileUpload from './components/forensics/forensic-file-upload';
import ForensicAnalysisDashboard from './components/forensics/forensic-analysis-dashboard';
import { NavBar } from './components/ui/tubelight-navbar';
import { Home, Upload, BarChart3, FileText } from 'lucide-react';
import './App.css';

/**
 * Main Forensic Analysis Application
 * Integrated React + TypeScript + Tailwind CSS + shadcn
 */
function App() {
  const [showAnalysis, setShowAnalysis] = React.useState(false);
  const [currentPage, setCurrentPage] = React.useState<'home' | 'upload' | 'analysis' | 'report'>('upload');

  const handleBeginAnalysis = () => {
    setShowAnalysis(true);
    setCurrentPage('upload');
  };

  const handleGoHome = () => {
    setShowAnalysis(false);
    setCurrentPage('upload');
  };

  const navItems = [
    { name: 'Home', url: '#', icon: Home },
    { name: 'Upload', url: '#', icon: Upload },
    { name: 'Analysis', url: '#', icon: BarChart3 },
    { name: 'Report', url: '#', icon: FileText }
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Tubelight NavBar - Only show when in analysis mode */}
      {showAnalysis && (
        <NavBar items={navItems} />
      )}

      {/* Hero Section */}
      {!showAnalysis && (
        <div onClick={handleBeginAnalysis} style={{ cursor: 'pointer' }}>
          <ForensicAnalysisHero />
        </div>
      )}

      {/* Analysis Section */}
      {showAnalysis && (
        <div className="min-h-screen bg-gray-950 pt-20">
          <div className="max-w-7xl mx-auto px-4 py-8">
            
            <div className="space-y-8">
              <section>
                <h2 className="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">
                  Upload Evidence
                </h2>
                <ForensicFileUpload />
              </section>

              <section>
                <h2 className="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">
                  Analysis Results
                </h2>
                <ForensicAnalysisDashboard />
              </section>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
