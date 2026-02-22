import React, { useState, useRef } from 'react';
import { cn } from '@/lib/utils';

interface UploadStatus {
  isUploading: boolean;
  progress: number;
  fileName?: string;
  error?: string;
  uploadSuccess?: boolean;
}

/**
 * Forensic File Upload Component
 * Handles disk image and evidence file uploads
 */
export const ForensicFileUpload: React.FC = () => {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({
    isUploading: false,
    progress: 0,
  });
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedExtensions = ['raw', 'dd', 'e01', 'img', 'iso', 'bin', 'dmg'];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    if (!fileExtension || !allowedExtensions.includes(fileExtension)) {
      setUploadStatus({
        isUploading: false,
        progress: 0,
        error: `Invalid file type. Allowed: ${allowedExtensions.join(', ')}`,
      });
      return;
    }

    setUploadStatus({
      isUploading: true,
      progress: 0,
      fileName: file.name,
    });

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Upload to Flask backend
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setUploadStatus({
        isUploading: false,
        progress: 100,
        fileName: file.name,
        uploadSuccess: true,
      });

      // Trigger analysis after upload
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('fileUploaded', { detail: data }));
        setShowDownloadMenu(true);
      }, 500);
    } catch (error) {
      setUploadStatus({
        isUploading: false,
        progress: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const handleDownload = async (format: 'pdf' | 'docx') => {
    setIsDownloading(true);
    try {
      const response = await fetch(`/api/export/${format}`);
      
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `forensic_report.${format === 'pdf' ? 'pdf' : 'docx'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      setUploadStatus({
        ...uploadStatus,
        error: error instanceof Error ? error.message : 'Download failed',
      });
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className={cn('w-full max-w-lg mx-auto p-6 rounded-lg border-2 border-dashed border-gray-600 hover:border-gray-500 transition-colors cursor-pointer')}>
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileSelect}
        disabled={uploadStatus.isUploading}
        className="hidden"
        accept=".raw,.dd,.e01,.img,.iso,.bin,.dmg"
      />

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploadStatus.isUploading}
        className={cn(
          'w-full py-4 px-6 rounded-lg font-bold text-center transition-all',
          uploadStatus.isUploading
            ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
            : 'bg-gray-700 text-white hover:bg-gray-600'
        )}
      >
        {uploadStatus.isUploading ? `Uploading: ${uploadStatus.fileName}` : 'SELECT EVIDENCE FILE'}
      </button>

      {uploadStatus.progress > 0 && uploadStatus.progress < 100 && (
        <div className="mt-4">
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-gray-400 h-2 rounded-full transition-all"
              style={{ width: `${uploadStatus.progress}%` }}
            ></div>
          </div>
          <p className="text-center text-gray-400 text-sm mt-2">{uploadStatus.progress}%</p>
        </div>
      )}

      {uploadStatus.error && (
        <p className="text-red-500 text-sm mt-4 text-center">{uploadStatus.error}</p>
      )}

      {uploadStatus.progress === 100 && uploadStatus.uploadSuccess && (
        <div className="mt-4 space-y-3">
          <p className="text-green-500 text-sm text-center">✓ Upload and analysis complete</p>
          
          <div className="relative">
            <button
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
              disabled={isDownloading}
              className="w-full py-2 px-4 rounded-lg bg-gray-700 hover:bg-gray-600 text-white font-semibold text-sm transition-all disabled:opacity-50"
            >
              {isDownloading ? 'Downloading...' : 'Download Report'}
            </button>
            
            {showDownloadMenu && (
              <div className="absolute top-full mt-2 w-full bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-10">
                <button
                  onClick={() => handleDownload('pdf')}
                  disabled={isDownloading}
                  className="w-full py-2 px-4 text-left hover:bg-gray-700 text-white text-sm first:rounded-t-lg disabled:opacity-50"
                >
                  📄 Download as PDF
                </button>
                <button
                  onClick={() => handleDownload('docx')}
                  disabled={isDownloading}
                  className="w-full py-2 px-4 text-left hover:bg-gray-700 text-white text-sm last:rounded-b-lg disabled:opacity-50"
                >
                  📝 Download as DOCX
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ForensicFileUpload;
