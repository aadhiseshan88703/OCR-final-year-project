import React from 'react';
import Navbar from '../components/Layout/Navbar';
import UploadZone from '../components/Upload/UploadZone';
import FilePreviewList from '../components/Upload/FilePreviewList';
import ProcessingProgress from '../components/Upload/ProcessingProgress';
import ResultCard from '../components/Results/ResultCard';
import { useUpload } from '../hooks/useUpload';
import { Download, AlertCircle, RefreshCw } from 'lucide-react';

const HomePage = () => {
  const {
    files,
    addFiles,
    removeFile,
    clearFiles,
    submitFiles,
    isProcessing,
    results,
    error,
    progress,
  } = useUpload();

  // Results are showing (may still be streaming in)
  const hasResults = results && results.length > 0;
  // All images done
  const isDone = progress && results && results.length >= progress.total && !isProcessing;

  const handleDownloadAll = () => {
    if (!results) return;
    const blob = new Blob([JSON.stringify(results, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ocr_results_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

        {/* ── Hero ─────────────────────────────────────────────────────── */}
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl mb-4">
            Transform Invoices into{' '}
            <span className="text-blue-600">Structured Data</span>
          </h1>
          <p className="text-lg text-gray-600">
            Upload your receipts and invoices. The OCR pipeline extracts text
            and structured fields — results appear <strong>image by image</strong> in
            real time.
          </p>
        </div>

        {/* ── Upload card ───────────────────────────────────────────────── */}
        <div className="bg-white p-6 sm:p-10 rounded-3xl shadow-xl shadow-blue-900/5 border border-gray-100 mb-12 relative overflow-hidden">
          {/* Decorative gradient blob */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50 rounded-full blur-3xl opacity-50 -translate-y-1/2 translate-x-1/2 pointer-events-none" />

          <UploadZone onFilesAdded={addFiles} isProcessing={isProcessing} />

          <FilePreviewList
            files={files}
            onRemove={removeFile}
            isProcessing={isProcessing}
          />

          {/* Live progress bar — visible while processing */}
          <ProcessingProgress progress={progress} isDone={isDone} />

          {/* Action buttons */}
          {files.length > 0 && !hasResults && (
            <div className="mt-8 flex justify-end gap-4 border-t border-gray-100 pt-6">
              <button
                id="btn-clear-files"
                onClick={clearFiles}
                disabled={isProcessing}
                className="px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                Clear All
              </button>
              <button
                id="btn-start-extraction"
                onClick={submitFiles}
                disabled={isProcessing}
                className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-600/20 transition-all flex items-center justify-center min-w-[200px] disabled:opacity-60"
              >
                {isProcessing ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="animate-spin" size={20} />
                    Uploading &amp; Processing…
                  </span>
                ) : (
                  'Start Extraction Pipeline'
                )}
              </button>
            </div>
          )}

          {/* Error banner */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 flex items-start gap-3">
              <AlertCircle className="flex-shrink-0 mt-0.5" size={20} />
              <div>
                <h4 className="font-semibold text-red-800">Error</h4>
                <p className="text-sm mt-1 text-red-700">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* ── Results section — appears as images finish ─────────────────── */}
        {hasResults && (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Extraction Results
                </h2>
                <p className="text-gray-500 mt-1">
                  {isProcessing
                    ? `${results.length} of ${progress?.total ?? '?'} images processed — more coming…`
                    : `${results.length} image${results.length !== 1 ? 's' : ''} processed.`}
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  id="btn-new-upload"
                  onClick={clearFiles}
                  className="px-4 py-2 border border-gray-300 bg-white text-gray-700 font-medium rounded-lg hover:bg-gray-50 flex items-center gap-2"
                >
                  <RefreshCw size={18} /> New Upload
                </button>
                {isDone && (
                  <button
                    id="btn-download-json"
                    onClick={handleDownloadAll}
                    className="px-4 py-2 bg-slate-900 text-white font-medium rounded-lg hover:bg-slate-800 shadow-sm flex items-center gap-2"
                  >
                    <Download size={18} /> Download JSON
                  </button>
                )}
              </div>
            </div>

            {results.map((res, index) => (
              <ResultCard key={`res-${index}-${res.image_name}`} result={res} />
            ))}

            {/* Inline spinner after last card while more images arrive */}
            {isProcessing && (
              <div className="flex items-center justify-center gap-3 py-8 text-blue-600 text-sm font-medium">
                <RefreshCw className="animate-spin" size={20} />
                Processing next image…
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default HomePage;
