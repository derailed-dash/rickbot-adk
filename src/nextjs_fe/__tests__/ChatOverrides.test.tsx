import { render, screen } from '@testing-library/react';
import Chat from '../components/Chat';
import { ThemeProvider } from '@mui/material/styles';
import theme from '../styles/theme';
import { useSession } from 'next-auth/react';
import axios from 'axios';

// Mock dependencies
jest.mock('next-auth/react');
jest.mock('axios');
jest.mock('react-markdown', () => (props: any) => <span>{props.children}</span>);
jest.mock('../components/AuthButton', () => () => <div>AuthButton</div>);

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn();

describe('Chat Component Overrides', () => {
  const mockSession = {
    data: {
      user: { name: 'Test User' },
      idToken: 'mock-id-token'
    },
    status: 'authenticated'
  };

  beforeEach(() => {
    (useSession as jest.Mock).mockReturnValue(mockSession);
    (axios.get as jest.Mock).mockResolvedValue({
      data: [{
        name: 'Rick',
        description: 'Rick Sanchez',
        avatar: '/avatars/rick.png',
        title: "Override Test Title",
        overview: "Smartest man",
        welcome: "Whatever",
        prompt_question: "What do you want?"
      }]
    });
  });

  it('applies the correct black border to the Persona Profile', async () => {
    // Render Chat within the ThemeProvider to ensure it has access to the theme
    render(
      <ThemeProvider theme={theme}>
        <Chat />
      </ThemeProvider>
    );

    // Wait for the component to render (and potential async effects)
    // The Persona Profile area has a borderLeft style.
    // We can identify it by the text content, e.g., "Override Test Title"
    const profileTitle = await screen.findByText("Override Test Title");
    
    // The parent Paper component has the border. We need to find the specific element.
    // We traverse up to find the Paper component (MuiPaper-root) that contains this title.
    const paperElement = profileTitle.closest('.MuiPaper-root');
    
    // Assert that the element exists and has the correct border color style.
    expect(paperElement).toBeInTheDocument();
    expect(paperElement).toHaveStyle('border-color: #000000');
  });
});
