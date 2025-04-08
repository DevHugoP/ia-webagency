import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProject } from '../services/projectService';
import { useProjects } from '../context/ProjectContext';
import './NewProject.css';

function NewProject() {
  const navigate = useNavigate();
  const { addProject } = useProjects();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    objectives: '',
    target_audience: '',
    constraints: '',
    deadline: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // Gestion des changements dans les champs du formulaire
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({ ...prevData, [name]: value }));
    
    // Effacer l'erreur si l'utilisateur modifie le champ
    if (errors[name]) {
      setErrors(prevErrors => ({ ...prevErrors, [name]: null }));
    }
  };

  // Validation du formulaire
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Le nom du projet est requis';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'La description du projet est requise';
    }
    
    if (!formData.objectives.trim()) {
      newErrors.objectives = 'Les objectifs du projet sont requis';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Valider le formulaire
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      // Appel API pour créer le projet
      const newProject = await createProject(formData);
      
      // Ajouter le projet au context
      addProject(newProject);
      
      // Rediriger vers la page du projet
      navigate(`/projects/${newProject.id}`);
    } catch (error) {
      setSubmitError(error.toString());
      setIsSubmitting(false);
    }
  };

  return (
    <div className="new-project-page">
      <header className="page-header">
        <h1>Créer un nouveau projet</h1>
        <p className="header-description">
          Décrivez votre projet en détail pour permettre à nos agents IA de comprendre vos besoins.
        </p>
      </header>

      {submitError && (
        <div className="error-message">
          <p>{submitError}</p>
        </div>
      )}

      <div className="form-container">
        <form onSubmit={handleSubmit} className="project-form">
          <div className="form-group">
            <label htmlFor="name">Nom du projet *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Ex: Site e-commerce de vêtements"
              className={errors.name ? 'input-error' : ''}
              disabled={isSubmitting}
            />
            {errors.name && <span className="error-text">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="description">Description du projet *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Décrivez le projet en détail..."
              rows={4}
              className={errors.description ? 'input-error' : ''}
              disabled={isSubmitting}
            />
            {errors.description && <span className="error-text">{errors.description}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="objectives">Objectifs du projet *</label>
            <textarea
              id="objectives"
              name="objectives"
              value={formData.objectives}
              onChange={handleChange}
              placeholder="Quels sont vos objectifs principaux?"
              rows={3}
              className={errors.objectives ? 'input-error' : ''}
              disabled={isSubmitting}
            />
            {errors.objectives && <span className="error-text">{errors.objectives}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="target_audience">Public cible</label>
            <textarea
              id="target_audience"
              name="target_audience"
              value={formData.target_audience}
              onChange={handleChange}
              placeholder="À qui s'adresse ce projet?"
              rows={2}
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="constraints">Contraintes techniques</label>
            <textarea
              id="constraints"
              name="constraints"
              value={formData.constraints}
              onChange={handleChange}
              placeholder="Technologies spécifiques, limitations, etc."
              rows={2}
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="deadline">Délai souhaité</label>
            <input
              type="text"
              id="deadline"
              name="deadline"
              value={formData.deadline}
              onChange={handleChange}
              placeholder="Ex: 3 semaines, fin juin 2023, etc."
              disabled={isSubmitting}
            />
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={() => navigate('/')}
              disabled={isSubmitting}
            >
              Annuler
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Création en cours...' : 'Créer le projet'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default NewProject;