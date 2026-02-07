import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Chat from '../components/Chat'
import { useSession } from 'next-auth/react'
import axios from 'axios'
import { ThemeProvider } from '@mui/material/styles'
import theme from '../styles/theme'

// Mock next-auth/react
jest.mock('next-auth/react')
// Mock axios
jest.mock('axios')
// Mock react-markdown
jest.mock('react-markdown', () => (props: any) => <span>{props.children}</span>)
// Mock fetch
global.fetch = jest.fn()

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn()

// Mock TextEncoder/TextDecoder
global.TextEncoder = require('util').TextEncoder
global.TextDecoder = require('util').TextDecoder

describe('Upgrade Required', () => {
  const mockSession = {
    data: {
      user: { name: 'Test User' },
      idToken: 'mock-id-token'
    },
    status: 'authenticated'
  }

  beforeEach(() => {
    ;(useSession as jest.Mock).mockReturnValue(mockSession)
    ;(axios.get as jest.Mock).mockResolvedValue({ data: [{ 
        name: 'Rick', 
        description: 'Rick Sanchez', 
        avatar: '/avatars/rick.png',
        title: "Standard Rickbot Title",
        overview: "Smartest man",
        welcome: "Whatever",
        prompt_question: "What do you want?"
    }, {
        name: 'SupporterRick',
        description: 'Supporter Only Rick',
        avatar: '/avatars/rick.png',
        title: "Supporter Rickbot Title",
        overview: "Supporter only",
        welcome: "Welcome Supporter",
        prompt_question: "What do you want, Supporter?"
    }] })
  })

  it('displays an upgrade required message when backend returns 403 UPGRADE_REQUIRED', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValue({
        status: 403,
        json: async () => ({
            error_code: "UPGRADE_REQUIRED",
            detail: "Upgrade Required: Access to the 'SupporterRick' persona is restricted to Supporters.",
            required_role: "supporter",
            personality: "SupporterRick"
        })
    })

    render(
        <ThemeProvider theme={theme}>
            <Chat />
        </ThemeProvider>
    )

    // Wait for personalities to load
    await waitFor(() => expect(screen.getByText("Standard Rickbot Title")).toBeInTheDocument())

    // Switch to SupporterRick (need to mock Header interaction or just use state if we could, but we test UI)
    // The Header has a personality selector.
    const select = screen.getByRole('combobox', { name: /Personality/i })
    fireEvent.mouseDown(select)
    
    const supporterOption = await screen.findByText("SupporterRick")
    fireEvent.click(supporterOption)

    // Verify it switched
    await waitFor(() => expect(screen.getByText("Supporter Rickbot Title")).toBeInTheDocument())

    // Send a message
    const input = screen.getByPlaceholderText('What do you want, Supporter?')
    fireEvent.change(input, { target: { value: 'Hello' } })
    fireEvent.click(screen.getByText('Send'))

    // Verify the upgrade required modal/message appears
    await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Upgrade Required/i })).toBeInTheDocument()
        expect(screen.getByText(/restricted to Supporters/i)).toBeInTheDocument()
    })

    // Verify it has a "Close" or "OK" button
    expect(screen.getByRole('button', { name: /Close/i })).toBeInTheDocument()
  })
})
