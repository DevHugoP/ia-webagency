import React, { useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useProjects } from '../context/ProjectContext';
import { fetchAgents } from '../services/agentService';
import ProjectCard from '../components/ProjectCard';
import AgentAvatar from '../components/AgentAvatar';
import './Dashboard.css';

function Dashboard() {
  const { 
    projects, 
    loading: projectsLoading, 
    error: projectsError, 
    loadProjects 
  } = useProjects();
  
  const [agents, setAgents] = React.useState([]);
  const [agentsLoading, setAgentsLoading] = React.useState(true);
  const [agentsError, setAgentsError] = React.useState(null);

  // Utilisation de useCallback pour optimiser les re-rendus
  const loadAgentsData = useCallback(async () => {
    try {
      setAgentsLoading(true);
      setAgentsError(null);
      
      const agentsData = await fetchAgents();
      setAgents(agentsData || []);
    } catch (error) {
      console.error("Erreur lors du chargement des agents:", error);
      setAgentsError("Impossible de charger les agents");
    } finally {
      setAgentsLoading(false);
    }
  }, []);

  // Charger les projets et les agents au montage du composant
  useEffect(() => {
    // Actualiser la liste des projets
    loadProjects();
    
    // Charger les agents
    loadAgentsData();
  }, [loadProjects, loadAgentsData]);

  // Gestion des états de chargement et d'erreur
  const renderProjectsSection = () => {
    if (projectsLoading) {
      return (
        <div className="loading">
          <div className="loading-spinner"></div>
          <span>Chargement des projets...</span>
        </div>
      );
    }

    if (projectsError) {
      return (
        <div className="error-message">
          <p>{projectsError}</p>
          <button onClick={loadProjects} className="btn btn-secondary">Réessayer</button>
        </div>
      );
    }

    if (projects.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <h3>Aucun projet pour le moment</h3>
          <p>Commencez par créer un nouveau projet pour débuter votre collaboration avec nos agents IA.</p>
          <Link to="/projects/new" className="btn btn-primary">Créer un projet</Link>
        </div>
      );
    }

    return (
      <div className="projects-grid">
        {projects.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    );
  };

  // Gestion des états de chargement et d'erreur pour les agents
  const renderAgentsSection = () => {
    if (agentsLoading) {
      return (
        <div className="loading">
          <div className="loading-spinner"></div>
          <span>Chargement des agents...</span>
        </div>
      );
    }

    if (agentsError) {
      return (
        <div className="error-message">
          <p>{agentsError}</p>
          <button onClick={loadAgentsData} className="btn btn-secondary">Réessayer</button>
        </div>
      );
    }

    return (
      <div className="agents-container">
        {agents.map((agent) => (
          <div key={agent.name} className="agent-item">
            <AgentAvatar 
              agent={agent} 
              size="medium" 
              showName={true} 
            />
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Tableau de bord</h1>
        <Link to="/projects/new" className="btn btn-primary">
          <i className="fas fa-plus"></i> Nouveau projet
        </Link>
      </header>

      {/* Section des agents */}
      <section className="agents-section">
        <h2>Équipe d'agents IA</h2>
        {renderAgentsSection()}
      </section>

      {/* Section des projets */}
      <section className="projects-section">
        <h2>Vos projets</h2>
        {renderProjectsSection()}
      </section>
    </div>
  );
}

export default Dashboard;