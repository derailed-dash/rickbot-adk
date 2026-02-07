import { render, screen, waitFor, act } from '@testing-library/react'
import Chat from '../components/Chat'
import { useSession } from 'next-auth/react'
import axios from 'axios'

// Mock dependencies
jest.mock('next-auth/react')
jest.mock('axios')
jest.mock('react-markdown', () => (props: any) => <span>{props.children}</span>)
global.fetch = jest.fn()
window.HTMLElement.prototype.scrollIntoView = jest.fn()

describe('Chat Loading State', () => {
    const mockSession = {
        data: { user: { name: 'Test User' }, idToken: 'mock-id-token' },
        status: 'authenticated'
    }

    beforeEach(() => {
        jest.clearAllMocks();
        (useSession as jest.Mock).mockReturnValue(mockSession);
        // Silence expected console errors during loading/retry tests
        jest.spyOn(console, 'error').mockImplementation(() => {});
    })

    afterEach(() => {
        (console.error as jest.Mock).mockRestore();
    })

    it('shows custom loading waiting for backend and retries until successful', async () => {
        // Mock axios to fail twice then succeed
        (axios.get as jest.Mock)
            .mockRejectedValueOnce(new Error('Backend not ready'))
            .mockRejectedValueOnce(new Error('Backend still not ready'))
            .mockResolvedValue({ 
                data: [{ 
                    name: 'Rick', 
                    description: 'Rick Sanchez', 
                    avatar: '/avatars/rick.png',
                    title: "Test Rickbot", 
                    overview: "Smartest man",
                    welcome: "Dub dub",
                    prompt_question: "What?"
                }] 
            });

        // Use real timers (default)
        // jest.useFakeTimers(); // Commented out

        render(<Chat />)

        // Expect to see the Rickbot-esque loading message
        expect(screen.getByText(/Heating up the portal gun/i)).toBeInTheDocument();
        
        // Wait for retries to happen and succeed
        // 2 failures * 2000ms + buffer = ~4-5s
        await waitFor(() => {
             expect(screen.getByText("Test Rickbot")).toBeInTheDocument()
        }, { timeout: 8000 });

        // Verify axios was called 3 times
        expect(axios.get).toHaveBeenCalledTimes(3);
    })
})
