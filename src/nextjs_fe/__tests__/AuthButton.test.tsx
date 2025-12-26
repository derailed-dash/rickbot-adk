import { render, screen, fireEvent } from '@testing-library/react'
import AuthButton from '../components/AuthButton'
import { useSession, signIn, signOut } from 'next-auth/react'

// Mock next-auth/react
jest.mock('next-auth/react')

describe('AuthButton', () => {
  it('renders sign in button when not authenticated', () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'unauthenticated',
    })

    render(<AuthButton />)

    expect(screen.getByText('Sign in')).toBeInTheDocument()
  })

  it('renders user name and sign out button when authenticated', () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'Rick Sanchez',
          image: '/rick.png',
        },
      },
      status: 'authenticated',
    })

    render(<AuthButton />)

    expect(screen.getByText('Rick Sanchez')).toBeInTheDocument()
    expect(screen.getByText('Sign out')).toBeInTheDocument()
  })

  it('calls signIn when sign in button is clicked', () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'unauthenticated',
    })

    render(<AuthButton />)

    fireEvent.click(screen.getByText('Sign in'))
    expect(signIn).toHaveBeenCalled()
  })

  it('calls signOut when sign out button is clicked', () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'Rick Sanchez',
        },
      },
      status: 'authenticated',
    })

    render(<AuthButton />)

    fireEvent.click(screen.getByText('Sign out'))
    expect(signOut).toHaveBeenCalled()
  })
})
