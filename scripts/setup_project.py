# scripts/setup_project.py
import os
import subprocess
import sys
import sqlite3

def check_ollama():
    try:
        # Vérifier si Ollama est installé
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        print(f"✅ Ollama détecté : {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la vérification d'Ollama: {e}")
        return False

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

def seed_knowledge():
    try:
        basic_knowledge = [
            {
                "agent": "vision",
                "category": "Méthodologie",
                "content": "Le Design Thinking se déroule en 5 phases: Empathie, Définition, Idéation, Prototypage, Test. Cette approche centrée utilisateur permet de résoudre des problèmes complexes en se concentrant sur les besoins réels des utilisateurs."
            },
            # Ajoutez les autres entrées de connaissances ici (comme dans votre script original)
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
            list_result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            
            if agent in list_result.stdout:
                print(f"  ➡️ L'agent {agent} existe déjà")
                continue
            
            # Créer l'agent avec le Modelfile
            with open(modelfile_path, 'r') as f:
                modelfile_content = f.read()
                print(f"Contenu du modelfile :\n{modelfile_content}")
            
            create_result = subprocess.run(
                ["ollama", "create", agent, "-f", modelfile_path],
                capture_output=True,
                text=True
            )
            
            if create_result.returncode == 0:
                print(f"✅ Agent {agent} créé avec succès")
                print(create_result.stdout)
            else:
                print(f"❌ Erreur lors de la création de l'agent {agent}")
                print(f"Sortie standard: {create_result.stdout}")
                print(f"Sortie d'erreur: {create_result.stderr}")
                success = False
        
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'agent {agent}: {e}")
            success = False
    
    return success

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