import React, { useState } from 'react';
import Navbar from '../components/Layout/Navbar';
import UploadZone from '../components/Upload/UploadZone';
import FilePreviewList from '../components/Upload/FilePreviewList';
import ResultCard from '../components/Results/ResultCard';
import { useUpload } from '../hooks/useUpload';
import { Download, AlertCircle, RefreshCw } from 'lucide-react';

const HomePage = () => {
  const { files, addFiles, removeFile, clearFiles, submitFiles, isProcessing, results, error } = useUpload();

  const handleDownloadAll = () => {
    if (!results) return;
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ocr_results_${new Date().getTime()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        
        {/* Header Section */}
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl mb-4">
            Transform Invoices into <span className="text-blue-600">Structured Data</span>
          </h1>
          <p className="text-lg text-gray-600">
            Upload your receipts and invoices. Our AI pipeline will sequentially extract text while preserving the visual layout and map it to structured JSON.
          </p>
        </div>

        {/* Upload Container */}
        <div className="bg-white p-6 sm:p-10 rounded-3xl shadow-xl shadow-blue-900/5 border border-gray-100 mb-12 relative overflow-hidden">
          {/* Subtle gradient background decoration */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50 rounded-full blur-3xl opacity-50 -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
          
          <UploadZone onFilesAdded={addFiles} isProcessing={isProcessing} />
          
          <FilePreviewList files={files} onRemove={removeFile} isProcessing={isProcessing} />
          
          {/* Action Bar */}
          {files.length > 0 && !results && (
            <div className="mt-8 flex justify-end gap-4 border-t border-gray-100 pt-6">
              <button
                onClick={clearFiles}
                disabled={isProcessing}
                className="px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                Clear All
              </button>
              <button
                onClick={submitFiles}
                disabled={isProcessing}
                className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-600/20 transition-all flex items-center justify-center min-w-[200px]"
              >
                {isProcessing ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="animate-spin" size={20} /> Processing...
                  </span>
                ) : (
                  'Start Extraction Pipeline'
                )}
              </button>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 flex items-start gap-3">
              <AlertCircle className="flex-shrink-0 mt-0.5" size={20} />
              <div>
                <h4 className="font-semibold text-red-800">Processing Failed</h4>
                <p className="text-sm mt-1 text-red-700">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Results Section */}
        {results && (
          <div className="space-y-6 animate-in slide-in-from-bottom-8 opacity-0 fade-in duration-700 fill-mode-forwards">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Extraction Results</h2>
                <p className="text-gray-500 mt-1">Processed {results.length} images sequentially.</p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={clearFiles}
                  className="px-4 py-2 border border-gray-300 bg-white text-gray-700 font-medium rounded-lg hover:bg-gray-50 flex items-center gap-2"
                >
                  <RefreshCw size={18} /> New Upload
                </button>
                <button
                  onClick={handleDownloadAll}
                  className="px-4 py-2 bg-slate-900 text-white font-medium rounded-lg hover:bg-slate-800 shadow-sm flex items-center gap-2"
                >
                  <Download size={18} /> Download JSON
                </button>
              </div>
            </div>

            {results.map((res, index) => (
              <ResultCard key={`res-${index}`} result={res} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default HomePage;
