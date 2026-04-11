import React from 'react';
import { Cpu, CheckCircle2 } from 'lucide-react';

/**
 * Live processing progress bar.
 * Shows how many images have been processed out of the total, with an
 * animated bar and a per-image status message.
 *
 * Props:
 *   progress  – { current: number, total: number } | null
 *   isDone    – boolean (all images finished)
 */
const ProcessingProgress = ({ progress, isDone }) => {
  if (!progress) return null;

  const { current, total } = progress;
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className="mt-6 p-5 bg-blue-50 border border-blue-100 rounded-2xl space-y-3">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2 text-sm font-semibold text-blue-800">
          {isDone ? (
            <>
              <CheckCircle2 size={18} className="text-green-600" />
              All {total} image{total !== 1 ? 's' : ''} processed
            </>
          ) : (
            <>
              <Cpu size={18} className="text-blue-600 animate-pulse" />
              Processing image {Math.min(current + 1, total)} of {total}…
            </>
          )}
        </span>
        <span className="text-sm font-bold text-blue-700">{pct}%</span>
      </div>

      {/* Progress bar track */}
      <div className="w-full h-3 bg-blue-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${
            isDone ? 'bg-green-500' : 'bg-blue-500'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Sub-label */}
      {!isDone && (
        <p className="text-xs text-blue-600">
          Results appear below as each image finishes — no need to wait for all
          images to complete.
        </p>
      )}
    </div>
  );
};

export default ProcessingProgress;
