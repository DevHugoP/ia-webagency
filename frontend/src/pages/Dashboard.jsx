import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useProjects } from '../context/ProjectContext';
import { fetchAgents } from '../services/agentService';
import ProjectCard from '../components/ProjectCard';
import AgentAvatar from '../components/AgentAvatar';
import './Dashboard.css';

function Dashboard() {
  const { projects, loading, error, loadProjects } = useProjects();
  const [agents, setAgents] = React.useState([]);
  const [agentsLoading, setAgentsLoading] = React.useState(true);

  // Chargement des projets et des agents au montage du composant
  useEffect(() => {
    // Actualiser la liste des projets
    loadProjects();
    
    // Charger la liste des agents
    const loadAgents = async () => {
      try {
        const agentsData = await fetchAgents();
        setAgents(agentsData);
      } catch (error) {
        console.error("Erreur lors du chargement des agents:", error);
      } finally {
        setAgentsLoading(false);
      }
    };
    
    loadAgents();
  }, [loadProjects]);

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
        
        {agentsLoading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            <span>Chargement des agents...</span>
          </div>
        ) : (
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
        )}
      </section>

      {/* Section des projets */}
      <section className="projects-section">
        <h2>Vos projets</h2>
        
        {loading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            <span>Chargement des projets...</span>
          </div>
        ) : error ? (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={loadProjects} className="btn btn-secondary">Réessayer</button>
          </div>
        ) : projects.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📁</div>
            <h3>Aucun projet pour le moment</h3>
            <p>Commencez par créer un nouveau projet pour débuter votre collaboration avec nos agents IA.</p>
            <Link to="/projects/new" className="btn btn-primary">Créer un projet</Link>
          </div>
        ) : (
          <>
            <div className="projects-grid">
              {projects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  );
}

export default Dashboard;