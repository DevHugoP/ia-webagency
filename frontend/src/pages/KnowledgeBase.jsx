import React, { useState, useEffect } from 'react';
import { fetchKnowledgeCategories, fetchKnowledgeByCategory, searchKnowledge } from '../services/knowledgeService';
import { fetchAgents } from '../services/agentService';
import AgentAvatar from '../components/AgentAvatar';
import './KnowledgeBase.css';

function KnowledgeBase() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [knowledgeItems, setKnowledgeItems] = useState([]);
  const [agents, setAgents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Charger les catégories et les agents au montage du composant
  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Charger les catégories
        const categoriesData = await fetchKnowledgeCategories();
        setCategories(categoriesData || []);
        
        // Si des catégories sont disponibles, sélectionner la première par défaut
        if (categoriesData && categoriesData.length > 0) {
          setSelectedCategory(categoriesData[0]);
        }
        
        // Charger les agents
        const agentsData = await fetchAgents();
        setAgents(agentsData || []);
        
      } catch (err) {
        console.error("Erreur lors du chargement des données initiales:", err);
        setError("Impossible de charger les données de la base de connaissances");
      } finally {
        setLoading(false);
      }
    };
    
    loadInitialData();
  }, []);

  // Charger les connaissances lorsque la catégorie sélectionnée change
  useEffect(() => {
    if (!selectedCategory) return;
    
    const loadKnowledgeForCategory = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const knowledge = await fetchKnowledgeByCategory(selectedCategory);
        setKnowledgeItems(knowledge || []);
        
      } catch (err) {
        console.error(`Erreur lors du chargement des connaissances pour la catégorie ${selectedCategory}:`, err);
        setError(`Impossible de charger les connaissances pour la catégorie "${selectedCategory}"`);
      } finally {
        setLoading(false);
      }
    };
    
    loadKnowledgeForCategory();
  }, [selectedCategory]);

  // Fonction de recherche
  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchTerm.trim()) return;
    
    setIsSearching(true);
    setLoading(true);
    setError(null);
    
    try {
      const results = await searchKnowledge(searchTerm);
      setKnowledgeItems(results || []);
      setSelectedCategory(null);
      
    } catch (err) {
      console.error("Erreur lors de la recherche:", err);
      setError(`Erreur lors de la recherche pour "${searchTerm}"`);
    } finally {
      setLoading(false);
      setIsSearching(true);
    }
  };

  // Réinitialiser la recherche
  const resetSearch = () => {
    setSearchTerm('');
    setIsSearching(false);
    
    if (categories.length > 0) {
      setSelectedCategory(categories[0]);
    }
  };

  // Obtenir l'avatar de l'agent pour un élément de connaissance
  const getAgentForKnowledgeItem = (agentName) => {
    const agent = agents.find(a => a.name === agentName);
    return agent || { name: agentName, title: agentName };
  };

  return (
    <div className="knowledge-base-page">
      <header className="kb-header">
        <div className="kb-title">
          <h1>Base de connaissances</h1>
          <p className="kb-description">
            Explorez les connaissances acquises par nos agents IA au fil des projets.
          </p>
        </div>
        
        <form className="kb-search-form" onSubmit={handleSearch}>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Rechercher dans la base de connaissances..."
            className="kb-search-input"
          />
          <button type="submit" className="btn btn-primary kb-search-button">
            <i className="fas fa-search"></i> Rechercher
          </button>
        </form>
      </header>

      {/* Filtres par catégorie */}
      <div className="kb-categories">
        {categories.map((category) => (
          <button
            key={category}
            className={`kb-category-button ${selectedCategory === category ? 'active' : ''}`}
            onClick={() => {
              setSelectedCategory(category);
              setIsSearching(false);
            }}
          >
            {category}
          </button>
        ))}
        
        {isSearching && (
          <button className="kb-category-button active search-results">
            Résultats de recherche
            <span className="reset-search" onClick={resetSearch}>×</span>
          </button>
        )}
      </div>

      {/* Contenu principal */}
      <div className="kb-content">
        {loading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            <span>Chargement des connaissances...</span>
          </div>
        ) : error ? (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => setSelectedCategory(categories[0])} className="btn btn-secondary">
              Réessayer
            </button>
          </div>
        ) : knowledgeItems.length === 0 ? (
          <div className="empty-state">
            {isSearching ? (
              <>
                <div className="empty-icon">🔍</div>
                <h3>Aucun résultat trouvé</h3>
                <p>Aucune connaissance ne correspond à votre recherche "{searchTerm}".</p>
                <button onClick={resetSearch} className="btn btn-primary">
                  Réinitialiser la recherche
                </button>
              </>
            ) : (
              <>
                <div className="empty-icon">📚</div>
                <h3>Aucune connaissance disponible</h3>
                <p>Cette catégorie ne contient pas encore de connaissances.</p>
              </>
            )}
          </div>
        ) : (
          <div className="kb-items">
            {knowledgeItems.map((item, index) => (
              <div key={index} className="kb-item">
                <div className="kb-item-header">
                  <div className="kb-item-agent">
                    <AgentAvatar
                      agent={getAgentForKnowledgeItem(item.agent)}
                      size="small"
                      showName={true}
                    />
                  </div>
                  
                  <div className="kb-item-meta">
                    <span className="kb-item-category">{item.category}</span>
                    <span className="kb-item-date">
                      {new Date(item.created_at).toLocaleDateString('fr-FR')}
                    </span>
                  </div>
                </div>
                
                <div className="kb-item-content">
                  {item.content}
                </div>
                
                {item.query && (
                  <div className="kb-item-query">
                    <span className="query-label">Question :</span> {item.query}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default KnowledgeBase;