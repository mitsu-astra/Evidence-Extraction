import * as React from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface LoginFormProps {
  onLogin?: () => void;
}

export default function LoginForm({ onLogin }: LoginFormProps) {
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")

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
        <Label htmlFor="login-email" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
          Email Address
        </Label>
        <Input
          id="login-email"
          type="email"
          placeholder="agent@forensic.core"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
          onClick={() => onLogin?.()}
          style={{
            background: '#b7410e',
            color: '#fff',
            border: 'none',
            letterSpacing: '0.15em',
          }}
        >
          LOGIN
        </button>
      </div>
    </div>
  )
}
