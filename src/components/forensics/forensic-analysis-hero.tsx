import React, { useEffect, useRef } from 'react';

/**
 * Forensic Analysis Hero Component
 * Modern 3D parallax landing page with forensic investigation theme
 * Features: 3D perspective, mouse parallax tracking, grain effect
 */
const ForensicAnalysisHero: React.FC = () => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const layersRef = useRef<HTMLDivElement[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Mouse Parallax Logic
    const handleMouseMove = (e: MouseEvent) => {
      const x = (window.innerWidth / 2 - e.pageX) / 25;
      const y = (window.innerHeight / 2 - e.pageY) / 25;

      // Rotate the 3D Canvas
      canvas.style.transform = `rotateX(${55 + y / 2}deg) rotateZ(${-25 + x / 2}deg)`;

      // Apply depth shift to layers
      layersRef.current.forEach((layer, index) => {
        if (!layer) return;
        const depth = (index + 1) * 15;
        const moveX = x * (index + 1) * 0.2;
        const moveY = y * (index + 1) * 0.2;
        layer.style.transform = `translateZ(${depth}px) translate(${moveX}px, ${moveY}px)`;
      });
    };

    // Entrance Animation
    canvas.style.opacity = '0';
    canvas.style.transform = 'rotateX(90deg) rotateZ(0deg) scale(0.8)';
    
    const timeout = setTimeout(() => {
      canvas.style.transition = 'all 2.5s cubic-bezier(0.16, 1, 0.3, 1)';
      canvas.style.opacity = '1';
      canvas.style.transform = 'rotateX(55deg) rotateZ(-25deg) scale(1)';
    }, 300);

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      clearTimeout(timeout);
    };
  }, []);

  return (
    <>
      <style>{`
        :root {
          --bg: #0a0a0a;
          --silver: #e0e0e0;
          --accent: #ff3c00;
          --grain-opacity: 0.15;
        }

        .forensic-hero-body {
          background-color: var(--bg);
          color: var(--silver);
          font-family: 'Syncopate', sans-serif;
          overflow: hidden;
          height: 100vh;
          width: 100vw;
          margin: 0;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .forensic-grain {
          position: fixed;
          top: 0; left: 0; width: 100%; height: 100%;
          pointer-events: none;
          z-index: 100;
          opacity: var(--grain-opacity);
        }

        .forensic-viewport {
          perspective: 2000px;
          width: 100vw; height: 100vh;
          display: flex; align-items: center; justify-content: center;
          overflow: hidden;
        }

        .forensic-canvas-3d {
          position: relative;
          width: 800px; height: 500px;
          transform-style: preserve-3d;
          transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .forensic-layer {
          position: absolute;
          inset: 0;
          border: 1px solid rgba(224, 224, 224, 0.1);
          background-size: cover;
          background-position: center;
          transition: transform 0.5s ease;
        }

        .forensic-layer-1 { 
          background-image: url('/background.jpg'); 
          filter: grayscale(1) contrast(1.2) brightness(0.5); 
        }
        .forensic-layer-2 { 
          background-image: url('/background.jpg'); 
          filter: grayscale(1) contrast(1.1) brightness(0.7); 
          opacity: 0.6; 
          mix-blend-mode: screen; 
        }
        .forensic-layer-3 { 
          background-image: url('/background.jpg'); 
          filter: grayscale(1) contrast(1.3) brightness(0.8); 
          opacity: 0.4; 
          mix-blend-mode: overlay; 
        }

        .forensic-contours {
          position: absolute;
          width: 200%; height: 200%;
          top: -50%; left: -50%;
          background-image: repeating-radial-gradient(circle at 50% 50%, transparent 0, transparent 40px, rgba(255,255,255,0.05) 41px, transparent 42px);
          transform: translateZ(120px);
          pointer-events: none;
        }

        .forensic-interface-grid {
          position: fixed;
          inset: 0;
          padding: 4rem;
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: auto 1fr auto;
          z-index: 10;
          pointer-events: none;
        }

        @import url('https://fonts.googleapis.com/css2?family=Righteous:wght@400;700&family=Oswald:wght@400;500&display=swap');

        .forensic-title {
          grid-column: 1 / -1;
          align-self: center;
          font-size: clamp(100px, 8vw, 200px);
          font-family: 'Oswald', 'Righteous', sans-serif;
          font-weight: 500;
          line-height: 0.9;
          letter-spacing: -0.01em;
          color: #B91C1C;
          text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }

        @import url('https://fonts.googleapis.com/css2?family=Righteous:wght@400;700&family=Oswald:wght@400;500&family=IBM+Plex+Serif:wght@400;600&family=Sora:wght@400;500;600&display=swap');

        .forensic-cta-button {
          pointer-events: auto;
          background: var(--silver);
          color: var(--bg);
          padding: 1rem 2rem;
          text-decoration: none;
          font-weight: 500;
          font-family: 'Sora', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          transition: 0.3s;
          cursor: pointer;
          border: none;
          font-size: 1rem;
        }

        .forensic-cta-button:hover { 
          background: var(--accent); 
          transform: translateY(-5px); 
        }

        .forensic-scroll-hint {
          position: absolute;
          bottom: 2rem; left: 50%;
          width: 1px; height: 60px;
          background: linear-gradient(to bottom, var(--silver), transparent);
          animation: forensic-flow 2s infinite ease-in-out;
        }

        @keyframes forensic-flow {
          0%, 100% { transform: scaleY(0); transform-origin: top; }
          50% { transform: scaleY(1); transform-origin: top; }
          51% { transform: scaleY(1); transform-origin: bottom; }
        }
      `}</style>

      <div className="forensic-hero-body">
        {/* SVG Filter for Grain */}
        <svg style={{ position: 'absolute', width: 0, height: 0 }}>
          <filter id="forensic-grain">
            <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" />
            <feColorMatrix type="saturate" values="0" />
          </filter>
        </svg>

        <div className="forensic-grain" style={{ filter: 'url(#forensic-grain)' }}></div>

        <div className="forensic-interface-grid">
          <div style={{ fontWeight: 700 }}>FORENSIC_CORE v2.1</div>
          <div style={{ textAlign: 'right', fontFamily: 'monospace', color: 'var(--accent)', fontSize: '0.7rem' }}>
            <div>ANALYSIS_ID: 034.0522-80MM</div>
            <div>CHAIN_OF_CUSTODY: VERIFIED</div>
          </div>

          <h1 className="forensic-title">EVIDENCE<br />EXTRACTION</h1>

          <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
              <p>[ DIGITAL FORENSIC ANALYSIS SUITE ]</p>
              <p>ADVANCED INVESTIGATION & DATA RECOVERY</p>
            </div>
            <button className="forensic-cta-button" onClick={() => {
              // Navigate to analysis or scroll to content
              window.location.hash = '#analysis';
            }}>BEGIN ANALYSIS</button>
          </div>
        </div>

        <div className="forensic-viewport">
          <div className="forensic-canvas-3d" ref={canvasRef}>
            <div className="forensic-layer forensic-layer-1" ref={(el) => (layersRef.current[0] = el!)}></div>
            <div className="forensic-layer forensic-layer-2" ref={(el) => (layersRef.current[1] = el!)}></div>
            <div className="forensic-layer forensic-layer-3" ref={(el) => (layersRef.current[2] = el!)}></div>
            <div className="forensic-contours"></div>
          </div>
        </div>

        <div className="forensic-scroll-hint"></div>
      </div>
    </>
  );
};

export default ForensicAnalysisHero;
