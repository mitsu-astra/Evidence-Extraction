import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# ============================================================================
# FORENSIC ANALYSIS PIPELINE - DEMO VERSION (No pytsk3 required)
# ============================================================================
# This is a demonstration version that shows the complete pipeline output
# without requiring pytsk3 library. It uses simulated forensic data.
# The actual version with pytsk3 would scan a real disk image.
# ============================================================================

class ForensicAnalyzerDemo:
    """Demo version of forensic disk analyzer for demonstration purposes."""
    
    def __init__(self, image_path: str):
        """Initialize the forensic analyzer with demo data."""
        self.image_path = image_path
        self.files_metadata = {}
        self.deleted_files_count = 0
        self.partition_info = {
            'filesystem_type': 'NTFS',
            'block_size': 4096,
            'block_count': 263626752,
        }
        self.generate_demo_data()
    
    def generate_demo_data(self):
        """Generate realistic forensic data for demonstration."""
        
        demo_files = [
            {
                'name': 'system.ini',
                'path': '/Windows/system.ini',
                'size': 2048,
                'inode': 5,
                'creation_time': '2020-01-15 10:30:00',
                'modification_time': '2022-06-20 14:15:00',
                'access_time': '2023-11-30 09:45:00',
                'is_deleted': False,
                'is_directory': False,
            },
            {
                'name': 'explorer.exe',
                'path': '/Windows/explorer.exe',
                'size': 4563392,
                'inode': 42,
                'creation_time': '2020-01-15 10:28:00',
                'modification_time': '2024-08-10 13:22:15',
                'access_time': '2026-02-21 08:15:30',
                'is_deleted': False,
                'is_directory': False,
            },
            {
                'name': 'Desktop',
                'path': '/Users/Admin/Desktop',
                'size': 0,
                'inode': 128,
                'creation_time': '2022-03-15 12:00:00',
                'modification_time': '2026-02-15 16:45:22',
                'access_time': '2026-02-21 09:30:00',
                'is_deleted': False,
                'is_directory': True,
            },
            {
                'name': 'malware.exe',
                'path': '/Users/Admin/Downloads/malware.exe',
                'size': 2048576,
                'inode': 256,
                'creation_time': '2025-10-15 22:45:00',
                'modification_time': '2025-10-15 22:45:00',
                'access_time': '2025-10-16 08:15:30',
                'is_deleted': False,
                'is_directory': False,
            },
            {
                'name': 'hiberfil.sys',
                'path': '/hiberfil.sys',
                'size': 4294967296,
                'inode': 512,
                'creation_time': '2020-01-15 10:25:00',
                'modification_time': '2026-02-21 04:30:00',
                'access_time': '2026-02-21 04:30:00',
                'is_deleted': False,
                'is_directory': False,
            },
            {
                'name': 'pagefile.sys',
                'path': '/pagefile.sys',
                'size': 2147483648,
                'inode': 1024,
                'creation_time': '2020-01-15 10:26:00',
                'modification_time': '2026-02-21 14:20:00',
                'access_time': '2026-02-21 14:20:00',
                'is_deleted': False,
                'is_directory': False,
            },
            {
                'name': 'deleted_file.tmp',
                'path': '/Users/Admin/AppData/Local/Temp/deleted_file.tmp',
                'size': 524288,
                'inode': 2048,
                'creation_time': '2025-12-10 15:30:00',
                'modification_time': '2025-12-15 10:45:00',
                'access_time': '2025-12-20 14:30:00',
                'is_deleted': True,
                'is_directory': False,
            },
            {
                'name': 'ransomware.dll',
                'path': '/Windows/System32/drivers/ransomware.dll',
                'size': 1048576,
                'inode': 4096,
                'creation_time': '2025-11-22 03:15:00',
                'modification_time': '2025-11-22 03:15:00',
                'access_time': '2025-11-23 09:00:00',
                'is_deleted': False,
                'is_directory': False,
            },
            {
                'name': 'script.ps1',
                'path': '/Users/Admin/Documents/script.ps1',
                'size': 8192,
                'inode': 8192,
                'creation_time': '2025-12-01 18:30:00',
                'modification_time': '2025-12-05 20:15:00',
                'access_time': '2025-12-10 08:45:00',
                'is_deleted': False,
                'is_directory': False,
            },
            {
                'name': 'batch_file.bat',
                'path': '/Startup/batch_file.bat',
                'size': 2048,
                'inode': 16384,
                'creation_time': '2025-11-15 14:20:00',
                'modification_time': '2025-11-20 09:30:00',
                'access_time': '2026-02-15 10:15:00',
                'is_deleted': False,
                'is_directory': False,
            },
            {
                'name': 'ntdll.dll',
                'path': '/Windows/System32/ntdll.dll',
                'size': 2105344,
                'inode': 32768,
                'creation_time': '2020-01-15 10:28:00',
                'modification_time': '2024-06-18 11:45:00',
                'access_time': '2026-02-21 09:10:00',
                'is_deleted': False,
                'is_directory': False,
            },
        ]
        
        # Store files in metadata
        for file_data in demo_files:
            unique_key = f"{file_data['inode']}_{file_data['name']}"
            self.files_metadata[unique_key] = file_data
            if file_data['is_deleted']:
                self.deleted_files_count += 1
    
    def open_disk_image(self) -> bool:
        """Simulate opening disk image."""
        try:
            print(f"[*] Opening disk image: {self.image_path}")
            print(f"[+] Detected RAW format (demo mode)")
            print(f"[+] Successfully opened disk image")
            return True
        except Exception as e:
            print(f"[-] Error opening disk image: {str(e)}")
            return False
    
    def detect_partitions(self) -> bool:
        """Simulate partition detection."""
        try:
            print(f"\n[*] Detecting partitions...")
            print(f"[+] Partition 1: Address=0, Offset=1048576, Size=1099508482048")
            print(f"[+] Successfully detected 1 partition")
            return True
        except Exception as e:
            print(f"[-] Error detecting partitions: {str(e)}")
            return False
    
    def open_filesystem(self) -> bool:
        """Simulate filesystem opening."""
        try:
            print(f"\n[*] Opening filesystem from first partition...")
            print(f"[+] Filesystem opened successfully")
            print(f"[+] Filesystem type: {self.partition_info['filesystem_type']}")
            print(f"[+] Block size: {self.partition_info['block_size']}")
            print(f"[+] Block count: {self.partition_info['block_count']}")
            return True
        except Exception as e:
            print(f"[-] Error opening filesystem: {str(e)}")
            return False
    
    def recursively_scan_files(self) -> bool:
        """Simulate file scanning (data already generated)."""
        try:
            print(f"\n[*] Starting recursive file scan...")
            print(f"[+] File scan completed")
            print(f"[+] Total files found: {len(self.files_metadata)}")
            print(f"[+] Deleted files found: {self.deleted_files_count}")
            return True
        except Exception as e:
            print(f"[-] Error during file scan: {str(e)}")
            return False
    
    def export_to_json(self, output_path: str) -> bool:
        """Export collected file metadata to JSON format."""
        try:
            print(f"\n[*] Exporting data to JSON...")
            
            export_data = {
                'forensic_report': {
                    'image_path': self.image_path,
                    'scan_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'partition_info': self.partition_info,
                    'summary': {
                        'total_partitions': 1,
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
            return False
    
    def generate_summary_from_model(self, json_data: str) -> str:
        """Generate a human-readable forensic summary from JSON data."""
        try:
            data = json.loads(json_data)
            forensic_data = data['forensic_report']
            
            summary = "=" * 70 + "\n"
            summary += "FORENSIC ANALYSIS REPORT\n"
            summary += "=" * 70 + "\n\n"
            
            summary += f"Image Path: {forensic_data['image_path']}\n"
            summary += f"Scan Timestamp: {forensic_data['scan_timestamp']}\n\n"
            
            summary += "FILESYSTEM INFORMATION:\n"
            summary += "-" * 70 + "\n"
            partition_info = forensic_data['partition_info']
            summary += f"Filesystem Type: {partition_info.get('filesystem_type', 'Unknown')}\n"
            summary += f"Block Size: {partition_info.get('block_size', 'Unknown')} bytes\n"
            summary += f"Block Count: {partition_info.get('block_count', 'Unknown')}\n\n"
            
            summary += "FILE STATISTICS:\n"
            summary += "-" * 70 + "\n"
            file_summary = forensic_data['summary']
            summary += f"Total Partitions: {file_summary['total_partitions']}\n"
            summary += f"Total Files: {file_summary['total_files']}\n"
            summary += f"Deleted Files: {file_summary['total_deleted_files']}\n\n"
            
            # Find largest file
            files = forensic_data['files']
            if files:
                largest_file = max(files.values(), key=lambda x: x['size'])
                summary += "LARGEST FILE:\n"
                summary += "-" * 70 + "\n"
                summary += f"Name: {largest_file['name']}\n"
                summary += f"Path: {largest_file['path']}\n"
                summary += f"Size: {largest_file['size']:,} bytes\n\n"
            
            # Find suspicious files by extension
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
            
            # Deleted files analysis
            deleted_files = [f for f in files.values() if f['is_deleted']]
            summary += "DELETED FILES:\n"
            summary += "-" * 70 + "\n"
            if deleted_files:
                summary += f"Found {len(deleted_files)} deleted files.\n"
                summary += "Details:\n\n"
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
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def save_summary(self, summary_text: str, output_path: str) -> bool:
        """Save the generated summary to a text file."""
        try:
            print(f"\n[*] Saving forensic summary...")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            
            print(f"[+] Summary saved successfully to: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error saving summary: {str(e)}")
            return False
    
    def run_analysis_pipeline(self, json_output: str, summary_output: str) -> bool:
        """Execute the complete forensic analysis pipeline."""
        print("\n" + "=" * 70)
        print("FORENSIC ANALYSIS PIPELINE - DEMO VERSION (pytsk3 not required)")
        print("=" * 70 + "\n")
        
        if not self.open_disk_image():
            return False
        
        if not self.detect_partitions():
            return False
        
        if not self.open_filesystem():
            return False
        
        if not self.recursively_scan_files():
            return False
        
        if not self.export_to_json(json_output):
            return False
        
        with open(json_output, 'r', encoding='utf-8') as f:
            json_data = f.read()
        
        summary = self.generate_summary_from_model(json_data)
        
        if not self.save_summary(summary, summary_output):
            return False
        
        print("\n" + "=" * 70)
        print("ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")
        
        return True


def main():
    """Main execution function."""
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    IMAGE_PATH = r"C:\forensics\image.raw"
    JSON_OUTPUT = r"D:\Forensics Application\forensic_report.json"
    SUMMARY_OUTPUT = r"D:\Forensics Application\forensic_summary.txt"
    
    # =========================================================================
    # EXECUTION
    # =========================================================================
    
    try:
        analyzer = ForensicAnalyzerDemo(IMAGE_PATH)
        success = analyzer.run_analysis_pipeline(JSON_OUTPUT, SUMMARY_OUTPUT)
        
        if success:
            print("\n[+] All operations completed successfully!")
            print(f"[+] JSON Report: {JSON_OUTPUT}")
            print(f"[+] Summary Report: {SUMMARY_OUTPUT}")
            
            # Print summary to console
            print("\n" + "=" * 70)
            print("GENERATED SUMMARY (preview):")
            print("=" * 70 + "\n")
            with open(SUMMARY_OUTPUT, 'r', encoding='utf-8') as f:
                print(f.read())
            
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
