import { get } from './api';

// Liste des agents prédéfinis avec des informations par défaut
const DEFAULT_AGENTS = [
  {
    name: 'vision',
    title: 'Stratège Digital',
    description: 'Expert en analyse stratégique et positionnement de marché'
  },
  {
    name: 'pixel',
    title: 'Designer UX/UI',
    description: 'Spécialiste de la conception d\'interfaces utilisateur'
  },
  {
    name: 'arch',
    title: 'Architecte Technique',
    description: 'Expert en architecture logicielle et conception système'
  },
  {
    name: 'script',
    title: 'Développeur Frontend',
    description: 'Spécialiste du développement d\'interfaces web interactives'
  },
  {
    name: 'node',
    title: 'Développeur Backend',
    description: 'Expert en développement de services et d\'APIs'
  },
  {
    name: 'data',
    title: 'Spécialiste Base de Données',
    description: 'Expert en modélisation et optimisation de données'
  },
  {
    name: 'secure',
    title: 'Expert Sécurité',
    description: 'Spécialiste en sécurité et protection des systèmes'
  },
  {
    name: 'test',
    title: 'Testeur QA',
    description: 'Expert en tests et assurance qualité'
  },
  {
    name: 'deploy',
    title: 'DevOps',
    description: 'Spécialiste du déploiement et de l\'infrastructure'
  },
  {
    name: 'pm',
    title: 'Chef de Projet',
    description: 'Expert en gestion de projet et coordination'
  }
];

/**
 * Récupère la liste de tous les agents disponibles
 * @returns {Promise<Array>} Liste des agents avec leurs informations
 */
export const fetchAgents = async () => {
  try {
    // Essayer de récupérer les agents depuis l'API
    const apiAgents = await get('/agents');
    
    // Si l'API retourne des données, les utiliser
    if (Array.isArray(apiAgents) && apiAgents.length > 0) {
      return apiAgents;
    }
    
    // Sinon, utiliser la liste par défaut
    return DEFAULT_AGENTS;
  } catch (error) {
    console.error("Erreur lors de la récupération des agents:", error);
    // En cas d'erreur, retourner la liste par défaut
    return DEFAULT_AGENTS;
  }
};

/**
 * Envoie un message à un agent spécifique
 * @param {string} agentName Nom de l'agent
 * @param {string} message Message à envoyer
 * @returns {Promise<Object>} Réponse de l'agent
 */
export const sendMessageToAgent = async (agentName, message) => {
  return get(`/agents/${agentName}`, { message });
};

/**
 * Récupère les connaissances spécifiques à un agent
 * @param {string} agentName Nom de l'agent
 * @returns {Promise<Array>} Liste des connaissances de l'agent
 */
export const fetchAgentKnowledge = async (agentName) => {
  try {
    const knowledge = await get(`/knowledge/${agentName}`);
    return Array.isArray(knowledge) ? knowledge : [];
  } catch (error) {
    console.error(`Erreur lors du chargement des connaissances de l'agent ${agentName}:`, error);
    return [];
  }
};

/**
 * Récupère les détails d'un agent par son nom
 * @param {string} agentName Nom de l'agent
 * @returns {Promise<Object|null>} Détails de l'agent
 */
export const fetchAgentDetails = async (agentName) => {
  try {
    // Récupérer tous les agents
    const agents = await fetchAgents();
    
    // Trouver l'agent correspondant
    const agent = agents.find(a => a.name === agentName);
    
    return agent || null;
  } catch (error) {
    console.error(`Erreur lors de la récupération des détails de l'agent ${agentName}:`, error);
    return null;
  }
};

// Créer un objet nommé avant de l'exporter
const agentService = {
  fetchAgents,
  sendMessageToAgent,
  fetchAgentKnowledge,
  fetchAgentDetails
};

export default agentService;