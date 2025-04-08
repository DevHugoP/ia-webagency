import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useProjects } from '../context/ProjectContext';
import { fetchDeliverable, startProjectWorkflow } from '../services/projectService';
import { fetchAgentDetails } from '../services/agentService';
import DeliverableViewer from '../components/DeliverableViewer';
import AgentAvatar from '../components/AgentAvatar';
import './ProjectDetail.css';

function ProjectDetail() {
  const { projectId } = useParams();
  const { loadProject, currentProject, loading, error } = useProjects();
  
  const [selectedDeliverable, setSelectedDeliverable] = useState(null);
  const [deliverableContent, setDeliverableContent] = useState('');
  const [deliverableLoading, setDeliverableLoading] = useState(false);
  const [deliverableError, setDeliverableError] = useState(null);
  
  const [isStartingWorkflow, setIsStartingWorkflow] = useState(false);
  const [workflowError, setWorkflowError] = useState(null);
  
  const [agentDetails, setAgentDetails] = useState({});

  // Charger les détails du projet
  useEffect(() => {
    loadProject(projectId);
  }, [projectId, loadProject]);

  // Charger les détails des agents associés aux livrables
  useEffect(() => {
    const loadAgentDetails = async () => {
      if (!currentProject || !currentProject.deliverables) return;
      
      const agents = new Set();
      currentProject.deliverables.forEach(deliverable => {
        if (deliverable.type) {
          agents.add(deliverable.type);
        }
      });
      
      const details = {};
      for (const agent of agents) {
        try {
          const agentData = await fetchAgentDetails(agent);
          if (agentData) {
            details[agent] = agentData;
          }
        } catch (error) {
          console.error(`Erreur lors du chargement des détails de l'agent ${agent}:`, error);
        }
      }
      
      setAgentDetails(details);
    };
    
    loadAgentDetails();
  }, [currentProject]);

  // Charger le contenu d'un livrable
  const handleSelectDeliverable = async (deliverable) => {
    if (selectedDeliverable === deliverable.name) {
      // Désélectionner si on clique sur le même livrable
      setSelectedDeliverable(null);
      setDeliverableContent('');
      return;
    }
    
    setSelectedDeliverable(deliverable.name);
    setDeliverableLoading(true);
    setDeliverableError(null);
    
    try {
      const data = await fetchDeliverable(projectId, deliverable.name);
      setDeliverableContent(data.content);
    } catch (error) {
      console.error("Erreur lors du chargement du livrable:", error);
      setDeliverableError(`Impossible de charger le livrable: ${error}`);
    } finally {
      setDeliverableLoading(false);
    }
  };

  // Démarrer le workflow du projet
  const handleStartWorkflow = async () => {
    setIsStartingWorkflow(true);
    setWorkflowError(null);
    
    try {
      await startProjectWorkflow(projectId);
      // Recharger le projet pour refléter le changement de statut
      await loadProject(projectId);
    } catch (error) {
      console.error("Erreur lors du démarrage du workflow:", error);
      setWorkflowError(`Impossible de démarrer le workflow: ${error}`);
    } finally {
      setIsStartingWorkflow(false);
    }
  };

  // Formater le statut du projet
  const formatStatus = (status) => {
    switch (status) {
      case 'completed': return 'Terminé';
      case 'in_progress': return 'En cours';
      case 'paused': return 'En pause';
      case 'failed': return 'Échec';
      default: return 'Créé';
    }
  };

  // Affichage pendant le chargement
  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <span>Chargement du projet...</span>
      </div>
    );
  }

  // Affichage en cas d'erreur
  if (error || !currentProject) {
    return (
      <div className="error-message">
        <p>{error || "Projet non trouvé"}</p>
        <Link to="/" className="btn btn-primary">Retour au tableau de bord</Link>
      </div>
    );
  }

  return (
    <div className="project-detail-page">
      <header className="project-header">
        <div className="project-header-content">
          <h1>{currentProject.name}</h1>
          <p className="project-description">{currentProject.description}</p>
          
          <div className="project-meta">
            <span className="project-status">
              Statut: <span className={`status-${currentProject.status}`}>
                {formatStatus(currentProject.status)}
              </span>
            </span>
            
            <span className="project-created">
              Créé le: {new Date(currentProject.created_at).toLocaleDateString('fr-FR')}
            </span>
          </div>
        </div>
        
        <div className="project-actions">
          {currentProject.status === 'created' && (
            <button 
              className="btn btn-primary"
              onClick={handleStartWorkflow}
              disabled={isStartingWorkflow}
            >
              {isStartingWorkflow ? 'Démarrage...' : 'Démarrer le projet'}
            </button>
          )}
        </div>
      </header>
      
      {workflowError && (
        <div className="error-message">
          <p>{workflowError}</p>
        </div>
      )}

      <div className="project-content">
        {/* Liste des livrables */}
        <div className="deliverables-list">
          <h2>Livrables du projet</h2>
          
          {currentProject.deliverables?.length > 0 ? (
            <ul className="deliverables">
              {currentProject.deliverables.map((deliverable) => {
                const isActive = selectedDeliverable === deliverable.name;
                const hasFeedback = deliverable.has_feedback;
                
                return (
                  <li 
                    key={deliverable.name}
                    className={`deliverable-item ${isActive ? 'active' : ''} ${hasFeedback ? 'has-feedback' : ''}`}
                    onClick={() => handleSelectDeliverable(deliverable)}
                  >
                    <div className="deliverable-name">
                      {deliverable.name}
                    </div>
                    
                    {deliverable.type && agentDetails[deliverable.type] && (
                      <div className="deliverable-agent">
                        <AgentAvatar 
                          agent={agentDetails[deliverable.type]} 
                          size="small" 
                          showName={false} 
                          clickable={false}
                        />
                      </div>
                    )}
                    
                    {hasFeedback && (
                      <span className="feedback-badge" title="Feedback envoyé">
                        <i className="fas fa-comment"></i>
                      </span>
                    )}
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className="empty-deliverables">
              <p>
                {currentProject.status === 'created' 
                  ? "Démarrez le projet pour générer des livrables."
                  : "Les livrables seront générés progressivement par nos agents IA."}
              </p>
            </div>
          )}
        </div>

        {/* Visualiseur de livrable */}
        <div className="deliverable-container">
          {selectedDeliverable ? (
            deliverableLoading ? (
              <div className="loading">
                <div className="loading-spinner"></div>
                <span>Chargement du livrable...</span>
              </div>
            ) : deliverableError ? (
              <div className="error-message">
                <p>{deliverableError}</p>
              </div>
            ) : (
              <DeliverableViewer 
                projectId={projectId} 
                deliverable={selectedDeliverable}
                agent={currentProject.deliverables.find(d => d.name === selectedDeliverable)?.type}
                content={deliverableContent}
              />
            )
          ) : (
            <div className="no-deliverable-selected">
              <div className="placeholder-icon">📄</div>
              <h3>Sélectionnez un livrable</h3>
              <p>Choisissez un livrable dans la liste pour afficher son contenu.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProjectDetail;