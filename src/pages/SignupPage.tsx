import { useNavigate } from 'react-router-dom';
import MultiStepLogin from '@/components/ui/multi-step-login';

export default function SignupPage() {
  const navigate = useNavigate();

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center px-4"
      style={{ background: '#0a0a0a', fontFamily: "'Courier Prime', monospace" }}
    >
      {/* Back button */}
      <button
        onClick={() => navigate('/')}
        className="fixed top-6 left-6 z-50 flex items-center gap-2 px-4 py-2 text-sm font-semibold transition-all duration-200"
        style={{
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.1)',
          color: 'rgba(255,255,255,0.5)',
          borderRadius: '8px',
        }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </button>

      {/* Subtle grid background */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
      />

      <div className="relative z-10 w-full max-w-md">
        <MultiStepLogin onComplete={() => navigate('/analysis')} />
        <p className="text-center mt-6 text-xs tracking-widest" style={{ color: 'rgba(255,255,255,0.25)' }}>
          ALREADY HAVE AN ACCOUNT?{' '}
          <button
            onClick={() => navigate('/login')}
            className="underline underline-offset-4 transition-colors"
            style={{ color: '#b7410e', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontSize: 'inherit', letterSpacing: 'inherit' }}
          >
            LOGIN
          </button>
        </p>
      </div>
    </div>
  );
}
