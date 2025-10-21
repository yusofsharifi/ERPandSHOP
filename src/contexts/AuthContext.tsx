import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'
import { STORAGE_KEYS, getStorageItem, setStorageItem, removeStorageItem } from '@/lib/utils'

interface User {
  id: string
  email: string
  name: string
  role: string
  avatar?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  updateProfile: (data: Partial<User>) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()
  const { t } = useTranslation()

  // Check for existing auth on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = getStorageItem(STORAGE_KEYS.TOKEN)
        const savedUser = getStorageItem(STORAGE_KEYS.USER)
        
        if (token && savedUser) {
          // Verify token with backend
          const response = await fetch('/api/auth/verify', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          })
          
          if (response.ok) {
            setUser(JSON.parse(savedUser))
          } else {
            // Token invalid, clear storage
            removeStorageItem(STORAGE_KEYS.TOKEN)
            removeStorageItem(STORAGE_KEYS.USER)
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        removeStorageItem(STORAGE_KEYS.TOKEN)
        removeStorageItem(STORAGE_KEYS.USER)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    const DEV_CREDENTIALS = {
      email: 'admin@bizgenius.local',
      password: 'Admin1234!',
      user: {
        id: 'dev-admin-1',
        email: 'admin@bizgenius.local',
        name: 'Admin User',
        role: 'Admin',
        avatar: '',
      },
      token: 'dev-token-abc-123',
    }

    try {
      setIsLoading(true)

      // Try real backend first
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        })

        if (response.ok) {
          const data = await response.json()
          // Store token and user data
          setStorageItem(STORAGE_KEYS.TOKEN, data.access_token)
          setStorageItem(STORAGE_KEYS.USER, JSON.stringify(data.user))
          setUser(data.user)
          toast.success(t('loginSuccess'))
          navigate('/dashboard')
          return
        } else {
          // Try to parse error body to detect 2FA requirement
          let errBody: any = null
          try {
            errBody = await response.json()
          } catch {}
          if (errBody && errBody.detail === '2FA_REQUIRED') {
            throw new Error('2FA_REQUIRED')
          }
        }
      } catch (err) {
        // Backend not available or network error - will attempt dev fallback below
        console.warn('Backend login failed, attempting dev fallback:', err)
      }

      // Development fallback: allow a local demo admin account
      if (import.meta.env.DEV && email === DEV_CREDENTIALS.email && password === DEV_CREDENTIALS.password) {
        setStorageItem(STORAGE_KEYS.TOKEN, DEV_CREDENTIALS.token)
        setStorageItem(STORAGE_KEYS.USER, JSON.stringify(DEV_CREDENTIALS.user))
        setUser(DEV_CREDENTIALS.user)
        toast.success('Logged in as demo admin')
        navigate('/dashboard')
        return
      }

      // If we reach here, login failed
      throw new Error('Login failed')
    } catch (error) {
      console.error('Login error:', error)
      toast.error(t('loginError'))
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (name: string, email: string, password: string) => {
    try {
      setIsLoading(true)
      
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      })

      if (!response.ok) {
        throw new Error('Registration failed')
      }

      const data = await response.json()
      
      // Store token and user data
      setStorageItem(STORAGE_KEYS.TOKEN, data.access_token)
      setStorageItem(STORAGE_KEYS.USER, JSON.stringify(data.user))
      
      setUser(data.user)
      toast.success(t('registerSuccess'))
      navigate('/dashboard')
    } catch (error) {
      console.error('Registration error:', error)
      toast.error('Registration failed')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    removeStorageItem(STORAGE_KEYS.TOKEN)
    removeStorageItem(STORAGE_KEYS.USER)
    setUser(null)
    navigate('/login')
    toast.success('Logged out successfully')
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      const token = getStorageItem(STORAGE_KEYS.TOKEN)
      
      const response = await fetch(`/api/users/${user?.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Profile update failed')
      }

      const updatedUser = await response.json()
      setUser(updatedUser)
      setStorageItem(STORAGE_KEYS.USER, JSON.stringify(updatedUser))
      toast.success(t('profileUpdated'))
    } catch (error) {
      console.error('Profile update error:', error)
      toast.error('Profile update failed')
      throw error
    }
  }

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateProfile,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
