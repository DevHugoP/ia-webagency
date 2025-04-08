# backend/config.py
import os

# Chemins des dossiers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_DIR = os.path.join(DATA_DIR, 'db')
PROJECTS_DIR = os.path.join(DATA_DIR, 'projects')
KNOWLEDGE_DIR = os.path.join(DATA_DIR, 'knowledge')

# Chemin de la base de données
DATABASE = os.path.join(DB_DIR, 'agency.db')

# Configuration de l'API
API_PREFIX = '/api'
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Configuration des agents
OLLAMA_BASE_MODEL = "llama3:8b"
AGENTS = [
    'vision', 'pixel', 'arch', 'script', 'node', 
    'data', 'secure', 'test', 'deploy', 'pm'
]

AGENT_TITLES = {
    'vision': 'Stratège Digital',
    'pixel': 'Designer UX/UI',
    'arch': 'Architecte Technique',
    'script': 'Développeur Frontend',
    'node': 'Développeur Backend',
    'data': 'Spécialiste BDD',
    'secure': 'Expert Sécurité',
    'test': 'Testeur QA',
    'deploy': 'DevOps',
    'pm': 'Chef de Projet'
}

# Mapping des étapes du workflow
WORKFLOW_STEPS = [
    {
        'id': '01_brief_strategique',
        'agent': 'vision',
        'title': 'Brief stratégique',
        'description': 'Analyse stratégique du projet'
    },
    {
        'id': '02_design_ux',
        'agent': 'pixel',
        'title': 'Design UX/UI',
        'description': 'Conception des wireframes et du design'
    },
    {
        'id': '03_architecture',
        'agent': 'arch',
        'title': 'Architecture technique',
        'description': 'Définition de l\'architecture technique'
    },
    {
        'id': '04_planning',
        'agent': 'pm',
        'title': 'Planning de projet',
        'description': 'Planification détaillée du projet'
    },
    {
        'id': '05_frontend',
        'agent': 'script',
        'title': 'Développement Frontend',
        'description': 'Implémentation de l\'interface utilisateur'
    },
    {
        'id': '06_backend',
        'agent': 'node',
        'title': 'Développement Backend',
        'description': 'Développement des API et services'
    },
    {
        'id': '07_database',
        'agent': 'data',
        'title': 'Base de données',
        'description': 'Conception de la base de données'
    },
    {
        'id': '08_securite',
        'agent': 'secure',
        'title': 'Audit de sécurité',
        'description': 'Analyse et recommandations de sécurité'
    },
    {
        'id': '09_tests',
        'agent': 'test',
        'title': 'Plan de tests',
        'description': 'Stratégie et scénarios de test'
    },
    {
        'id': '10_deploiement',
        'agent': 'deploy',
        'title': 'Plan de déploiement',
        'description': 'Stratégie de déploiement et configuration'
    }
]

# Configuration du frontend (pour CORS)
FRONTEND_URL = 'http://localhost:3000'

# Fonction pour créer les dossiers nécessaires
def ensure_directories():
    """Crée les dossiers nécessaires s'ils n'existent pas"""
    for directory in [DATA_DIR, DB_DIR, PROJECTS_DIR, KNOWLEDGE_DIR]:
        os.makedirs(directory, exist_ok=True)