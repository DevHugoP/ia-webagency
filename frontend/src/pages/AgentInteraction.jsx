import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchAgentDetails, sendMessageToAgent, fetchAgentKnowledge } from '../services/agentService';
import ReactMarkdown from 'react-markdown';
import AgentAvatar from '../components/AgentAvatar';
import './AgentInteraction.css';

function AgentInteraction() {
  const { agentName } = useParams();
  const [agent, setAgent] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);
  const [knowledge, setKnowledge] = useState([]);
  
  const messagesEndRef = useRef(null);

  // Charger les détails de l'agent
  useEffect(() => {
    const loadAgentData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const agentData = await fetchAgentDetails(agentName);
        
        if (!agentData) {
          throw new Error(`Agent "${agentName}" non trouvé`);
        }
        
        setAgent(agentData);
        
        // Ajouter un message de bienvenue
        setMessages([{
          id: 'welcome',
          sender: 'agent',
          content: `Bonjour, je suis ${agentData.title || agentData.name}, ${agentData.description || 'un agent IA spécialisé'}. Comment puis-je vous aider aujourd'hui?`,
          timestamp: new Date()
        }]);
        
        // Charger les connaissances de l'agent
        const knowledgeData = await fetchAgentKnowledge(agentName);
        setKnowledge(knowledgeData || []);
        
      } catch (err) {
        console.error(`Erreur lors du chargement des données de l'agent ${agentName}:`, err);
        setError(err.toString());
      } finally {
        setIsLoading(false);
      }
    };
    
    loadAgentData();
  }, [agentName]);

  // Faire défiler vers le bas lorsque de nouveaux messages sont ajoutés
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Envoyer un message à l'agent
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || isSending) return;
    
    const userMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: newMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsSending(true);
    
    try {
      const response = await sendMessageToAgent(agentName, newMessage);
      
      const agentMessage = {
        id: `agent-${Date.now()}`,
        sender: 'agent',
        content: response.response || "Je n'ai pas pu traiter votre demande. Veuillez réessayer.",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      console.error("Erreur lors de l'envoi du message:", err);
      
      const errorMessage = {
        id: `error-${Date.now()}`,
        sender: 'system',
        content: `Erreur: ${err}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  // Affichage pendant le chargement
  if (isLoading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <span>Chargement de l'agent {agentName}...</span>
      </div>
    );
  }

  // Affichage en cas d'erreur
  if (error || !agent) {
    return (
      <div className="error-message">
        <p>{error || `Agent "${agentName}" non trouvé`}</p>
        <Link to="/" className="btn btn-primary">Retour au tableau de bord</Link>
      </div>
    );
  }

  return (
    <div className="agent-interaction-page">
      <div className="agent-sidebar">
        <div className="agent-profile">
          <AgentAvatar agent={agent} size="large" showName={false} clickable={false} />
          <h2 className="agent-title">{agent.title || agent.name}</h2>
          <p className="agent-description">{agent.description}</p>
        </div>
        
        <div className="agent-knowledge">
          <h3>Base de connaissances</h3>
          {knowledge.length > 0 ? (
            <ul className="knowledge-list">
              {knowledge.slice(0, 5).map((item, index) => (
                <li key={index} className="knowledge-item">
                  <span className="knowledge-category">{item.category}</span>
                  <p>{item.content.length > 100 
                    ? `${item.content.substring(0, 100)}...` 
                    : item.content}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="no-knowledge">Aucune connaissance disponible pour cet agent.</p>
          )}
        </div>
      </div>
      
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.sender}-message`}
            >
              {message.sender === 'agent' && (
                <div className="message-avatar">
                  <AgentAvatar agent={agent} size="small" showName={false} clickable={false} />
                </div>
              )}
              
              <div className="message-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
          
          {isSending && (
            <div className="message agent-message typing">
              <div className="message-avatar">
                <AgentAvatar agent={agent} size="small" showName={false} clickable={false} />
              </div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <form className="chat-input" onSubmit={handleSendMessage}>
          <textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={`Poser une question à ${agent.title || agent.name}...`}
            disabled={isSending}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(e);
              }
            }}
          />
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isSending || !newMessage.trim()}
          >
            <i className="fas fa-paper-plane"></i>
          </button>
        </form>
      </div>
    </div>
  );
}

export default AgentInteraction;