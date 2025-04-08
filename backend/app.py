# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import sys

# Ajouter le répertoire courant au chemin de recherche Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import des modules de l'application
from database.db import init_db, get_db
import config
import sqlite3

# Initialisation de l'application
app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin pour le développement

# S'assurer que les dossiers nécessaires existent
os.makedirs('data/db', exist_ok=True)
os.makedirs('data/projects', exist_ok=True)
os.makedirs('data/knowledge', exist_ok=True)

# Initialiser la base de données dans le contexte de l'application
with app.app_context():
    init_db()

# Import des modules qui utilisent la base de données (après initialisation)
from agents.agent_manager import AgentManager, get_agent_manager
from agents.workflow import ProjectWorkflow, get_project_workflow
from utils.file_manager import save_brief, get_deliverable, save_feedback, get_brief

# Initialiser le gestionnaire d'agents
with app.app_context():
    agent_manager = get_agent_manager()

# Routes pour les projets
@app.route('/api/projects', methods=['GET'])
def get_projects():
    db = get_db()
    projects = db.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    return jsonify([{
        'id': project['id'],
        'name': project['name'],
        'description': project['description'],
        'status': project['status'],
        'created_at': project['created_at']
    } for project in projects])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    objectives = data.get('objectives')
    target_audience = data.get('target_audience')
    constraints = data.get('constraints')
    deadline = data.get('deadline')
    
    if not name or not description:
        return jsonify({'error': 'Name and description are required'}), 400
    
    # Créer le brief complet
    brief = f"""
    # Brief de projet : {name}
    
    ## Description
    {description}
    
    ## Objectifs
    {objectives}
    
    ## Public cible
    {target_audience}
    
    ## Contraintes
    {constraints}
    
    ## Délai
    {deadline}
    """
    
    # Sauvegarder le brief dans un fichier
    save_brief(name, brief)
    
    # Ajouter le projet à la base de données
    db = get_db()
    cursor = db.execute(
        'INSERT INTO projects (name, description, status) VALUES (?, ?, ?)',
        (name, description, 'created')
    )
    project_id = cursor.lastrowid
    db.commit()
    
    return jsonify({
        'id': project_id,
        'name': name,
        'description': description,
        'status': 'created'
    }), 201

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    db = get_db()
    project = db.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Récupérer les livrables du projet
    deliverables = []
    project_dir = f"data/projects/{project['name']}/deliverables"
    if os.path.exists(project_dir):
        for file in os.listdir(project_dir):
            if file.endswith('.md'):
                deliverables.append({
                    'name': file,
                    'type': file.split('_')[0] if '_' in file else 'other',
                    'has_feedback': os.path.exists(f"data/projects/{project['name']}/feedback/{file.replace('.md', '')}_feedback.md")
                })
    
    return jsonify({
        'id': project['id'],
        'name': project['name'],
        'description': project['description'],
        'status': project['status'],
        'created_at': project['created_at'],
        'deliverables': deliverables
    })

@app.route('/api/projects/<int:project_id>/start', methods=['POST'])
def start_project_workflow(project_id):
    db = get_db()
    project = db.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Mettre à jour le statut du projet
    db.execute('UPDATE projects SET status = ? WHERE id = ?', ('in_progress', project_id))
    db.commit()
    
    # Démarrer le workflow du projet en arrière-plan
    # Note: Dans une vraie application, cela serait fait avec une tâche asynchrone (Celery, etc.)
    workflow = get_project_workflow(agent_manager, project['name'])
    workflow.start()
    
    return jsonify({'status': 'workflow_started'})

@app.route('/api/projects/<int:project_id>/deliverables/<path:deliverable_name>', methods=['GET'])
def get_project_deliverable(project_id, deliverable_name):
    db = get_db()
    project = db.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    content = get_deliverable(project['name'], deliverable_name)
    if not content:
        return jsonify({'error': 'Deliverable not found'}), 404
    
    return jsonify({
        'name': deliverable_name,
        'content': content
    })

@app.route('/api/projects/<int:project_id>/feedback', methods=['POST'])
def add_feedback(project_id):
    data = request.json
    deliverable = data.get('deliverable')
    feedback = data.get('feedback')
    
    if not deliverable or not feedback:
        return jsonify({'error': 'Deliverable name and feedback content are required'}), 400
    
    db = get_db()
    project = db.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Sauvegarder le feedback
    save_feedback(project['name'], deliverable, feedback)
    
    # Envoyer le feedback à l'agent approprié pour révision
    deliverable_type = deliverable.split('_')[0] if '_' in deliverable else 'other'
    agent_mapping = {
        '01': 'vision',
        '02': 'pixel',
        '03': 'arch',
        '04': 'pm',
        '05': 'script',
        '06': 'node',
        '07': 'data',
        '08': 'secure',
        '09': 'test',
        '10': 'deploy'
    }
    
    agent_name = agent_mapping.get(deliverable_type)
    if agent_name:
        # Dans une vraie application, cela serait fait avec une tâche asynchrone
        agent_manager.process_feedback(project['name'], deliverable, feedback, agent_name)
    
    return jsonify({'status': 'feedback_received'})

# Routes pour les agents
@app.route('/api/agents', methods=['GET'])
def get_agents():
    agents = agent_manager.list_agents()
    return jsonify(agents)

@app.route('/api/agents/<agent_name>', methods=['POST'])
def interact_with_agent(agent_name):
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    response = agent_manager.ask_agent(agent_name, message)
    return jsonify({'response': response})

# Routes pour la base de connaissances
@app.route('/api/knowledge', methods=['GET'])
def get_knowledge_categories():
    db = get_db()
    categories = db.execute('SELECT DISTINCT category FROM knowledge').fetchall()
    return jsonify([category['category'] for category in categories])

@app.route('/api/knowledge/<category>', methods=['GET'])
def get_knowledge_by_category(category):
    db = get_db()
    items = db.execute('SELECT * FROM knowledge WHERE category = ?', (category,)).fetchall()
    return jsonify([{
        'id': item['id'],
        'agent': item['agent'],
        'content': item['content'],
        'created_at': item['created_at']
    } for item in items])

@app.route('/api/knowledge/search', methods=['GET'])
def search_knowledge():
    search_term = request.args.get('q', '')
    if not search_term:
        return jsonify([])
    
    db = get_db()
    items = db.execute(
        'SELECT * FROM knowledge WHERE content LIKE ? OR query LIKE ?',
        (f'%{search_term}%', f'%{search_term}%')
    ).fetchall()
    
    return jsonify([{
        'id': item['id'],
        'agent': item['agent'],
        'category': item['category'],
        'query': item['query'],
        'content': item['content'],
        'created_at': item['created_at']
    } for item in items])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)