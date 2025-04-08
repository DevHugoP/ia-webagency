# backend/utils/__init__.py
"""
Utilitaires pour l'application IA-WebAgency.
Ce module contient des fonctions et classes utilitaires utilisées
à travers l'application.
"""

from .file_manager import (
    save_brief,
    get_brief,
    save_deliverable,
    get_deliverable,
    save_feedback,
    get_feedback,
    list_project_files
)

__all__ = [
    'save_brief',
    'get_brief',
    'save_deliverable',
    'get_deliverable',
    'save_feedback',
    'get_feedback',
    'list_project_files'
]