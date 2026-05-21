const API_BASE_URL = (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL) || (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'http://localhost:8000';

async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || response.statusText);
  }
  return response.json();
}

export const api = {
  // Datasets
  getDatasets: () => fetch(`${API_BASE_URL}/api/datasets`).then(handleResponse),
  getDataset: (id) => fetch(`${API_BASE_URL}/api/datasets/${id}`).then(handleResponse),

  // Upload
  uploadDataset: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    }).then(handleResponse);
  },

  // Preprocessing
  preprocess: (datasetId, params = {}) =>
    fetch(`${API_BASE_URL}/api/preprocess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset_id: datasetId, ...params }),
    }).then(handleResponse),

  // TDA Computation
  computeTDA: (patchId, params = {}) =>
    fetch(`${API_BASE_URL}/api/compute-tda`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: patchId, ...params }),
    }).then(handleResponse),

  // Results
  getResults: (jobId) => fetch(`${API_BASE_URL}/api/results/${jobId}`).then(handleResponse),

  // Demo
  runDemo: () =>
    fetch(`${API_BASE_URL}/api/demo`, {
      method: 'POST',
    }).then(handleResponse),

  // Resources
  getResources: (type) => fetch(`${API_BASE_URL}/api/resources/${type}`).then(handleResponse),
  getResourceContent: (type, path) => fetch(`${API_BASE_URL}/api/resources/${type}/${encodeURIComponent(path)}`).then(handleResponse),
  
  // Export
  exportResults: (jobId) => fetch(`${API_BASE_URL}/api/export/${jobId}`).then(handleResponse),
};
