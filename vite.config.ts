import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import os from 'os'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // ── Cache outside OneDrive ─────────────────────────────────────────────
  // The project lives on OneDrive which intercepts every file-system read.
  // Storing Vite's pre-bundle cache in the system temp dir (C:\AppData\...\Temp)
  // bypasses OneDrive entirely and cuts cold-start time from 60-90s to <5s.
  cacheDir: path.join(os.tmpdir(), '.vite-forensic-cache'),

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        timeout: 60000,
      },
    },
    // Pre-transform the critical-path files when the dev server starts so
    // the first browser request gets already-compiled modules immediately
    warmup: {
      clientFiles: [
        './src/main.tsx',
        './src/App.tsx',
        './src/components/forensics/forensic-analysis-hero.tsx',
      ],
    },
  },

  optimizeDeps: {
    // Declaring all deps up-front lets Vite skip the file-system discovery
    // phase entirely — it bundles exactly these packages without scanning
    // thousands of node_modules files through the OneDrive driver
    include: [
      'react',
      'react-dom',
      'react-dom/client',
      'react-router-dom',
      'framer-motion',
      'lucide-react',
      'clsx',
      'tailwind-merge',
    ],
    // Limit entry-point scanning to the single root file only
    entries: ['./src/main.tsx'],
  },

  build: {
    rollupOptions: {
      output: {
        // Split vendor libs into separate cacheable chunks so the main
        // app bundle stays small and browsers can cache deps independently
        manualChunks: {
          'vendor-react':  ['react', 'react-dom', 'react-router-dom'],
          'vendor-motion': ['framer-motion'],
          'vendor-icons':  ['lucide-react'],
        },
      },
    },
  },
})
