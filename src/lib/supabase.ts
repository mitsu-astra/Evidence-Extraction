/**
 * SUPABASE AUTH CLIENT
 * Browser-side authentication using Supabase
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://fidpogwffsrfzbjhghcr.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZHBvZ3dmZnNyZnpiamhnaGNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyNjMyNzEsImV4cCI6MjA1NjgzOTI3MX0.gcKQ7Ns0dT5uF2oGJexHH3coqMFPD1mX30MgVZzWh0k'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
