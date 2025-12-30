import { render, screen } from '@testing-library/react'
import Header from '../components/Header'
import { ThemeProvider } from '@mui/material/styles'
import theme from '../styles/theme'
import { Personality } from '../types/chat'

// Mock next-auth/react
jest.mock('next-auth/react', () => ({
  useSession: jest.fn(() => ({ data: null, status: 'unauthenticated' })),
  signIn: jest.fn(),
  signOut: jest.fn(),
}))

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

        const headerContainer = screen.getByRole('banner') // Assuming we use component="header" or role="banner"
        
        // This test will fail initially because we haven't implemented the layout or the role
        expect(headerContainer).toBeInTheDocument()
        
        // Check for Rickbot logo
        expect(screen.getByText('Rickbot')).toBeInTheDocument()
        
        // Check for Auth section (handled by AuthButton)
        // Since we mocked useSession to unauthenticated, it should show "Sign in"
        expect(screen.getByText('Sign in')).toBeInTheDocument()

        // Check for Actions section (Meeseeks icon)
        expect(screen.getByTestId('meeseeks-box-icon')).toBeInTheDocument()
    })
})
