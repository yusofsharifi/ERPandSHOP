import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, Menu, Bell } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import ThemeSwitcher from './ThemeSwitcher'
import LanguageToggle from './LanguageToggle'
import NotificationBell from './NotificationBell'
import UserAvatar from './UserAvatar'

interface NavbarHeaderProps {
  onMenuClick: () => void
  sidebarOpen: boolean
}

const NavbarHeader = ({ onMenuClick, sidebarOpen }: NavbarHeaderProps) => {
  const [searchQuery, setSearchQuery] = useState('')
  const { t, i18n } = useTranslation()
  const isRTL = i18n.language === 'fa'

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Search:', searchQuery)
    // Implement search functionality
  }

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-4">
        {/* Menu Button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className={`${isRTL ? 'ml-4' : 'mr-4'} lg:hidden`}
        >
          <Menu className="h-5 w-5" />
        </Button>

        {/* Search Bar */}
        <div className="flex-1 max-w-md">
          <form onSubmit={handleSearch} className="relative">
            <Search className={`absolute ${isRTL ? 'right-3' : 'left-3'} top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4`} />
            <Input
              type="search"
              placeholder={t('search')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full ${isRTL ? 'pr-10' : 'pl-10'}`}
            />
          </form>
        </div>

        {/* Right Side Actions */}
        <div className={`flex items-center space-x-4 ${isRTL ? 'space-x-reverse' : ''} ${isRTL ? 'mr-4' : 'ml-4'}`}>
          {/* Theme Switcher */}
          <ThemeSwitcher />
          
          {/* Language Toggle */}
          <LanguageToggle />
          
          {/* Notifications */}
          <NotificationBell />
          
          {/* User Avatar */}
          <UserAvatar />
        </div>
      </div>
    </header>
  )
}

export default NavbarHeader
