import { get } from './api';

/**
 * Récupère toutes les catégories de connaissances
 * @returns {Promise<Array>} Liste des catégories
 */
export const fetchKnowledgeCategories = async () => {
  return get('/knowledge');
};

/**
 * Récupère les connaissances d'une catégorie spécifique
 * @param {string} category Nom de la catégorie
 * @returns {Promise<Array>} Liste des éléments de connaissance
 */
export const fetchKnowledgeByCategory = async (category) => {
  return get(`/knowledge/${category}`);
};

/**
 * Récupère les connaissances associées à un agent spécifique
 * @param {string} agentName Nom de l'agent
 * @returns {Promise<Array>} Liste des connaissances de l'agent
 */
export const fetchKnowledgeByAgent = async (agentName) => {
  return get(`/knowledge?agent=${agentName}`);
};

/**
 * Recherche dans la base de connaissances
 * @param {string} query Termes de recherche
 * @returns {Promise<Array>} Résultats de recherche
 */
export const searchKnowledge = async (query) => {
  return get(`/knowledge/search?q=${encodeURIComponent(query)}`);
};

// Créer un objet nommé avant de l'exporter
const knowledgeService = {
  fetchKnowledgeCategories,
  fetchKnowledgeByCategory,
  fetchKnowledgeByAgent,
  searchKnowledge
};

export default knowledgeService;