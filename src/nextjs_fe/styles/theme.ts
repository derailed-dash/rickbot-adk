import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#39FF14', // Neon Portal Green
    },
    secondary: {
      main: '#b026ff', // Neon Purple
    },
    background: {
      default: '#000000',
      paper: '#000000',
    },
  },
  typography: {
    fontFamily: 'Courier New, monospace',
  },
});

export default theme;
