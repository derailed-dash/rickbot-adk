import * as React from 'react';
import Head from 'next/head';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Chat from '../components/Chat';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
        default: '#121212',
        paper: '#1e1e1e'
    }
  },
  typography: {
      fontFamily: 'Courier New, monospace',
  }
});

export default function Home() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Head>
        <title>Rickbot</title>
        <meta name="description" content="Rickbot Chatbot" />
        <link rel="icon" href="/avatars/rick.png" />
      </Head>
      <Chat />
    </ThemeProvider>
  );
}
