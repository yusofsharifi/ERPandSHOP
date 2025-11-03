import { ReactNode } from 'react'

interface ProtectedRouteProps {
  children: ReactNode
}

// Temporarily disable authentication gating: always render protected children.
// Revert this file to restore auth checks after testing.
const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  return children as any
}

export default ProtectedRoute
