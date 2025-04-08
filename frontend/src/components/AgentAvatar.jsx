import React from 'react';
import { Link } from 'react-router-dom';
import './AgentAvatar.css';

function AgentAvatar({ agent, size = 'medium', showName = true, clickable = true }) {
  // Mapping des agents vers des icônes et couleurs spécifiques
  const agentIconMap = {
    vision: { icon: '👁️', color: '#4a6bff' },
    pixel: { icon: '🎨', color: '#6c47ff' },
    arch: { icon: '🏗️', color: '#4a8bff' },
    script: { icon: '📱', color: '#4affcb' },
    node: { icon: '🔌', color: '#47ff6c' },
    data: { icon: '💾', color: '#47ddff' },
    secure: { icon: '🔒', color: '#ff4a6b' },
    test: { icon: '🧪', color: '#ffab00' },
    deploy: { icon: '🚀', color: '#ff7847' },
    pm: { icon: '📊', color: '#a347ff' }
  };

  // Obtenir l'icône et la couleur pour l'agent
  const { icon, color } = agentIconMap[agent.name] || { icon: '🤖', color: '#999999' };

  // Définir les classes en fonction de la taille
  const sizeClass = `agent-avatar-${size}`;

  // Construire le contenu de l'avatar
  const avatarContent = (
    <div className={`agent-avatar ${sizeClass}`} style={{ backgroundColor: color }}>
      <span className="agent-icon">{icon}</span>
      {showName && <span className="agent-name">{agent.title || agent.name}</span>}
    </div>
  );

  // Retourner l'avatar cliquable ou non selon la prop
  if (clickable) {
    return (
      <Link to={`/agents/${agent.name}`} className="agent-avatar-link">
        {avatarContent}
      </Link>
    );
  }

  return avatarContent;
}

export default AgentAvatar;