import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#39FF14', // Neon Portal Green
    },
    secondary: {
      main: '#FF40FF', // Brighter Neon Pink
    },
    background: {
      default: '#000000',
      paper: '#000000',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontFamily: 'Courier New, monospace' },
    h2: { fontFamily: 'Courier New, monospace' },
    h3: { fontFamily: 'Courier New, monospace' },
    h4: { fontFamily: 'Courier New, monospace' },
    h5: { fontFamily: 'Courier New, monospace' },
    h6: { fontFamily: 'Courier New, monospace' },
  },
});

export default theme;
