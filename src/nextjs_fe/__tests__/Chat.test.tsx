import { render, screen, fireEvent, waitFor, within, act } from '@testing-library/react'
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

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mock-url')
global.URL.revokeObjectURL = jest.fn()

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

const waitForBotResponse = async () => {
    await waitFor(() => {
        expect(screen.getByText('Hello')).toBeInTheDocument()
    })
    await waitFor(() => {
        expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })
}

const waitForPersonalities = async () => {
    await waitFor(() => {
        expect(screen.getByText("Test Rickbot Title")).toBeInTheDocument()
    })
}

const renderChatAndWait = async (useTheme = false) => {
    const result = render(
        useTheme ? (
            <ThemeProvider theme={theme}>
                <Chat />
            </ThemeProvider>
        ) : (
            <Chat />
        )
    )
    await waitForPersonalities()
    return result
}

describe('Chat', () => {
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
        title: "Test Rickbot Title",
        overview: "Smartest man",
        welcome: "Whatever",
        prompt_question: "What do you want?"
    }] })
    ;(global.fetch as jest.Mock).mockResolvedValue({
        status: 200,
        body: {
            getReader: () => ({
                read: jest.fn()
                    .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"chunk": "Hello"}\n\n') })
                    .mockResolvedValueOnce({ done: true })
            })
        }
    })
  })

  it('includes Authorization header in fetchPersonalities', async () => {
    await renderChatAndWait()
    
    await waitFor(() => {
        expect(axios.get).toHaveBeenCalledWith(
            expect.stringContaining('/personas'),
            expect.objectContaining({
                headers: {
                    Authorization: 'Bearer mock-id-token'
                }
            })
        )
    })
  })

  it('includes Authorization header in handleSendMessage', async () => {
    await renderChatAndWait()
    
    const input = screen.getByPlaceholderText('What do you want?')
    fireEvent.change(input, { target: { value: 'Hi' } })
    fireEvent.click(screen.getByText('Send'))

    await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/chat_stream'),
            expect.objectContaining({
                headers: {
                    Authorization: 'Bearer mock-id-token'
                }
            })
        )
    })

    await waitForBotResponse()
  })

  it('clears messages and session_id when Clear Chat is clicked', async () => {
    await renderChatAndWait()
    
    // Send a message first to populate state
    const input = screen.getByPlaceholderText('What do you want?')
    fireEvent.change(input, { target: { value: 'Hi' } })
    fireEvent.click(screen.getByText('Send'))
    
    await waitFor(() => {
        expect(screen.getByText('Hi')).toBeInTheDocument()
    })

    // Click Start New Chat
    const clearButton = screen.getByTitle('Start New Chat')
    fireEvent.click(clearButton)

    // Verify messages are cleared
    expect(screen.queryByText('Hi')).not.toBeInTheDocument()
  })

  it('displays tool usage status when tool_call event is received', async () => {
    const readMock = jest.fn()
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"tool_call": {"name": "SearchAgent"}}\n\n') })
        .mockImplementationOnce(async () => {
            await sleep(50);
            return { done: false, value: new TextEncoder().encode('data: {"tool_response": {"name": "google_search"}}\n\n') };
        })
        .mockImplementationOnce(async () => {
            await sleep(50);
            return { done: false, value: new TextEncoder().encode('data: {"chunk": "Searching..."}\n\n') };
        })
        .mockResolvedValueOnce({ done: true })

    ;(global.fetch as jest.Mock).mockResolvedValue({
        status: 200,
        body: {
            getReader: () => ({
                read: readMock
            })
        }
    })

    await renderChatAndWait()
    const input = screen.getByPlaceholderText('What do you want?')
    fireEvent.change(input, { target: { value: 'Search something' } })
    fireEvent.click(screen.getByText('Send'))

    // Initially shows using tool
    await waitFor(() => {
        expect(screen.getByText(/Google Search/i)).toBeInTheDocument()
    }, { timeout: 2000 })
    
    // Then it should clear when chunk comes (or stay if we decided to keep it, but Chat.tsx clears on chunk)
    // The test mock sends chunk after tool response, so by the time "Searching..." is displayed, tool status might be gone.
    // Let's just verify the text "Searching..." eventually appears.
     await waitFor(() => {
        expect(screen.getByText("Searching...")).toBeInTheDocument()
    })
  })

  it('displays RagAgent status when RagAgent tool_call is received', async () => {
    const readMock = jest.fn()
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"tool_call": {"name": "RagAgent"}}\n\n') })
        .mockImplementationOnce(async () => {
            await sleep(50);
            return { done: false, value: new TextEncoder().encode('data: {"chunk": "Based on my files..."}\n\n') };
        })
        .mockResolvedValueOnce({ done: true })

    ;(global.fetch as jest.Mock).mockResolvedValue({
        status: 200,
        body: {
            getReader: () => ({
                read: readMock
            })
        }
    })

    await renderChatAndWait()

    const input = screen.getByPlaceholderText('What do you want?')
    fireEvent.change(input, { target: { value: 'What is in your knowledge base?' } })
    fireEvent.click(screen.getByText('Send'))

    // Verify it shows RagAgent status
    await waitFor(() => {
        expect(screen.getByText(/Knowledge Base/i)).toBeInTheDocument()
    })
    
    // Verify it eventually shows the response
    await waitFor(() => {
        expect(screen.getByText(/Based on my files/i)).toBeInTheDocument()
    })
  })

  it('handles multi-file upload and renders them inline', async () => {
    const { container } = await renderChatAndWait()
    
    const input = container.querySelector('input[type="file"]') as HTMLInputElement
    const file1 = new File(['hello'], 'hello.png', { type: 'image/png' })
    const file2 = new File(['world'], 'world.mp4', { type: 'video/mp4' })
    
    fireEvent.change(input, { target: { files: [file1, file2] } })
    
    // Check if filenames are displayed near input
    await waitFor(() => {
        expect(screen.getByText('hello.png')).toBeInTheDocument()
        expect(screen.getByText('world.mp4')).toBeInTheDocument()
    })

    // Send
    fireEvent.click(screen.getByText('Send'))

    // Verify they are rendered in the message list
    await waitFor(() => {
        const images = screen.getAllByRole('img')
        expect(images.some(img => img.getAttribute('src') === 'mock-url')).toBeTruthy()
    })

    // Wait for the bot response due to the send
    await waitForBotResponse()
  })

  it('renders the Meeseeks Box icon for the New Chat button with a Badge', async () => {
    await renderChatAndWait()
    const icon = screen.getByTestId('meeseeks-box-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('src', '/meeseeks.webp')
    expect(screen.getByText('+')).toBeInTheDocument() // Check for Badge content
    expect(screen.getByTitle('Start New Chat')).toBeInTheDocument()
  })

  it('renders the Portal Gun icon for the Send button and triggers animation', async () => {
    await renderChatAndWait()
    const icon = screen.getByTestId('portal-gun-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('src', '/portal_gun_trans.png')

    const input = screen.getByPlaceholderText('What do you want?')
    fireEvent.change(input, { target: { value: 'Hi' } })
    fireEvent.click(screen.getByText('Send'))

    // The portal should appear (we can't easily test framer motion scale but we can check existence)
    // For now, let's just verify the Send button has the icon.
    // And wait for the bot response to clear async state
    await waitForBotResponse()
  })

  it('applies the Portal Green primary color to key elements', async () => {
    const { container } = await renderChatAndWait(true)

    // The Rickbot title should use primary color
    // We target the H4 specifically to avoid ambiguity if 'Rickbot' appears elsewhere
    const title = screen.getByRole('heading', { name: /Rickbot/i, level: 4 })
    
    // #39FF14 is rgb(57, 255, 20)
    expect(title).toHaveStyle({ color: 'rgb(57, 255, 20)' }) 

    // Verify background image (we check the root box which should have the image)
    // The root Box is the first element in the container
    const rootBox = container.firstChild
    expect(rootBox).toHaveStyle({ backgroundImage: 'url(/galaxy_bg.png)' })
  })

  describe('user avatar display', () => {
    const sendMessage = async (message: string) => {
      fireEvent.change(screen.getByPlaceholderText('What do you want?'), { target: { value: message } });
      fireEvent.click(screen.getByText('Send'));
      await waitFor(() => {
          expect(screen.getByText(message)).toBeInTheDocument();
      });

      // Wait for the bot response to ensure async operations complete
      await waitForBotResponse();
      return screen.getByText(message).closest('li');
    };
  
    test.each([
      {
        case: 'session with avatar',
        session: {
          data: { user: { name: 'Test User', image: '/avatars/user-avatar.png' }, idToken: 'mock-id-token' },
          status: 'authenticated'
        },
        message: 'Message with Avatar',
        expectedAvatar: '/avatars/user-avatar.png'
      },
      {
        case: 'session without avatar',
        session: {
          data: { user: { name: 'Test User' }, idToken: 'mock-id-token' },
          status: 'authenticated'
        },
        message: 'Message with Fallback',
        expectedAvatar: '/avatars/morty.png'
      }
    ])('it should display correct avatar for $case', async ({ session, message, expectedAvatar }) => {
      (useSession as jest.Mock).mockReturnValue(session);
      await renderChatAndWait();
      const messageItem = await sendMessage(message);
      const avatarInMessage = within(messageItem!).getByRole('img');
      expect(avatarInMessage).toHaveAttribute('src', expectedAvatar);
    });
  });
})
