import { render, screen } from '@testing-library/react'
import Thinking from '../components/Thinking'

describe('Thinking', () => {
  it('renders nothing when action and activeTool are null', () => {
    const { container } = render(<Thinking action={null} activeTool={null} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders Thinking... when action is Thinking...', () => {
    render(<Thinking action="Thinking..." activeTool={null} />)
    expect(screen.getByText(/Thinking/)).toBeInTheDocument()
  })

  it('renders tool name and pulse when activeTool is running', () => {
    render(<Thinking action="Using tool..." activeTool={{ name: 'google_search', status: 'running' }} />)
    expect(screen.getByText(/Google Search/)).toBeInTheDocument()
  })

  it('renders tool name and Done when activeTool is completed', () => {
    render(<Thinking action="Using tool..." activeTool={{ name: 'google_search', status: 'completed' }} />)
    expect(screen.getByText(/Google Search \(Done\)/)).toBeInTheDocument()
  })

  it('renders Responding when action is Responding...', () => {
    render(<Thinking action="Responding..." activeTool={null} />)
    expect(screen.getByText('Responding')).toBeInTheDocument()
  })
})
