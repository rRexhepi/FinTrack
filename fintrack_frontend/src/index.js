import React from 'react';
import ReactDOM from 'react-dom/client'; // Updated import for React 18
import App from './App';

// Material-UI imports
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';


// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', 
    },
    secondary: {
      main: '#dc004e', 
    },
  },
  typography: {

  },

});