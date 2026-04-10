import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const uploadFiles = async (files) => {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  try {
    const response = await axios.post(`${API_BASE_URL}/process`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Server error occurred during processing');
    } else if (error.request) {
      throw new Error('Could not connect to the OCR backend. Please check if the server is running.');
    } else {
      throw new Error('An error occurred while preparing the upload.');
    }
  }
};

export const checkHealth = async () => {
    try {
        const res = await axios.get(`${API_BASE_URL}/health`);
        return res.data.status === 'ok';
    } catch {
        return false;
    }
}
