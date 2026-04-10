import { useState, useCallback } from 'react';
import { uploadFiles } from '../services/api';

export const useUpload = () => {
  const [files, setFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const addFiles = useCallback((newFiles) => {
    setFiles((prev) => {
      // Avoid duplicates
      const existingNames = new Set(prev.map(f => f.name));
      const filtered = newFiles.filter(f => !existingNames.has(f.name));
      return [...prev, ...filtered];
    });
    // Clear previous results or errors on new file add
    setResults(null);
    setError(null);
  }, []);

  const removeFile = useCallback((fileName) => {
    setFiles((prev) => prev.filter(f => f.name !== fileName));
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
    setResults(null);
    setError(null);
  }, []);

  const submitFiles = async () => {
    if (files.length === 0) return;
    
    setIsProcessing(true);
    setError(null);
    setResults(null);
    
    try {
      const data = await uploadFiles(files);
      setResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return {
    files,
    addFiles,
    removeFile,
    clearFiles,
    submitFiles,
    isProcessing,
    results,
    error
  };
};
