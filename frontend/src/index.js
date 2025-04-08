import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Import d'une police de caractères Google Fonts
import '@fontsource/inter/400.css'; 
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';

// Import de Font Awesome pour les icônes
import { library } from '@fortawesome/fontawesome-svg-core';
import { fab } from '@fortawesome/free-brands-svg-icons';
import { 
  faPlus, 
  faBars, 
  faTimes, 
  faPaperPlane, 
  faCalendarAlt, 
  faFileAlt, 
  faComment,
  faSearch,
  faChevronRight,
  faChevronLeft,
  faUser,
  faCog,
  faHome,
  faRobot,
  faBook,
  faDatabase
} from '@fortawesome/free-solid-svg-icons';

// Ajout des icônes à la bibliothèque Font Awesome
library.add(
  fab, 
  faPlus, 
  faBars, 
  faTimes, 
  faPaperPlane, 
  faCalendarAlt, 
  faFileAlt, 
  faComment,
  faSearch,
  faChevronRight,
  faChevronLeft,
  faUser,
  faCog,
  faHome,
  faRobot,
  faBook,
  faDatabase
);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
