"""
FORENSIC ANALYSIS WEB APPLICATION
Modern, Futuristic Frontend with Backend Analysis
Supports: RAW, DD, E01 disk images and USB drives
Exports: PDF and DOC formats
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import json
import threading
from datetime import datetime
from pathlib import Path
from forensic_pipeline_advanced import AdvancedForensicAnalyzer
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

app = Flask(__name__)
app.secret_key = 'forensic-analysis-secret-key-2026'

# Configuration
UPLOAD_FOLDER = r'D:\Forensics Application\uploads'
OUTPUT_FOLDER = r'D:\Forensics Application\analysis_output'
ALLOWED_EXTENSIONS = {'raw', 'dd', 'e01', 'img', 'iso', 'bin', 'dmg'}

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global analysis status tracker
analysis_status = {
    'current': None,
    'progress': 0,
    'status': 'idle',
    'message': '',
    'errors': [],
    'results': None
}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def run_forensic_analysis(image_path, analysis_id):
    """Run forensic analysis in background thread."""
    global analysis_status
    
    try:
        analysis_status['current'] = analysis_id
        analysis_status['status'] = 'analyzing'
        analysis_status['progress'] = 10
        analysis_status['message'] = 'Starting forensic analysis...'
        
        analyzer = AdvancedForensicAnalyzer(image_path, use_demo=False)
        
        analysis_status['progress'] = 25
        analysis_status['message'] = 'Opening disk image...'
        if not analyzer.open_disk_image():
            raise Exception("Failed to open disk image")
        
        analysis_status['progress'] = 35
        analysis_status['message'] = 'Detecting partitions...'
        if not analyzer.detect_partitions():
            raise Exception("Failed to detect partitions")
        
        analysis_status['progress'] = 45
        analysis_status['message'] = 'Opening filesystem...'
        if not analyzer.open_filesystem():
            raise Exception("Failed to open filesystem")
        
        analysis_status['progress'] = 55
        analysis_status['message'] = 'Scanning files recursively...'
        if not analyzer.recursively_scan_files():
            raise Exception("Failed to scan files")
        
        analysis_status['progress'] = 65
        analysis_status['message'] = 'Computing file hashes...'
        if not analyzer.compute_file_hashes():
            raise Exception("Failed to compute hashes")
        
        analysis_status['progress'] = 75
        analysis_status['message'] = 'Detecting encryption and network artifacts...'
        encrypted_items = analyzer.detect_encryption()
        network_artifacts = analyzer.detect_network_artifacts()
        
        analysis_status['progress'] = 85
        analysis_status['message'] = 'Generating reports...'
        
        # Generate JSON report
        json_path = os.path.join(OUTPUT_FOLDER, f'{analysis_id}_report.json')
        if not analyzer.export_to_json(json_path):
            raise Exception("Failed to export JSON")
        
        # Generate timeline report
        timeline_path = os.path.join(OUTPUT_FOLDER, f'{analysis_id}_timeline.txt')
        if not analyzer.generate_timeline_report(timeline_path):
            raise Exception("Failed to generate timeline")
        
        # Generate extension report
        extension_path = os.path.join(OUTPUT_FOLDER, f'{analysis_id}_extensions.txt')
        if not analyzer.generate_extension_report(extension_path):
            raise Exception("Failed to generate extension report")
        
        # Generate summary report
        summary_path = os.path.join(OUTPUT_FOLDER, f'{analysis_id}_summary.txt')
        if not analyzer.generate_summary_report(json_path, summary_path):
            raise Exception("Failed to generate summary")
        
        analysis_status['progress'] = 95
        analysis_status['message'] = 'Finalizing analysis...'
        
        # Prepare results data
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        analysis_status['results'] = {
            'json_path': json_path,
            'summary_path': summary_path,
            'timeline_path': timeline_path,
            'extension_path': extension_path,
            'analysis_id': analysis_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'image_path': image_path,
            'data': json_data
        }
        
        analysis_status['progress'] = 100
        analysis_status['status'] = 'completed'
        analysis_status['message'] = 'Analysis completed successfully!'
        
    except Exception as e:
        analysis_status['status'] = 'error'
        analysis_status['message'] = f'Error: {str(e)}'
        analysis_status['errors'].append(str(e))
        print(f"[-] Forensic Analysis Error: {str(e)}")

def generate_pdf_report(analysis_id, results):
    """Generate PDF report from analysis results."""
    try:
        pdf_path = os.path.join(OUTPUT_FOLDER, f'{analysis_id}_report.pdf')
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, 
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00E5FF'),
            spaceAfter=30,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#00BCD4'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
        
        # Content
        content = []
        
        # Title
        content.append(Paragraph("🔍 FORENSIC ANALYSIS REPORT", title_style))
        content.append(Spacer(1, 0.2*inch))
        
        # Header Info
        data = results['data']['forensic_report']
        
        header_data = [
            ['Report Generated', results['timestamp']],
            ['Image Analyzed', data['image_path']],
            ['Filesystem', data['partition_info'].get('filesystem_type', 'Unknown')],
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E0F2F1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))
        
        content.append(header_table)
        content.append(Spacer(1, 0.2*inch))
        
        # Summary Statistics
        content.append(Paragraph("📊 SUMMARY STATISTICS", heading_style))
        
        summary = data['summary']
        summary_text = f"""
        <b>Total Files:</b> {summary['total_files']:,}<br/>
        <b>Deleted Files:</b> {summary['total_deleted_files']}<br/>
        <b>Suspicious Files:</b> {summary['suspicious_files_count']}<br/>
        <b>Encrypted Items:</b> {summary['encrypted_items_count']}<br/>
        <b>Network Artifacts:</b> {summary['network_artifacts_count']}<br/>
        """
        
        content.append(Paragraph(summary_text, normal_style))
        content.append(Spacer(1, 0.2*inch))
        
        # File Statistics
        content.append(Paragraph("📈 FILE EXTENSION DISTRIBUTION", heading_style))
        
        extensions = data.get('file_extension_statistics', {})
        ext_data = [['Extension', 'Count']]
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:15]:
            ext_data.append([ext, str(count)])
        
        ext_table = Table(ext_data, colWidths=[3*inch, 1.5*inch])
        ext_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00BCD4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8F8')]),
        ]))
        
        content.append(ext_table)
        content.append(Spacer(1, 0.3*inch))
        
        # Suspicious Files
        files = data['files']
        suspicious_files = [
            f for f in files.values()
            if any(f['name'].lower().endswith(ext) for ext in ['.exe', '.bat', '.ps1', '.dll', '.scr', '.vbs'])
        ]
        
        if suspicious_files:
            content.append(PageBreak())
            content.append(Paragraph("⚠️ SUSPICIOUS FILES DETECTED", heading_style))
            
            sus_data = [['Name', 'Path', 'Size', 'Modified']]
            for f in suspicious_files[:20]:
                sus_data.append([
                    f['name'][:30],
                    f['path'][:40],
                    f"{f['size'] / (1024*1024):.2f} MB" if f['size'] > 1024*1024 else f"{f['size'] / 1024:.2f} KB",
                    f['modification_time'][:10]
                ])
            
            sus_table = Table(sus_data, colWidths=[1.2*inch, 2.2*inch, 1*inch, 1.6*inch])
            sus_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B6B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFE0E0')]),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
            ]))
            
            content.append(sus_table)
        
        # Encrypted Items
        encrypted = data.get('encrypted_items', [])
        if encrypted:
            content.append(Spacer(1, 0.2*inch))
            content.append(Paragraph("🔐 ENCRYPTED ITEMS", heading_style))
            
            enc_text = ""
            for item in encrypted[:10]:
                size_mb = item['size'] / (1024*1024*1024)
                enc_text += f"<b>{item['name']}</b> ({size_mb:.2f} GB)<br/>"
                enc_text += f"Path: {item['path']}<br/>"
                enc_text += f"Modified: {item['modified']}<br/><br/>"
            
            content.append(Paragraph(enc_text, normal_style))
        
        # Build PDF
        doc.build(content)
        return pdf_path
        
    except Exception as e:
        print(f"[-] PDF Generation Error: {str(e)}")
        return None

def generate_doc_report(analysis_id, results):
    """Generate Word (DOCX) report from analysis results."""
    try:
        doc_path = os.path.join(OUTPUT_FOLDER, f'{analysis_id}_report.docx')
        
        doc = Document()
        
        # Add title
        title = doc.add_heading('🔍 FORENSIC ANALYSIS REPORT', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title.runs[0]
        title_run.font.color.rgb = RGBColor(0, 229, 255)
        
        # Add datetime
        date_para = doc.add_paragraph(f"Report Generated: {results['timestamp']}")
        date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add image info
        doc.add_heading('📋 EVIDENCE INFORMATION', level=1)
        
        info_table = doc.add_table(rows=3, cols=2)
        info_table.style = 'Light Grid Accent 1'
        
        info_table.cell(0, 0).text = 'Image Path'
        info_table.cell(0, 1).text = results['image_path']
        info_table.cell(1, 0).text = 'Analysis Date'
        info_table.cell(1, 1).text = results['timestamp']
        
        data = results['data']['forensic_report']
        info_table.cell(2, 0).text = 'Filesystem Type'
        info_table.cell(2, 1).text = data['partition_info'].get('filesystem_type', 'Unknown')
        
        doc.add_paragraph()
        
        # Summary Statistics
        doc.add_heading('📊 SUMMARY STATISTICS', level=1)
        
        summary = data['summary']
        stats_para = doc.add_paragraph()
        stats_para.add_run(f"Total Files: ").bold = True
        stats_para.add_run(f"{summary['total_files']:,}\n")
        
        stats_para.add_run(f"Deleted Files: ").bold = True
        stats_para.add_run(f"{summary['total_deleted_files']}\n")
        
        stats_para.add_run(f"Suspicious Files: ").bold = True
        stats_para.add_run(f"{summary['suspicious_files_count']}\n")
        
        stats_para.add_run(f"Encrypted Items: ").bold = True
        stats_para.add_run(f"{summary['encrypted_items_count']}\n")
        
        stats_para.add_run(f"Network Artifacts: ").bold = True
        stats_para.add_run(f"{summary['network_artifacts_count']}\n")
        
        doc.add_paragraph()
        
        # File Extensions
        doc.add_heading('📈 FILE EXTENSION DISTRIBUTION', level=1)
        
        extensions = data.get('file_extension_statistics', {})
        ext_table = doc.add_table(rows=min(16, len(extensions) + 1), cols=2)
        ext_table.style = 'Light Grid Accent 1'
        
        ext_table.cell(0, 0).text = 'Extension'
        ext_table.cell(0, 1).text = 'Count'
        
        for idx, (ext, count) in enumerate(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:15]):
            ext_table.cell(idx + 1, 0).text = str(ext)
            ext_table.cell(idx + 1, 1).text = str(count)
        
        doc.add_page_break()
        
        # Suspicious Files
        files = data['files']
        suspicious_files = [
            f for f in files.values()
            if any(f['name'].lower().endswith(ext) for ext in ['.exe', '.bat', '.ps1', '.dll', '.scr', '.vbs'])
        ]
        
        if suspicious_files:
            doc.add_heading('⚠️ SUSPICIOUS FILES DETECTED', level=1)
            
            sus_para = doc.add_paragraph()
            sus_para.add_run(f"Found {len(suspicious_files)} suspicious files:\n").bold = True
            
            for f in suspicious_files[:20]:
                sus_item = doc.add_paragraph(style='List Bullet')
                sus_item.add_run(f['name']).bold = True
                sus_item.add_run(f"\nPath: {f['path']}\n")
                sus_item.add_run(f"Size: {f['size'] / (1024*1024):.2f} MB\n" if f['size'] > 1024*1024 else f"Size: {f['size'] / 1024:.2f} KB\n")
                sus_item.add_run(f"Modified: {f['modification_time']}")
        
        # Encrypted Items
        encrypted = data.get('encrypted_items', [])
        if encrypted:
            doc.add_heading('🔐 ENCRYPTED ITEMS', level=1)
            
            for item in encrypted[:10]:
                enc_para = doc.add_paragraph(style='List Bullet')
                enc_para.add_run(f"{item['name']}").bold = True
                size_gb = item['size'] / (1024*1024*1024)
                enc_para.add_run(f" ({size_gb:.2f} GB)\n")
                enc_para.add_run(f"Path: {item['path']}\n")
                enc_para.add_run(f"Modified: {item['modified']}")
        
        # Save document
        doc.save(doc_path)
        return doc_path
        
    except Exception as e:
        print(f"[-] DOC Generation Error: {str(e)}")
        return None

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render main dashboard."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current analysis status."""
    return jsonify(analysis_status)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Start forensic analysis."""
    global analysis_status
    
    try:
        data = request.json
        image_path = data.get('image_path')
        
        if not image_path:
            return jsonify({'error': 'No image path provided'}), 400
        
        if not os.path.exists(image_path):
            return jsonify({'error': f'Image file not found: {image_path}'}), 400
        
        analysis_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(
            target=run_forensic_analysis,
            args=(image_path, analysis_id)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'message': 'Analysis started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format>', methods=['GET'])
def export_report(format):
    """Export report as PDF or DOC."""
    global analysis_status
    
    try:
        if not analysis_status['results']:
            return jsonify({'error': 'No analysis results available'}), 400
        
        results = analysis_status['results']
        analysis_id = results['analysis_id']
        
        if format.lower() == 'pdf':
            pdf_path = generate_pdf_report(analysis_id, results)
            if pdf_path and os.path.exists(pdf_path):
                return send_file(pdf_path, mimetype='application/pdf', 
                               as_attachment=True, 
                               download_name=f'forensic_report_{analysis_id}.pdf')
            else:
                return jsonify({'error': 'Failed to generate PDF'}), 500
        
        elif format.lower() == 'doc' or format.lower() == 'docx':
            doc_path = generate_doc_report(analysis_id, results)
            if doc_path and os.path.exists(doc_path):
                return send_file(doc_path, 
                               mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                               as_attachment=True,
                               download_name=f'forensic_report_{analysis_id}.docx')
            else:
                return jsonify({'error': 'Failed to generate DOCX'}), 500
        
        else:
            return jsonify({'error': 'Invalid format. Use "pdf" or "doc"'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results')
def get_results():
    """Get analysis results."""
    global analysis_status
    
    if not analysis_status['results']:
        return jsonify({'error': 'No results available'}), 400
    
    # Return results summary (don't send entire JSON to avoid size issues)
    results = analysis_status['results']
    data = results['data']['forensic_report']
    
    return jsonify({
        'timestamp': results['timestamp'],
        'image_path': results['image_path'],
        'summary': data['summary'],
        'extensions': data.get('file_extension_statistics', {}),
        'encrypted_items': data.get('encrypted_items', []),
        'network_artifacts': data.get('network_artifacts', [])
    })

@app.route('/api/reset')
def reset_analysis():
    """Reset analysis for new one."""
    global analysis_status
    
    analysis_status = {
        'current': None,
        'progress': 0,
        'status': 'idle',
        'message': '',
        'errors': [],
        'results': None
    }
    
    return jsonify({'success': True, 'message': 'Analysis reset'})

if __name__ == '__main__':
    print("\n" + "="*80)
    print(" FORENSIC ANALYSIS WEB APPLICATION - STARTING")
    print("="*80)
    print("\n[+] Frontend: http://localhost:5000")
    print("[+] Backend: Flask Server")
    print("[+] Upload Folder: " + UPLOAD_FOLDER)
    print("[+] Output Folder: " + OUTPUT_FOLDER)
    print("\n" + "="*80 + "\n")
    
    app.run(debug=False, host='localhost', port=5000, threaded=True)
