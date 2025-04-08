import React, { createContext, useState, useEffect, useContext } from 'react';
import { fetchProjects, fetchProjectById } from '../services/projectService';

// Création du contexte
const ProjectContext = createContext();

// Hook personnalisé pour utiliser le contexte
export function useProjects() {
  return useContext(ProjectContext);
}

// Fournisseur du contexte
export function ProjectProvider({ children }) {
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Charger tous les projets
  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await fetchProjects();
      setProjects(data);
      setError(null);
    } catch (err) {
      console.error("Erreur lors du chargement des projets:", err);
      setError("Impossible de charger les projets. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  // Charger un projet spécifique
  const loadProject = async (projectId) => {
    setLoading(true);
    try {
      const data = await fetchProjectById(projectId);
      setCurrentProject(data);
      setError(null);
      return data;
    } catch (err) {
      console.error(`Erreur lors du chargement du projet ${projectId}:`, err);
      setError("Impossible de charger le projet. Veuillez réessayer.");
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Ajouter un nouveau projet à la liste
  const addProject = (project) => {
    setProjects(prevProjects => [...prevProjects, project]);
  };

  // Mettre à jour un projet existant
  const updateProject = (updatedProject) => {
    setProjects(prevProjects => 
      prevProjects.map(project => 
        project.id === updatedProject.id ? updatedProject : project
      )
    );
    
    if (currentProject && currentProject.id === updatedProject.id) {
      setCurrentProject(updatedProject);
    }
  };

  // Charger les projets au montage du composant
  useEffect(() => {
    loadProjects();
  }, []);

  // Valeurs exposées par le contexte
  const value = {
    projects,
    currentProject,
    loading,
    error,
    loadProjects,
    loadProject,
    addProject,
    updateProject,
    setCurrentProject
  };

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
}

export default ProjectContext;