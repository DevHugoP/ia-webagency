# backend/utils/file_manager.py
"""
Gestionnaire de fichiers pour l'application IA-WebAgency.

Ce module gère les opérations de fichiers pour les projets,
incluant la sauvegarde et la récupération de briefs, livrables et feedbacks.
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Chemin de base pour les données
BASE_DATA_DIR = Path('data')
PROJECTS_DIR = BASE_DATA_DIR / 'projects'


def ensure_project_directories(project_name):
    """
    Assure que les répertoires nécessaires pour un projet existent.
    
    Args:
        project_name (str): Nom du projet
    """
    project_dir = PROJECTS_DIR / project_name
    
    # Création des sous-répertoires du projet
    for subdir in ['brief', 'deliverables', 'feedback', 'temp']:
        os.makedirs(project_dir / subdir, exist_ok=True)
    
    return project_dir


def save_brief(project_name, content):
    """
    Sauvegarde le brief d'un projet.
    
    Args:
        project_name (str): Nom du projet
        content (str): Contenu du brief
        
    Returns:
        str: Chemin du fichier sauvegardé
    """
    project_dir = ensure_project_directories(project_name)
    brief_path = project_dir / 'brief' / 'initial_brief.md'
    
    with open(brief_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Aussi sauvegarder une copie en JSON pour faciliter l'accès par API
    brief_meta = {
        'project_name': project_name,
        'created_at': datetime.now().isoformat(),
        'content': content
    }
    
    with open(project_dir / 'brief' / 'brief_meta.json', 'w', encoding='utf-8') as file:
        json.dump(brief_meta, file, ensure_ascii=False, indent=2)
    
    return str(brief_path)


def get_brief(project_name):
    """
    Récupère le brief d'un projet.
    
    Args:
        project_name (str): Nom du projet
        
    Returns:
        str: Contenu du brief ou None si non trouvé
    """
    brief_path = PROJECTS_DIR / project_name / 'brief' / 'initial_brief.md'
    
    if not brief_path.exists():
        return None
    
    with open(brief_path, 'r', encoding='utf-8') as file:
        return file.read()


def save_deliverable(project_name, deliverable_id, content, agent=None):
    """
    Sauvegarde un livrable de projet.
    
    Args:
        project_name (str): Nom du projet
        deliverable_id (str): Identifiant du livrable (ex: "01_brief_strategique")
        content (str): Contenu du livrable
        agent (str, optional): Nom de l'agent ayant créé le livrable
        
    Returns:
        str: Chemin du fichier sauvegardé
    """
    project_dir = ensure_project_directories(project_name)
    deliverable_path = project_dir / 'deliverables' / f"{deliverable_id}.md"
    
    with open(deliverable_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Sauvegarder les métadonnées
    deliverable_meta = {
        'id': deliverable_id,
        'project_name': project_name,
        'agent': agent,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    meta_path = project_dir / 'deliverables' / f"{deliverable_id}_meta.json"
    with open(meta_path, 'w', encoding='utf-8') as file:
        json.dump(deliverable_meta, file, ensure_ascii=False, indent=2)
    
    return str(deliverable_path)


def get_deliverable(project_name, deliverable_id):
    """
    Récupère un livrable de projet.
    
    Args:
        project_name (str): Nom du projet
        deliverable_id (str): Identifiant du livrable ou nom du fichier
        
    Returns:
        str: Contenu du livrable ou None si non trouvé
    """
    # Si le deliverable_id contient déjà l'extension, on l'utilise tel quel
    if not deliverable_id.endswith('.md'):
        deliverable_id = f"{deliverable_id}.md"
    
    deliverable_path = PROJECTS_DIR / project_name / 'deliverables' / deliverable_id
    
    if not deliverable_path.exists():
        return None
    
    with open(deliverable_path, 'r', encoding='utf-8') as file:
        return file.read()


def save_feedback(project_name, deliverable_id, feedback_content):
    """
    Sauvegarde le feedback pour un livrable.
    
    Args:
        project_name (str): Nom du projet
        deliverable_id (str): Identifiant du livrable
        feedback_content (str): Contenu du feedback
        
    Returns:
        str: Chemin du fichier de feedback
    """
    project_dir = ensure_project_directories(project_name)
    
    # Si deliverable_id contient l'extension, on l'enlève pour le feedback
    if deliverable_id.endswith('.md'):
        deliverable_id = deliverable_id[:-3]
    
    feedback_path = project_dir / 'feedback' / f"{deliverable_id}_feedback.md"
    
    with open(feedback_path, 'w', encoding='utf-8') as file:
        file.write(feedback_content)
    
    # Sauvegarder les métadonnées
    feedback_meta = {
        'deliverable_id': deliverable_id,
        'project_name': project_name,
        'created_at': datetime.now().isoformat()
    }
    
    meta_path = project_dir / 'feedback' / f"{deliverable_id}_feedback_meta.json"
    with open(meta_path, 'w', encoding='utf-8') as file:
        json.dump(feedback_meta, file, ensure_ascii=False, indent=2)
    
    return str(feedback_path)


def get_feedback(project_name, deliverable_id):
    """
    Récupère le feedback pour un livrable.
    
    Args:
        project_name (str): Nom du projet
        deliverable_id (str): Identifiant du livrable
        
    Returns:
        str: Contenu du feedback ou None si non trouvé
    """
    # Si deliverable_id contient l'extension, on l'enlève pour le feedback
    if deliverable_id.endswith('.md'):
        deliverable_id = deliverable_id[:-3]
    
    feedback_path = PROJECTS_DIR / project_name / 'feedback' / f"{deliverable_id}_feedback.md"
    
    if not feedback_path.exists():
        return None
    
    with open(feedback_path, 'r', encoding='utf-8') as file:
        return file.read()


def list_project_files(project_name):
    """
    Liste tous les fichiers d'un projet par catégorie.
    
    Args:
        project_name (str): Nom du projet
        
    Returns:
        dict: Dictionnaire avec les catégories et fichiers associés
    """
    project_dir = PROJECTS_DIR / project_name
    
    if not project_dir.exists():
        return {
            'brief': [],
            'deliverables': [],
            'feedback': []
        }
    
    result = {
        'brief': [],
        'deliverables': [],
        'feedback': []
    }
    
    # Récupération des briefs
    brief_dir = project_dir / 'brief'
    if brief_dir.exists():
        result['brief'] = [
            {
                'name': f.name,
                'path': str(f.relative_to(PROJECTS_DIR)),
                'created_at': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            for f in brief_dir.glob('*.md')
        ]
    
    # Récupération des livrables
    deliverables_dir = project_dir / 'deliverables'
    if deliverables_dir.exists():
        result['deliverables'] = []
        for f in deliverables_dir.glob('*.md'):
            # Ignorer les fichiers méta
            if '_meta' in f.name:
                continue
                
            deliverable_id = f.stem
            
            # Vérifier s'il y a un feedback associé
            has_feedback = (project_dir / 'feedback' / f"{deliverable_id}_feedback.md").exists()
            
            # Vérifier s'il y a des métadonnées
            meta_file = deliverables_dir / f"{deliverable_id}_meta.json"
            agent = None
            if meta_file.exists():
                try:
                    with open(meta_file, 'r', encoding='utf-8') as meta_f:
                        meta = json.load(meta_f)
                        agent = meta.get('agent')
                except:
                    pass
            
            result['deliverables'].append({
                'id': deliverable_id,
                'name': f.name,
                'agent': agent,
                'path': str(f.relative_to(PROJECTS_DIR)),
                'has_feedback': has_feedback,
                'created_at': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
    
    # Récupération des feedbacks
    feedback_dir = project_dir / 'feedback'
    if feedback_dir.exists():
        result['feedback'] = [
            {
                'name': f.name,
                'deliverable_id': f.stem.replace('_feedback', ''),
                'path': str(f.relative_to(PROJECTS_DIR)),
                'created_at': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            for f in feedback_dir.glob('*_feedback.md')
        ]
    
    return result


def archive_project(project_name, include_temp=False):
    """
    Archive un projet dans un fichier zip.
    
    Args:
        project_name (str): Nom du projet
        include_temp (bool): Inclure les fichiers temporaires
        
    Returns:
        str: Chemin du fichier d'archive
    """
    import zipfile
    from datetime import datetime
    
    project_dir = PROJECTS_DIR / project_name
    if not project_dir.exists():
        return None
    
    # Création d'un nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = PROJECTS_DIR / f"{project_name}_archive_{timestamp}.zip"
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(project_dir):
            rel_dir = Path(root).relative_to(PROJECTS_DIR)
            
            # Ignorer le dossier temp si spécifié
            if not include_temp and 'temp' in str(rel_dir).split(os.sep):
                continue
                
            for file in files:
                file_path = Path(root) / file
                zipf.write(file_path, Path(project_name) / file_path.relative_to(project_dir))
    
    return str(archive_path)