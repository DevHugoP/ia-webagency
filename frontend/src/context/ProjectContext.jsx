import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
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

  // Charger tous les projets - version optimisée
  const loadProjects = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchProjects();
      // S'assurer que data est toujours un tableau, même si undefined
      setProjects(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Erreur lors du chargement des projets:", err);
      setError("Impossible de charger les projets. Veuillez réessayer.");
      setProjects([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Charger un projet spécifique
  const loadProject = useCallback(async (projectId) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchProjectById(projectId);
      setCurrentProject(data);
      return data;
    } catch (err) {
      console.error(`Erreur lors du chargement du projet ${projectId}:`, err);
      setError("Impossible de charger le projet. Veuillez réessayer.");
      setCurrentProject(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Ajouter un nouveau projet à la liste
  const addProject = useCallback((project) => {
    setProjects(prevProjects => {
      // Vérifier si le projet existe déjà pour éviter les doublons
      const projectExists = prevProjects.some(p => p.id === project.id);
      return projectExists 
        ? prevProjects.map(p => p.id === project.id ? project : p)
        : [...prevProjects, project];
    });
  }, []);

  // Mettre à jour un projet existant
  const updateProject = useCallback((updatedProject) => {
    setProjects(prevProjects => 
      prevProjects.map(project => 
        project.id === updatedProject.id ? updatedProject : project
      )
    );
    
    if (currentProject && currentProject.id === updatedProject.id) {
      setCurrentProject(updatedProject);
    }
  }, [currentProject]);

  // Charger les projets au montage du composant
  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

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