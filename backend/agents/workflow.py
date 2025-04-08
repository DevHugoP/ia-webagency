# backend/agents/workflow.py
"""
Gestionnaire de workflow pour les projets de l'application IA-WebAgency.

Ce module gère le flux de travail séquentiel des projets, coordonnant
les différentes étapes et les interactions entre les agents.
"""

import os
import json
import time
from enum import Enum
import threading
import logging
from datetime import datetime

# Import des configurations
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import WORKFLOW_STEPS
from database.db import get_db, query_db, update_db
from utils.file_manager import save_deliverable, get_brief

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('workflow')


class WorkflowStatus(Enum):
    """États possibles pour un workflow"""
    PENDING = "pending"       # En attente de démarrage
    PROCESSING = "processing" # En cours d'exécution
    COMPLETED = "completed"   # Terminé avec succès
    FAILED = "failed"         # Échoué
    PAUSED = "paused"         # Mis en pause


class WorkflowStep:
    """Représentation d'une étape du workflow"""
    
    def __init__(self, step_config):
        """
        Initialise une étape du workflow.
        
        Args:
            step_config (dict): Configuration de l'étape
        """
        self.id = step_config['id']
        self.agent = step_config['agent']
        self.title = step_config['title']
        self.description = step_config['description']
        self.status = WorkflowStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.result = None
        
    def to_dict(self):
        """
        Convertit l'étape en dictionnaire.
        
        Returns:
            dict: Représentation de l'étape sous forme de dictionnaire
        """
        return {
            'id': self.id,
            'agent': self.agent,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result
        }


class ProjectWorkflow:
    """Gestionnaire de workflow pour un projet"""
    
    def __init__(self, agent_manager, project_name):
        """
        Initialise un workflow de projet.
        
        Args:
            agent_manager (AgentManager): Gestionnaire d'agents
            project_name (str): Nom du projet
        """
        self.agent_manager = agent_manager
        self.project_name = project_name
        self.steps = [WorkflowStep(step) for step in WORKFLOW_STEPS]
        self.status = WorkflowStatus.PENDING
        self.current_step_index = 0
        self.lock = threading.Lock()
        self.thread = None
        
        # Sauvegarde de l'état initial du workflow
        self._save_state()
        
    def start(self):
        """
        Démarre le workflow dans un thread séparé.
        
        Returns:
            bool: True si le workflow a démarré, False sinon
        """
        with self.lock:
            if self.status != WorkflowStatus.PENDING and self.status != WorkflowStatus.PAUSED:
                logger.warning(f"Workflow du projet {self.project_name} déjà démarré ou terminé")
                return False
            
            self.status = WorkflowStatus.PROCESSING
            
            # Mise à jour du statut du projet
            db = get_db()
            db.execute(
                "UPDATE projects SET status = ? WHERE name = ?",
                ("in_progress", self.project_name)
            )
            db.commit()
            
            # Démarrage du thread de workflow
            self.thread = threading.Thread(target=self._run_workflow)
            self.thread.daemon = True
            self.thread.start()
            
            logger.info(f"Workflow du projet {self.project_name} démarré")
            return True
    
    def _run_workflow(self):
        """Exécute le workflow étape par étape"""
        try:
            # Vérifier si on reprend un workflow existant
            if self.current_step_index > 0:
                logger.info(f"Reprise du workflow du projet {self.project_name} à l'étape {self.current_step_index}")
            
            # Exécution des étapes
            while self.current_step_index < len(self.steps):
                with self.lock:
                    # Vérifier si le workflow est en pause
                    if self.status == WorkflowStatus.PAUSED:
                        self._save_state()
                        return
                    
                    current_step = self.steps[self.current_step_index]
                    current_step.status = WorkflowStatus.PROCESSING
                    current_step.started_at = datetime.now()
                
                logger.info(f"Exécution de l'étape {current_step.id} pour le projet {self.project_name}")
                
                # Traitement de l'étape par l'agent approprié
                result = self.agent_manager.process_project_step(
                    self.project_name,
                    current_step.id,
                    current_step.agent
                )
                
                with self.lock:
                    # Mise à jour de l'état de l'étape
                    current_step.completed_at = datetime.now()
                    current_step.result = result
                    
                    if result.get('success', False):
                        current_step.status = WorkflowStatus.COMPLETED
                        logger.info(f"Étape {current_step.id} du projet {self.project_name} terminée avec succès")
                    else:
                        current_step.status = WorkflowStatus.FAILED
                        logger.error(f"Étape {current_step.id} du projet {self.project_name} échouée: {result.get('message')}")
                        # On continue quand même les étapes suivantes
                    
                    # Passage à l'étape suivante
                    self.current_step_index += 1
                    self._save_state()
                
                # Pause entre les étapes pour éviter de surcharger les ressources
                time.sleep(1)
            
            # Toutes les étapes sont terminées
            with self.lock:
                self.status = WorkflowStatus.COMPLETED
                
                # Mise à jour du statut du projet
                db = get_db()
                db.execute(
                    "UPDATE projects SET status = ? WHERE name = ?",
                    ("completed", self.project_name)
                )
                db.commit()
                
                logger.info(f"Workflow du projet {self.project_name} terminé avec succès")
                self._save_state()
        
        except Exception as e:
            # En cas d'erreur non gérée
            with self.lock:
                self.status = WorkflowStatus.FAILED
                
                # Mise à jour du statut du projet
                db = get_db()
                db.execute(
                    "UPDATE projects SET status = ? WHERE name = ?",
                    ("failed", self.project_name)
                )
                db.commit()
                
                logger.error(f"Erreur dans le workflow du projet {self.project_name}: {e}")
                self._save_state()
    
    def pause(self):
        """
        Met le workflow en pause.
        
        Returns:
            bool: True si le workflow a été mis en pause, False sinon
        """
        with self.lock:
            if self.status != WorkflowStatus.PROCESSING:
                logger.warning(f"Impossible de mettre en pause le workflow du projet {self.project_name} (statut: {self.status.value})")
                return False
            
            self.status = WorkflowStatus.PAUSED
            
            # Mise à jour du statut du projet
            db = get_db()
            db.execute(
                "UPDATE projects SET status = ? WHERE name = ?",
                ("paused", self.project_name)
            )
            db.commit()
            
            logger.info(f"Workflow du projet {self.project_name} mis en pause")
            self._save_state()
            return True
    
    def resume(self):
        """
        Reprend un workflow mis en pause.
        
        Returns:
            bool: True si le workflow a repris, False sinon
        """
        return self.start()
    
    def get_status(self):
        """
        Récupère l'état actuel du workflow.
        
        Returns:
            dict: État du workflow
        """
        with self.lock:
            return {
                'project_name': self.project_name,
                'status': self.status.value,
                'current_step': self.current_step_index,
                'total_steps': len(self.steps),
                'steps': [step.to_dict() for step in self.steps]
            }
    
    def _save_state(self):
        """Sauvegarde l'état du workflow"""
        workflow_state = {
            'project_name': self.project_name,
            'status': self.status.value,
            'current_step_index': self.current_step_index,
            'steps': [step.to_dict() for step in self.steps],
            'updated_at': datetime.now().isoformat()
        }
        
        # Créer le dossier de workflow s'il n'existe pas
        workflow_dir = os.path.join('data', 'projects', self.project_name, 'workflow')
        os.makedirs(workflow_dir, exist_ok=True)
        
        # Sauvegarder l'état
        state_path = os.path.join(workflow_dir, 'workflow_state.json')
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_state, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, agent_manager, project_name):
        """
        Charge un workflow existant.
        
        Args:
            agent_manager (AgentManager): Gestionnaire d'agents
            project_name (str): Nom du projet
            
        Returns:
            ProjectWorkflow: Instance du workflow ou None si non trouvé
        """
        state_path = os.path.join('data', 'projects', project_name, 'workflow', 'workflow_state.json')
        
        if not os.path.exists(state_path):
            logger.warning(f"Aucun état de workflow trouvé pour le projet {project_name}")
            return None
        
        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                workflow_state = json.load(f)
            
            # Création d'une nouvelle instance
            workflow = cls(agent_manager, project_name)
            
            # Restauration de l'état
            workflow.status = WorkflowStatus(workflow_state['status'])
            workflow.current_step_index = workflow_state['current_step_index']
            
            # Restauration des étapes
            for i, step_data in enumerate(workflow_state['steps']):
                if i < len(workflow.steps):
                    step = workflow.steps[i]
                    step.status = WorkflowStatus(step_data['status'])
                    step.started_at = datetime.fromisoformat(step_data['started_at']) if step_data['started_at'] else None
                    step.completed_at = datetime.fromisoformat(step_data['completed_at']) if step_data['completed_at'] else None
                    step.result = step_data['result']
            
            logger.info(f"Workflow du projet {project_name} chargé avec succès (statut: {workflow.status.value})")
            return workflow
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement du workflow du projet {project_name}: {e}")
            return None


def get_project_workflow(agent_manager, project_name):
    """
    Récupère ou crée un workflow pour un projet.
    
    Args:
        agent_manager (AgentManager): Gestionnaire d'agents
        project_name (str): Nom du projet
        
    Returns:
        ProjectWorkflow: Instance du workflow
    """
    # Essayer de charger un workflow existant
    workflow = ProjectWorkflow.load(agent_manager, project_name)
    
    # Si aucun workflow n'existe, en créer un nouveau
    if workflow is None:
        workflow = ProjectWorkflow(agent_manager, project_name)
    
    return workflow