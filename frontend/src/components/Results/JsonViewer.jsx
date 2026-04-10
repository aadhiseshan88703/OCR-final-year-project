import React from 'react';

const JsonViewer = ({ data }) => {
  return (
    <div className="bg-slate-900 rounded-xl overflow-hidden mt-4 shadow-inner border border-slate-700">
      <div className="bg-slate-800 px-4 py-2 border-b border-slate-700 flex justify-between items-center text-xs font-mono text-slate-400">
        <span>structured_data.json</span>
        <button 
          onClick={() => navigator.clipboard.writeText(JSON.stringify(data, null, 2))}
          className="hover:text-blue-400 transition-colors"
        >
          Copy JSON
        </button>
      </div>
      <div className="p-4 max-h-[400px] overflow-auto custom-scrollbar">
        <pre className="text-sm font-mono text-green-400 whitespace-pre-wrap break-words">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default JsonViewer;
