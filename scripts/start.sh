cat > scripts/start.sh << 'EOF'
#!/bin/bash
# scripts/start.sh

# Arrêter le script en cas d'erreur
set -e

echo "=== Démarrage de l'agence web IA ==="

# Vérifier si Ollama est installé
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama n'est pas installé. Veuillez l'installer depuis https://ollama.ai"
    exit 1
fi

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé."
    exit 1
fi

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé."
    exit 1
fi

# Vérifier si npm est installé
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé."
    exit 1
fi

# Vérifier que Ollama est en cours d'exécution
if ! ollama list &> /dev/null; then
    echo "⚠️ Ollama ne semble pas être en cours d'exécution."
    echo "Démarrage d'Ollama..."
    ollama serve &
    # Attendre que le service démarre
    sleep 5
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source venv/bin/activate

# Configurer le projet
echo "Configuration du projet..."
python3 scripts/setup_project.py

# Installer les dépendances npm pour le frontend
echo "Installation des dépendances frontend..."
cd frontend && npm install && cd ..

# Démarrer le backend et le frontend dans des terminaux séparés
echo "Démarrage des services..."

# Fonction pour arrêter tous les processus à la sortie
function cleanup {
    echo "Arrêt des services..."
    kill $(jobs -p) 2>/dev/null
}

# Enregistrer la fonction de nettoyage pour s'exécuter à la sortie
trap cleanup EXIT

# Démarrer le backend
echo "Démarrage du backend..."
cd backend && python3 app.py &
BACKEND_PID=$!

# Attendre que le backend démarre
sleep 3

# Démarrer le frontend
echo "Démarrage du frontend..."
cd frontend && npm start &
FRONTEND_PID=$!

echo "✅ Services démarrés avec succès!"
echo "📋 Interface web: http://localhost:3000"
echo "🚀 API: http://localhost:5001"
echo "Appuyez sur Ctrl+C pour arrêter tous les services."

# Attendre que l'utilisateur appuie sur Ctrl+C
wait $BACKEND_PID $FRONTEND_PID
EOF