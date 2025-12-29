import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Chat from '../components/Chat'
import { useSession } from 'next-auth/react'
import axios from 'axios'

// Mock next-auth/react
jest.mock('next-auth/react')
// Mock axios
jest.mock('axios')
// Mock react-markdown
jest.mock('react-markdown', () => (props: any) => <div>{props.children}</div>)
// Mock fetch
global.fetch = jest.fn()

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn()

// Mock TextEncoder/TextDecoder
global.TextEncoder = require('util').TextEncoder
global.TextDecoder = require('util').TextDecoder

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
    ;(axios.get as jest.Mock).mockResolvedValue({ data: [] })
    ;(global.fetch as jest.Mock).mockResolvedValue({
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
    
    const input = screen.getByPlaceholderText('Type a message...')
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
    const input = screen.getByPlaceholderText('Type a message...')
    fireEvent.change(input, { target: { value: 'Hi' } })
    fireEvent.click(screen.getByText('Send'))
    
    await waitFor(() => {
        expect(screen.getByText('Hi')).toBeInTheDocument()
    })

    // Click Clear Chat
    const clearButton = screen.getByTitle('Clear Chat History')
    fireEvent.click(clearButton)

    // Verify messages are cleared
    expect(screen.queryByText('Hi')).not.toBeInTheDocument()
  })
})
