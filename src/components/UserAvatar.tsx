import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion, AnimatePresence } from 'framer-motion'
import { User, Settings, LogOut, ChevronDown } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/Button'

const UserAvatar = () => {
  const [isOpen, setIsOpen] = useState(false)
  const { user, logout } = useAuth()
  const { t, i18n } = useTranslation()
  const isRTL = i18n.language === 'fa'

  const handleLogout = () => {
    logout()
    setIsOpen(false)
  }

  if (!user) return null

  return (
    <div className="relative">
      {/* User Button */}
      <Button
        variant="ghost"
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center space-x-2 h-10 px-3 ${isRTL ? 'space-x-reverse' : ''}`}
      >
        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center overflow-hidden">
          {user.avatar ? (
            <img 
              src={user.avatar} 
              alt={user.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <User className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
        <div className="hidden md:block text-left">
          <p className="text-sm font-medium">{user.name}</p>
          <p className="text-xs text-muted-foreground">{user.role}</p>
        </div>
        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />
            
            {/* Dropdown Panel */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              transition={{ duration: 0.2 }}
              className={`absolute top-12 ${isRTL ? 'left-0' : 'right-0'} z-50 w-64 bg-card border border-border rounded-lg shadow-lg`}
            >
              {/* User Info */}
              <div className="p-4 border-b border-border">
                <div className={`flex items-center space-x-3 ${isRTL ? 'space-x-reverse' : ''}`}>
                  <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center overflow-hidden">
                    {user.avatar ? (
                      <img 
                        src={user.avatar} 
                        alt={user.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User className="h-6 w-6 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{user.name}</p>
                    <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                    <span className="inline-block px-2 py-1 text-xs bg-primary/10 text-primary rounded-full mt-1">
                      {user.role}
                    </span>
                  </div>
                </div>
              </div>

              {/* Menu Items */}
              <div className="py-2">
                <Link
                  to="/profile"
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center space-x-3 px-4 py-2 text-sm hover:bg-muted transition-colors ${
                    isRTL ? 'space-x-reverse' : ''
                  }`}
                >
                  <User className="h-4 w-4" />
                  <span>{t('profile')}</span>
                </Link>
                
                <Link
                  to="/settings"
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center space-x-3 px-4 py-2 text-sm hover:bg-muted transition-colors ${
                    isRTL ? 'space-x-reverse' : ''
                  }`}
                >
                  <Settings className="h-4 w-4" />
                  <span>{t('settings')}</span>
                </Link>

                <div className="border-t border-border my-2" />
                
                <button
                  onClick={handleLogout}
                  className={`flex items-center space-x-3 px-4 py-2 text-sm hover:bg-muted transition-colors text-destructive w-full ${
                    isRTL ? 'space-x-reverse' : ''
                  }`}
                >
                  <LogOut className="h-4 w-4" />
                  <span>{t('logout')}</span>
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

export default UserAvatar
