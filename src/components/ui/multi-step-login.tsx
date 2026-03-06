import * as React from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface MultiStepLoginProps {
  onComplete?: () => void;
}

export default function MultiStepLogin({ onComplete }: MultiStepLoginProps) {
  const [step, setStep] = React.useState<number>(1)
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [otp, setOtp] = React.useState("")
  const [twoFA, setTwoFA] = React.useState("")

  const nextStep = () => setStep((prev) => Math.min(prev + 1, 3))
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1))

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
          CREATE ACCOUNT
        </h2>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-2">
        {[1, 2, 3].map((s) => (
          <React.Fragment key={s}>
            <div
              className="flex-1 h-0.5 rounded-full transition-all duration-500"
              style={{ background: step >= s ? '#b7410e' : 'rgba(255,255,255,0.1)' }}
            />
          </React.Fragment>
        ))}
      </div>
      <p className="text-xs tracking-widest uppercase text-center -mt-3" style={{ color: 'rgba(255,255,255,0.3)' }}>
        STEP {step} OF 3
      </p>

      {/* Step 1 — Email */}
      {step === 1 && (
        <div className="flex flex-col gap-4">
          <Label htmlFor="email" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
            Email Address
          </Label>
          <Input
            id="email"
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
          <button
            className="mt-2 w-full py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
            onClick={nextStep}
            style={{
              background: '#b7410e',
              color: '#fff',
              border: 'none',
              letterSpacing: '0.15em',
            }}
          >
            NEXT →
          </button>
        </div>
      )}

      {/* Step 2 — Password + OTP */}
      {step === 2 && (
        <div className="flex flex-col gap-4">
          <Label htmlFor="password" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
            Password
          </Label>
          <Input
            id="password"
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
          <Label htmlFor="otp" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
            OTP <span style={{ color: 'rgba(255,255,255,0.3)' }}>(Optional)</span>
          </Label>
          <Input
            id="otp"
            type="text"
            placeholder="123456"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.12)',
              color: '#e0e0e0',
              borderRadius: '4px',
            }}
          />
          <div className="flex justify-between gap-3 mt-2">
            <button
              className="flex-1 py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
              onClick={prevStep}
              style={{
                background: 'transparent',
                color: 'rgba(255,255,255,0.5)',
                border: '1px solid rgba(255,255,255,0.15)',
                letterSpacing: '0.12em',
              }}
            >
              ← BACK
            </button>
            <button
              className="flex-1 py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
              onClick={nextStep}
              style={{
                background: '#b7410e',
                color: '#fff',
                border: 'none',
                letterSpacing: '0.12em',
              }}
            >
              NEXT →
            </button>
          </div>
        </div>
      )}

      {/* Step 3 — 2FA */}
      {step === 3 && (
        <div className="flex flex-col gap-4">
          <Label htmlFor="2fa" className="text-xs tracking-widest uppercase" style={{ color: 'rgba(255,255,255,0.6)' }}>
            2FA Verification Code
          </Label>
          <Input
            id="2fa"
            type="text"
            placeholder="Enter verification code"
            value={twoFA}
            onChange={(e) => setTwoFA(e.target.value)}
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.12)',
              color: '#e0e0e0',
              borderRadius: '4px',
            }}
          />
          <div className="flex justify-between gap-3 mt-2">
            <button
              className="flex-1 py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
              onClick={prevStep}
              style={{
                background: 'transparent',
                color: 'rgba(255,255,255,0.5)',
                border: '1px solid rgba(255,255,255,0.15)',
                letterSpacing: '0.12em',
              }}
            >
              ← BACK
            </button>
            <button
              className="flex-1 py-2 rounded text-sm font-bold tracking-widest uppercase transition-all duration-200"
              onClick={() => onComplete?.()}
              style={{
                background: '#b7410e',
                color: '#fff',
                border: 'none',
                letterSpacing: '0.1em',
              }}
            >
              VERIFY & SIGN UP
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
