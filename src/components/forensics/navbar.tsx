import React from 'react';
import { cn } from '@/lib/utils';

interface NavbarProps {
  onHome: () => void;
  currentPage?: 'upload' | 'analysis' | 'report';
}

/**
 * Forensic Analysis Navbar - Sleek Cyberpunk Style
 * Clean white/cyan aesthetic with modern design
 */
export const Navbar: React.FC<NavbarProps> = ({ onHome, currentPage = 'upload' }) => {
  return (
    <>
      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-15px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes lineGlow {
          0%, 100% {
            box-shadow: 0 0 5px rgba(34, 211, 238, 0.3);
          }
          50% {
            box-shadow: 0 0 15px rgba(34, 211, 238, 0.6);
          }
        }

        .navbar-container {
          animation: slideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .nav-link {
          position: relative;
          transition: all 0.3s ease;
          color: #d1d5db;
          font-weight: 600;
          font-size: 0.9rem;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }

        .nav-link::after {
          content: '';
          position: absolute;
          bottom: -6px;
          left: 0;
          width: 0;
          height: 2px;
          background: #06b6d4;
          transition: width 0.3s ease;
        }

        .nav-link:hover {
          color: #06b6d4;
        }

        .nav-link:hover::after {
          width: 100%;
        }

        .nav-link.active {
          color: #06b6d4;
          animation: lineGlow 2s ease-in-out infinite;
        }

        .home-button {
          position: relative;
          overflow: hidden;
          padding: 0.6rem 1.5rem;
          background: transparent;
          border: 1.5px solid #06b6d4;
          color: #06b6d4;
          font-size: 0.85rem;
          font-weight: 700;
          letter-spacing: 0.12em;
          cursor: pointer;
          transition: all 0.3s ease;
          text-transform: uppercase;
          border-radius: 2px;
        }

        .home-button:hover {
          background: rgba(6, 182, 212, 0.1);
          box-shadow: 0 0 15px rgba(6, 182, 212, 0.4), inset 0 0 15px rgba(6, 182, 212, 0.1);
          transform: translateY(-2px);
        }

        .logo-cyan {
          color: #06b6d4;
        }

        .nav-divider {
          width: 1px;
          height: 24px;
          background: linear-gradient(180deg, transparent, #06b6d4, transparent);
          opacity: 0.4;
        }
      `}</style>

      <nav className="navbar-container fixed top-0 left-0 right-0 z-50"
        style={{
          background: 'rgba(15, 23, 42, 0.9)',
          backdropFilter: 'blur(8px)',
          borderBottom: '1.5px solid rgba(6, 182, 212, 0.3)',
          padding: '1rem 2rem',
        }}>
        <div className="max-w-7xl mx-auto px-4 py-2 flex items-center justify-between">
          {/* Logo / Branding */}
          <div className="flex items-center gap-3">
            <div style={{
              width: '32px',
              height: '32px',
              border: '2px solid #06b6d4',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1rem',
            }} className="logo-cyan">
              ◆
            </div>
            <div>
              <h1 style={{
                fontSize: '1rem',
                fontWeight: 700,
                letterSpacing: '0.1em',
              }} className="logo-cyan">
                FORENSIC
              </h1>
              <p style={{
                fontSize: '0.7rem',
                color: '#9ca3af',
                letterSpacing: '0.08em',
              }}>
                ANALYSIS
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            <div className="flex gap-8 items-center">
              <a
                href="#upload"
                className={cn('nav-link', currentPage === 'upload' && 'active')}
              >
                Upload
              </a>
              <div className="nav-divider"></div>
              <a
                href="#analysis"
                className={cn('nav-link', currentPage === 'analysis' && 'active')}
              >
                Analysis
              </a>
              <div className="nav-divider"></div>
              <a
                href="#report"
                className={cn('nav-link', currentPage === 'report' && 'active')}
              >
                Report
              </a>
            </div>

            {/* Home Button */}
            <button
              onClick={onHome}
              className="home-button"
              title="Return to landing page"
            >
              ← HOME
            </button>
          </div>
        </div>

        {/* Bottom accent line */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: 'linear-gradient(90deg, transparent, #06b6d4, transparent)',
          opacity: 0.2,
        }}></div>
      </nav>
    </>
  );
};

export default Navbar;
