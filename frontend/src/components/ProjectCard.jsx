import React from 'react';
import { Link } from 'react-router-dom';
import './ProjectCard.css';

function ProjectCard({ project }) {
  // Fonction pour obtenir la classe CSS en fonction du statut
  const getStatusClass = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'in_progress':
        return 'status-in-progress';
      case 'paused':
        return 'status-paused';
      case 'failed':
        return 'status-failed';
      default:
        return 'status-created';
    }
  };

  // Fonction pour obtenir le texte du statut en français
  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Terminé';
      case 'in_progress':
        return 'En cours';
      case 'paused':
        return 'En pause';
      case 'failed':
        return 'Échec';
      default:
        return 'Créé';
    }
  };

  // Formatage de la date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(date);
  };

  return (
    <div className="project-card">
      <div className={`project-status ${getStatusClass(project.status)}`}>
        {getStatusText(project.status)}
      </div>
      
      <h3 className="project-title">{project.name}</h3>
      
      <p className="project-description">
        {project.description.length > 120
          ? `${project.description.substring(0, 120)}...`
          : project.description}
      </p>
      
      <div className="project-meta">
        <span className="project-date">
          <i className="far fa-calendar-alt"></i> Créé le {formatDate(project.created_at)}
        </span>
        
        {project.deliverables && (
          <span className="project-deliverables">
            <i className="far fa-file-alt"></i> {project.deliverables?.length || 0} livrables
          </span>
        )}
      </div>
      
      <Link to={`/projects/${project.id}`} className="project-link">
        <button className="btn btn-primary">Voir le projet</button>
      </Link>
    </div>
  );
}

export default ProjectCard;