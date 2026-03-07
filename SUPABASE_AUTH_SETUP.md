# SUPABASE AUTHENTICATION SETUP GUIDE

## ✅ Files Created

**Frontend Auth:**
- `src/lib/supabase.ts` - Supabase client configuration
- `src/lib/auth-context.tsx` - React auth context provider
- `.env.local` - Environment variables for Vite

**Updated Components:**
- `src/components/ui/login-form.tsx` - Now uses Supabase auth
- `src/components/ui/multi-step-login.tsx` - Now uses Supabase auth
- `src/main.tsx` - Wrapped with AuthProvider

## 📋 Supabase Dashboard Setup

### Step 1: Enable Email Authentication

1. Go to https://app.supabase.com
2. Select your project: `fidpogwffsrfzbjhghcr`
3. Navigate to **Authentication** → **Providers**
4. Enable **Email** provider (should already be enabled)

### Step 2: Configure Email Templates (Optional)

1. Go to **Authentication** → **Email Templates**
2. Customize these templates:
   - **Confirm signup** - Sent when user signs up
   - **Magic Link** - For passwordless login
   - **Change Email Address** - Email change verification
   - **Reset Password** - Password reset flow

### Step 3: Configure Site URL

1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL** to: `http://localhost:5173`
3. Add **Redirect URLs**:
   - `http://localhost:5173/analysis`
   - `http://localhost:5173/login`
   - `http://localhost:5173/signup`

### Step 4: Adjust Auth Settings

1. Go to **Authentication** → **Settings**
2. Configure:
   - **Enable email confirmations**: ✓ (recommended)
   - **Secure email change**: ✓
   - **Minimum password length**: 8 characters
   - **Password strength**: Strong

### Step 5: User Management

View registered users at:
**Authentication** → **Users**

You can:
- View all registered users
- Manually create users
- Delete users
- Reset passwords
- Confirm emails manually

## 🔧 Install Dependencies

Run this command to install the Supabase client library:

```bash
npm install @supabase/supabase-js
```

## 🚀 Testing Authentication

### 1. Start the frontend:
```bash
npm run dev
```

### 2. Test signup:
- Navigate to http://localhost:5173/signup
- Enter email and password
- Complete 3-step form
- Check email for confirmation link

### 3. Test login:
- Navigate to http://localhost:5173/login
- Enter registered email/password
- Click LOGIN
- You'll be redirected to /analysis

## 🛡️ Row Level Security (RLS)

If you want users to only see their own data:

```sql
-- Enable RLS on forensic_reports table
ALTER TABLE forensic_reports ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their own reports
CREATE POLICY "Users can view own reports"
ON forensic_reports
FOR SELECT
USING (auth.uid() = user_id::uuid);

-- Create policy: Users can insert their own reports
CREATE POLICY "Users can insert own reports"
ON forensic_reports
FOR INSERT
WITH CHECK (auth.uid() = user_id::uuid);
```

Update your `supabase_client.py` to use the authenticated user's ID:

```python
from flask import request

def save_analysis_report(...):
    # Get user ID from Supabase JWT token in Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.replace('Bearer ', '')
        # Validate token and extract user_id
        # user_id = validate_supabase_token(token)
    
    data = {
        # ... other fields
        "user_id": user_id,  # Use actual user ID from auth
    }
```

## 🔐 Auth Flow

**Signup:**
1. User fills out signup form
2. Frontend calls `supabase.auth.signUp()`
3. Supabase creates user account
4. Confirmation email sent
5. User clicks confirmation link
6. Account activated

**Login:**
1. User enters credentials
2. Frontend calls `supabase.auth.signInWithPassword()`
3. Supabase validates credentials
4. Session token returned
5. Auto-redirect to /analysis

**Session Management:**
- Sessions persist across page refreshes
- Tokens stored in localStorage
- Auto-refresh before expiration
- Sign out clears all tokens

## 🎯 Using Auth in Your App

### Get current user:
```tsx
import { useAuth } from '@/lib/auth-context'

function MyComponent() {
  const { user, session, loading } = useAuth()
  
  if (loading) return <div>Loading...</div>
  if (!user) return <div>Please log in</div>
  
  return <div>Welcome, {user.email}!</div>
}
```

### Protect routes:
```tsx
import { useAuth } from '@/lib/auth-context'
import { Navigate } from 'react-router-dom'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) return <div>Loading...</div>
  if (!user) return <Navigate to="/login" />
  
  return children
}
```

### Sign out:
```tsx
function LogoutButton() {
  const { signOut } = useAuth()
  
  return (
    <button onClick={signOut}>
      Sign Out
    </button>
  )
}
```

## 📱 API Integration

When making API calls to Flask backend, send the Supabase token:

```tsx
const { session } = useAuth()

fetch('http://localhost:5000/api/analysis', {
  headers: {
    'Authorization': `Bearer ${session?.access_token}`
  }
})
```

Verify tokens in Flask:
```python
from supabase import create_client
import jwt

def verify_supabase_token(token):
    # Verify JWT token
    supabase = get_supabase_client()
    user = supabase.auth.get_user(token)
    return user
```

## ✅ Verification Checklist

- [ ] Supabase client installed (`@supabase/supabase-js`)
- [ ] Email provider enabled in Supabase dashboard
- [ ] Site URL configured in Supabase
- [ ] Login form works (try logging in)
- [ ] Signup form works (try creating account)
- [ ] Email confirmation received
- [ ] Session persists on page refresh
- [ ] Sign out works
- [ ] Protected routes redirect to login

## 🐛 Troubleshooting

**"Invalid API key"**
- Check `.env.local` has correct `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
- Restart dev server after changing env vars

**"Email not confirmed"**
- Check spam folder for confirmation email
- Manually confirm user in Supabase dashboard → Authentication → Users

**"CORS error"**
- Ensure Site URL matches your frontend URL exactly
- Add redirect URLs in Supabase dashboard

**Session not persisting**
- Check browser localStorage for `supabase.auth.token`
- Ensure cookies are enabled
- Check browser console for errors

## 🎉 Done!

Your app now has full authentication powered by Supabase! Users can:
- ✓ Sign up with email/password
- ✓ Log in securely
- ✓ Persist sessions
- ✓ Reset passwords
- ✓ Receive email confirmations

Next steps:
- Add OAuth providers (Google, GitHub)
- Implement password reset flow
- Add user profiles
- Protect analysis routes
