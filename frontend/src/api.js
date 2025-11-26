import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file, collection = 'default') => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(
    `${API_URL}/upload?collection=${encodeURIComponent(collection)}`, 
    formData, 
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  
  return response.data;
};

export const queryDocuments = async (query, numResults = 5, collection = 'default') => {
  const response = await api.post('/query', {
    query,
    num_results: numResults,
    collection: collection,
  });
  
  return response.data;
};

export const getCollections = async () => {
  const response = await api.get('/collections');
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export const deleteAllDocuments = async () => {
  const response = await api.delete('/documents');
  return response.data;
};

export const getDocumentsInCollection = async (collectionName) => {
  const response = await api.get(`/collections/${encodeURIComponent(collectionName)}/documents`);
  return response.data;
};

export const getDocumentDetails = async (collectionName, documentId) => {
  const response = await api.get(`/collections/${encodeURIComponent(collectionName)}/documents/${encodeURIComponent(documentId)}`);
  return response.data;
};

export const deleteDocument = async (collectionName, documentId) => {
  const response = await api.delete(`/collections/${encodeURIComponent(collectionName)}/documents/${encodeURIComponent(documentId)}`);
  return response.data;
};

export const deleteCollection = async (collectionName) => {
  const response = await api.delete(`/collections/${encodeURIComponent(collectionName)}`);
  return response.data;
};

export const getChunks = async (collectionName, limit = 100, offset = 0) => {
  const response = await api.get(`/collections/${encodeURIComponent(collectionName)}/chunks`, {
    params: { limit, offset }
  });
  return response.data;
};

export default api;
