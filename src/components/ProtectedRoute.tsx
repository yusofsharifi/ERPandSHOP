import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { ReactNode } from 'react'

interface ProtectedRouteProps {
  children: ReactNode
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    )
  }

  // Allow temporary bypass for testing pages without login.
  // Enable by adding ?noauth=1 to the URL or setting localStorage.setItem('bypassAuth','1').
  const bypass = typeof window !== 'undefined' && (new URLSearchParams(window.location.search).get('noauth') === '1' || window.localStorage.getItem('bypassAuth') === '1')

  if (!isAuthenticated && !bypass) {
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
