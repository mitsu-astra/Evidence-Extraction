import pytsk3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# Try to import pyewf for .E01 support (optional)
try:
    import pyewf
    HAS_PYEWF = True
except ImportError:
    HAS_PYEWF = False

# ============================================================================
# FORENSIC ANALYSIS PIPELINE - PYTSK3 IMPLEMENTATION
# ============================================================================
# This script analyzes a RAW disk image and extracts file metadata
# for forensic reporting and suspicious file detection.
# ============================================================================

class ForensicAnalyzer:
    """Main class for forensic disk analysis using pytsk3."""
    
    def __init__(self, image_path: str):
        """
        Initialize the forensic analyzer with a disk image path.
        
        Args:
            image_path: Absolute path to the RAW disk image file
        """
        self.image_path = image_path
        self.img = None
        self.partitions = []
        self.filesystem = None
        self.files_metadata = {}
        self.deleted_files_count = 0
        self.partition_info = {}
        
    def open_disk_image(self) -> bool:
        """
        Open the disk image using pytsk3.
        Supports both RAW and .E01 (Encase) formats.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.image_path):
                raise FileNotFoundError(f"Disk image not found: {self.image_path}")
            
            print(f"[*] Opening disk image: {self.image_path}")
            
            # Detect image format by extension
            file_extension = os.path.splitext(self.image_path)[1].lower()
            
            if file_extension == '.e01':
                # Handle .E01 (Encase) format
                if not HAS_PYEWF:
                    print(f"[-] .E01 format requires pyewf library")
                    print(f"[!] Install with: pip install pyewf")
                    return False
                
                print(f"[+] Detected .E01 (Encase) format")
                print(f"[*] Opening with pyewf...")
                
                try:
                    # Open the .E01 image with pyewf (accepts list of files for segmented images)
                    ewf_handle = pyewf.open([self.image_path])
                    
                    # Create a pytsk3-compatible image object from the EWF handle
                    self.img = pytsk3.Img_open_file_io(ewf_handle)
                    print(f"[+] Successfully opened .E01 image with pyewf")
                    
                except Exception as ewf_error:
                    print(f"[-] Error opening .E01 with pyewf: {str(ewf_error)}")
                    raise
                
            else:
                # Handle RAW format (default)
                print(f"[+] Detected RAW format")
                self.img = pytsk3.Img_open(self.image_path)
                print(f"[+] Successfully opened RAW disk image")
            
            return True
            
        except Exception as e:
            print(f"[-] Error opening disk image: {str(e)}")
            traceback.print_exc()
            return False
    
    def detect_partitions(self) -> bool:
        """
        Detect and list all partitions in the disk image.
        
        Returns:
            bool: True if partitions detected, False otherwise
        """
        try:
            print(f"\n[*] Detecting partitions...")
            
            try:
                vs = pytsk3.VS_open(self.img, offset=0)
                print(f"[+] Volume system detected")
            except Exception as e:
                print(f"[!] Could not detect volume system, trying generic approach: {str(e)}")
                vs = None
            
            if vs:
                partition_count = 0
                for partition in vs:
                    if partition.flags == pytsk3.TSK_VS_PART_FLAG_ALLOC:
                        self.partitions.append({
                            'address': partition.addr,
                            'offset': partition.start * 512,
                            'size': partition.len * 512
                        })
                        partition_count += 1
                        print(f"[+] Partition {partition_count}: Address={partition.addr}, "
                              f"Offset={partition.start * 512}, Size={partition.len * 512}")
                
                if partition_count == 0:
                    print(f"[!] No allocated partitions found, attempting to use entire image")
                    self.partitions.append({
                        'address': 0,
                        'offset': 0,
                        'size': None
                    })
                    return True
                return partition_count > 0
            else:
                print(f"[!] No partition system detected, using entire image as partition")
                self.partitions.append({
                    'address': 0,
                    'offset': 0,
                    'size': None
                })
                return True
                
        except Exception as e:
            print(f"[-] Error detecting partitions: {str(e)}")
            traceback.print_exc()
            return False
    
    def open_filesystem(self) -> bool:
        """
        Open the first valid filesystem from the detected partitions.
        
        Returns:
            bool: True if filesystem opened successfully, False otherwise
        """
        try:
            print(f"\n[*] Opening filesystem from first partition...")
            
            if not self.partitions:
                raise ValueError("No partitions detected")
            
            partition = self.partitions[0]
            offset = partition['offset']
            
            try:
                self.filesystem = pytsk3.FS_open(self.img, offset=offset)
                fs_info = self.filesystem.info
                
                self.partition_info = {
                    'filesystem_type': fs_info.fs_type if hasattr(fs_info, 'fs_type') else 'Unknown',
                    'block_size': fs_info.block_size if hasattr(fs_info, 'block_size') else 0,
                    'block_count': fs_info.block_count if hasattr(fs_info, 'block_count') else 0,
                }
                
                print(f"[+] Filesystem opened successfully")
                print(f"[+] Filesystem type: {self.partition_info['filesystem_type']}")
                print(f"[+] Block size: {self.partition_info['block_size']}")
                print(f"[+] Block count: {self.partition_info['block_count']}")
                return True
                
            except Exception as e:
                print(f"[-] Error opening filesystem: {str(e)}")
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"[-] Error in filesystem opening: {str(e)}")
            traceback.print_exc()
            return False
    
    def convert_timestamp(self, timestamp: int) -> str:
        """
        Convert Unix timestamp to human-readable format.
        
        Args:
            timestamp: Unix timestamp (seconds since epoch)
            
        Returns:
            str: Formatted datetime string
        """
        try:
            if timestamp == 0:
                return "Unknown"
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "Invalid"
    
    def recursively_scan_files(self, directory=None) -> bool:
        """
        Recursively scan all files in the filesystem and collect metadata.
        
        Args:
            directory: Starting directory (None for root)
            
        Returns:
            bool: True if scan completed
        """
        try:
            print(f"\n[*] Starting recursive file scan...")
            
            if directory is None:
                directory = self.filesystem.open_dir(path="/")
            
            self._scan_directory(directory, "/", "")
            print(f"[+] File scan completed")
            print(f"[+] Total files found: {len(self.files_metadata)}")
            print(f"[+] Deleted files found: {self.deleted_files_count}")
            return True
            
        except Exception as e:
            print(f"[-] Error during file scan: {str(e)}")
            traceback.print_exc()
            return False
    
    def _scan_directory(self, directory_obj, dir_path: str, prefix: str = ""):
        """
        Recursive helper function to scan directory contents.
        
        Args:
            directory_obj: pytsk3 directory object
            dir_path: Current directory path
            prefix: String prefix for output formatting
        """
        try:
            for entry in directory_obj:
                # Skip special entries
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
                    
                    # Collect file metadata
                    file_meta = {
                        'name': file_name,
                        'path': full_path,
                        'size': inode_obj.size if hasattr(inode_obj, 'size') else 0,
                        'inode': inode,
                        'creation_time': self.convert_timestamp(inode_obj.crtime if hasattr(inode_obj, 'crtime') else 0),
                        'modification_time': self.convert_timestamp(inode_obj.mtime if hasattr(inode_obj, 'mtime') else 0),
                        'access_time': self.convert_timestamp(inode_obj.atime if hasattr(inode_obj, 'atime') else 0),
                        'is_deleted': is_deleted,
                        'is_directory': bool(inode_obj.flags & pytsk3.TSK_FS_INODE_FLAG_ALLOC) and bool(inode_obj.mode & pytsk3.TSK_FS_INODE_MODE_DIR),
                    }
                    
                    # Store metadata with unique key
                    unique_key = f"{inode}_{file_name}"
                    self.files_metadata[unique_key] = file_meta
                    
                    # Recursively scan subdirectories
                    if file_meta['is_directory']:
                        try:
                            sub_dir = self.filesystem.open_dir(inode=inode)
                            self._scan_directory(sub_dir, full_path + "/", prefix + "  ")
                        except Exception as e:
                            print(f"[!] Could not open directory {full_path}: {str(e)}")
                
                except Exception as e:
                    print(f"[!] Error processing file {full_path}: {str(e)}")
                    
        except Exception as e:
            print(f"[-] Error scanning directory: {str(e)}")
    
    def export_to_json(self, output_path: str) -> bool:
        """
        Export collected file metadata to JSON format.
        
        Args:
            output_path: Path where JSON file should be saved
            
        Returns:
            bool: True if successful
        """
        try:
            print(f"\n[*] Exporting data to JSON...")
            
            export_data = {
                'forensic_report': {
                    'image_path': self.image_path,
                    'scan_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'partition_info': self.partition_info,
                    'summary': {
                        'total_partitions': len(self.partitions),
                        'total_files': len(self.files_metadata),
                        'total_deleted_files': self.deleted_files_count,
                    },
                    'files': self.files_metadata
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            
            print(f"[+] JSON exported successfully to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[-] Error exporting JSON: {str(e)}")
            traceback.print_exc()
            return False
    
    def _call_ollama(self, prompt: str, model: str = "llama3", timeout: int = 180) -> str:
        """
        Call a local Ollama instance to generate text.
        Returns the generated text, or empty string on failure.
        """
        import requests
        try:
            print(f"[*] Querying Ollama ({model}) …")
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout,
            )
            if resp.status_code == 200:
                text = resp.json().get("response", "").strip()
                if text:
                    print(f"[+] Ollama returned {len(text)} chars.")
                    return text
                print("[!] Ollama returned empty response — using rule-based fallback.")
            else:
                print(f"[!] Ollama returned status {resp.status_code} — using rule-based fallback.")
        except requests.ConnectionError:
            print("[!] Ollama not reachable at localhost:11434 — using rule-based fallback.")
        except Exception as exc:
            print(f"[!] Ollama error: {exc} — using rule-based fallback.")
        return ""

    def _build_data_facts(self, forensic_data: dict) -> str:
        """Build a concise, fact-only summary string for LLM prompts."""
        partition_info = forensic_data.get('partition_info', {})
        file_summary = forensic_data.get('summary', {})
        files = forensic_data.get('files', {})
        extensions = forensic_data.get('file_extension_statistics', {})
        encrypted = forensic_data.get('encrypted_items', [])
        network = forensic_data.get('network_artifacts', [])

        suspicious_extensions = ['.exe', '.bat', '.ps1', '.dll', '.scr', '.vbs', '.js']
        suspicious_files = [
            f for f in files.values()
            if any(f['name'].lower().endswith(ext) for ext in suspicious_extensions)
        ]
        deleted_files = [f for f in files.values() if f.get('is_deleted')]

        lines = [
            f"Image path: {forensic_data.get('image_path', 'N/A')}",
            f"Scan timestamp: {forensic_data.get('scan_timestamp', 'N/A')}",
            f"Filesystem type: {partition_info.get('filesystem_type', 'Unknown')}",
            f"Block size: {partition_info.get('block_size', 'Unknown')} bytes",
            f"Block count: {partition_info.get('block_count', 'Unknown')}",
            f"Total partitions: {file_summary.get('total_partitions', 0)}",
            f"Total files: {file_summary.get('total_files', 0)}",
            f"Deleted files: {file_summary.get('total_deleted_files', 0)}",
            f"Suspicious files (by extension): {len(suspicious_files)}",
            f"Encrypted items: {file_summary.get('encrypted_items_count', len(encrypted))}",
            f"Network artifacts: {file_summary.get('network_artifacts_count', len(network))}",
        ]

        # Top extensions
        top_ext = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_ext:
            lines.append("Top file extensions: " + ", ".join(f"{e} ({c})" for e, c in top_ext))

        # Suspicious file names
        if suspicious_files:
            lines.append("Suspicious file names: " + ", ".join(f['name'] for f in suspicious_files[:15]))

        # Deleted file names
        if deleted_files:
            lines.append("Deleted file names (top 10): " + ", ".join(
                f['name'] for f in sorted(deleted_files, key=lambda x: x['modification_time'], reverse=True)[:10]
            ))

        # Encrypted item names
        if encrypted:
            lines.append("Encrypted item names: " + ", ".join(i['name'] for i in encrypted[:10]))

        # Network artifact names
        if network:
            lines.append("Network artifact names: " + ", ".join(i['name'] for i in network[:10]))

        return "\n".join(lines)

    def generate_summary_from_model(self, json_data: str) -> str:
        """
        Generate a human-readable forensic summary from JSON data.
        Tries Ollama/Llama 3 first; falls back to a structured rule-based summary.

        Args:
            json_data: JSON data as string

        Returns:
            str: Summary text
        """
        try:
            data = json.loads(json_data)
            forensic_data = data['forensic_report']
        except Exception as e:
            return f"Error parsing JSON data: {str(e)}"

        # ── Try LLM-generated summary via Ollama ─────────────────────────
        data_facts = self._build_data_facts(forensic_data)
        llm_prompt = (
            "You are a digital forensics report writer.\n\n"
            "STRICT RULES:\n"
            "- ONLY use the facts provided below. Do NOT assume, speculate, or invent any information.\n"
            "- If a metric is zero, say so. Do NOT fabricate threats or risks that are not in the data.\n"
            "- Do NOT use markdown formatting. Use plain text with section headers.\n"
            "- Write in formal, professional forensic report language.\n\n"
            "Write a structured forensic analysis summary with these sections:\n"
            "1. EVIDENCE OVERVIEW — what disk image was analyzed, filesystem type, scan timestamp\n"
            "2. FILE STATISTICS — total files, deleted files, file type distribution\n"
            "3. SUSPICIOUS FILES — list each suspicious file by name, path, size, and modification date. "
            "If none were found, state that clearly.\n"
            "4. DELETED FILES — list recovered deleted files. If none, state that clearly.\n"
            "5. ENCRYPTED ITEMS — list encrypted items found. If none, state that clearly.\n"
            "6. NETWORK ARTIFACTS — list network-related artifacts. If none, state that clearly.\n"
            "7. FINDINGS SUMMARY — brief factual recap. Do NOT speculate on intent or threat level "
            "unless the data explicitly supports it.\n\n"
            f"=== DATA (facts only) ===\n{data_facts}\n=== END DATA ==="
        )

        llm_summary = self._call_ollama(llm_prompt)
        if llm_summary:
            # Wrap LLM output in a header/footer
            result = "=" * 70 + "\n"
            result += "FORENSIC ANALYSIS REPORT  (Generated by Llama 3)\n"
            result += "=" * 70 + "\n\n"
            result += llm_summary + "\n\n"
            result += "=" * 70 + "\n"
            result += "END OF REPORT\n"
            result += "=" * 70 + "\n"
            return result

        # ── Fallback: rule-based structured summary ──────────────────────
        print("[*] Generating rule-based summary …")
        partition_info = forensic_data.get('partition_info', {})
        file_summary = forensic_data.get('summary', {})
        files = forensic_data.get('files', {})

        summary = "=" * 70 + "\n"
        summary += "FORENSIC ANALYSIS REPORT\n"
        summary += "=" * 70 + "\n\n"

        summary += f"Image Path: {forensic_data.get('image_path', 'N/A')}\n"
        summary += f"Scan Timestamp: {forensic_data.get('scan_timestamp', 'N/A')}\n\n"

        summary += "FILESYSTEM INFORMATION:\n"
        summary += "-" * 70 + "\n"
        summary += f"Filesystem Type: {partition_info.get('filesystem_type', 'Unknown')}\n"
        summary += f"Block Size: {partition_info.get('block_size', 'Unknown')} bytes\n"
        summary += f"Block Count: {partition_info.get('block_count', 'Unknown')}\n\n"

        summary += "FILE STATISTICS:\n"
        summary += "-" * 70 + "\n"
        summary += f"Total Partitions: {file_summary.get('total_partitions', 0)}\n"
        summary += f"Total Files: {file_summary.get('total_files', 0)}\n"
        summary += f"Deleted Files: {file_summary.get('total_deleted_files', 0)}\n\n"

        # Largest file
        if files:
            largest_file = max(files.values(), key=lambda x: x['size'])
            summary += "LARGEST FILE:\n"
            summary += "-" * 70 + "\n"
            summary += f"Name: {largest_file['name']}\n"
            summary += f"Path: {largest_file['path']}\n"
            summary += f"Size: {largest_file['size']:,} bytes\n\n"

        # Suspicious files
        suspicious_extensions = ['.exe', '.bat', '.ps1', '.dll', '.scr', '.vbs', '.js']
        suspicious_files = [
            f for f in files.values()
            if any(f['name'].lower().endswith(ext) for ext in suspicious_extensions)
        ]

        summary += "SUSPICIOUS FILES (by extension):\n"
        summary += "-" * 70 + "\n"
        if suspicious_files:
            summary += f"Found {len(suspicious_files)} suspicious files:\n\n"
            for f in sorted(suspicious_files, key=lambda x: x['size'], reverse=True)[:20]:
                summary += f"  Name: {f['name']}\n"
                summary += f"  Path: {f['path']}\n"
                summary += f"  Size: {f['size']:,} bytes\n"
                summary += f"  Modified: {f['modification_time']}\n"
                summary += f"  Deleted: {'Yes' if f['is_deleted'] else 'No'}\n\n"
        else:
            summary += "No suspicious files detected.\n\n"

        # Deleted files
        deleted_files = [f for f in files.values() if f['is_deleted']]
        summary += "DELETED FILES:\n"
        summary += "-" * 70 + "\n"
        if deleted_files:
            summary += f"Found {len(deleted_files)} deleted files.\n"
            summary += "Top 10 by modification date:\n\n"
            for f in sorted(deleted_files, key=lambda x: x['modification_time'], reverse=True)[:10]:
                summary += f"  Name: {f['name']}\n"
                summary += f"  Path: {f['path']}\n"
                summary += f"  Size: {f['size']:,} bytes\n"
                summary += f"  Modified: {f['modification_time']}\n\n"
        else:
            summary += "No deleted files detected.\n\n"

        summary += "=" * 70 + "\n"
        summary += "END OF REPORT\n"
        summary += "=" * 70 + "\n"

        return summary
    
    def save_summary(self, summary_text: str, output_path: str) -> bool:
        """
        Save the generated summary to a text file.
        
        Args:
            summary_text: Summary text to save
            output_path: Path where summary should be saved
            
        Returns:
            bool: True if successful
        """
        try:
            print(f"\n[*] Saving forensic summary...")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            
            print(f"[+] Summary saved successfully to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[-] Error saving summary: {str(e)}")
            traceback.print_exc()
            return False
    
    def run_analysis_pipeline(self, json_output: str, summary_output: str) -> bool:
        """
        Execute the complete forensic analysis pipeline.
        
        Args:
            json_output: Path for JSON output file
            summary_output: Path for summary output file
            
        Returns:
            bool: True if pipeline completed successfully
        """
        print("\n" + "=" * 70)
        print("FORENSIC ANALYSIS PIPELINE - PYTSK3")
        print("=" * 70 + "\n")
        
        # Step 1: Open disk image (PART 1)
        if not self.open_disk_image():
            return False
        
        # Step 2: Detect partitions (PART 1)
        if not self.detect_partitions():
            return False
        
        # Step 3: Open filesystem (PART 1)
        if not self.open_filesystem():
            return False
        
        # Step 4: Recursively scan files (PART 1)
        if not self.recursively_scan_files():
            return False
        
        # Step 5: Export to JSON (PART 2)
        if not self.export_to_json(json_output):
            return False
        
        # Step 6: Generate summary using model (PART 3)
        with open(json_output, 'r', encoding='utf-8') as f:
            json_data = f.read()
        
        summary = self.generate_summary_from_model(json_data)
        
        # Step 7: Save summary (PART 3)
        if not self.save_summary(summary, summary_output):
            return False
        
        print("\n" + "=" * 70)
        print("ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")
        
        return True


def main():
    """Main execution function."""
    
    # =========================================================================
    # CONFIGURATION - UPDATE THESE PATHS
    # =========================================================================
    # Absolute Windows path to disk image (supports RAW and .E01 formats)
    # Examples:
    #   RAW format: r"C:\forensics\image.raw"
    #   .E01 format (requires pyewf): r"C:\forensics\image.E01"
    IMAGE_PATH = r"C:\forensics\image.raw"
    
    # Absolute Windows path for JSON output report
    JSON_OUTPUT = r"D:\Forensics Application\forensic_report.json"
    
    # Absolute Windows path for text summary report
    SUMMARY_OUTPUT = r"D:\Forensics Application\forensic_summary.txt"
    
    # =========================================================================
    # EXECUTION
    # =========================================================================
    
    try:
        analyzer = ForensicAnalyzer(IMAGE_PATH)
        success = analyzer.run_analysis_pipeline(JSON_OUTPUT, SUMMARY_OUTPUT)
        
        if success:
            print("\n[+] All operations completed successfully!")
            print(f"[+] JSON Report: {JSON_OUTPUT}")
            print(f"[+] Summary Report: {SUMMARY_OUTPUT}")
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
