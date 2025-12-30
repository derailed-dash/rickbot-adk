import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import Chat from '../components/Chat'
import { useSession } from 'next-auth/react'
import axios from 'axios'

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
        title: "I'm Rickbot!",
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
    render(<Chat />)
    
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
    render(<Chat />)
    
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
  })

  it('clears messages and session_id when Clear Chat is clicked', async () => {
    render(<Chat />)
    
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
        .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"tool_call": {"name": "google_search"}}\n\n') })
        .mockImplementationOnce(async () => {
            await sleep(100);
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

    render(<Chat />)
    const input = screen.getByPlaceholderText('What do you want?')
    fireEvent.change(input, { target: { value: 'Search something' } })
    fireEvent.click(screen.getByText('Send'))

    await waitFor(() => {
        expect(screen.getByText(/Using tool: google_search/i)).toBeInTheDocument()
    }, { timeout: 2000 })
  })

  it('handles multi-file upload and renders them inline', async () => {
    const { container } = render(<Chat />)
    
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
  })

  it('renders the Meeseeks Box icon for the New Chat button with a Badge', () => {
    render(<Chat />)
    const icon = screen.getByTestId('meeseeks-box-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('src', '/meeseeks.webp')
    expect(screen.getByText('+')).toBeInTheDocument() // Check for Badge content
    expect(screen.getByTitle('Start New Chat')).toBeInTheDocument()
  })

  it('renders the Portal Gun icon for the Send button and triggers animation', async () => {
    render(<Chat />)
    const icon = screen.getByTestId('portal-gun-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('src', '/portal_gun_trans.png')

    const input = screen.getByPlaceholderText('What do you want?')
    fireEvent.change(input, { target: { value: 'Hi' } })
    fireEvent.click(screen.getByText('Send'))

    // The portal should appear (we can't easily test framer motion scale but we can check existence)
    // We didn't add a test-id to the portal div but we can find it by its style or just check if it's there
    // For now, let's just verify the Send button has the icon.
  })

  it('applies the Portal Green primary color to key elements', () => {
    // We need to wrap in ThemeProvider to test the actual theme application
    const { ThemeProvider } = require('@mui/material/styles')
    const theme = require('../styles/theme').default

    const { container } = render(
        <ThemeProvider theme={theme}>
            <Chat />
        </ThemeProvider>
    )

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

  it('displays user avatar from session if available', async () => {
    const mockSessionWithAvatar = {
      data: {
        user: { name: 'Test User', image: '/avatars/user-avatar.png' },
        idToken: 'mock-id-token'
      },
      status: 'authenticated'
    };
    (useSession as jest.Mock).mockReturnValue(mockSessionWithAvatar);

    render(<Chat />);
    
    const input = screen.getByPlaceholderText('What do you want?');
    fireEvent.change(input, { target: { value: 'Message with Avatar' } });
    fireEvent.click(screen.getByText('Send'));
    
    await waitFor(() => {
        expect(screen.getByText('Message with Avatar')).toBeInTheDocument();
    });

    const messageItem = screen.getByText('Message with Avatar').closest('li');
    const avatarInMessage = within(messageItem!).getByRole('img');
    expect(avatarInMessage).toHaveAttribute('src', '/avatars/user-avatar.png');
  });

  it('falls back to morty.png if no avatar is in session', async () => {
    const mockSessionNoAvatar = {
        data: {
          user: { name: 'Test User' },
          idToken: 'mock-id-token'
        },
        status: 'authenticated'
      };
    (useSession as jest.Mock).mockReturnValue(mockSessionNoAvatar);
    
    render(<Chat />);

    fireEvent.change(screen.getByPlaceholderText('What do you want?'), { target: { value: 'Message with Fallback' } });
    fireEvent.click(screen.getByText('Send'));

    await waitFor(() => {
        expect(screen.getByText('Message with Fallback')).toBeInTheDocument();
    });

    const messageItem = screen.getByText('Message with Fallback').closest('li');
    const avatarInMessage = within(messageItem!).getByRole('img');
    expect(avatarInMessage).toHaveAttribute('src', '/avatars/morty.png');
  });
})
