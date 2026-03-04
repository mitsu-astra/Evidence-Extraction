# COMPLETE FORENSIC ANALYSIS DATA FLOW PIPELINE

**Project:** PS_FORENSIC Evidence Extraction System  
**Date Created:** March 1, 2026  
**Version:** 1.0

---

## TABLE OF CONTENTS

1. [Project Structure & Folder Responsibilities](#project-structure--folder-responsibilities)
2. [Frontend Layer (React + TypeScript)](#frontend-layer-react--typescript)
3. [Backend Layer (Flask API)](#backend-layer-flask-api)
4. [Analysis Engine Layer (Python)](#analysis-engine-layer-python)
5. [Data Generation & Storage](#data-generation--storage)
6. [Complete End-to-End Flow](#complete-end-to-end-flow)
7. [Key Data Transformations](#key-data-transformations)
8. [Folder Responsibilities Summary](#folder-responsibilities-summary)
9. [Data Flow Complexity](#data-flow-complexity)

---

## PROJECT STRUCTURE & FOLDER RESPONSIBILITIES

```
Evidence-Extraction/
├── src/                          ← REACT FRONTEND (TypeScript)
│   ├── components/
│   │   ├── forensics/
│   │   │   ├── forensic-file-upload.tsx        ← File upload UI component
│   │   │   ├── forensic-analysis-dashboard.tsx ← Results display dashboard
│   │   │   └── forensic-analysis-hero.tsx      ← Landing page hero section
│   │   └── ui/                                  ← Reusable UI components (navbar, glitch)
│   └── App.tsx                                  ← Main application routing & layout
│
├── public/                       ← Static frontend assets (images, favicon, fonts)
├── templates/                    ← HTML templates for report generation
├── uploads/                      ← UPLOADED DISK IMAGES (temporary storage)
│   └── [user-uploaded E01/RAW files here]
│
├── analysis_output/              ← GENERATED REPORTS & ANALYSIS ARTIFACTS
│   └── [timestamp_folders like 20260228_094921_ABC123/]
│       ├── report.json           ← Structured forensic data (2-5 MB JSON)
│       ├── summary.txt           ← Human-readable text summary (100 KB)
│       ├── timeline.txt          ← Chronological timeline events (200 KB)
│       ├── extensions.txt        ← File type analysis results (50 KB)
│       ├── report.pdf            ← Formatted PDF report (5-10 MB, 20+ pages)
│       └── report.docx           ← Word document report (3-5 MB, 20+ pages)
│
├── forensic-env/                 ← Python virtual environment (isolated dependencies)
├── libewf/                       ← libewf library source for E01 format support
│
├── forensic_pipeline.py          ← Basic forensic analyzer using pytsk3
├── forensic_pipeline_advanced.py ← Advanced analyzer with LLM integration (MAIN LOGIC)
├── forensic_web_app.py           ← Flask backend API (649 lines)
├── requirements_web.txt          ← Python package dependencies
├── package.json                  ← npm dependencies (React, Vite, etc.)
├── tsconfig.json                 ← TypeScript configuration
├── vite.config.ts                ← Frontend build configuration
└── START_WEB_APP.bat/.ps1        ← Scripts to launch backend & frontend
```

---

## FRONTEND LAYER (React + TypeScript)

### **2.1 Entry Point: `src/App.tsx`**

**What it does:**
- Defines complete app routing structure (Home page `/` and Analysis page `/analysis`)
- Renders main navigation bar with tabs (Home, Upload, Analysis, Report)
- Manages tab switching state using `useState` hook
- Implements glitch background effect for visual appeal
- Routes requests to different components based on active tab
- Handles responsive design and layout

**Component Structure:**
```
App (root component)
├── HeroPage                    ← Landing page with introduction
└── AnalysisPage               ← Main analysis interface
    ├── NavBar                 ← Tab navigation (Home, Upload, Analysis, Report)
    ├── HomeTab                ← Statistics display section
    ├── Upload Tab             ← ForensicFileUpload component
    │   └── ForensicAnalysisDashboard (displays results below upload)
    ├── Analysis Tab           ← Coming soon placeholder
    └── Report Tab             ← Coming soon placeholder
```

### **2.2 File Upload Component: `src/components/forensics/forensic-file-upload.tsx`**

**Complete step-by-step flow:**

#### **Step 1: User File Selection**
```
User clicks upload button
    ↓
File picker dialog opens
    ↓
User selects E01 file (e.g., drive1.E01, 5 GB)
    ↓
Component validates file extension:
  Allowed: .raw, .dd, .e01, .img, .iso, .bin, .dmg
    ↓
If invalid format:
  └─ Show error message "Invalid file type. Allowed: raw, dd, e01..."
    ↓
If valid format:
  └─ Proceed to upload
```

#### **Step 2: File Upload to Backend**
```
User clicks "Upload" or file auto-uploads
    ↓
Browser creates FormData:
  {
    file: <File object - 5 GB data>
  }
    ↓
React sends HTTP POST request:
  POST http://localhost:5000/api/upload
  Headers: multipart/form-data
  Body: FormData with file
    ↓
Flask backend receives request
    ↓
Server validates file again (security check)
    ↓
File saved to disk:
  ./uploads/drive1_1735567200.E01
    ↓
Flask returns response:
  {
    "filepath": "/uploads/drive1_1735567200.E01",
    "filename": "drive1_1735567200.E01",
    "size": 5242880000
  }
    ↓
Frontend updates state: uploadStatus.uploadSuccess = true
    ↓
User sees: "Upload complete! Starting analysis..."
```

#### **Step 3: Trigger Analysis**
```
After successful upload, React automatically sends:
  POST http://localhost:5000/api/analyze
  {
    "image_path": "/uploads/drive1_1735567200.E01"
  }
    ↓
Flask backend receives request
    ↓
Creates unique analysis ID:
  analysis_id = "20260228_094921_ABC123"
    ↓
Starts background thread:
  run_forensic_analysis(
    image_path="/uploads/drive1_1735567200.E01",
    analysis_id="20260228_094921_ABC123"
  )
    ↓
Main Flask thread returns immediately (IMPORTANT - doesn't block):
  {
    "analysis_id": "20260228_094921_ABC123",
    "message": "Analysis started"
  }
    ↓
React stores analysis_id in component state
```

#### **Step 4: Poll for Progress**
```
React sets up interval timer (polls every 1 second)
    ↓
While analysis running:
  GET http://localhost:5000/api/status/20260228_094921_ABC123
    ↓
  Flask returns current status:
  {
    "status": "analyzing",
    "progress": 45,
    "message": "Scanning filesystem...",
    "errors": []
  }
    ↓
  React updates progress bar:
    Visual: ████████░░░░░░░░░░░░ 45%
    Message: "Scanning filesystem..."
    ↓
  Wait 1 second, poll again
    ↓
  Repeat until status = "complete"
```

#### **Step 5: Retrieve Results**
```
When Flask returns status = "complete":
    ↓
React sends: GET /api/results/20260228_094921_ABC123
    ↓
Flask reads JSON from disk:
  ./analysis_output/20260228_094921_ABC123/report.json
    ↓
Flask returns full forensic data (2-5 MB JSON)
    ↓
React receives and stores in state
    ↓
React displays results in ForensicAnalysisDashboard
```

### **2.3 Results Dashboard: `src/components/forensics/forensic-analysis-dashboard.tsx`**

**What it displays:**

1. **Summary Statistics Section**
   - Total files found: 15,432
   - Deleted files: 287
   - Suspicious files: 12 (flagged for review)
   - Encrypted items: 3 (BitLocker, TrueCrypt, etc.)
   - Network artifacts: 8

2. **File Extension Statistics**
   - Table showing file type distribution
   - .exe: 234 files
   - .dll: 567 files
   - .txt: 1,234 files
   - .pdf: 89 files
   - And hundreds of other extensions

3. **Suspicious Files List**
   - Red-highlighted table of suspicious files
   - Shows: name, path, size, modified date
   - Examples: malware.exe, ransomware.dll, batch_file.bat

4. **Encrypted Containers**
   - List of detected encrypted items
   - Shows encryption type and size

5. **Timeline View**
   - Chronological events (newest first)
   - Shows file modifications, accesses, creations
   - 15,000+ events searchable and sortable

6. **Download/Export Buttons**
   - "Download PDF" button → generates formatted PDF
   - "Download DOCX" button → generates Word document
   - "Copy Results" button → copies JSON to clipboard

7. **LLM Analysis Section**
   - Displays security assessment from Ollama
   - Shows recommendations and risk indicators

---

## BACKEND LAYER (Flask API)

### **3.1 Flask App: `forensic_web_app.py` (649 lines)**

This is your **main API server** handling all HTTP requests from React frontend.

**Flask Configuration:**
```python
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
app.secret_key = 'forensic-analysis-secret-key-2026'

# Configuration paths
UPLOAD_FOLDER = './uploads/'              # Temporary storage for user files
OUTPUT_FOLDER = './analysis_output/'      # Storage for results
ALLOWED_EXTENSIONS = {'raw', 'dd', 'e01', 'img', 'iso', 'bin', 'dmg'}

# Global state tracker (in-memory)
analysis_status = {
    'current': None,          # Current analysis ID
    'progress': 0,            # 0-100%
    'status': 'idle',         # idle, analyzing, complete, error
    'message': '',            # Status message
    'errors': [],             # Error list
    'results': None           # Result reference
}
```

**Why background threads?**
- Analysis takes 5-30+ minutes for large disk images
- Without threading, Flask would be locked (frontend would freeze)
- Threading allows multiple concurrent analyses
- Frontend can poll progress without blocking backend

### **3.2 API Endpoints**

#### **ENDPOINT 1: POST `/api/upload`**

**Purpose:** Receive uploaded disk image file

**Request:**
```
POST /api/upload HTTP/1.1
Content-Type: multipart/form-data

[binary file data - E01 image]
```

**Backend processing:**
```python
1. Receive multipart request
2. Validate file extension
3. Generate unique filename with timestamp
4. Save to ./uploads/ folder
5. Return success response
```

**Response:**
```json
{
  "filepath": "/uploads/drive1_1735567200.E01",
  "filename": "drive1_1735567200.E01",
  "size": 5242880000
}
```

#### **ENDPOINT 2: POST `/api/analyze`**

**Purpose:** Start forensic analysis (asynchronously)

**Request:**
```json
{
  "image_path": "/uploads/drive1_1735567200.E01"
}
```

**Backend processing:**
```python
1. Receive analysis request
2. Generate unique analysis_id: "20260228_094921_ABC123"
3. Create output folder: ./analysis_output/20260228_094921_ABC123/
4. START BACKGROUND THREAD with:
     run_forensic_analysis(image_path, analysis_id)
5. Update global status: status='analyzing', progress=0
6. Return immediately (don't wait for analysis to complete)
```

**Response:**
```json
{
  "analysis_id": "20260228_094921_ABC123",
  "message": "Analysis started"
}
```

#### **ENDPOINT 3: GET `/api/status/<analysis_id>`**

**Purpose:** Check current progress of analysis

**Request:**
```
GET /api/status/20260228_094921_ABC123
```

**Backend processing:**
```python
1. Look up analysis_id in global status
2. Return current progress
3. Doesn't wait for completion
```

**Response - While analyzing:**
```json
{
  "status": "analyzing",
  "progress": 45,
  "message": "Scanning filesystem...",
  "errors": []
}
```

**Response - After complete:**
```json
{
  "status": "complete",
  "progress": 100,
  "message": "Analysis complete",
  "errors": []
}
```

**Response - If error:**
```json
{
  "status": "error",
  "progress": 45,
  "message": "Error analyzing disk",
  "errors": ["pytsk3 library not installed", "E01 format not supported"]
}
```

#### **ENDPOINT 4: GET `/api/results/<analysis_id>`**

**Purpose:** Retrieve complete analysis results

**Request:**
```
GET /api/results/20260228_094921_ABC123
```

**Backend processing:**
```python
1. Wait for analysis to complete (if still running)
2. Read JSON report from disk:
     ./analysis_output/20260228_094921_ABC123/report.json
3. Parse and return full forensic data
```

**Response (example structure):**
```json
{
  "forensic_report": {
    "image_path": "/uploads/drive1_1735567200.E01",
    "scan_timestamp": "2026-02-28 09:49:21",
    "partition_info": {
      "filesystem_type": "NTFS",
      "block_size": 4096,
      "block_count": 263626752
    },
    "summary": {
      "total_partitions": 1,
      "total_files": 15432,
      "total_deleted_files": 287,
      "suspicious_files_count": 12,
      "encrypted_items_count": 3,
      "network_artifacts_count": 8
    },
    "files": {
      "0_system.ini": {
        "name": "system.ini",
        "path": "/Windows/system.ini",
        "size": 2048,
        "hash_sha256": "a7f8c3e2d9f1b4a6e5d4c3b2a1f0e9d8",
        "creation_time": "2020-01-15 10:30:00",
        "modification_time": "2022-06-20 14:15:00",
        "access_time": "2023-11-30 09:45:00",
        "is_deleted": false,
        "is_directory": false
      },
      "42_explorer.exe": {
        "name": "explorer.exe",
        "path": "/Windows/explorer.exe",
        "size": 4563392,
        "hash_sha256": "b8f9d4f3e1a2c3d4e5f6a7b8c9d0e1f2",
        "creation_time": "2020-01-15 10:28:00",
        "modification_time": "2024-08-10 13:22:15",
        "access_time": "2026-02-21 08:15:30",
        "is_deleted": false,
        "is_directory": false
      }
      // ... 15,430 more files
    },
    "suspicious_files": [
      {
        "name": "malware.exe",
        "path": "/Users/Admin/Downloads/malware.exe",
        "size": 2048576,
        "risk_level": "HIGH",
        "reason": "Executable in user Downloads"
      },
      // ... 11 more suspicious files
    ],
    "encrypted_items": [
      {
        "name": "encrypted.img",
        "path": "/Users/Admin/Documents/encrypted.img",
        "size": 10737418240,
        "encryption_type": "BitLocker",
        "modified": "2026-02-01 10:45:00"
      }
      // ... 2 more encrypted containers
    ],
    "file_extension_statistics": {
      ".exe": 234,
      ".dll": 567,
      ".txt": 1234,
      ".pdf": 89
      // ... hundreds of extensions
    },
    "timeline": [
      {
        "timestamp": "2026-02-21 14:20:00",
        "event_type": "modification",
        "file": "/pagefile.sys",
        "size": 2147483648
      }
      // ... 15,000 more timeline events
    ],
    "llm_analysis": "SECURITY ASSESSMENT: High-risk indicators detected..."
  }
}
```

#### **ENDPOINT 5: GET `/api/download/pdf/<analysis_id>`**

**Purpose:** Download analysis as PDF

**Request:**
```
GET /api/download/pdf/20260228_094921_ABC123
```

**Backend processing:**
```python
1. Wait for analysis to complete (if needed)
2. Check if PDF already exists:
     ./analysis_output/20260228_094921_ABC123/report.pdf
3. If not exists, generate it using ReportLab
4. Send file as HTTP attachment
```

**What PDF contains:**
- Professional header with image information
- Summary statistics in formatted tables
- File extension distribution (top 15)
- Color-coded suspicious files (RED alerts)
- Encrypted items details
- Timeline information
- LLM security assessment
- 20-30 pages total
- File size: 5-10 MB

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="report_20260228_094921.pdf"

[binary PDF data]
```

#### **ENDPOINT 6: GET `/api/download/docx/<analysis_id>`**

**Purpose:** Download analysis as Word document

**Request:**
```
GET /api/download/docx/20260228_094921_ABC123
```

**Backend processing:**
```python
1. Wait for analysis to complete (if needed)
2. Check if DOCX already exists:
     ./analysis_output/20260228_094921_ABC123/report.docx
3. If not exists, generate using python-docx library
4. Send file as HTTP attachment
```

**What DOCX contains:**
- Formatted headings and sections
- Professional tables for statistics
- Color-coded alerts for suspicious items
- Embedded file lists (sortable in Word)
- Page breaks for sections
- Editable document (users can add notes)
- 20-30 pages total
- File size: 3-5 MB

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="report_20260228_094921.docx"

[binary DOCX data]
```

---

## ANALYSIS ENGINE LAYER (Python)

### **4.1 Main Analyzer: `forensic_pipeline_advanced.py` (809 lines)**

This is where the **actual forensic analysis happens**. The Flask backend calls this.

**Class: `AdvancedForensicAnalyzer`**

#### **Initialization Phase**

```python
analyzer = AdvancedForensicAnalyzer(
    image_path="/uploads/drive1.E01",
    use_demo=False  # Use real pytsk3/pyewf if available
)
```

**What happens during initialization:**
```
1. Check if pytsk3 library installed
   └─ Required for filesystem parsing
   
2. Check if pyewf library installed
   └─ Required for .E01 format support
   
3. Check if Ollama LLM running
   └─ GET http://localhost:11434/api/tags
   
4. Initialize empty data structures:
   ├─ files_metadata = {}     # All extracted files
   ├─ file_hashes = {}        # SHA256 hashes
   ├─ timeline_events = []    # Chronological events
   ├─ encrypted_items = []    # Detected encryption
   └─ suspicious_extensions = ['.exe', '.bat', '.ps1', ...]
   
5. If libraries missing → Fall back to DEMO MODE
   └─ Uses synthetic demo data instead of real analysis
```

#### **Image Opening: `open_disk_image()`**

```
Process E01 or RAW file
        ↓
Detect file extension
        ↓
┌─ If .E01 (Encase format):
│  ├─ Check if pyewf library available
│  ├─ Use pyewf to open EWF handle
│  ├─ Create pytsk3-compatible wrapper (EWFImgInfo class)
│  └─ Result: self.img (disk image object)
│
└─ If .RAW format:
   ├─ Directly open with pytsk3
   └─ Result: self.img (disk image object)

Error handling:
  If libraries missing or file doesn't exist:
  └─ Fall back to DEMO MODE
```

**Why need both pyewf + pytsk3?**
- **pyewf library**: Reads compressed .E01 Encase format
  - Handles segmented images (image.E01, image.E02, etc.)
  - Decompresses data streams
  
- **pytsk3 library**: Parses filesystem structure
  - Reads partition tables (MBR, GPT)
  - Parses filesystems (NTFS, FAT32, ext4, APFS)
  - Extracts file metadata and inodes
  
Together: Can extract files from any E01 image on any filesystem

#### **Partition Detection: `detect_partitions()`**

```
Disk image loaded (self.img)
        ↓
Use pytsk3 Volume System (VS) parser
        ↓
Read partition table:
  └─ MBR (Master Boot Record) - traditional
  └─ GPT (GUID Partition Table) - modern
        ↓
For each partition found:
  ├─ Get address (starting sector)
  ├─ Get offset (byte position on disk)
  └─ Get size (number of bytes)
        ↓
Example output:
  Partition 0:
    Address: 0
    Offset: 1,048,576 bytes (after MBR)
    Size: 1,099,508,482,048 bytes (1 TB)
  
  Partition 1:
    Address: 1
    Offset: 1,099,512,377,344 bytes
    Size: 549,755,813,888 bytes (512 GB)
```

#### **Filesystem Opening: `open_filesystem()`**

```
First partition detected
        ↓
Use pytsk3 FS (File System) parser
        ↓
Attempt to mount filesystem
        ↓
Auto-detect filesystem type:
  ├─ NTFS (Windows primary)
  ├─ FAT32 (older Windows, USB drives)
  ├─ exFAT (external drives)
  ├─ ext4 (Linux primary)
  ├─ ext3, ext2 (older Linux)
  ├─ HFS+ (macOS)
  └─ Others (UFS, Btrfs, etc.)
        ↓
Extract filesystem metadata:
  ├─ Block size (typically 4,096 bytes)
  ├─ Total blocks available
  ├─ Free space
  ├─ Used space
  ├─ Inode count
  ├─ Inode size
  └─ Creation timestamp
        ↓
Result: self.filesystem (filesystem object for file access)
```

#### **Recursive File Scanning: `recursively_scan_files()` → `_scan_directory()`**

This is the **core analysis engine** - most time-consuming step.

```
Initialize: Start at root directory /
        ↓
For EACH file/folder entry in current directory:
  ├─ Get filename from directory entry
  ├─ Get inode number (unique file identifier)
  ├─ Check allocation status:
  │   ├─ Allocated bit set? → File still exists
  │   └─ Allocated bit clear? → File deleted (recoverable)
  │
  ├─ Open inode object for file metadata:
  │   ├─ File size (bytes)
  │   ├─ Creation time (crtime)
  │   ├─ Modification time (mtime)
  │   ├─ Access time (atime)
  │   ├─ Change time (ctime)
  │   ├─ File mode (regular file? directory? symlink?)
  │   ├─ Permission bits (755, 644, etc.)
  │   ├─ Owner UID / Group GID
  │   └─ Link count
  │
  ├─ Store complete metadata:
  │   files_metadata[unique_key] = {
  │     'name': 'malware.exe',
  │     'path': '/Users/Admin/Downloads/malware.exe',
  │     'size': 2048576,
  │     'inode': 256,
  │     'creation_time': '2025-10-15 22:45:00',
  │     'modification_time': '2025-10-15 22:45:00',
  │     'access_time': '2025-10-16 08:15:30',
  │     'is_deleted': false,
  │     'is_directory': false
  │   }
  │
  ├─ Extract file extension:
  │   └─ Add to file_extension_stats counter:
  │       file_extension_stats['.exe'] += 1
  │
  ├─ Check if deleted:
  │   └─ If is_deleted = true:
  │       deleted_files_count += 1
  │
  ├─ If directory:
  │   └─ Recursive call: _scan_directory(subdirectory)
  │       Will scan all files inside:
  │       /Windows → /Windows/System32 → 1000s of .dll files
  │       /Users → /Users/Admin → all user documents
  │       /Program Files → all installed apps
  │       And so on...
  │
  └─ Add to timeline events:
      timeline_events.append({
        'timestamp': modification_time,
        'event_type': 'modification',
        'file': file_path,
        'size': file_size
      })

FINAL RESULTS:
  Total files scanned: 15,432 files
  Deleted files found: 287 deleted files (recoverable)
  Total size analyzed: 1+ TB
  Total timeline events: 15,000+ events
```

**Time complexity:**
- Depends on disk size and file count
- Typical: 5-10 minutes for 1 TB disk
- Large: 20-30+ minutes for 5+ TB disk

#### **Hash Computation: `compute_file_hashes()`**

For **each file** found in filesystem:

```
File: /Windows/explorer.exe (size: 4.5 MB)
        ↓
Read file from disk IN CHUNKS:
  ├─ Chunk 1: 65 KB
  ├─ Chunk 2: 65 KB
  ├─ Chunk 3: 65 KB
  └─ ... until entire file read
        ↓
Hash each chunk with SHA256:
  hash_object = hashlib.sha256()
  
  For each chunk:
    hash_object.update(chunk_bytes)
        ↓
Final hash: 
  sha256_hash = hash_object.hexdigest()
  Result: "a7f8c3e2d9f1b4a6e5d4c3b2a1f0e9d8c7b6a5f"
        ↓
Store in dictionary:
  file_hashes["42_explorer.exe"] = "a7f8c3e2d9f1b4a6..."
```

**Why chunk-based reading?**
- Prevents loading entire file into RAM
- For 5 GB file, would require 5 GB RAM if loaded at once
- Streaming approach uses minimal memory

**Why SHA256 hashes?**
1. **Detect file tampering** (hash changed = file modified)
2. **Identify duplicate files** (same hash = same content)
3. **Match against malware databases** (known malicious hashes)
4. **Evidence integrity** (cryptographic proof of file contents)

#### **Suspicious File Detection: `detect_suspicious_patterns()`**

```
For EACH file in files_metadata:
        ↓
CHECK FILE EXTENSION:
  If extension in suspicious list:
    ├─ .exe (Windows executable)
    ├─ .bat (Batch script)
    ├─ .ps1 (PowerShell script)
    ├─ .vbs (VBScript)
    ├─ .dll (Dynamic library)
    ├─ .scr (Screensaver)
    ├─ .js (JavaScript)
    ├─ .com (DOS executable)
    ├─ .msi (Windows installer)
    ├─ .sys (System driver)
    ├─ .pif (Program info file)
    ├─ .cmd (Command script)
    ├─ .jar (Java archive)
    └─ .sh (Shell script)
        ↓
  Then add to suspicious_files[] list:
    {
      'name': 'malware.exe',
      'path': '/Users/Admin/Downloads/malware.exe',
      'size': 2048576,
      'risk_level': 'HIGH',
      'reason': 'Executable found in Downloads folder'
    }
        ↓
CHECK PATH PATTERNS:
  If file path matches suspicious pattern:
    ├─ Recently created (< 7 days old)
    ├─ Modified after creation (sign of malicious persistence)
    ├─ Located in Startup folders (auto-run location)
    ├─ Located in Temp folders (temporary malware staging)
    ├─ Obfuscated name (random characters, suspicious patterns)
    └─ Hidden file (filename starts with . or has hidden flag)
        ↓
  Mark with elevated risk level
```

**Result:**
- 12 suspicious files flagged
- Red alerts in reports
- Highlighted for analyst review

#### **Encryption Detection: `detect_encrypted_containers()`**

```
For EACH file in filesystem:
        ↓
Read FIRST 512 BYTES (file header/magic bytes)
        ↓
COMPARE AGAINST ENCRYPTION SIGNATURES:
  
  TrueCrypt signature:    b'TRUE'
  VeraCrypt signature:    b'VERA'
  BitLocker signature:    b'VALID_TABLE'
  LUKS signature:         b'LUKS\xba\xbe'
  PGP signature:          b'\x99'
  And others...
        ↓
IF SIGNATURE MATCHES:
  Add to encrypted_items[] list:
    {
      'name': 'encrypted.img',
      'path': '/Users/Admin/Documents/encrypted.img',
      'size': 10737418240,
      'encryption_type': 'BitLocker',
      'modified': '2026-02-01 10:45:00'
    }
```

**What this means:**
- BitLocker (3 GB): Windows full-disk encryption
- TrueCrypt (10 GB): Legacy encryption container
- LUKS (2 GB): Linux Unified Key Setup
- **Result:** 3 encrypted containers found → potential data hiding

#### **Timeline Construction: `build_timeline()`**

```
For EACH file in files_metadata:
        ↓
Extract TIMESTAMPS:
  ├─ Creation time (crtime)    "2025-10-15 22:45:00"
  ├─ Modification time (mtime) "2025-10-15 22:45:00"
  └─ Access time (atime)       "2025-10-16 08:15:30"
        ↓
Create TIMELINE EVENTS:
  {
    'timestamp': '2025-10-15 22:45:00',
    'event_type': 'file_created',
    'file': '/Users/Admin/Downloads/malware.exe',
    'size': 2048576
  }
        ↓
REPEAT FOR ALL FILES
        ↓
SORT CHRONOLOGICALLY (newest first)
        ↓
RESULT - Timeline shows what happened:
  2026-02-21 14:20:00 → Modified: /pagefile.sys (system memory swap)
  2026-02-21 09:10:00 → Accessed: /Windows/System32/ntdll.dll (critical system)
  2026-02-21 08:15:30 → Accessed: /Windows/explorer.exe (file manager launch)
  2026-02-20 15:30:00 → Modified: /Windows/System32/drivers/etc/hosts (DNS config)
  2025-12-20 14:30:00 → Accessed: /Users/Admin/AppData/Local/Temp/deleted_file.tmp
  ...

SIGNIFICANCE:
  Can see suspicious activity patterns:
  - Large file access at unusual times
  - System files modified by malware
  - Hosts file changed (potential DNS hijack)
  - Multiple executables accessed in sequence
```

### **4.2 LLM Integration: `call_local_llm()`**

```
Analysis data ready
        ↓
CHECK IF OLLAMA RUNNING:
  GET http://localhost:11434/api/tags
    ├─ If successful → llm_available = True
    └─ If fails → llm_available = False
        ↓
IF LLM AVAILABLE:
  FORMAT FORENSIC DATA INTO PROMPT:
    """
    You are a forensic security analyst. Analyze this disk evidence:
    
    - Disk Image: drive1.E01 (1 TB, NTFS)
    - Total Files: 15,432
    - Deleted Files: 287
    - Suspicious Files: 12 (.exe, .dll, .ps1)
    - Encrypted Containers: 3 (BitLocker, TrueCrypt, LUKS)
    - Timeline: Last activity 2 hours ago
    - High-risk Activities:
      * Executable in Downloads folder
      * Host file modified 3 days ago
      * Encrypted container with recent modifications
      * Multiple system files accessed in sequence
    
    Provide concise security assessment and recommendations.
    """
        ↓
  POST TO OLLAMA:
    POST http://localhost:11434/api/generate
    {
      "model": "llama2",
      "prompt": "[formatted prompt above]",
      "stream": false,
      "temperature": 0.7
    }
        ↓
  WAIT FOR RESPONSE (up to 120 seconds):
    llama2 analyzes forensic data
    Generates security assessment
        ↓
  RECEIVE LLM ANALYSIS:
    """
    SECURITY ASSESSMENT: HIGH RISK
    
    Critical Findings:
    - Malware indicators detected in Downloads
    - Encryption containers suggest data exfiltration attempt
    - Host file modification indicates DNS manipulation
    - Timeline shows sustained suspicious activity
    
    Recommendations:
    1. IMMEDIATE: Isolate system from network
    2. URGENT: Analyze network traffic logs
    3. HIGH: Examine deleted files for recovery
    4. HIGH: Check for lateral movement indicators
    5. MEDIUM: Document chain of custody
    """
        ↓
  STORE IN llm_analysis field
  
ELSE (LLM NOT AVAILABLE):
  Skip LLM analysis
  Use rule-based assessment only
```

---

## DATA GENERATION & STORAGE

### **5.1 JSON Report Generation: `generate_json_report()`**

```
Analysis complete
        ↓
CREATE ANALYSIS FOLDER:
  analysis_id = "20260228_094921_ABC123"
  mkdir ./analysis_output/20260228_094921_ABC123/
        ↓
BUILD JSON STRUCTURE:
{
  "forensic_report": {
    "image_path": "/uploads/drive1.E01",
    "scan_timestamp": "2026-02-28 09:49:21",
    
    "partition_info": {
      "filesystem_type": "NTFS",
      "block_size": 4096,
      "block_count": 263626752,
      "total_size_bytes": 1099508482048
    },
    
    "summary": {
      "total_partitions": 1,
      "total_files": 15432,
      "total_deleted_files": 287,
      "suspicious_files_count": 12,
      "encrypted_items_count": 3,
      "network_artifacts_count": 8
    },
    
    "files": {
      "0_system.ini": {
        "name": "system.ini",
        "path": "/Windows/system.ini",
        "size": 2048,
        "inode": 5,
        "hash_sha256": "a7f8c3e2d9f1b4a6e5d4c3b2a1f0e9d8...",
        "creation_time": "2020-01-15 10:30:00",
        "modification_time": "2022-06-20 14:15:00",
        "access_time": "2023-11-30 09:45:00",
        "is_deleted": false,
        "is_directory": false
      },
      // ... 15,431 more files
    },
    
    "suspicious_files": [
      {
        "name": "malware.exe",
        "path": "/Users/Admin/Downloads/malware.exe",
        "size": 2048576,
        "risk_level": "HIGH"
      },
      // ... 11 more
    ],
    
    "encrypted_items": [
      {
        "name": "encrypted.img",
        "path": "/Users/Admin/Documents/encrypted.img",
        "size": 10737418240,
        "encryption_type": "BitLocker"
      },
      // ... 2 more
    ],
    
    "file_extension_statistics": {
      ".exe": 234,
      ".dll": 567,
      ".txt": 1234,
      ".pdf": 89
      // ... hundreds more
    },
    
    "timeline": [
      {
        "timestamp": "2026-02-21 14:20:00",
        "event_type": "modification",
        "file": "/pagefile.sys",
        "size": 2147483648
      },
      // ... 15,000 more events
    ],
    
    "llm_analysis": "SECURITY ASSESSMENT: High-risk indicators detected..."
  }
}
        ↓
SAVE TO DISK:
  ./analysis_output/20260228_094921_ABC123/report.json
  
  File size: 2-5 MB
  Total lines: 15,000+
```

### **5.2 Text Summary Generation: `generate_summary_report()`**

```
Reads JSON report
        ↓
Formats into HUMAN-READABLE TEXT:

══════════════════════════════════════════════════════════════════════════════
COMPREHENSIVE FORENSIC ANALYSIS REPORT
══════════════════════════════════════════════════════════════════════════════

Image Path: /uploads/drive1.E01
Scan Timestamp: 2026-02-28 09:49:21
Analysis Duration: 12 minutes 34 seconds

FILESYSTEM INFORMATION:
────────────────────────────────────────────────────────────────────────────
Filesystem Type: NTFS
Block Size: 4,096 bytes
Block Count: 263,626,752
Total Capacity: 1.0 TB
Used Space: 750 GB (75%)
Free Space: 250 GB (25%)

FILE STATISTICS:
────────────────────────────────────────────────────────────────────────────
Total Partitions: 1
Total Files Found: 15,432
├─ Regular files: 14,800
├─ Directories: 632
└─ Symlinks: 0

Deleted Files: 287 (recoverable)
Suspicious Files: 12 (requires review)
Encrypted Items: 3 (potential data hiding)
Network Artifacts: 8 (connection history)

SUSPICIOUS FILES DETECTED:
────────────────────────────────────────────────────────────────────────────
1. malware.exe
   ├─ Location: /Users/Admin/Downloads/malware.exe
   ├─ Size: 2.0 MB
   ├─ Created: 2025-10-15 22:45:00
   ├─ Modified: 2025-10-15 22:45:00
   ├─ Accessed: 2025-10-16 08:15:30
   ├─ Hash: a7f8c3e2d9f1b4a6...
   ├─ Risk Level: HIGH
   └─ Reason: Executable in user Downloads

[... 11 more suspicious files ...]

ENCRYPTED CONTAINERS:
────────────────────────────────────────────────────────────────────────────
1. encrypted.img (10.0 GB)
   ├─ Location: /Users/Admin/Documents/encrypted.img
   ├─ Encryption Type: BitLocker
   ├─ Last Modified: 2026-02-01 10:45:00
   └─ Note: Potential evidence of data hiding

[... 2 more encrypted containers ...]

FILE EXTENSION DISTRIBUTION (Top 20):
────────────────────────────────────────────────────────────────────────────
.exe:   234 files (3.8%)
.dll:   567 files (9.2%)
.txt:  1,234 files (20.1%)
.pdf:    89 files (1.4%)
[...]

TIMELINE (Recent Activity - Last 30 Days):
────────────────────────────────────────────────────────────────────────────
2026-02-21 14:20:00 - Modified: /pagefile.sys (2.0 GB)
2026-02-21 09:10:00 - Accessed: /Windows/System32/ntdll.dll
2026-02-21 08:15:30 - Accessed: /Windows/explorer.exe
2026-02-20 15:30:00 - Modified: /Windows/System32/drivers/etc/hosts
2025-12-20 14:30:00 - Accessed: /Users/Admin/AppData/Local/Temp/deleted_file.tmp
[... 15,000 more events ...]

LLM ANALYSIS & SECURITY ASSESSMENT:
────────────────────────────────────────────────────────────────────────────
SECURITY ASSESSMENT: HIGH RISK

Critical Findings:
- Malware indicators detected in downloaded files
- Suspicious activity pattern observed
- Encrypted containers suggest data hiding
- Timeline shows sustained suspicious access patterns

Recommendations:
1. IMMEDIATE: Isolate system from network
2. URGENT: Examine network logs for command & control
3. HIGH: Recover and analyze deleted files
4. HIGH: Check for lateral movement
5. MEDIUM: Document evidence chain of custody

════════════════════════════════════════════════════════════════════════════════

        ↓
SAVE TO DISK:
  ./analysis_output/20260228_094921_ABC123/summary.txt
  
  File size: 100-200 KB
  Human readable, no special formatting needed
```

### **5.3 PDF Report Generation: `generate_pdf_report()`**

```
Uses ReportLab library (Python PDF generation)
        ↓
CREATE FORMATTED PDF:
  ├─ Title Page
  │  └─ "FORENSIC ANALYSIS REPORT"
  │
  ├─ Page 1: Image Information
  │  ├─ Image Path: /uploads/drive1.E01
  │  ├─ File Size: 5 GB
  │  ├─ File Hash: SHA256...
  │  ├─ Analysis Date: 2026-02-28 09:49:21
  │  └─ Duration: 12 minutes 34 seconds
  │
  ├─ Page 2-3: Summary Statistics (Tables)
  │  ├─ Total Files: 15,432
  │  ├─ Deleted Files: 287
  │  ├─ Suspicious Files: 12 (RED highlighted)
  │  ├─ Encrypted Items: 3
  │  └─ Network Artifacts: 8
  │
  ├─ Page 4-5: File Extension Distribution (Chart-like Table)
  │  ├─ .exe: 234 files
  │  ├─ .dll: 567 files
  │  ├─ .txt: 1,234 files
  │  └─ ... (top 15 extensions)
  │
  ├─ Page 6-10: Suspicious Files (RED alerts)
  │  ├─ Name | Path | Size | Hash | Risk Level
  │  ├─ [Table with RED background for high-risk items]
  │  └─ Up to 20 suspicious files per page
  │
  ├─ Page 11-15: Encrypted Containers
  │  ├─ Name, Location, Type, Size
  │  ├─ Encryption signature detected
  │  └─ "Potential evidence of data hiding"
  │
  ├─ Page 16-20: Timeline (Recent Activity)
  │  ├─ Chronological events
  │  ├─ Timestamp, Event Type, File, Size
  │  └─ Last 30 days of activity
  │
  └─ Page 21-30: LLM Analysis & Recommendations
     ├─ Security Assessment
     ├─ Critical Findings
     ├─ Risk Indicators
     └─ Recommended Actions

STYLING:
  ├─ Professional colors (Cyan, Red for alerts)
  ├─ Clear typography and spacing
  ├─ Alternating row colors for tables
  ├─ Page headers/footers with analysis ID
  └─ QR code linking to full JSON report (optional)

        ↓
SAVE TO DISK:
  ./analysis_output/20260228_094921_ABC123/report.pdf
  
  File size: 5-10 MB
  Pages: 20-30
  Fully searchable text
```

### **5.4 DOCX Report Generation: `generate_docx_report()`**

```
Uses python-docx library (Microsoft Word generation)
        ↓
CREATE WORD DOCUMENT:
  ├─ Title: "FORENSIC ANALYSIS REPORT"
  ├─ Subtitle with analysis ID and timestamp
  │
  ├─ Section 1: Executive Summary
  │  ├─ Overview of findings
  │  ├─ Risk level assessment
  │  └─ Key recommendations
  │
  ├─ Section 2: Image Information
  │  ├─ File path, size, hash
  │  └─ Analysis metadata
  │
  ├─ Section 3: Statistics (Formatted Table)
  │  ├─ Total files, deleted files, suspicious files
  │  └─ Color-coded rows for risk levels
  │
  ├─ Section 4: Suspicious Files (RED alerts)
  │  ├─ Sortable table in Word
  │  ├─ Red background for high-risk items
  │  └─ Can add analyst notes/comments
  │
  ├─ Section 5: Encrypted Items
  │  ├─ List of detected encryption
  │  └─ Encryption type and significance
  │
  ├─ Section 6: Timeline
  │  ├─ Chronological table of events
  │  └─ Can filter/sort in Word
  │
  └─ Section 7: LLM Analysis
     ├─ Security assessment
     ├─ Findings and recommendations
     └─ Copy-paste analyst notes section

FORMATTING:
  ├─ Professional Word styles
  ├─ Formatted headings (Heading 1, 2, 3)
  ├─ Color-coded tables
  ├─ Page breaks between sections
  ├─ Printable layout
  ├─ Editable by users (can add annotations)
  └─ Compatible with Word 2010+, Google Docs, LibreOffice

ADVANTAGES OVER PDF:
  ├─ Can edit and add notes
  ├─ Can reorganize sections
  ├─ Can share with annotations
  ├─ Smaller file size
  └─ Works in all office suites

        ↓
SAVE TO DISK:
  ./analysis_output/20260228_094921_ABC123/report.docx
  
  File size: 3-5 MB
  Pages: 20-30 (depending on content)
  Fully editable
```

---

## COMPLETE END-TO-END FLOW

### **Step 1: User Interaction (React Frontend)**

```
User opens http://localhost:5173 in browser
    ↓
Sees forensic analysis interface
    ↓
Clicks "Upload Evidence" button
    ↓
File picker opens
    ↓
User selects drive1.E01 (5 GB disk image)
    ↓
Component validates: Is extension .E01? YES ✓
    ↓
Shows progress bar "Uploading..."
    ↓
React starts upload
```

### **Step 2: File Upload (Flask Backend)**

```
React sends: POST /api/upload (multipart/form-data with file)
    ↓
Flask receives file stream
    ↓
Backend validates extension again (security check)
    ↓
Generates unique filename with timestamp:
  drive1_1735567200.E01
    ↓
Saves to: ./uploads/drive1_1735567200.E01
    ↓
Returns success: {
  "filepath": "/uploads/drive1_1735567200.E01",
  "size": 5242880000
}
    ↓
React shows: "Upload complete! Starting analysis..."
```

### **Step 3: Start Analysis (Flask Backend)**

```
React sends: POST /api/analyze { "image_path": "/uploads/drive1..." }
    ↓
Flask creates unique ID: "20260228_094921_ABC123"
    ↓
Creates output folder: ./analysis_output/20260228_094921_ABC123/
    ↓
STARTS BACKGROUND THREAD with run_forensic_analysis()
    ↓
Main thread returns immediately: {
  "analysis_id": "20260228_094921_ABC123"
}
    ↓
React stores analysis_id in state
    ↓
React shows: "Analysis starting..."
```

### **Step 4: Forensic Analysis (Background Thread)**

```
BACKGROUND THREAD RUNNING:

[5%] Initialize analyzer
  └─ Check pytsk3/pyewf availability
  └─ Check Ollama LLM status

[10%] Open disk image
  └─ pyewf opens .E01 file
  └─ pytsk3 creates filesystem view

[15%] Detect partitions
  └─ Read partition table
  └─ Find 1 partition of 1 TB

[20%] Open filesystem
  └─ Detect NTFS filesystem
  └─ Read filesystem metadata

[25-85%] Recursive file scan (LONGEST STEP)
  ├─ Start at root /
  ├─ Recursively scan ALL subdirectories:
  │   /Windows → /Windows/System32 → 1000s of .dll files
  │   /Users → /Users/Admin → all user documents
  │   /Program Files → all installed applications
  │   And entire disk recursively...
  ├─ For each file:
  │   ├─ Extract metadata
  │   ├─ Check if deleted
  │   ├─ Check suspicious extension
  │   ├─ Compute SHA256 hash
  │   └─ Add to timeline
  └─ Results:
      15,432 files scanned
      287 deleted files recovered

[88%] Detect suspicious patterns
  └─ Find 12 suspicious files (.exe, .dll, .ps1)
  └─ Flag files in Downloads folder
  └─ Flag recently modified files

[90%] Detect encrypted containers
  └─ Scan file headers for encryption signatures
  └─ Find 3 encrypted containers

[92%] Build timeline
  └─ Sort all events chronologically
  └─ 15,000+ timeline events

[95%] Call local LLM
  └─ Send forensic data to Ollama
  └─ llama2 analyzes data
  └─ Get security assessment (30-50 seconds)

[98%] Generate reports
  ├─ Create JSON structure (2-5 MB)
  ├─ Generate text summary (100 KB)
  ├─ Generate timeline report (200 KB)
  ├─ Generate PDF (ReportLab, 20+ pages)
  └─ Generate DOCX (python-docx, 20+ pages)

[100%] Mark complete
  └─ Update status: "complete"
  └─ Store results reference

DURATION: 5-30 minutes (depending on disk size)
```

### **Step 5: Progress Polling (React Frontend)**

```
While analysis running:
    ↓
React polls every 1 second:
  GET /api/status/20260228_094921_ABC123
    ↓
Flask returns:
  {
    "status": "analyzing",
    "progress": 45,
    "message": "Scanning filesystem..."
  }
    ↓
React updates progress bar:
  ████████░░░░░░░░░░░░ 45%
    ↓
React updates message:
  "Scanning filesystem..."
    ↓
Wait 1 second, poll again
    ↓
User sees LIVE progress updates every second
```

### **Step 6: Results Retrieval (Flask Backend)**

```
When status = "complete":
    ↓
React sends: GET /api/results/20260228_094921_ABC123
    ↓
Flask reads: ./analysis_output/20260228_094921_ABC123/report.json
    ↓
Parses JSON (15,000+ lines)
    ↓
Returns full structure with all forensic data
    ↓
React receives JSON (2-5 MB data transfer)
```

### **Step 7: Display Results (React Frontend)**

```
ForensicAnalysisDashboard component renders:

┌─────────────────────────────────────────────────┐
│ ANALYSIS RESULTS                                │
├─────────────────────────────────────────────────┤
│ Summary                                         │
│ • Total Files: 15,432                          │
│ • Deleted Files: 287                           │
│ • Suspicious Files: 12 ⚠️                       │
│ • Encrypted Items: 3 🔐                         │
├─────────────────────────────────────────────────┤
│ Suspicious Files                                │
│ [Table with RED highlighting]                   │
│  malware.exe | /Users/.../Downloads | 2.0 MB  │
│  ransomware.dll | /Windows/System32 | 1.0 MB  │
│  [... 10 more ...]                              │
├─────────────────────────────────────────────────┤
│ All Files (scrollable, 15,432 rows)             │
│ [Table with all file metadata]                  │
├─────────────────────────────────────────────────┤
│ Timeline (Recent Activity)                      │
│ [Chronological list, 15,000+ events]            │
├─────────────────────────────────────────────────┤
│ [📥 Download PDF] [📥 Download DOCX]           │
└─────────────────────────────────────────────────┘
```

### **Step 8: Export Reports (React + Flask)**

```
User clicks "Download PDF":
    ↓
React sends: GET /api/download/pdf/20260228_094921_ABC123
    ↓
Flask reads or generates: ./analysis_output/.../report.pdf
    ↓
Sends file as download (5-10 MB)
    ↓
Browser downloads: report_20260228_094921.pdf
    ↓
User opens in Adobe Reader / Preview
    ↓
PDF shows professional forensic report

User clicks "Download DOCX":
    ↓
Similar flow but saves as Word document
    ↓
Browser downloads: report_20260228_094921.docx
    ↓
User opens in Microsoft Word
    ↓
Can edit, copy, add notes, share easily
```

---

## KEY DATA TRANSFORMATIONS

### **E01 Binary File → Readable Forensic Report**

```
drive1.E01 (5 GB compressed binary)
    ↓
[pyewf reads EWF compression format]
    ↓
Raw disk data stream (1 TB when decompressed)
    ↓
[pytsk3 parses filesystem structure]
    ↓
File metadata + inode information
    ↓
[AdvancedForensicAnalyzer processes]
    ├─ Extracts: name, size, timestamps, deleted status
    ├─ Computes: SHA256 hashes
    ├─ Classifies: suspicious extensions, encryption types
    └─ Organizes: timeline, statistics
    ↓
Python data structures (dictionaries, lists)
    ↓
[Converted to JSON format]
    ↓
JavaScript receives JSON (via HTTP)
    ↓
[React displays in browser UI]
    ↓
User can export:
    ├─ [ReportLab formats to PDF]
    ├─ [python-docx formats to DOCX]
    └─ [Text export]
    ↓
Professional human-readable forensic reports
    ↓
User downloads and archives reports
```

---

## FOLDER RESPONSIBILITIES SUMMARY

| Folder | Purpose | Responsibility | File Types |
|--------|---------|-----------------|-----------|
| **src/** | React frontend source | UI rendering, user interaction | .tsx, .ts, .css |
| **src/components/forensics/** | Forensic components | Upload, dashboard, results | .tsx files |
| **uploads/** | Temporary storage | Holds uploaded E01/RAW files | .E01, .raw, .dd, .img |
| **analysis_output/** | Generated reports | Stores all analysis artifacts | .json, .txt, .pdf, .docx |
| **forensic-env/** | Python environment | Isolated Python dependencies | venv, packages |
| **libewf/** | EWF library | Handles E01 format | .c, .h, .o libraries |
| **public/** | Static assets | Frontend images, fonts | .png, .jpg, .woff |
| **templates/** | HTML templates | Report templates | .html files |

---

## DATA FLOW COMPLEXITY

### **Why This System Is Complex:**

1. **Large File Handling** (E01 images 5-500 GB)
   - Streamed, not loaded entirely into RAM
   - Chunk-by-chunk processing
   - Memory-efficient design

2. **Recursive Filesystem Traversal** (15,000+ files)
   - Every file scanned for metadata
   - Deleted files recovered and analyzed
   - Deep directory structures (100+ levels)
   - Timeline built from all timestamps

3. **Hash Computation** (SHA256 for each file)
   - CPU intensive for large files
   - Must read entire file content
   - Streaming approach uses minimal RAM

4. **LLM Integration** (optional but powerful)
   - Sends forensic data to Ollama
   - Gets intelligent analysis/recommendations
   - 30-120 second wait time
   - Fallback if LLM unavailable

5. **Multi-Format Report Generation** (JSON, PDF, DOCX, TXT)
   - JSON for data interchange (2-5 MB)
   - PDF with formatting (5-10 MB, 20+ pages)
   - DOCX for editing (3-5 MB, 20+ pages)
   - Text for human reading (100-200 KB)

6. **Asynchronous Processing**
   - Flask doesn't block on analysis
   - Browser polls for progress
   - Multiple users can analyze simultaneously
   - Background threads managed carefully

7. **Cross-Stack Communication**
   - React (frontend) → Flask (backend)
   - Flask → Python analysis engine
   - Multiple HTTP requests per analysis
   - WebSocket alternative (not currently used)

---

## SUMMARY

Your forensic analysis system is a **sophisticated multi-layer pipeline**:

1. **Frontend Layer**: React UI for file upload and result display
2. **API Layer**: Flask backend exposing REST endpoints
3. **Analysis Layer**: Python forensic engine with LLM integration
4. **Storage Layer**: Disk storage for uploads and generated reports
5. **Export Layer**: Multiple report formats (JSON, PDF, DOCX, TXT)

**Key Flow:**
```
Upload E01 → Async Analysis → Progress Polling → Results Display → Export Reports
```

**Total Time:** 5-30 minutes per analysis (depending on disk size)
**Maximum Concurrent:** Unlimited (each analysis runs in separate thread)
**Report Size:** 2-10 MB per analysis
**Scalability:** Can handle multiple users with separate analysis threads

---

**Document Version:** 1.0  
**Last Updated:** March 1, 2026  
**Status:** Complete and Ready for Implementation  

---

*This documentation provides a comprehensive guide to your forensic analysis pipeline, covering all components from user interaction to report generation.*
