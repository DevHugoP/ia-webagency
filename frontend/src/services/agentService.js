import { get, post } from './api';

/**
 * Récupère la liste de tous les agents disponibles
 * @returns {Promise<Array>} Liste des agents avec leurs informations
 */
export const fetchAgents = async () => {
  return get('/agents');
};

/**
 * Envoie un message à un agent spécifique
 * @param {string} agentName Nom de l'agent
 * @param {string} message Message à envoyer
 * @returns {Promise<Object>} Réponse de l'agent
 */
export const sendMessageToAgent = async (agentName, message) => {
  return post(`/agents/${agentName}`, { message });
};

/**
 * Récupère les connaissances spécifiques à un agent
 * @param {string} agentName Nom de l'agent
 * @returns {Promise<Array>} Liste des connaissances de l'agent
 */
export const fetchAgentKnowledge = async (agentName) => {
  return get(`/knowledge?agent=${agentName}`);
};

/**
 * Récupère les détails d'un agent par son nom
 * @param {string} agentName Nom de l'agent
 * @returns {Promise<Object>} Détails de l'agent
 */
export const fetchAgentDetails = async (agentName) => {
  const agents = await fetchAgents();
  return agents.find(agent => agent.name === agentName) || null;
};

// Créer un objet nommé avant de l'exporter
const agentService = {
  fetchAgents,
  sendMessageToAgent,
  fetchAgentKnowledge,
  fetchAgentDetails
};

export default agentService;