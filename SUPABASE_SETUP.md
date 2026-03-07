# Supabase Integration Guide

## Overview
Your forensic analysis application now includes **Supabase** integration for cloud database storage of:
- ✅ Forensic analysis reports
- ✅ RAG query history  
- ✅ User analytics

## Setup Instructions

### 1. Create a Supabase Project
1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in project details and create

### 2. Get Your Credentials
1. In your Supabase project, go to **Settings** > **API**
2. Copy these two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public key** (long string starting with `eyJ...`)

### 3. Configure Your Application
1. Open the `.env` file in your project root
2. Replace the placeholder values:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   ```
3. Save the file

### 4. Create Database Tables
1. In Supabase, go to **SQL Editor**
2. Click "New Query"
3. Copy the SQL schema from `supabase_client.py` (run `python supabase_client.py` to see it)
4. Or copy this SQL:

```sql
-- Forensic Reports Table
CREATE TABLE IF NOT EXISTS forensic_reports (
    id BIGSERIAL PRIMARY KEY,
    analysis_id TEXT UNIQUE NOT NULL,
    image_name TEXT NOT NULL,
    report_data JSONB NOT NULL,
    summary TEXT,
    user_id TEXT,
    file_count INTEGER DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RAG Queries Table
CREATE TABLE IF NOT EXISTS rag_queries (
    id BIGSERIAL PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    chunks_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (analysis_id) REFERENCES forensic_reports(analysis_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_forensic_reports_analysis_id ON forensic_reports(analysis_id);
CREATE INDEX IF NOT EXISTS idx_forensic_reports_user_id ON forensic_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_forensic_reports_created_at ON forensic_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rag_queries_analysis_id ON rag_queries(analysis_id);

-- Enable Row Level Security
ALTER TABLE forensic_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_queries ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for now)
CREATE POLICY "Enable all access for forensic_reports" ON forensic_reports FOR ALL USING (true);
CREATE POLICY "Enable all access for rag_queries" ON rag_queries FOR ALL USING (true);
```

5. Click "Run" to execute the SQL

### 5. Test the Connection
Run this command to test your Supabase connection:
```bash
python supabase_client.py
```

You should see: ✓ Supabase is configured!

## Features

### Automatic Storage
- Every completed analysis is **automatically saved** to Supabase
- RAG queries and responses are logged for analytics
- No manual action required!

### API Endpoints

#### Check Status
```
GET /api/supabase/status
```
Returns Supabase configuration and connection status

#### List Reports
```
GET /api/supabase/reports?limit=50
```
Get all saved forensic reports (most recent first)

#### Get Specific Report
```
GET /api/supabase/reports/{analysis_id}
```
Retrieve full details of a specific analysis

#### Delete Report
```
DELETE /api/supabase/reports/{analysis_id}
```
Remove a report from the database

### Usage Examples

**Python:**
```python
import requests

# List all reports
response = requests.get('http://localhost:5000/api/supabase/reports')
reports = response.json()['reports']

# Get a specific report
analysis_id = "20260307_143052"
response = requests.get(f'http://localhost:5000/api/supabase/reports/{analysis_id}')
report = response.json()['report']
```

**JavaScript (Frontend):**
```javascript
// List all reports
const response = await fetch('http://localhost:5000/api/supabase/reports');
const { reports } = await response.json();

// Get specific report
const analysisId = "20260307_143052";
const reportResponse = await fetch(`http://localhost:5000/api/supabase/reports/${analysisId}`);
const { report } = await reportResponse.json();
```

## Database Schema

### forensic_reports Table
| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key |
| analysis_id | TEXT | Unique analysis identifier (timestamp-based) |
| image_name | TEXT | Name of the analyzed disk image |
| report_data | JSONB | Full forensic report JSON |
| summary | TEXT | Analysis summary text |
| user_id | TEXT | Optional user identifier |
| file_count | INTEGER | Number of files found |
| total_size | BIGINT | Total size in bytes |
| created_at | TIMESTAMP | When the analysis was created |

### rag_queries Table
| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key |
| analysis_id | TEXT | Related forensic report |
| query | TEXT | User's question |
| response | TEXT | RAG system's answer |
| chunks_used | INTEGER | Number of context chunks retrieved |
| created_at | TIMESTAMP | When the query was made |

## Benefits

✅ **Cloud Backup** - All your analysis reports are safely stored in the cloud  
✅ **History** - Access past analyses anytime, from anywhere  
✅ **Analytics** - Track which types of questions users ask  
✅ **Collaboration** - Share reports with your team (add user auth later)  
✅ **Scalability** - Supabase handles millions of records effortlessly  

## Optional: Add User Authentication

To add user authentication:
1. Enable Supabase Auth in your project settings
2. Update the Row Level Security policies to filter by `auth.uid()`
3. Add login/signup to your frontend
4. Pass user tokens in API requests

## Troubleshooting

**Error: "Supabase not configured"**
- Make sure `.env` file has correct SUPABASE_URL and SUPABASE_KEY
- Restart the Flask server after updating `.env`

**Error: "relation 'forensic_reports' does not exist"**
- Run the SQL schema in Supabase SQL Editor
- Make sure tables were created successfully

**Connection timeout**
- Check your internet connection
- Verify the Supabase URL is correct
- Check if your firewall blocks Supabase

## Next Steps

1. ✅ Configure `.env` with your Supabase credentials
2. ✅ Run SQL schema to create tables
3. ✅ Test with `python supabase_client.py`
4. ✅ Start the web app and run an analysis
5. ✅ Check Supabase dashboard to see your data!

Your forensic reports are now backed up to the cloud! 🚀
