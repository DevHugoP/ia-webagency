# backend/database/__init__.py
"""
Module de base de données pour l'application IA-WebAgency.
Ce module gère la connexion et les opérations sur la base de données.
"""

from .db import (
    init_db,
    get_db,
    close_db,
    query_db,
    insert_db
)

__all__ = [
    'init_db',
    'get_db',
    'close_db',
    'query_db',
    'insert_db'
]