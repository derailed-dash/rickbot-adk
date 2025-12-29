import { render, screen } from '@testing-library/react'
import PrivacyPolicy from '../pages/privacy'

describe('PrivacyPolicy', () => {
  it('renders the privacy policy content', () => {
    render(<PrivacyPolicy />)
    expect(screen.getByText('Privacy Policy')).toBeInTheDocument()
    expect(screen.getByText(/1. Information We Do Not Collect/i)).toBeInTheDocument()
  })

  it('has a link back to the chat', () => {
    render(<PrivacyPolicy />)
    const backButton = screen.getByText(/Back to Chat/i)
    expect(backButton).toBeInTheDocument()
  })
})
