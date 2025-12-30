import { render, screen, fireEvent } from '@testing-library/react'
import Header from '../components/Header'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import theme from '../styles/theme'
import { Personality } from '../types/chat'
import useMediaQuery from '@mui/material/useMediaQuery';

// Mock next-auth/react
jest.mock('next-auth/react', () => ({
  useSession: jest.fn(() => ({ data: null, status: 'unauthenticated' })),
  signIn: jest.fn(),
  signOut: jest.fn(),
}))

// Mock useMediaQuery
jest.mock('@mui/material/useMediaQuery');

const mockPersonalities: Personality[] = [
    { 
        name: 'Rick', 
        description: 'Rick Sanchez', 
        avatar: '/avatars/rick.png',
        title: "I'm Rickbot!",
        overview: "Smartest man",
        welcome: "Whatever",
        prompt_question: "What do you want?"
    }
]

describe('Header', () => {
    beforeEach(() => {
        (useMediaQuery as jest.Mock).mockReturnValue(false); // Default to desktop
    });

    it('renders logo, auth, and actions in a 3-column layout on desktop', () => {
        const onPersonalityChange = jest.fn()
        const onClearChat = jest.fn()

        render(
            <ThemeProvider theme={theme}>
                <Header 
                    personalities={mockPersonalities}
                    selectedPersonality={mockPersonalities[0]}
                    onPersonalityChange={onPersonalityChange}
                    onClearChat={onClearChat}
                />
            </ThemeProvider>
        )

        const headerContainer = screen.getByRole('banner')
        expect(headerContainer).toBeInTheDocument()
        expect(screen.getByText('Rickbot')).toBeInTheDocument()
        expect(screen.getByText('Sign in')).toBeInTheDocument()
        expect(screen.getByTestId('meeseeks-box-icon')).toBeInTheDocument()
        expect(screen.getAllByText((content, element) => {
            const hasText = (node: Element) => node.textContent === 'Newchat' || node.textContent === 'New chat' || (node.textContent?.includes('New') && node.textContent?.includes('chat'));
            const elementHasText = element ? hasText(element) : false;
            return elementHasText;
        })[0]).toBeInTheDocument()
    })

    it('renders hamburger menu on mobile and toggles drawer', async () => {
        (useMediaQuery as jest.Mock).mockReturnValue(true); // Simulate mobile

        const onPersonalityChange = jest.fn()
        const onClearChat = jest.fn()

        render(
            <ThemeProvider theme={theme}>
                <Header 
                    personalities={mockPersonalities}
                    selectedPersonality={mockPersonalities[0]}
                    onPersonalityChange={onPersonalityChange}
                    onClearChat={onClearChat}
                />
            </ThemeProvider>
        )

        // Menu icon should be present
        const menuButton = screen.getByLabelText('menu'); // We will use aria-label="menu"
        expect(menuButton).toBeInTheDocument()

        // Auth and Persona selector should NOT be in the document initially
        expect(screen.queryByText('Sign in')).not.toBeInTheDocument()

        // Click menu button
        fireEvent.click(menuButton)

        // Now drawer content should be present
        expect(screen.getByText('Sign in')).toBeInTheDocument()
        expect(screen.getByLabelText(/Personality/i)).toBeInTheDocument()
    })
})
