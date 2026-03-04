import React, { useEffect, useState } from 'react'

const DEFAULTS = {
  '--card-bg': '#0f1724',
  '--card-border': '#334155',
  '--card-text': '#ffffff'
}

function applyVars(vars: Record<string,string>) {
  const root = document.documentElement
  Object.entries(vars).forEach(([k,v]) => root.style.setProperty(k, v))
}

export default function ColorPicker() {
  const [open, setOpen] = useState(false)
  const [bg, setBg] = useState<string>(DEFAULTS['--card-bg'])
  const [border, setBorder] = useState<string>(DEFAULTS['--card-border'])
  const [text, setText] = useState<string>(DEFAULTS['--card-text'])

  useEffect(() => {
    // load from localStorage
    try {
      const saved = localStorage.getItem('card_colors')
      if (saved) {
        const parsed = JSON.parse(saved)
        setBg(parsed['--card-bg'] || DEFAULTS['--card-bg'])
        setBorder(parsed['--card-border'] || DEFAULTS['--card-border'])
        setText(parsed['--card-text'] || DEFAULTS['--card-text'])
        applyVars(parsed)
      } else {
        applyVars(DEFAULTS)
      }
    } catch (e) {
      applyVars(DEFAULTS)
    }
  }, [])

  useEffect(() => {
    const vars = {
      '--card-bg': bg,
      '--card-border': border,
      '--card-text': text
    }
    applyVars(vars)
    localStorage.setItem('card_colors', JSON.stringify(vars))
  }, [bg, border, text])

  const reset = () => {
    setBg(DEFAULTS['--card-bg'])
    setBorder(DEFAULTS['--card-border'])
    setText(DEFAULTS['--card-text'])
    applyVars(DEFAULTS)
    localStorage.removeItem('card_colors')
  }

  return (
    <div className="fixed bottom-6 right-6 z-60">
      <div className="flex flex-col items-end gap-2">
        <button
          onClick={() => setOpen(s => !s)}
          className="px-3 py-2 rounded-full bg-gray-800 border border-gray-700 text-sm text-white shadow-lg"
        >
          {open ? 'Close' : 'Color Wheel'}
        </button>

        {open && (
          <div className="mt-2 w-56 p-4 bg-gray-900 border border-gray-700 rounded-lg shadow-xl text-sm text-gray-200">
            <div className="mb-3">
              <label className="block text-xs text-gray-400 mb-1">Card Background</label>
              <input type="color" value={bg} onChange={e => setBg(e.target.value)} className="w-full h-8 p-0" />
            </div>
            <div className="mb-3">
              <label className="block text-xs text-gray-400 mb-1">Card Border</label>
              <input type="color" value={border} onChange={e => setBorder(e.target.value)} className="w-full h-8 p-0" />
            </div>
            <div className="mb-3">
              <label className="block text-xs text-gray-400 mb-1">Card Text</label>
              <input type="color" value={text} onChange={e => setText(e.target.value)} className="w-full h-8 p-0" />
            </div>
            <div className="flex justify-between items-center">
              <button onClick={reset} className="text-xs text-red-400">Reset</button>
              <span className="text-xs text-gray-400">Saved locally</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
