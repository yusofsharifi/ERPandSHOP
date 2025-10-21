import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { useTranslation } from 'react-i18next'
import LanguageToggle from './LanguageToggle'
import ThemeSwitcher from './ThemeSwitcher'

interface AuthCardProps {
  title: string
  description: string
  children: ReactNode
}

const AuthCard = ({ title, description, children }: AuthCardProps) => {
  const { i18n } = useTranslation()

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Header with theme and language toggles */}
        <div className={`flex justify-between items-center mb-6 ${i18n.language === 'fa' ? 'flex-row-reverse' : ''}`}>
          <div className="flex items-center gap-2">
            <LanguageToggle />
            <ThemeSwitcher />
          </div>
          <h1 className="text-2xl font-bold text-primary">BizGenius</h1>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold">{title}</CardTitle>
            <CardDescription className="text-base">{description}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {children}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>BizGenius ERP & E-Commerce Platform</p>
          <p className="mt-1">© 2024 All rights reserved</p>
        </div>
      </motion.div>
    </div>
  )
}

export default AuthCard
