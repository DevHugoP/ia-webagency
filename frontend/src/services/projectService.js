import { get, post } from './api';
// put et del sont importés mais pas utilisés pour le moment
// Nous les gardons pour une utilisation future et désactivons l'avertissement ESLint
// eslint-disable-next-line no-unused-vars
import { put, del } from './api';

/**
 * Récupère tous les projets
 * @returns {Promise<Array>} Liste des projets
 */
export const fetchProjects = async () => {
  return get('/projects');
};

/**
 * Récupère un projet par son ID
 * @param {number} projectId ID du projet
 * @returns {Promise<Object>} Détails du projet
 */
export const fetchProjectById = async (projectId) => {
  return get(`/projects/${projectId}`);
};

/**
 * Crée un nouveau projet
 * @param {Object} projectData Données du projet à créer
 * @returns {Promise<Object>} Projet créé
 */
export const createProject = async (projectData) => {
  return post('/projects', projectData);
};

/**
 * Démarre le workflow d'un projet
 * @param {number} projectId ID du projet
 * @returns {Promise<Object>} Statut du workflow
 */
export const startProjectWorkflow = async (projectId) => {
  return post(`/projects/${projectId}/start`, {});
};

/**
 * Récupère un livrable spécifique d'un projet
 * @param {number} projectId ID du projet
 * @param {string} deliverableName Nom du livrable
 * @returns {Promise<Object>} Contenu du livrable
 */
export const fetchDeliverable = async (projectId, deliverableName) => {
  return get(`/projects/${projectId}/deliverables/${deliverableName}`);
};

/**
 * Envoie un feedback sur un livrable
 * @param {number} projectId ID du projet
 * @param {string} deliverable Nom du livrable
 * @param {string} feedback Contenu du feedback
 * @returns {Promise<Object>} Statut du feedback
 */
export const submitFeedback = async (projectId, deliverable, feedback) => {
  return post(`/projects/${projectId}/feedback`, { deliverable, feedback });
};

/**
 * Récupère l'état du workflow d'un projet
 * @param {number} projectId ID du projet
 * @returns {Promise<Object>} État du workflow
 */
export const fetchWorkflowStatus = async (projectId) => {
  return get(`/projects/${projectId}/workflow`);
};

/**
 * Archive un projet
 * @param {number} projectId ID du projet
 * @returns {Promise<Object>} Statut de l'archivage
 */
export const archiveProject = async (projectId) => {
  return post(`/projects/${projectId}/archive`, {});
};

// Créer un objet nommé avant de l'exporter
const projectService = {
  fetchProjects,
  fetchProjectById,
  createProject,
  startProjectWorkflow,
  fetchDeliverable,
  submitFeedback,
  fetchWorkflowStatus,
  archiveProject
};

export default projectService;