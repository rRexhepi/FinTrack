import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Material-UI imports
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#0d47a1', // Dark Blue
    },
    secondary: {
      main: '#1b5e20', // Dark Green
    },
    background: {
      default: '#f5f5f5', // Light Grey
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    // ... customize other typography as needed
  },
});

// Render the application
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Normalize CSS */}
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
