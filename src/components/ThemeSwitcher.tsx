import { Button } from '@/components/ui/Button'
import { useTheme } from '@/contexts/ThemeContext'
import { Moon, Sun } from 'lucide-react'

const ThemeSwitcher = () => {
  const { theme, setTheme, isDark } = useTheme()

  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }

  const getIcon = () => {
    if (theme === 'system') {
      return isDark ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />
    }
    return theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />
  }

  const getTitle = () => {
    switch (theme) {
      case 'light':
        return 'Switch to dark mode'
      case 'dark':
        return 'Switch to system theme'
      case 'system':
        return 'Switch to light mode'
      default:
        return 'Toggle theme'
    }
  }

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={toggleTheme}
      className="h-9 w-9"
      title={getTitle()}
    >
      {getIcon()}
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}

export default ThemeSwitcher
