import { useState, useCallback, useRef } from 'react';
import { uploadFilesForStreaming, createResultStream } from '../services/api';

export const useUpload = () => {
  const [files, setFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  // Live progress: { current: number, total: number }
  const [progress, setProgress] = useState(null);
  // Keep a ref to the EventSource so we can close it on unmount / clear
  const streamRef = useRef(null);

  const addFiles = useCallback((newFiles) => {
    setFiles((prev) => {
      const existingNames = new Set(prev.map((f) => f.name));
      const fresh = newFiles.filter((f) => !existingNames.has(f.name));
      return [...prev, ...fresh];
    });
    setResults(null);
    setError(null);
    setProgress(null);
  }, []);

  const removeFile = useCallback((fileName) => {
    setFiles((prev) => prev.filter((f) => f.name !== fileName));
  }, []);

  const clearFiles = useCallback(() => {
    // Also close any open stream
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }
    setFiles([]);
    setResults(null);
    setError(null);
    setProgress(null);
  }, []);

  /**
   * Main submit handler.
   * 1. Uploads files → gets job_id (fast, just file transfer)
   * 2. Opens SSE stream → results arrive image-by-image in real time
   */
  const submitFiles = useCallback(async () => {
    if (files.length === 0) return;

    setIsProcessing(true);
    setError(null);
    setResults(null);
    setProgress({ current: 0, total: files.length });

    try {
      // ── Step 1: Upload files and get job_id ────────────────────────────
      const { job_id, file_count } = await uploadFilesForStreaming(files);

      // ── Step 2: Open SSE stream ─────────────────────────────────────────
      const stream = createResultStream(job_id);
      streamRef.current = stream;

      const collected = [];
      // Track whether the server sent the __done__ sentinel.
      // Some browsers fire onerror when the server closes the SSE connection
      // naturally — we must NOT show an error in that case.
      let doneReceived = false;

      stream.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Backend signals "all done"
        if (data.__done__) {
          doneReceived = true;
          stream.close();
          streamRef.current = null;
          setIsProcessing(false);
          setProgress({ current: file_count, total: file_count });
          return;
        }

        // Normal result — append and show immediately
        collected.push(data);
        // Spread into a new array so React re-renders
        setResults([...collected]);
        setProgress({ current: collected.length, total: file_count });
      };

      stream.onerror = () => {
        stream.close();
        streamRef.current = null;
        setIsProcessing(false);
        // Only show an error if the server never sent __done__.
        // If doneReceived is true this is just the browser closing the
        // finished SSE connection — perfectly normal, not an error.
        if (!doneReceived && collected.length < file_count) {
          setError('Connection lost while processing. Please try again.');
        }
      };

    } catch (err) {
      setError(err.message);
      setIsProcessing(false);
      setProgress(null);
    }
  }, [files]);

  return {
    files,
    addFiles,
    removeFile,
    clearFiles,
    submitFiles,
    isProcessing,
    results,
    error,
    progress,
  };
};
