# backend/agents/__init__.py
"""
Module de gestion des agents IA pour l'application IA-WebAgency.
Ce module gère les interactions avec les agents et le workflow des projets.
"""

from .agent_manager import (
    AgentManager,
    get_agent_manager
)

from .workflow import (
    ProjectWorkflow,
    WorkflowStep,
    WorkflowStatus
)

__all__ = [
    'AgentManager',
    'get_agent_manager',
    'ProjectWorkflow',
    'WorkflowStep',
    'WorkflowStatus'
]