import React from 'react';
import { X, FileImage, HardDrive } from 'lucide-react';

const formatBytes = (bytes, decimals = 2) => {
  if (!+bytes) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
};

const FilePreviewList = ({ files, onRemove, isProcessing }) => {
  if (!files || files.length === 0) return null;

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <HardDrive size={20} className="text-blue-500"/> 
          Selected Files <span className="bg-blue-100 text-blue-700 text-xs py-0.5 px-2 rounded-full font-bold">{files.length}</span>
        </h3>
      </div>
      
      <div className="flex flex-col gap-3">
        {files.map((file, idx) => (
          <div 
            key={`${file.name}-${idx}`} 
            className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow group"
          >
            <div className="flex items-center gap-4 overflow-hidden">
              <div className="w-12 h-12 flex-shrink-0 bg-blue-50 rounded-lg flex items-center justify-center text-blue-500 overflow-hidden relative">
                {/* For actual images we can display thumbnail, otherwise an icon */}
                {file.type.startsWith('image/') ? (
                  <img src={URL.createObjectURL(file)} alt="preview" className="w-full h-full object-cover" />
                ) : (
                  <FileImage size={24} />
                )}
              </div>
              <div className="flex flex-col overflow-hidden">
                <span className="text-sm font-medium text-gray-900 truncate" title={file.name}>
                  {idx + 1}. {file.name}
                </span>
                <span className="text-xs text-gray-500 mt-0.5">{formatBytes(file.size)}</span>
              </div>
            </div>
            
            <button
              type="button"
              onClick={() => onRemove(file.name)}
              disabled={isProcessing}
              className={`p-2 rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors ${
                isProcessing ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              title="Remove file"
            >
              <X size={18} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FilePreviewList;
