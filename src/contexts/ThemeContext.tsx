import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { STORAGE_KEYS, getStorageItem, setStorageItem } from '@/lib/utils'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  isDark: boolean
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: ReactNode
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const savedTheme = getStorageItem(STORAGE_KEYS.THEME) as Theme
    return savedTheme || 'system'
  })

  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const updateTheme = () => {
      const root = window.document.documentElement
      root.classList.remove('light', 'dark')

      let effectiveTheme: 'light' | 'dark'

      if (theme === 'system') {
        effectiveTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
          ? 'dark'
          : 'light'
      } else {
        effectiveTheme = theme
      }

      root.classList.add(effectiveTheme)
      setIsDark(effectiveTheme === 'dark')
    }

    updateTheme()

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      if (theme === 'system') {
        updateTheme()
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
    setStorageItem(STORAGE_KEYS.THEME, newTheme)
  }

  const value: ThemeContextType = {
    theme,
    setTheme,
    isDark,
  }

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
