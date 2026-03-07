import * as React from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface KmitLoginFormProps {
  onLogin?: () => void;
}

export default function KmitLoginForm({ onLogin }: KmitLoginFormProps) {
  const [uid, setUid] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [retrievedInfo, setRetrievedInfo] = React.useState<{
    uid: string;
    email: string;
    password: string;
    full_name?: string;
  } | null>(null)

  // Get today's password for existing user
  const handleGetPassword = async () => {
    if (!uid) {
      setError("Please enter your UID")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid: uid.toUpperCase() }),
      })

      const data = await response.json()

      if (data.success) {
        setRetrievedInfo({
          uid: data.uid,
          email: data.email,
          password: data.password,
          full_name: data.full_name,
        })
        setPassword(data.password)
        setError(null)
      } else {
        setError(data.error || "UID not found")
        setRetrievedInfo(null)
      }
    } catch (err) {
      setError("Failed to connect to server")
      setRetrievedInfo(null)
    }

    setLoading(false)
  }

  // Login with UID + password
  const handleLogin = () => {
    if (!uid || !password) {
      setError("Please get your password first")
      return
    }

    // Store credentials and navigate
    localStorage.setItem('kmit_uid', uid.toUpperCase())
    localStorage.setItem('kmit_email', retrievedInfo?.email || '')
    onLogin?.()
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
          EXISTING USER LOGIN
        </h2>
      </div>

      {/* Instructions */}
      <div className="p-3 rounded text-xs" style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#60a5fa' }}>
        <strong>📌 Note:</strong> Passwords change daily for security. Enter your UID to get today's password.
      </div>

      <div className="flex flex-col gap-4">
        {/* Error */}
        {error && (
          <div className="p-3 rounded text-sm" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#ef4444' }}>
            {error}
          </div>
        )}

        {/* Retrieved Credentials */}
        {retrievedInfo && (
          <div className="p-4 rounded text-sm space-y-2" style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)', color: '#22c55e' }}>
            <p><strong>✓ UID:</strong> {retrievedInfo.uid}</p>
            <p><strong>✓ Email:</strong> {retrievedInfo.email}</p>
            {retrievedInfo.full_name && <p><strong>✓ Name:</strong> {retrievedInfo.full_name}</p>}
            <p className="pt-2 border-t" style={{ borderColor: 'rgba(34, 197, 94, 0.2)' }}>
              <strong>🔑 Today's Password:</strong> <code className="px-2 py-1 rounded" style={{ background: 'rgba(0,0,0,0.3)', color: '#fbbf24' }}>{retrievedInfo.password}</code>
            </p>
          </div>
        )}
        
        {/* UID Input */}
        <Label htmlFor="uid" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
          Enter Your UID
        </Label>
        <Input
          id="uid"
          type="text"
          placeholder="KMIT123456"
          value={uid}
          onChange={(e) => setUid(e.target.value.toUpperCase())}
          onKeyPress={(e) => e.key === 'Enter' && !retrievedInfo && handleGetPassword()}
          disabled={loading || !!retrievedInfo}
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.12)',
            color: '#e0e0e0',
            borderRadius: '4px',
          }}
        />

        {/* Get Password Button */}
        {!retrievedInfo && (
          <button
            className="w-full py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
            onClick={handleGetPassword}
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
            {loading ? 'RETRIEVING...' : 'GET TODAY\'S PASSWORD'}
          </button>
        )}

        {/* Login Button (shown after password retrieved) */}
        {retrievedInfo && (
          <>
            <Label htmlFor="password" className="text-xs tracking-widest uppercase mt-2" style={{ color: 'rgba(255,255,255,0.6)' }}>
              Confirm Password
            </Label>
            <Input
              id="password"
              type="text"
              value={password}
              disabled
              style={{
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid rgba(255,255,255,0.08)',
                color: '#22c55e',
                borderRadius: '4px',
              }}
            />
            
            <button
              className="w-full py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
              onClick={handleLogin}
              style={{
                background: '#22c55e',
                color: '#000',
                border: 'none',
                letterSpacing: '0.15em',
              }}
            >
              PROCEED TO ANALYSIS →
            </button>
          </>
        )}
      </div>
    </div>
  )
}
