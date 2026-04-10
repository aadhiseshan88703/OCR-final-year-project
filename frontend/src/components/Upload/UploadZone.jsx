import React, { useCallback, useState } from 'react';
import { UploadCloud } from 'lucide-react';

const UploadZone = ({ onFilesAdded, isProcessing }) => {
  const [isDragOptions, setIsDragOptions] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragOptions(true);
    } else if (e.type === 'dragleave') {
      setIsDragOptions(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOptions(false);
    
    if (isProcessing) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArray = Array.from(e.dataTransfer.files);
      const validFiles = filesArray.filter(f => f.type.startsWith('image/'));
      if (validFiles.length > 0) {
        onFilesAdded(validFiles);
      }
    }
  }, [onFilesAdded, isProcessing]);

  const handleChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      onFilesAdded(filesArray);
      // Reset input value to allow selecting same files again if needed
      e.target.value = null;
    }
  };

  return (
    <div 
      className={`relative w-full border-2 border-dashed rounded-2xl transition-all duration-300 flex flex-col items-center justify-center p-12 text-center
        ${isDragOptions ? 'border-blue-500 bg-blue-50 shadow-inner' : 'border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50'}
        ${isProcessing ? 'opacity-50 cursor-not-allowed pointer-events-none' : 'cursor-pointer'}
      `}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        multiple
        accept="image/*"
        onChange={handleChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isProcessing}
      />
      
      <div className="bg-blue-100 text-blue-600 p-4 rounded-full mb-4 shadow-sm group-hover:scale-110 transition-transform">
        <UploadCloud size={32} />
      </div>
      
      <h3 className="text-xl font-semibold text-gray-800 mb-2">
        {isDragOptions ? 'Drop files now' : 'Click or Drag images to upload'}
      </h3>
      <p className="text-sm text-gray-500 mb-4 max-w-xs">
        Ensure your invoices or receipts are clearly visible. Supports JPG, PNG, WEBP.
      </p>
      
      <button 
        type="button"
        disabled={isProcessing}
        className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg text-sm hover:bg-gray-50 hover:text-blue-600 transition-colors pointer-events-none shadow-sm"
      >
        Select Files
      </button>
    </div>
  );
};

export default UploadZone;
