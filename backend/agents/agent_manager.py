# backend/agents/agent_manager.py
"""
Gestionnaire des agents IA pour l'application IA-WebAgency.

Ce module fournit les fonctionnalités pour interagir avec les agents IA
via Ollama, gérer leur état et traiter leurs réponses.
"""

import os
import json
import time
import subprocess
import requests
from threading import Lock
from flask import g, current_app
import logging
from datetime import datetime

# Import des configurations
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import OLLAMA_BASE_MODEL, AGENTS, AGENT_TITLES
from database.db import get_db, insert_db, query_db, update_db
from utils.file_manager import save_deliverable, get_brief, get_deliverable, get_feedback

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('agent_manager')

# URL de l'API Ollama
OLLAMA_API_URL = "http://localhost:11434/api"

class AgentManager:
    """
    Gestionnaire des agents IA pour l'application IA-WebAgency.
    Cette classe gère l'interaction avec les agents via l'API Ollama.
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'agents"""
        self.lock = Lock()  # Pour éviter les conflits d'accès concurrents
        self.ensure_agents_exist()
        logger.info("AgentManager initialisé avec succès")
    
    def ensure_agents_exist(self):
        """Vérifie que tous les agents existent dans Ollama, sinon les crée"""
        try:
            # Liste des modèles disponibles
            response = requests.get(f"{OLLAMA_API_URL}/tags")
            if response.status_code != 200:
                logger.error(f"Erreur lors de la récupération des modèles: {response.text}")
                return False
            
            available_models = [model['name'] for model in response.json().get('models', [])]
            
            # Vérifier chaque agent
            for agent in AGENTS:
                if agent not in available_models:
                    logger.warning(f"L'agent {agent} n'existe pas, création en cours...")
                    self.create_agent(agent)
                else:
                    logger.info(f"L'agent {agent} existe déjà")
            
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des agents: {e}")
            return False
    
    def create_agent(self, agent_name):
        """
        Crée un agent Ollama à partir de son modelfile.
        
        Args:
            agent_name (str): Nom de l'agent à créer
        
        Returns:
            bool: True si l'agent a été créé avec succès, False sinon
        """
        try:
            modelfile_path = f"agents/modelfiles/{agent_name}.modelfile"
            
            if not os.path.exists(modelfile_path):
                logger.error(f"Modelfile introuvable pour {agent_name}")
                return False
            
            # Lire le contenu du modelfile
            with open(modelfile_path, 'r') as f:
                modelfile_content = f.read()
            
            # Créer le modèle via l'API
            response = requests.post(
                f"{OLLAMA_API_URL}/create",
                json={
                    "name": agent_name,
                    "modelfile": modelfile_content
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur lors de la création de l'agent {agent_name}: {response.text}")
                return False
            
            logger.info(f"Agent {agent_name} créé avec succès")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'agent {agent_name}: {e}")
            return False
    
    def list_agents(self):
        """
        Liste tous les agents disponibles avec leurs informations.
        
        Returns:
            list: Liste des agents avec leurs métadonnées
        """
        agents_info = []
        
        for agent in AGENTS:
            agents_info.append({
                'name': agent,
                'title': AGENT_TITLES.get(agent, agent.capitalize()),
                'description': self.get_agent_description(agent)
            })
        
        return agents_info
    
    def get_agent_description(self, agent_name):
        """
        Obtient la description d'un agent à partir de son modelfile.
        
        Args:
            agent_name (str): Nom de l'agent
            
        Returns:
            str: Description de l'agent ou description par défaut
        """
        modelfile_path = f"backend/agents/modelfiles/{agent_name}.modelfile"
        
        if not os.path.exists(modelfile_path):
            return "Agent spécialisé"
        
        try:
            with open(modelfile_path, 'r') as f:
                content = f.read()
                
                # Extraire la description à partir du système prompt
                if 'Ton rôle est de ' in content:
                    description = content.split('Ton rôle est de ')[1].split('\n')[0]
                    return description
            
            return "Agent spécialisé"
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la description de l'agent {agent_name}: {e}")
            return "Agent spécialisé"
    
    def ask_agent(self, agent_name, message, temperature=0.7, max_tokens=2000):
        """
        Pose une question à un agent et retourne sa réponse.
        
        Args:
            agent_name (str): Nom de l'agent
            message (str): Question ou instruction pour l'agent
            temperature (float): Température de génération (0.0 - 1.0)
            max_tokens (int): Nombre maximum de tokens à générer
            
        Returns:
            str: Réponse de l'agent ou message d'erreur
        """
        if agent_name not in AGENTS:
            return f"Agent {agent_name} non reconnu"
        
        try:
            # Appel à l'API Ollama
            with self.lock:  # Assurer un accès séquentiel pour éviter les conflits
                response = requests.post(
                    f"{OLLAMA_API_URL}/generate",
                    json={
                        "model": agent_name,
                        "prompt": message,
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "stream": False
                    }
                )
            
            if response.status_code != 200:
                logger.error(f"Erreur lors de l'appel à l'agent {agent_name}: {response.text}")
                return f"Erreur de communication avec l'agent: {response.text}"
            
            # Extraction de la réponse
            response_data = response.json()
            agent_response = response_data.get('response', "Pas de réponse de l'agent")
            
            # Stocker la réponse dans la base de connaissances
            self.store_agent_response(agent_name, message, agent_response)
            
            return agent_response
        
        except Exception as e:
            logger.error(f"Erreur lors de l'interaction avec l'agent {agent_name}: {e}")
            return f"Erreur: {str(e)}"
    
    def store_agent_response(self, agent_name, query, response, category="Général", project_id=None):
        """
        Stocke une réponse d'agent dans la base de connaissances.
        
        Args:
            agent_name (str): Nom de l'agent
            query (str): Question posée
            response (str): Réponse de l'agent
            category (str): Catégorie de la connaissance
            project_id (int, optional): ID du projet associé
        
        Returns:
            int: ID de l'entrée de connaissance créée
        """
        try:
            db = get_db()
            
            # Insertion dans la base de données
            cursor = db.execute(
                """
                INSERT INTO knowledge 
                (agent, category, query, content, project_id) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (agent_name, category, query, response, project_id)
            )
            
            knowledge_id = cursor.lastrowid
            db.commit()
            
            logger.info(f"Réponse de l'agent {agent_name} stockée avec l'ID {knowledge_id}")
            return knowledge_id
        
        except Exception as e:
            logger.error(f"Erreur lors du stockage de la réponse de l'agent {agent_name}: {e}")
            return None
    
    def process_project_step(self, project_name, step_id, agent_name, context=None):
        """
        Traite une étape du workflow d'un projet.
        
        Args:
            project_name (str): Nom du projet
            step_id (str): ID de l'étape (ex: "01_brief_strategique")
            agent_name (str): Nom de l'agent à utiliser
            context (dict, optional): Contexte supplémentaire pour l'agent
            
        Returns:
            dict: Résultat du traitement de l'étape
        """
        # Récupérer les informations du projet
        db = get_db()
        project = query_db("SELECT * FROM projects WHERE name = ?", (project_name,), one=True)
        
        if not project:
            logger.error(f"Projet {project_name} non trouvé")
            return {
                "success": False,
                "message": f"Projet {project_name} non trouvé"
            }
        
        project_id = project['id']
        
        # Enregistrer le début de l'étape
        interaction_id = insert_db(
            """
            INSERT INTO interactions 
            (project_id, agent, step_id, status) 
            VALUES (?, ?, ?, ?)
            """,
            (project_id, agent_name, step_id, 'processing')
        )
        
        try:
            # Préparer le prompt pour l'agent
            prompt = self.prepare_step_prompt(project_name, step_id, agent_name, context)
            
            # Obtenir la réponse de l'agent
            agent_response = self.ask_agent(agent_name, prompt)
            
            # Sauvegarder le livrable
            deliverable_path = save_deliverable(
                project_name, 
                step_id, 
                agent_response, 
                agent=agent_name
            )
            
            # Mettre à jour l'état de l'interaction
            update_db(
                """
                UPDATE interactions 
                SET status = ?, content = ?, completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                """,
                ('completed', agent_response, interaction_id)
            )
            
            logger.info(f"Étape {step_id} du projet {project_name} complétée par l'agent {agent_name}")
            
            return {
                "success": True,
                "deliverable_path": deliverable_path,
                "step_id": step_id,
                "agent": agent_name
            }
            
        except Exception as e:
            # Mettre à jour l'état de l'interaction en cas d'erreur
            update_db(
                """
                UPDATE interactions 
                SET status = ?, content = ?, completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                """,
                ('failed', str(e), interaction_id)
            )
            
            logger.error(f"Erreur lors du traitement de l'étape {step_id} du projet {project_name}: {e}")
            
            return {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "step_id": step_id,
                "agent": agent_name
            }
    
    def prepare_step_prompt(self, project_name, step_id, agent_name, context=None):
        """
        Prépare le prompt pour une étape spécifique.
        
        Args:
            project_name (str): Nom du projet
            step_id (str): ID de l'étape
            agent_name (str): Nom de l'agent
            context (dict, optional): Contexte supplémentaire
            
        Returns:
            str: Prompt formaté pour l'agent
        """
        # Récupérer le brief du projet
        brief = get_brief(project_name)
        
        if not brief:
            logger.error(f"Brief du projet {project_name} non trouvé")
            brief = f"Projet: {project_name}"
        
        # Récupérer les livrables précédents si nécessaire
        previous_deliverables = []
        
        # Charger les livrables précédents en fonction de l'étape actuelle
        step_number = int(step_id.split('_')[0])
        for i in range(1, step_number):
            prev_step_id = f"{i:02d}_" + self.get_step_name_by_number(i)
            prev_content = get_deliverable(project_name, prev_step_id)
            
            if prev_content:
                prev_agent = self.get_agent_by_step_number(i)
                previous_deliverables.append({
                    "step_id": prev_step_id,
                    "agent": prev_agent,
                    "content": prev_content
                })
        
        # Récupérer les feedbacks précédents si disponibles
        feedback = get_feedback(project_name, step_id)
        
        # Construction du prompt
        prompt = f"""
# Projet: {project_name}

## Brief du projet
{brief}

"""
        
        # Ajouter les livrables précédents
        if previous_deliverables:
            prompt += "## Livrables précédents\n\n"
            
            for deliverable in previous_deliverables:
                prompt += f"### {deliverable['step_id']} (par {AGENT_TITLES.get(deliverable['agent'], deliverable['agent'])})\n"
                prompt += f"{deliverable['content'][:500]}...\n\n"
        
        # Ajouter le feedback s'il existe
        if feedback:
            prompt += f"""
## Feedback précédent sur ce livrable
{feedback}

"""
        
        # Ajouter des instructions pour l'étape
        prompt += f"""
## Ta mission
Tu es {AGENT_TITLES.get(agent_name, agent_name)} sur ce projet.
Ta tâche est de produire le livrable '{step_id}'.

Fournis un livrable de qualité professionnelle, avec une structure claire et détaillée.
"""
        
        # Ajouter du contexte spécifique si fourni
        if context:
            prompt += f"""
## Contexte supplémentaire
{context.get('instructions', '')}
"""
        
        return prompt
    
    def get_step_name_by_number(self, step_number):
        """
        Obtient le nom d'une étape par son numéro.
        
        Args:
            step_number (int): Numéro de l'étape
            
        Returns:
            str: Nom de l'étape
        """
        step_mapping = {
            1: "brief_strategique",
            2: "design_ux",
            3: "architecture",
            4: "planning",
            5: "frontend",
            6: "backend",
            7: "database",
            8: "securite",
            9: "tests",
            10: "deploiement"
        }
        
        return step_mapping.get(step_number, f"etape_{step_number}")
    
    def get_agent_by_step_number(self, step_number):
        """
        Obtient le nom de l'agent associé à une étape par son numéro.
        
        Args:
            step_number (int): Numéro de l'étape
            
        Returns:
            str: Nom de l'agent
        """
        agent_mapping = {
            1: "vision",
            2: "pixel",
            3: "arch",
            4: "pm",
            5: "script",
            6: "node",
            7: "data",
            8: "secure",
            9: "test",
            10: "deploy"
        }
        
        return agent_mapping.get(step_number, "pm")
    
    def process_feedback(self, project_name, deliverable_id, feedback_content, agent_name):
        """
        Traite un feedback sur un livrable.
        
        Args:
            project_name (str): Nom du projet
            deliverable_id (str): ID du livrable
            feedback_content (str): Contenu du feedback
            agent_name (str): Nom de l'agent associé au livrable
            
        Returns:
            dict: Résultat du traitement du feedback
        """
        # Sauvegarder le feedback
        from utils.file_manager import save_feedback
        feedback_path = save_feedback(project_name, deliverable_id, feedback_content)
        
        # Obtenir les détails du projet
        db = get_db()
        project = query_db("SELECT * FROM projects WHERE name = ?", (project_name,), one=True)
        
        if not project:
            logger.error(f"Projet {project_name} non trouvé")
            return {
                "success": False,
                "message": f"Projet {project_name} non trouvé"
            }
        
        project_id = project['id']
        
        # Enregistrer le feedback dans la base de données
        step_id = deliverable_id
        if step_id.endswith('.md'):
            step_id = step_id[:-3]
            
        feedback_id = insert_db(
            """
            INSERT INTO feedback 
            (project_id, step_id, feedback, status) 
            VALUES (?, ?, ?, ?)
            """,
            (project_id, step_id, feedback_content, 'pending')
        )
        
        # Dans une vraie application, on pourrait ici lancer une tâche asynchrone
        # pour faire traiter le feedback par l'agent et générer une nouvelle version
        
        logger.info(f"Feedback pour {deliverable_id} du projet {project_name} enregistré")
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "feedback_path": feedback_path
        }


# Singleton pour le gestionnaire d'agents
_agent_manager_instance = None
_agent_manager_lock = Lock()

def get_agent_manager():
    """
    Retourne l'instance unique du gestionnaire d'agents.
    
    Returns:
        AgentManager: Instance du gestionnaire d'agents
    """
    global _agent_manager_instance
    
    with _agent_manager_lock:
        if _agent_manager_instance is None:
            _agent_manager_instance = AgentManager()
        
        return _agent_manager_instance