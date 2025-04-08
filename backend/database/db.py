# backend/database/db.py
"""
Gestionnaire de base de données pour l'application IA-WebAgency.

Ce module fournit des fonctions pour initialiser et interagir avec la base 
de données SQLite de l'application.
"""

import sqlite3
import os
from flask import g, current_app
from pathlib import Path
import sys
import json
from datetime import datetime

# Chemin vers la base de données
import sys
import os

# Ajout du répertoire parent au chemin de recherche Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE, DB_DIR


def get_db():
    """
    Récupère la connexion à la base de données pour la requête en cours.
    
    Returns:
        sqlite3.Connection: Connexion à la base de données
    """
    if 'db' not in g:
        # Assurer que le répertoire de la base de données existe
        os.makedirs(DB_DIR, exist_ok=True)
        
        # Créer la connexion à la base de données
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Configurer la connexion pour retourner des lignes en tant que dictionnaires
        g.db.row_factory = sqlite3.Row
    
    return g.db


def close_db(e=None):
    """
    Ferme la connexion à la base de données.
    
    Args:
        e: Exception qui a déclenché la fermeture (inutilisé)
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()


def init_db():
    """
    Initialise la base de données en créant les tables nécessaires.
    """
    # Assurer que le répertoire de la base de données existe
    os.makedirs(DB_DIR, exist_ok=True)
    
    db = get_db()
    
    try:
        # Création des tables
        db.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            status TEXT DEFAULT 'created',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        db.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            category TEXT NOT NULL,
            query TEXT,
            content TEXT NOT NULL,
            project_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        ''')
        
        db.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            agent TEXT NOT NULL,
            step_id TEXT NOT NULL,
            content TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        ''')
        
        db.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            step_id TEXT NOT NULL,
            feedback TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        ''')
        
        # Commit des changements
        db.commit()
        
        # Vérifier si la base de connaissances est vide, si oui, l'initialiser avec des données de base
        if db.execute('SELECT COUNT(*) FROM knowledge').fetchone()[0] == 0:
            seed_knowledge(db)
        
    except sqlite3.Error as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}", file=sys.stderr)
        # Rollback en cas d'erreur
        db.rollback()
        raise


def seed_knowledge(db):
    """
    Remplit la base de connaissances avec des données initiales.
    
    Args:
        db (sqlite3.Connection): Connexion à la base de données
    """
    basic_knowledge = [
        {
            "agent": "vision",
            "category": "Méthodologie",
            "content": "Le Design Thinking se déroule en 5 phases: Empathie, Définition, Idéation, Prototypage, Test. Cette approche centrée utilisateur permet de résoudre des problèmes complexes en se concentrant sur les besoins réels des utilisateurs."
        },
        {
            "agent": "pixel",
            "category": "Principes UI",
            "content": "Les 10 heuristiques de Nielsen sont des principes fondamentaux pour la conception d'interfaces: visibilité de l'état du système, correspondance avec le monde réel, contrôle et liberté utilisateur, cohérence et standards, prévention des erreurs, reconnaissance plutôt que rappel, flexibilité et efficacité, esthétique et design minimaliste, aide à la reconnaissance et récupération d'erreurs, aide et documentation."
        },
        {
            "agent": "arch",
            "category": "Patterns",
            "content": "Le pattern MVC (Model-View-Controller) sépare une application en trois composants interconnectés: le modèle (données), la vue (interface utilisateur) et le contrôleur (logique de l'application). Cette séparation permet une meilleure organisation du code et facilite la maintenance et l'évolution."
        },
        {
            "agent": "script",
            "category": "Frameworks",
            "content": "React est une bibliothèque JavaScript pour construire des interfaces utilisateur. Ses principes clés sont: le Virtual DOM pour des mises à jour efficaces, les composants réutilisables, le flux de données unidirectionnel et l'état (state) pour gérer les données dynamiques."
        },
        {
            "agent": "node",
            "category": "API REST",
            "content": "Les principes RESTful incluent: interface uniforme, sans état, mise en cache, architecture client-serveur, système en couches et code à la demande. Les endpoints API doivent suivre des conventions de nommage cohérentes et utiliser les verbes HTTP appropriés (GET, POST, PUT, DELETE)."
        },
        {
            "agent": "data",
            "category": "Optimisation",
            "content": "L'indexation de base de données améliore les performances des requêtes en permettant au moteur de base de données de trouver rapidement les données sans scanner toutes les lignes. Un index doit être créé sur les colonnes fréquemment utilisées dans les clauses WHERE, JOIN et ORDER BY."
        },
        {
            "agent": "secure",
            "category": "OWASP",
            "content": "Le Top 10 OWASP inclut: injection, authentification brisée, exposition de données sensibles, entités XML externes, contrôle d'accès défaillant, mauvaise configuration de sécurité, cross-site scripting (XSS), désérialisation non sécurisée, utilisation de composants vulnérables, et journalisation/surveillance insuffisante."
        },
        {
            "agent": "test",
            "category": "Méthodes",
            "content": "La pyramide de tests recommande une répartition optimale entre différents types de tests: nombreux tests unitaires à la base, tests d'intégration au milieu, et tests end-to-end au sommet. Cette approche offre un bon équilibre entre vitesse d'exécution, couverture et fiabilité."
        },
        {
            "agent": "deploy",
            "category": "CI/CD",
            "content": "L'intégration continue (CI) consiste à automatiser l'intégration des changements de code de plusieurs contributeurs dans un référentiel partagé. Le déploiement continu (CD) automatise la livraison d'applications dans les environnements de production."
        },
        {
            "agent": "pm",
            "category": "Agile",
            "content": "La méthodologie Scrum organise le travail en sprints (itérations de 2-4 semaines) avec des rôles clés (Product Owner, Scrum Master, équipe de développement) et des événements réguliers (planification de sprint, mêlées quotidiennes, revue de sprint, rétrospective)."
        }
    ]
    
    try:
        for item in basic_knowledge:
            db.execute(
                "INSERT INTO knowledge (agent, category, content) VALUES (?, ?, ?)",
                (item["agent"], item["category"], item["content"])
            )
        
        db.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'initialisation des connaissances: {e}", file=sys.stderr)
        db.rollback()


def query_db(query, args=(), one=False):
    """
    Exécute une requête SELECT sur la base de données.
    
    Args:
        query (str): Requête SQL
        args (tuple): Arguments pour la requête
        one (bool): Si True, retourne seulement le premier résultat
        
    Returns:
        list or dict: Résultats de la requête
    """
    db = get_db()
    cursor = db.execute(query, args)
    
    rv = cursor.fetchall()
    cursor.close()
    
    return (rv[0] if rv else None) if one else rv


def insert_db(query, args=()):
    """
    Exécute une requête d'insertion sur la base de données.
    
    Args:
        query (str): Requête SQL d'insertion
        args (tuple): Arguments pour la requête
        
    Returns:
        int: ID de la ligne insérée
    """
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    
    return cursor.lastrowid


def update_db(query, args=()):
    """
    Exécute une requête de mise à jour sur la base de données.
    
    Args:
        query (str): Requête SQL de mise à jour
        args (tuple): Arguments pour la requête
        
    Returns:
        int: Nombre de lignes affectées
    """
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    
    return cursor.rowcount


def delete_db(query, args=()):
    """
    Exécute une requête de suppression sur la base de données.
    
    Args:
        query (str): Requête SQL de suppression
        args (tuple): Arguments pour la requête
        
    Returns:
        int: Nombre de lignes supprimées
    """
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    
    return cursor.rowcount


def backup_db():
    """
    Crée une sauvegarde de la base de données.
    
    Returns:
        str: Chemin du fichier de sauvegarde
    """
    # Créer un nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(DB_DIR) / f"agency_backup_{timestamp}.db"
    
    # Ouvrir la connexion source
    source = sqlite3.connect(DATABASE)
    
    # Créer la sauvegarde
    backup = sqlite3.connect(str(backup_path))
    source.backup(backup)
    
    # Fermer les connexions
    backup.close()
    source.close()
    
    return str(backup_path)