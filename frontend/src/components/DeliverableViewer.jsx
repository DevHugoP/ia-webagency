import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { submitFeedback } from '../services/projectService';
import AgentAvatar from './AgentAvatar';
import './DeliverableViewer.css';

function DeliverableViewer({ projectId, deliverable, agent, content }) {
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackContent, setFeedbackContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState(null);

  // Formatage de l'ID du livrable pour l'affichage
  const formatDeliverableId = (id) => {
    // Remplace les underscores par des espaces et met en majuscule la première lettre
    const parts = id.split('_');
    
    // Si l'ID commence par un numéro, on le retire
    if (/^\d+/.test(parts[0])) {
      parts.shift();
    }
    
    return parts
      .map(part => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ');
  };

  // Gestion de la soumission du feedback
  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    
    if (!feedbackContent.trim()) {
      setFeedbackMessage({
        type: 'error',
        text: 'Veuillez saisir un feedback avant de soumettre.'
      });
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await submitFeedback(projectId, deliverable, feedbackContent);
      
      setFeedbackMessage({
        type: 'success',
        text: 'Feedback soumis avec succès. L\'agent va traiter votre retour.'
      });
      
      setShowFeedbackForm(false);
      setFeedbackContent('');
    } catch (error) {
      setFeedbackMessage({
        type: 'error',
        text: `Erreur lors de la soumission du feedback: ${error}`
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="deliverable-viewer">
      <div className="deliverable-header">
        <h2 className="deliverable-title">
          {formatDeliverableId(deliverable)}
        </h2>
        
        {agent && (
          <div className="deliverable-agent">
            <span>Créé par</span>
            <AgentAvatar 
              agent={{ name: agent, title: agent }}
              size="small"
              showName={true}
              clickable={false}
            />
          </div>
        )}
      </div>

      <div className="deliverable-content">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>

      <div className="deliverable-actions">
        <button 
          className="btn btn-secondary"
          onClick={() => setShowFeedbackForm(!showFeedbackForm)}
        >
          {showFeedbackForm ? 'Annuler' : 'Donner un feedback'}
        </button>
      </div>

      {showFeedbackForm && (
        <div className="feedback-form">
          <h3>Votre feedback</h3>
          <form onSubmit={handleSubmitFeedback}>
            <textarea
              value={feedbackContent}
              onChange={(e) => setFeedbackContent(e.target.value)}
              placeholder="Donnez vos commentaires, corrections ou suggestions..."
              rows={6}
              disabled={isSubmitting}
            />
            <div className="form-actions">
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Envoi en cours...' : 'Envoyer le feedback'}
              </button>
            </div>
          </form>
        </div>
      )}

      {feedbackMessage && (
        <div className={`feedback-message ${feedbackMessage.type}`}>
          {feedbackMessage.text}
        </div>
      )}
    </div>
  );
}

export default DeliverableViewer;