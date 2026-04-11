import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, AlertTriangle, FileText, Code } from 'lucide-react';
import JsonViewer from './JsonViewer';

const ResultCard = ({ result }) => {
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'json'
  const [isExpanded, setIsExpanded] = useState(true);

  const isSuccess = result.status === 'success';

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-6 transition-all">
      {/* Header */}
      <div 
        className="bg-gray-50 border-b border-gray-200 px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-gray-100"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-sm">
            {result.image_number}
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">{result.image_name}</h4>
            <div className="flex items-center gap-2 mt-1">
              {isSuccess ? (
                <span className="flex items-center gap-1 text-xs font-medium text-green-600">
                  <CheckCircle size={14} /> Processed Successfully
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs font-medium text-red-600">
                  <AlertTriangle size={14} /> Processing Failed
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="text-gray-400">
          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="p-0">
          {!isSuccess ? (
            <div className="p-6 bg-red-50 text-red-700">
              {result.error && (
                <p className="font-semibold text-red-800 mb-2 flex items-center gap-2">
                  <AlertTriangle className="flex-shrink-0" size={18} />
                  {result.error}
                </p>
              )}
              <p className="text-sm flex items-start gap-2 text-red-600">
                <AlertTriangle className="flex-shrink-0 mt-0.5" size={16} />
                <span>{result.error_message || 'Unknown error occurred during processing.'}</span>
              </p>
            </div>
          ) : (
            <>
              <div className="border-b border-gray-200 px-6 pt-4 flex gap-6">
                <button
                  className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                    activeTab === 'text' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                  onClick={() => setActiveTab('text')}
                >
                  <FileText size={16} /> Extracted Text (Layout Preserved)
                </button>
                <button
                  className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                    activeTab === 'json' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                  onClick={() => setActiveTab('json')}
                >
                  <Code size={16} /> Structured JSON
                </button>
              </div>
              
              <div className="p-6 bg-gray-50">
                {activeTab === 'text' && (
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-inner">
                    {result.extracted_text ? (
                      <pre className="whitespace-pre font-mono text-sm text-gray-800 break-words max-h-[500px] overflow-auto custom-scrollbar">
                        {result.extracted_text}
                      </pre>
                    ) : (
                      <p className="text-gray-500 text-center italic py-8">No text extracted from this image.</p>
                    )}
                  </div>
                )}

                {activeTab === 'json' && (
                  <JsonViewer data={result.structured_data || {}} />
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ResultCard;
