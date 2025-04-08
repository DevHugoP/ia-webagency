# scripts/setup_project.py
import os
import subprocess
import sqlite3
import json
import sys

# Vérifier si Ollama est installé
def check_ollama():
    try:
        result = subprocess.run(["ollama", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama détecté: {result.stdout.strip()}")
            return True
        else:
            print("❌ Erreur lors de la vérification d'Ollama")
            return False
    except FileNotFoundError:
        print("❌ Ollama n'est pas installé. Veuillez l'installer depuis https://ollama.ai")
        return False

# Initialisation de la base de données
def init_database():
    try:
        os.makedirs('data/db', exist_ok=True)
        db_path = 'data/db/agency.db'
        
        with sqlite3.connect(db_path) as db:
            # Table des projets
            db.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Table de la base de connaissances
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
            
            # Table des interactions agent-projet
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
            
            # Table des feedback
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
            
            db.commit()
        
        print("✅ Base de données initialisée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        return False

# Création des agents dans Ollama
def setup_agents():
    agents = [
        'vision', 'pixel', 'arch', 'script', 'node', 
        'data', 'secure', 'test', 'deploy', 'pm'
    ]
    
    success = True
    for agent in agents:
        modelfile_path = f"backend/agents/modelfiles/{agent}.modelfile"
        
        if not os.path.exists(modelfile_path):
            print(f"❌ Modelfile manquant pour {agent}")
            success = False
            continue
        
        try:
            print(f"🔄 Création de l'agent {agent}...")
            # Vérifier si l'agent existe déjà
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            
            if agent in result.stdout:
                print(f"  ➡️ L'agent {agent} existe déjà, mise à jour...")
                subprocess.run(["ollama", "rm", agent], check=True)
            
            # Créer l'agent avec le Modelfile
            result = subprocess.run(
                ["ollama", "create", agent, "-f", modelfile_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Agent {agent} créé avec succès")
            else:
                print(f"❌ Erreur lors de la création de l'agent {agent}: {result.stderr}")
                success = False
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de la création de l'agent {agent}: {e}")
            success = False
    
    return success

# Création des dossiers de projet
def create_folders():
    folders = [
        'data/projects',
        'data/knowledge',
        'data/db'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    print("✅ Structure de dossiers créée")
    return True

# Pré-remplissage de la base de connaissances
def seed_knowledge():
    try:
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
        
        conn = sqlite3.connect('data/db/agency.db')
        cursor = conn.cursor()
        
        for item in basic_knowledge:
            cursor.execute(
                "INSERT INTO knowledge (agent, category, content) VALUES (?, ?, ?)",
                (item["agent"], item["category"], item["content"])
            )
        
        conn.commit()
        conn.close()
        
        print("✅ Base de connaissances initialisée avec des données de base")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de connaissances: {e}")
        return False

# Script principal
def main():
    print("\n=== Configuration de l'Agence Web IA ===\n")
    
    # Vérifier Ollama
    if not check_ollama():
        print("\n❌ Configuration échouée: Ollama est requis")
        sys.exit(1)
    
    # Créer les dossiers
    create_folders()
    
    # Initialiser la base de données
    if not init_database():
        print("\n❌ Configuration échouée: Erreur d'initialisation de la base de données")
        sys.exit(1)
    
    # Pré-remplir la base de connaissances
    seed_knowledge()
    
    # Configurer les agents
    if not setup_agents():
        print("\n⚠️ Certains agents n'ont pas pu être configurés. Vérifiez les erreurs ci-dessus.")
    
    print("\n✅ Configuration terminée! L'agence IA est prête à l'emploi.")
    print("\nPour démarrer l'application:")
    print("1. Lancez le backend: cd backend && python app.py")
    print("2. Lancez le frontend: cd frontend && npm start")

if __name__ == "__main__":
    main()