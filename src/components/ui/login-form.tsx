import * as React from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/lib/auth-context"

interface LoginFormProps {
  onLogin?: () => void;
}

export default function LoginForm({ onLogin }: LoginFormProps) {
  const { signIn } = useAuth()
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const handleLogin = async () => {
    if (!email || !password) {
      setError("Please enter both email and password")
      return
    }

    setLoading(true)
    setError(null)

    const { error: authError } = await signIn(email, password)

    if (authError) {
      setError(authError.message)
      setLoading(false)
    } else {
      // Success - navigate to analysis page
      onLogin?.()
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
          LOGIN
        </h2>
      </div>

      {/* Email */}
      <div className="flex flex-col gap-4">
        {error && (
          <div className="p-3 rounded text-sm" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#ef4444' }}>
            {error}
          </div>
        )}
        
        <Label htmlFor="login-email" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
          Email Address
        </Label>
        <Input
          id="login-email"
          type="email"
          placeholder="agent@forensic.core"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          disabled={loading}
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.12)',
            color: '#e0e0e0',
            borderRadius: '4px',
          }}
        />

        {/* Password */}
        <Label htmlFor="login-password" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
          Password
        </Label>
        <Input
          id="login-password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          disabled={loading}
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.12)',
            color: '#e0e0e0',
            borderRadius: '4px',
          }}
        />

        {/* Login button */}
        <button
          className="mt-2 w-full py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
          onClick={handleLogin}
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
          {loading ? 'LOGGING IN...' : 'LOGIN'}
        </button>
      </div>
    </div>
  )
}
