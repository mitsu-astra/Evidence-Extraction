import * as React from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface KmitSignupFormProps {
  onComplete?: () => void;
}

export default function KmitSignupForm({ onComplete }: KmitSignupFormProps) {
  const [email, setEmail] = React.useState("")
  const [fullName, setFullName] = React.useState("")
  const [department, setDepartment] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [success, setSuccess] = React.useState(false)
  const [credentials, setCredentials] = React.useState<{
    uid: string;
    email: string;
    password: string;
  } | null>(null)

  const handleSignup = async () => {
    if (!email) {
      setError("Email is required")
      return
    }

    if (!email.toLowerCase().endsWith('@kmit.edu.in')) {
      setError("Only @kmit.edu.in email addresses are allowed")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:5000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.toLowerCase(),
          full_name: fullName.trim() || null,
          department: department.trim() || null,
        }),
      })

      const data = await response.json()

      if (data.success) {
        setSuccess(true)
        setCredentials({
          uid: data.uid,
          email: data.email,
          password: data.password,
        })
        setError(null)
        
        // Auto-redirect after 10 seconds
        setTimeout(() => {
          onComplete?.()
        }, 10000)
      } else {
        setError(data.error || "Signup failed")
      }
    } catch (err) {
      setError("Failed to connect to server")
    }

    setLoading(false)
  }

  const handleProceed = () => {
    if (credentials) {
      localStorage.setItem('kmit_uid', credentials.uid)
      localStorage.setItem('kmit_email', credentials.email)
      onComplete?.()
    }
  }

  return (
    <div
      className="w-full max-w-md mx-auto border rounded-lg overflow-hidden p-8 flex flex-col gap-6"
      style={{
        background: 'rgba(10, 10, 10, 0.85)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(12px)',
        fontFamily: "'Courier Prime', monospace",
      }}
    >
      {/* Header */}
      <div className="text-center mb-2">
        <p className="text-xs tracking-[0.25em] uppercase mb-1" style={{ color: 'rgba(255,255,255,0.4)' }}>
          FORENSIC CORE v2.1
        </p>
        <h2 className="text-2xl font-bold tracking-widest uppercase" style={{ color: '#e0e0e0', fontFamily: "'Oswald', sans-serif" }}>
          {success ? 'ACCOUNT CREATED' : 'NEW USER SIGNUP'}
        </h2>
      </div>

      {/* Success View */}
      {success && credentials && (
        <div className="flex flex-col gap-4">
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ background: 'rgba(34, 197, 94, 0.1)', border: '2px solid rgba(34, 197, 94, 0.3)' }}>
              <svg className="w-8 h-8" style={{ color: '#22c55e' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>

          <div className="p-4 rounded space-y-3" style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
            <p className="text-sm font-bold tracking-wide uppercase" style={{ color: '#22c55e' }}>
              📌 SAVE THESE CREDENTIALS
            </p>
            
            <div className="space-y-2 pt-2 border-t" style={{ borderColor: 'rgba(34, 197, 94, 0.2)' }}>
              <p className="text-xs" style={{ color: 'rgba(255,255,255,0.7)' }}>
                <strong style={{ color: '#22c55e' }}>UID:</strong>{' '}
                <code className="px-2 py-1 rounded" style={{ background: 'rgba(0,0,0,0.4)', color: '#fbbf24' }}>
                  {credentials.uid}
                </code>
              </p>
              <p className="text-xs" style={{ color: 'rgba(255,255,255,0.7)' }}>
                <strong style={{ color: '#22c55e' }}>Email:</strong> {credentials.email}
              </p>
              <p className="text-xs" style={{ color: 'rgba(255,255,255,0.7)' }}>
                <strong style={{ color: '#22c55e' }}>Today's Password:</strong>{' '}
                <code className="px-2 py-1 rounded" style={{ background: 'rgba(0,0,0,0.4)', color: '#fbbf24' }}>
                  {credentials.password}
                </code>
              </p>
            </div>

            <div className="pt-3 text-xs space-y-1" style={{ color: 'rgba(255,255,255,0.5)' }}>
              <p>⚠️ Your password changes daily for security.</p>
              <p>💡 Use your UID to login and get new passwords.</p>
            </div>
          </div>

          <button
            className="w-full py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
            onClick={handleProceed}
            style={{
              background: '#22c55e',
              color: '#000',
              border: 'none',
              letterSpacing: '0.15em',
            }}
          >
            PROCEED TO ANALYSIS →
          </button>
        </div>
      )}

      {/* Signup Form */}
      {!success && (
        <div className="flex flex-col gap-4">
          {/* Instructions */}
          <div className="p-3 rounded text-xs" style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#60a5fa' }}>
            <strong>🎓 KMIT Students/Faculty Only</strong><br />
            Use your official @kmit.edu.in email address
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 rounded text-sm" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#ef4444' }}>
              {error}
            </div>
          )}

          {/* Email */}
          <Label htmlFor="email" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
            KMIT Email Address *
          </Label>
          <Input
            id="email"
            type="email"
            placeholder="yourname@kmit.edu.in"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.12)',
              color: '#e0e0e0',
              borderRadius: '4px',
            }}
          />

          {/* Full Name */}
          <Label htmlFor="fullName" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
            Full Name (Optional)
          </Label>
          <Input
            id="fullName"
            type="text"
            placeholder="John Doe"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            disabled={loading}
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.12)',
              color: '#e0e0e0',
              borderRadius: '4px',
            }}
          />

          {/* Department */}
          <Label htmlFor="department" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
            Department (Optional)
          </Label>
          <select
            id="department"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            disabled={loading}
            className="w-full px-3 py-2 rounded text-sm"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.12)',
              color: '#e0e0e0',
              borderRadius: '4px',
            }}
          >
            <option value="">Select Department</option>
            <option value="CSE">Computer Science & Engineering</option>
            <option value="ECE">Electronics & Communication Engg.</option>
            <option value="EEE">Electrical & Electronics Engg.</option>
            <option value="MECH">Mechanical Engineering</option>
            <option value="CIVIL">Civil Engineering</option>
            <option value="IT">Information Technology</option>
            <option value="MBA">Management Studies</option>
          </select>

          {/* Signup Button */}
          <button
            className="mt-2 w-full py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
            onClick={handleSignup}
            disabled={loading}
            style={{
              background: loading ? '#6b2509' : '#b7410e',
              color: '#fff',
              border: 'none',
              letterSpacing: '0.15em',
              opacity: loading ? 0.7 : 1,
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'CREATING ACCOUNT...' : 'CREATE ACCOUNT'}
          </button>
        </div>
      )}
    </div>
  )
}
