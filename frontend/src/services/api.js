import axios from 'axios';

// Use relative path in dev so Vite proxy handles /api/* → backend
// This also fixes SSE stream CORS + buffering issues in development.
const API_BASE_URL = '/api';

/**
 * Step 1 – Upload files and get a streaming job_id back.
 * Files are sent in the exact array order; the backend preserves that order.
 * @param {File[]} files
 * @returns {Promise<{job_id: string, file_count: number}>}
 */
export const uploadFilesForStreaming = async (files) => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));

  try {
    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      // Generous timeout just for the upload phase
      timeout: 60_000,
    });
    return response.data; // { job_id, file_count }
  } catch (error) {
    throw _formatError(error);
  }
};

/**
 * Step 2 – Return a native browser EventSource connected to the SSE stream.
 * The caller is responsible for adding onmessage / onerror handlers and
 * calling .close() when done.
 * @param {string} jobId
 * @returns {EventSource}
 */
export const createResultStream = (jobId) =>
  new EventSource(`${API_BASE_URL}/stream/${jobId}`);

/**
 * Legacy single-call upload (used by test_backend_api.py and as fallback).
 * Returns all results at once — no streaming.
 * @param {File[]} files
 * @returns {Promise<{results: Array}>}
 */
export const uploadFiles = async (files) => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));

  try {
    const response = await axios.post(`${API_BASE_URL}/process`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: files.length * 5 * 60 * 1000,
    });
    return response.data;
  } catch (error) {
    throw _formatError(error);
  }
};

export const checkHealth = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
    return res.data.status === 'ok';
  } catch {
    return false;
  }
};

function _formatError(error) {
  if (error.response) {
    return new Error(
      error.response.data?.detail || 'Server error occurred during processing.'
    );
  }
  if (error.request) {
    return new Error(
      'Could not connect to the OCR backend. Please check if the server is running.'
    );
  }
  return new Error('An error occurred while preparing the upload.');
}
