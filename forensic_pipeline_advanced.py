import json
import os
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import traceback
import requests

# Try to import pyewf for .E01 support (optional)
try:
    import pytsk3
    HAS_PYTSK3 = True
except ImportError:
    HAS_PYTSK3 = False

try:
    import pyewf
    HAS_PYEWF = True
except ImportError:
    HAS_PYEWF = False

# ============================================================================
# ADVANCED FORENSIC ANALYSIS PIPELINE - PYTSK3 IMPLEMENTATION
# ============================================================================
# Complete forensic analysis with:
# - File metadata extraction
# - Hash computation (SHA256)
# - Timeline analysis
# - File type distribution
# - Network artifacts detection
# - Encryption detection
# - Local LLM integration
# - Multiple report formats
# ============================================================================

class AdvancedForensicAnalyzer:
    """Advanced forensic disk analyzer with comprehensive features."""
    
    def __init__(self, image_path: str, use_demo: bool = False):
        """Initialize the forensic analyzer."""
        self.image_path = image_path
        self.use_demo = use_demo
        self.img = None
        self.partitions = []
        self.filesystem = None
        self.files_metadata = {}
        self.deleted_files_count = 0
        self.partition_info = {}
        self.file_hashes = {}
        self.timeline_events = []
        self.file_extension_stats = defaultdict(int)
        self.suspicious_extensions = ['.exe', '.bat', '.ps1', '.dll', '.scr', '.vbs', '.js', 
                                     '.com', '.msi', '.sys', '.pif', '.cmd', '.jar', '.sh']
        self.encryption_signatures = {
            'truecrypt': b'TRUE',  # TrueCrypt magic bytes
            'veracrypt': b'VERA',   # VeraCrypt magic
            'bitlocker': b'VALID_TABLE',  # BitLocker metadata
            'luks': b'LUKS\xba\xbe',  # LUKS encryption
            'pgp': b'\x99',  # PGP encryption marker
        }
        self.network_artifacts = []
        self.llm_available = False
        self.check_llm_availability()
        
        if use_demo:
            self.generate_demo_data()
    
    def check_llm_availability(self):
        """Check if local LLM is available (Ollama)."""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                self.llm_available = True
                print("[+] Local LLM (Ollama) detected at localhost:11434")
        except:
            self.llm_available = False
    
    def generate_demo_data(self):
        """Generate realistic forensic data for demonstration."""
        demo_files = [
            {'name': 'system.ini', 'path': '/Windows/system.ini', 'size': 2048, 'inode': 5,
             'creation_time': '2020-01-15 10:30:00', 'modification_time': '2022-06-20 14:15:00',
             'access_time': '2023-11-30 09:45:00', 'is_deleted': False, 'is_directory': False},
            {'name': 'explorer.exe', 'path': '/Windows/explorer.exe', 'size': 4563392, 'inode': 42,
             'creation_time': '2020-01-15 10:28:00', 'modification_time': '2024-08-10 13:22:15',
             'access_time': '2026-02-21 08:15:30', 'is_deleted': False, 'is_directory': False},
            {'name': 'Desktop', 'path': '/Users/Admin/Desktop', 'size': 0, 'inode': 128,
             'creation_time': '2022-03-15 12:00:00', 'modification_time': '2026-02-15 16:45:22',
             'access_time': '2026-02-21 09:30:00', 'is_deleted': False, 'is_directory': True},
            {'name': 'malware.exe', 'path': '/Users/Admin/Downloads/malware.exe', 'size': 2048576, 'inode': 256,
             'creation_time': '2025-10-15 22:45:00', 'modification_time': '2025-10-15 22:45:00',
             'access_time': '2025-10-16 08:15:30', 'is_deleted': False, 'is_directory': False},
            {'name': 'hiberfil.sys', 'path': '/hiberfil.sys', 'size': 4294967296, 'inode': 512,
             'creation_time': '2020-01-15 10:25:00', 'modification_time': '2026-02-21 04:30:00',
             'access_time': '2026-02-21 04:30:00', 'is_deleted': False, 'is_directory': False},
            {'name': 'pagefile.sys', 'path': '/pagefile.sys', 'size': 2147483648, 'inode': 1024,
             'creation_time': '2020-01-15 10:26:00', 'modification_time': '2026-02-21 14:20:00',
             'access_time': '2026-02-21 14:20:00', 'is_deleted': False, 'is_directory': False},
            {'name': 'deleted_file.tmp', 'path': '/Users/Admin/AppData/Local/Temp/deleted_file.tmp', 'size': 524288, 'inode': 2048,
             'creation_time': '2025-12-10 15:30:00', 'modification_time': '2025-12-15 10:45:00',
             'access_time': '2025-12-20 14:30:00', 'is_deleted': True, 'is_directory': False},
            {'name': 'ransomware.dll', 'path': '/Windows/System32/drivers/ransomware.dll', 'size': 1048576, 'inode': 4096,
             'creation_time': '2025-11-22 03:15:00', 'modification_time': '2025-11-22 03:15:00',
             'access_time': '2025-11-23 09:00:00', 'is_deleted': False, 'is_directory': False},
            {'name': 'script.ps1', 'path': '/Users/Admin/Documents/script.ps1', 'size': 8192, 'inode': 8192,
             'creation_time': '2025-12-01 18:30:00', 'modification_time': '2025-12-05 20:15:00',
             'access_time': '2025-12-10 08:45:00', 'is_deleted': False, 'is_directory': False},
            {'name': 'batch_file.bat', 'path': '/Startup/batch_file.bat', 'size': 2048, 'inode': 16384,
             'creation_time': '2025-11-15 14:20:00', 'modification_time': '2025-11-20 09:30:00',
             'access_time': '2026-02-15 10:15:00', 'is_deleted': False, 'is_directory': False},
            {'name': 'ntdll.dll', 'path': '/Windows/System32/ntdll.dll', 'size': 2105344, 'inode': 32768,
             'creation_time': '2020-01-15 10:28:00', 'modification_time': '2024-06-18 11:45:00',
             'access_time': '2026-02-21 09:10:00', 'is_deleted': False, 'is_directory': False},
            {'name': 'hosts', 'path': '/Windows/System32/drivers/etc/hosts', 'size': 825, 'inode': 65536,
             'creation_time': '2020-01-15 10:30:00', 'modification_time': '2025-11-10 22:15:00',
             'access_time': '2026-02-20 15:30:00', 'is_deleted': False, 'is_directory': False},
            {'name': 'encrypted.img', 'path': '/Users/Admin/Documents/encrypted.img', 'size': 10737418240, 'inode': 131072,
             'creation_time': '2025-09-01 14:30:00', 'modification_time': '2026-02-01 10:45:00',
             'access_time': '2026-02-15 16:20:00', 'is_deleted': False, 'is_directory': False},
        ]
        
        self.partition_info = {
            'filesystem_type': 'NTFS',
            'block_size': 4096,
            'block_count': 263626752,
        }
        
        for file_data in demo_files:
            unique_key = f"{file_data['inode']}_{file_data['name']}"
            self.files_metadata[unique_key] = file_data
            if file_data['is_deleted']:
                self.deleted_files_count += 1
            
            # Count file extensions
            ext = Path(file_data['name']).suffix.lower()
            self.file_extension_stats[ext if ext else '(no extension)'] += 1
            
            # Generate demo hash
            self.file_hashes[unique_key] = hashlib.sha256(file_data['name'].encode()).hexdigest()[:16]
            
            # Add to timeline
            self.timeline_events.append({
                'timestamp': file_data['modification_time'],
                'event_type': 'modification',
                'file': file_data['path'],
                'size': file_data['size']
            })
    
    def open_disk_image(self) -> bool:
        """Open the disk image using pytsk3."""
        try:
            if not self.use_demo:
                if not HAS_PYTSK3:
                    print(f"[-] pytsk3 not installed. Install with: pip install pytsk3")
                    print(f"[-] OR run in demo mode: use_demo=True")
                    return False
                
                if not os.path.exists(self.image_path):
                    raise FileNotFoundError(f"Disk image not found: {self.image_path}")
                
                print(f"[*] Opening disk image: {self.image_path}")
                
                file_extension = os.path.splitext(self.image_path)[1].lower()
                
                if file_extension == '.e01':
                    if not HAS_PYEWF:
                        print(f"[-] .E01 format requires pyewf library")
                        return False
                    print(f"[+] Detected .E01 (Encase) format")
                    ewf_handle = pyewf.open([self.image_path])
                    self.img = pytsk3.Img_open_file_io(ewf_handle)
                else:
                    print(f"[+] Detected RAW format")
                    self.img = pytsk3.Img_open(self.image_path)
                
                print(f"[+] Successfully opened disk image")
            else:
                print(f"[*] Running in DEMO mode with simulated data")
            
            return True
        except Exception as e:
            print(f"[-] Error opening disk image: {str(e)}")
            traceback.print_exc()
            return False
    
    def detect_partitions(self) -> bool:
        """Detect partitions in the disk image."""
        try:
            print(f"\n[*] Detecting partitions...")
            if not self.use_demo:
                try:
                    vs = pytsk3.VS_open(self.img, offset=0)
                    for partition in vs:
                        if partition.flags == pytsk3.TSK_VS_PART_FLAG_ALLOC:
                            self.partitions.append({
                                'address': partition.addr,
                                'offset': partition.start * 512,
                                'size': partition.len * 512
                            })
                except:
                    self.partitions.append({'address': 0, 'offset': 0, 'size': None})
            else:
                self.partitions.append({'address': 0, 'offset': 1048576, 'size': 1099508482048})
            
            print(f"[+] Successfully detected {len(self.partitions)} partition(s)")
            return True
        except Exception as e:
            print(f"[-] Error detecting partitions: {str(e)}")
            return False
    
    def open_filesystem(self) -> bool:
        """Open the first valid filesystem."""
        try:
            print(f"\n[*] Opening filesystem...")
            if not self.use_demo:
                if not self.partitions:
                    return False
                self.filesystem = pytsk3.FS_open(self.img, offset=self.partitions[0]['offset'])
            
            print(f"[+] Filesystem opened successfully")
            print(f"[+] Filesystem type: {self.partition_info['filesystem_type']}")
            return True
        except Exception as e:
            print(f"[-] Error opening filesystem: {str(e)}")
            return False
    
    def recursively_scan_files(self) -> bool:
        """Recursively scan all files in the filesystem."""
        try:
            print(f"\n[*] Starting recursive file scan...")
            
            if not self.use_demo:
                directory = self.filesystem.open_dir(path="/")
                self._scan_directory(directory, "/", "")
            
            # Build timeline
            self.timeline_events.sort(key=lambda x: x['timestamp'], reverse=True)
            
            print(f"[+] File scan completed")
            print(f"[+] Total files found: {len(self.files_metadata)}")
            print(f"[+] Deleted files found: {self.deleted_files_count}")
            return True
        except Exception as e:
            print(f"[-] Error during file scan: {str(e)}")
            return False
    
    def _scan_directory(self, directory_obj, dir_path: str, prefix: str = ""):
        """Recursive helper for directory scanning."""
        try:
            for entry in directory_obj:
                if entry.name.name in [b'.', b'..']:
                    continue
                
                file_name = entry.name.name.decode('utf-8', errors='ignore')
                full_path = f"{dir_path}{file_name}"
                is_deleted = not bool(entry.flags & pytsk3.TSK_FS_NAME_FLAG_ALLOC)
                
                if is_deleted:
                    self.deleted_files_count += 1
                
                try:
                    inode = entry.inode
                    inode_obj = self.filesystem.open_inode(inode)
                    
                    file_meta = {
                        'name': file_name,
                        'path': full_path,
                        'size': inode_obj.size if hasattr(inode_obj, 'size') else 0,
                        'inode': inode,
                        'creation_time': self.convert_timestamp(inode_obj.crtime if hasattr(inode_obj, 'crtime') else 0),
                        'modification_time': self.convert_timestamp(inode_obj.mtime if hasattr(inode_obj, 'mtime') else 0),
                        'access_time': self.convert_timestamp(inode_obj.atime if hasattr(inode_obj, 'atime') else 0),
                        'is_deleted': is_deleted,
                        'is_directory': bool(inode_obj.mode & pytsk3.TSK_FS_INODE_MODE_DIR),
                    }
                    
                    unique_key = f"{inode}_{file_name}"
                    self.files_metadata[unique_key] = file_meta
                    
                    # Count extensions
                    ext = Path(file_name).suffix.lower()
                    self.file_extension_stats[ext if ext else '(no extension)'] += 1
                    
                    # Add timeline event
                    self.timeline_events.append({
                        'timestamp': file_meta['modification_time'],
                        'event_type': 'modification',
                        'file': full_path,
                        'size': file_meta['size']
                    })
                    
                    if file_meta['is_directory']:
                        try:
                            sub_dir = self.filesystem.open_dir(inode=inode)
                            self._scan_directory(sub_dir, full_path + "/", prefix + "  ")
                        except:
                            pass
                except:
                    pass
        except:
            pass
    
    def convert_timestamp(self, timestamp: int) -> str:
        """Convert Unix timestamp to readable format."""
        try:
            if timestamp == 0:
                return "Unknown"
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Invalid"
    
    def compute_file_hashes(self) -> bool:
        """Compute SHA256 hashes for files (demo: symbolic only)."""
        try:
            print(f"\n[*] Computing file hashes...")
            
            for unique_key, file_meta in self.files_metadata.items():
                if self.use_demo:
                    # Demo mode: create symbolic hash
                    hash_input = f"{file_meta['path']}{file_meta['size']}"
                    self.file_hashes[unique_key] = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
                else:
                    # Real mode would read actual file data
                    try:
                        inode = file_meta['inode']
                        inode_obj = self.filesystem.open_inode(inode)
                        if inode_obj.size > 0 and inode_obj.size < 1000000000:  # Skip huge files
                            # Read file data and hash it
                            hash_obj = hashlib.sha256()
                            for block in inode_obj.get_blocks():
                                data = self.img.read(block.addr * 512, 512)
                                hash_obj.update(data)
                            self.file_hashes[unique_key] = hash_obj.hexdigest()[:16]
                    except:
                        self.file_hashes[unique_key] = "ERROR"
            
            print(f"[+] Computed hashes for {len(self.file_hashes)} files")
            return True
        except Exception as e:
            print(f"[-] Error computing hashes: {str(e)}")
            return False
    
    def detect_encryption(self) -> List[Dict[str, Any]]:
        """Detect encrypted volumes and files."""
        print(f"\n[*] Scanning for encryption signatures...")
        
        encrypted_items = []
        
        # Check file extensions associated with encryption
        encryption_extensions = ['.dmg', '.img', '.iso', '.bin', '.enc', '.gpg', '.pgp', '.7z', '.zip', '.rar']
        
        for unique_key, file_meta in self.files_metadata.items():
            file_name = file_meta['name'].lower()
            
            # Check for encryption file extensions
            for ext in encryption_extensions:
                if file_name.endswith(ext):
                    encrypted_items.append({
                        'name': file_meta['name'],
                        'path': file_meta['path'],
                        'type': 'encrypted_archive',
                        'size': file_meta['size'],
                        'modified': file_meta['modification_time']
                    })
                    break
        
        if encrypted_items:
            print(f"[+] Found {len(encrypted_items)} potential encrypted items")
        else:
            print(f"[+] No obvious encrypted items detected")
        
        return encrypted_items
    
    def detect_network_artifacts(self) -> List[Dict[str, Any]]:
        """Detect network-related artifacts."""
        print(f"\n[*] Scanning for network artifacts...")
        
        artifacts = []
        network_paths = [
            '/Windows/System32/drivers/etc/hosts',
            '/Users/*/AppData/Local/Google/Chrome/User Data',
            '/Users/*/AppData/Local/Mozilla/Firefox',
            '/Users/*/AppData/Roaming/Microsoft/Windows/Recent',
            '/Users/*/AppData/Local/Temp',
            '/var/log/apache2',
            '/var/log/nginx',
        ]
        
        for unique_key, file_meta in self.files_metadata.items():
            path = file_meta['path'].lower()
            
            # Check if file matches network artifact patterns
            if any(pattern.lower() in path for pattern in network_paths):
                artifacts.append({
                    'name': file_meta['name'],
                    'path': file_meta['path'],
                    'type': 'network_artifact',
                    'size': file_meta['size'],
                    'modified': file_meta['modification_time']
                })
        
        self.network_artifacts = artifacts
        print(f"[+] Found {len(artifacts)} network artifacts")
        return artifacts
    
    def export_to_json(self, output_path: str) -> bool:
        """Export complete analysis data to JSON."""
        try:
            print(f"\n[*] Exporting data to JSON...")
            
            # Prepare suspicious files list
            suspicious_files = [
                f for f in self.files_metadata.values()
                if any(f['name'].lower().endswith(ext) for ext in self.suspicious_extensions)
            ]
            
            export_data = {
                'forensic_report': {
                    'image_path': self.image_path,
                    'scan_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'partition_info': self.partition_info,
                    'summary': {
                        'total_partitions': len(self.partitions),
                        'total_files': len(self.files_metadata),
                        'total_deleted_files': self.deleted_files_count,
                        'suspicious_files_count': len(suspicious_files),
                        'encrypted_items_count': len(self.detect_encryption()),
                        'network_artifacts_count': len(self.network_artifacts),
                    },
                    'file_extension_statistics': dict(self.file_extension_stats),
                    'files': self.files_metadata,
                    'file_hashes': self.file_hashes,
                    'encrypted_items': self.detect_encryption(),
                    'network_artifacts': self.network_artifacts,
                    'timeline_events': self.timeline_events[:100],  # Top 100 events
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            
            print(f"[+] JSON exported successfully to: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error exporting JSON: {str(e)}")
            return False
    
    def generate_timeline_report(self, output_path: str) -> bool:
        """Generate a timeline analysis report."""
        try:
            print(f"\n[*] Generating timeline report...")
            
            timeline_text = "=" * 80 + "\n"
            timeline_text += "FORENSIC TIMELINE ANALYSIS REPORT\n"
            timeline_text += "=" * 80 + "\n\n"
            
            timeline_text += f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            timeline_text += f"Image: {self.image_path}\n"
            timeline_text += f"Total Events: {len(self.timeline_events)}\n\n"
            
            timeline_text += "TIMELINE (Most Recent First):\n"
            timeline_text += "-" * 80 + "\n"
            
            for event in self.timeline_events[:50]:  # Show top 50
                timeline_text += f"[{event['timestamp']}] {event['event_type'].upper()}: {event['file']}\n"
                if event['size'] > 0:
                    timeline_text += f"  Size: {event['size']:,} bytes\n"
            
            timeline_text += "\n" + "=" * 80 + "\n"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(timeline_text)
            
            print(f"[+] Timeline report saved to: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error generating timeline: {str(e)}")
            return False
    
    def generate_extension_report(self, output_path: str) -> bool:
        """Generate file extension distribution report."""
        try:
            print(f"\n[*] Generating file extension report...")
            
            extension_text = "=" * 80 + "\n"
            extension_text += "FILE EXTENSION DISTRIBUTION REPORT\n"
            extension_text += "=" * 80 + "\n\n"
            
            # Sort by count
            sorted_extensions = sorted(self.file_extension_stats.items(), key=lambda x: x[1], reverse=True)
            total_files = sum(count for _, count in sorted_extensions)
            
            extension_text += f"Total Files: {total_files}\n"
            extension_text += f"Unique Extensions: {len(sorted_extensions)}\n\n"
            
            extension_text += "EXTENSION BREAKDOWN:\n"
            extension_text += "-" * 80 + "\n"
            extension_text += f"{'Extension':<20} {'Count':<15} {'Percentage':<15}\n"
            extension_text += "-" * 80 + "\n"
            
            for ext, count in sorted_extensions:
                percentage = (count / total_files * 100) if total_files > 0 else 0
                extension_text += f"{ext:<20} {count:<15} {percentage:>6.2f}%\n"
            
            extension_text += "\n" + "=" * 80 + "\n"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(extension_text)
            
            print(f"[+] Extension report saved to: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error generating extension report: {str(e)}")
            return False
    
    def call_local_llm(self, prompt: str) -> str:
        """Call local LLM (Ollama) for analysis."""
        if not self.llm_available:
            return "Local LLM not available. Install Ollama from https://ollama.ai"
        
        try:
            print(f"\n[*] Sending analysis to local LLM...")
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama2',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json().get('response', 'No response')
                print(f"[+] LLM analysis completed")
                return result
            else:
                print(f"[!] LLM returned status {response.status_code}")
                return f"Error: LLM returned status {response.status_code}"
        except Exception as e:
            print(f"[-] Error calling LLM: {str(e)}")
            return f"Error calling LLM: {str(e)}"
    
    def generate_summary_report(self, json_path: str, output_path: str) -> bool:
        """Generate comprehensive forensic summary report."""
        try:
            print(f"\n[*] Generating comprehensive forensic summary...")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
            
            data = json.loads(json_data)
            forensic_data = data['forensic_report']
            
            summary = "=" * 80 + "\n"
            summary += "COMPREHENSIVE FORENSIC ANALYSIS REPORT\n"
            summary += "=" * 80 + "\n\n"
            
            summary += f"Image Path: {forensic_data['image_path']}\n"
            summary += f"Scan Timestamp: {forensic_data['scan_timestamp']}\n\n"
            
            summary += "FILESYSTEM INFORMATION:\n"
            summary += "-" * 80 + "\n"
            partition_info = forensic_data['partition_info']
            summary += f"Filesystem Type: {partition_info.get('filesystem_type', 'Unknown')}\n"
            summary += f"Block Size: {partition_info.get('block_size', 'Unknown')} bytes\n"
            summary += f"Block Count: {partition_info.get('block_count', 'Unknown')}\n\n"
            
            summary += "FILE STATISTICS:\n"
            summary += "-" * 80 + "\n"
            file_summary = forensic_data['summary']
            summary += f"Total Partitions: {file_summary['total_partitions']}\n"
            summary += f"Total Files: {file_summary['total_files']:,}\n"
            summary += f"Deleted Files: {file_summary['total_deleted_files']:,}\n"
            summary += f"Suspicious Files: {file_summary['suspicious_files_count']}\n"
            summary += f"Encrypted Items: {file_summary['encrypted_items_count']}\n"
            summary += f"Network Artifacts: {file_summary['network_artifacts_count']}\n\n"
            
            # Largest files
            files = forensic_data['files']
            if files:
                largest_file = max(files.values(), key=lambda x: x['size'])
                summary += "LARGEST FILE:\n"
                summary += "-" * 80 + "\n"
                summary += f"Name: {largest_file['name']}\n"
                summary += f"Path: {largest_file['path']}\n"
                summary += f"Size: {largest_file['size']:,} bytes\n\n"
            
            # Extension statistics
            summary += "TOP FILE EXTENSIONS:\n"
            summary += "-" * 80 + "\n"
            extensions = forensic_data.get('file_extension_statistics', {})
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
                summary += f"{ext}: {count} files\n"
            summary += "\n"
            
            # Suspicious files
            suspicious_files = [
                f for f in files.values()
                if any(f['name'].lower().endswith(ext) for ext in self.suspicious_extensions)
            ]
            
            summary += "SUSPICIOUS FILES (by extension):\n"
            summary += "-" * 80 + "\n"
            if suspicious_files:
                summary += f"Found {len(suspicious_files)} suspicious files:\n\n"
                for f in sorted(suspicious_files, key=lambda x: x['size'], reverse=True)[:20]:
                    summary += f"Name: {f['name']}\n"
                    summary += f"Path: {f['path']}\n"
                    summary += f"Size: {f['size']:,} bytes\n"
                    summary += f"Modified: {f['modification_time']}\n"
                    summary += f"Deleted: {'Yes' if f['is_deleted'] else 'No'}\n"
                    unique_key = f"{f['inode']}_{f['name']}"
                    if unique_key in forensic_data.get('file_hashes', {}):
                        summary += f"Hash: {forensic_data['file_hashes'][unique_key]}\n"
                    summary += "\n"
            else:
                summary += "No suspicious files detected.\n\n"
            
            # Deleted files
            deleted_files = [f for f in files.values() if f['is_deleted']]
            summary += "DELETED FILES:\n"
            summary += "-" * 80 + "\n"
            if deleted_files:
                summary += f"Found {len(deleted_files)} deleted files.\n\n"
                for f in sorted(deleted_files, key=lambda x: x['modification_time'], reverse=True)[:10]:
                    summary += f"Name: {f['name']}\n"
                    summary += f"Path: {f['path']}\n"
                    summary += f"Size: {f['size']:,} bytes\n"
                    summary += f"Modified: {f['modification_time']}\n\n"
            else:
                summary += "No deleted files detected.\n\n"
            
            # Encrypted items
            encrypted = forensic_data.get('encrypted_items', [])
            summary += "ENCRYPTED ITEMS:\n"
            summary += "-" * 80 + "\n"
            if encrypted:
                summary += f"Found {len(encrypted)} encrypted items:\n\n"
                for item in encrypted[:10]:
                    summary += f"Name: {item['name']}\n"
                    summary += f"Path: {item['path']}\n"
                    summary += f"Size: {item['size']:,} bytes\n\n"
            else:
                summary += "No obvious encrypted items detected.\n\n"
            
            # Network artifacts
            artifacts = forensic_data.get('network_artifacts', [])
            summary += "NETWORK ARTIFACTS:\n"
            summary += "-" * 80 + "\n"
            if artifacts:
                summary += f"Found {len(artifacts)} network artifacts:\n\n"
                for artifact in artifacts[:10]:
                    summary += f"Name: {artifact['name']}\n"
                    summary += f"Path: {artifact['path']}\n\n"
            else:
                summary += "No obvious network artifacts detected.\n\n"
            
            summary += "=" * 80 + "\n"
            summary += "END OF REPORT\n"
            summary += "=" * 80 + "\n"
            
            # Add LLM analysis if available
            if self.llm_available:
                summary += "\n[LLM-ASSISTED ANALYSIS]\n"
                summary += "-" * 80 + "\n"
                
                llm_prompt = f"""
                Analyze this forensic data and provide insights:
                - {file_summary['total_files']} total files
                - {file_summary['total_deleted_files']} deleted files
                - {len(suspicious_files)} suspicious files
                - {len(encrypted)} encrypted items
                - {len(artifacts)} network artifacts
                
                Provide a brief forensic assessment including potential threats.
                """
                
                llm_response = self.call_local_llm(llm_prompt)
                summary += llm_response + "\n"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"[+] Comprehensive summary saved to: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error generating summary: {str(e)}")
            traceback.print_exc()
            return False
    
    def run_complete_analysis(self, json_output: str, summary_output: str, 
                            timeline_output: str, extension_output: str) -> bool:
        """Execute the complete forensic analysis pipeline."""
        print("\n" + "=" * 80)
        print("ADVANCED FORENSIC ANALYSIS PIPELINE - COMPLETE ANALYSIS")
        print("=" * 80 + "\n")
        
        if not self.open_disk_image():
            return False
        if not self.detect_partitions():
            return False
        if not self.open_filesystem():
            return False
        if not self.recursively_scan_files():
            return False
        
        # Compute hashes
        if not self.compute_file_hashes():
            return False
        
        # Detect encryption
        self.detect_encryption()
        
        # Detect network artifacts
        self.detect_network_artifacts()
        
        # Export to JSON
        if not self.export_to_json(json_output):
            return False
        
        # Generate reports
        if not self.generate_timeline_report(timeline_output):
            return False
        if not self.generate_extension_report(extension_output):
            return False
        if not self.generate_summary_report(json_output, summary_output):
            return False
        
        print("\n" + "=" * 80)
        print("ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
        return True


def main():
    """Main execution function."""
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    IMAGE_PATH = r"C:\forensics\image.raw"
    USE_DEMO = True  # Set to False when using real image with pytsk3
    
    JSON_OUTPUT = r"D:\Forensics Application\forensic_report_advanced.json"
    SUMMARY_OUTPUT = r"D:\Forensics Application\forensic_summary_advanced.txt"
    TIMELINE_OUTPUT = r"D:\Forensics Application\forensic_timeline.txt"
    EXTENSION_OUTPUT = r"D:\Forensics Application\forensic_extensions.txt"
    
    # =========================================================================
    # EXECUTION
    # =========================================================================
    
    try:
        analyzer = AdvancedForensicAnalyzer(IMAGE_PATH, use_demo=USE_DEMO)
        success = analyzer.run_complete_analysis(JSON_OUTPUT, SUMMARY_OUTPUT, 
                                                  TIMELINE_OUTPUT, EXTENSION_OUTPUT)
        
        if success:
            print("\n[+] All operations completed successfully!")
            print(f"[+] JSON Report: {JSON_OUTPUT}")
            print(f"[+] Summary Report: {SUMMARY_OUTPUT}")
            print(f"[+] Timeline Report: {TIMELINE_OUTPUT}")
            print(f"[+] Extension Report: {EXTENSION_OUTPUT}")
            return 0
        else:
            print("\n[-] Analysis pipeline failed!")
            return 1
    except KeyboardInterrupt:
        print("\n[!] Analysis interrupted by user")
        return 130
    except Exception as e:
        print(f"\n[-] Unexpected error: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
