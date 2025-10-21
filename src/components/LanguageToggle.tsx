import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'
import { Languages } from 'lucide-react'

const LanguageToggle = () => {
  const { i18n } = useTranslation()

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'fa' : 'en'
    i18n.changeLanguage(newLang)
  }

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={toggleLanguage}
      className="h-9 w-9"
      title={i18n.language === 'en' ? 'Switch to فارسی' : 'Switch to English'}
    >
      <Languages className="h-4 w-4" />
      <span className="sr-only">Toggle language</span>
    </Button>
  )
}

export default LanguageToggle
