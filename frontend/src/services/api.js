import axios from 'axios';

// Configuration de l'URL de base de l'API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

// Instance Axios configurée
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Gérer les différents types d'erreurs
    const errorMessage = error.response?.data?.error || 
                         error.message || 
                         'Une erreur inconnue est survenue';
                         
    console.error('API Error:', errorMessage);
    return Promise.reject(errorMessage);
  }
);

// Fonctions génériques pour les appels API
export const get = async (url) => {
  return api.get(url);
};

export const post = async (url, data) => {
  return api.post(url, data);
};

export const put = async (url, data) => {
  return api.put(url, data);
};

export const del = async (url) => {
  return api.delete(url);
};

export default api;