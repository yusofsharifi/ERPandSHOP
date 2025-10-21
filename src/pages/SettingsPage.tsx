import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { 
  Settings, 
  Globe, 
  Palette, 
  Shield, 
  Bell, 
  Database, 
  Download,
  Upload,
  Trash2,
  Save
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { useTheme } from '@/contexts/ThemeContext'
import ThemeSwitcher from '@/components/ThemeSwitcher'
import LanguageToggle from '@/components/LanguageToggle'

const SettingsPage = () => {
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: false,
    marketing: true,
  })
  
  const [company, setCompany] = useState({
    name: 'BizGenius Company',
    email: 'contact@bizgenius.com',
    phone: '+1 (555) 123-4567',
    address: '123 Business St, City, Country',
    website: 'https://bizgenius.com',
    tax_id: 'TAX123456789',
  })

  const { t, i18n } = useTranslation()
  const { theme } = useTheme()
  const isRTL = i18n.language === 'fa'

  const handleNotificationChange = (key: string, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }))
  }

  const handleCompanyChange = (key: string, value: string) => {
    setCompany(prev => ({ ...prev, [key]: value }))
  }

  const saveSettings = () => {
    console.log('Saving settings:', { notifications, company })
    // Implement save logic
  }

  const exportData = () => {
    console.log('Exporting data...')
    // Implement export logic
  }

  const importData = () => {
    console.log('Importing data...')
    // Implement import logic
  }

  const clearCache = () => {
    console.log('Clearing cache...')
    // Implement cache clearing logic
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold tracking-tight">{t('settings')}</h1>
        <p className="text-muted-foreground">
          Manage your application preferences and business settings
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Appearance Settings */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                <Palette className="h-5 w-5" />
                <span>Appearance</span>
              </CardTitle>
              <CardDescription>
                Customize the look and feel of your application
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Theme Setting */}
              <div className="space-y-3">
                <Label>Theme</Label>
                <div className={`flex items-center justify-between p-3 border rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div>
                    <p className="font-medium text-sm">Color Scheme</p>
                    <p className="text-xs text-muted-foreground">
                      Current: {theme.charAt(0).toUpperCase() + theme.slice(1)}
                    </p>
                  </div>
                  <ThemeSwitcher />
                </div>
              </div>

              {/* Language Setting */}
              <div className="space-y-3">
                <Label>Language</Label>
                <div className={`flex items-center justify-between p-3 border rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div>
                    <p className="font-medium text-sm">Interface Language</p>
                    <p className="text-xs text-muted-foreground">
                      Current: {i18n.language === 'fa' ? 'فارسی' : 'English'}
                    </p>
                  </div>
                  <LanguageToggle />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Notification Settings */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                <Bell className="h-5 w-5" />
                <span>Notifications</span>
              </CardTitle>
              <CardDescription>
                Choose when and how you want to be notified
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div>
                    <p className="font-medium text-sm capitalize">{key} Notifications</p>
                    <p className="text-xs text-muted-foreground">
                      {key === 'email' && 'Receive notifications via email'}
                      {key === 'push' && 'Browser push notifications'}
                      {key === 'sms' && 'SMS notifications for urgent matters'}
                      {key === 'marketing' && 'Marketing and promotional emails'}
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => handleNotificationChange(key, e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Company Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader>
              <CardTitle className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                <Settings className="h-5 w-5" />
                <span>Company Information</span>
              </CardTitle>
              <CardDescription>
                Update your business details and contact information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="company-name">Company Name</Label>
                  <Input
                    id="company-name"
                    value={company.name}
                    onChange={(e) => handleCompanyChange('name', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="company-email">Business Email</Label>
                  <Input
                    id="company-email"
                    type="email"
                    value={company.email}
                    onChange={(e) => handleCompanyChange('email', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="company-phone">Phone Number</Label>
                  <Input
                    id="company-phone"
                    type="tel"
                    value={company.phone}
                    onChange={(e) => handleCompanyChange('phone', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="company-website">Website</Label>
                  <Input
                    id="company-website"
                    type="url"
                    value={company.website}
                    onChange={(e) => handleCompanyChange('website', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="company-tax">Tax ID</Label>
                  <Input
                    id="company-tax"
                    value={company.tax_id}
                    onChange={(e) => handleCompanyChange('tax_id', e.target.value)}
                  />
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <Label htmlFor="company-address">Business Address</Label>
                <textarea
                  id="company-address"
                  rows={3}
                  value={company.address}
                  onChange={(e) => handleCompanyChange('address', e.target.value)}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Data Management */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                <Database className="h-5 w-5" />
                <span>Data Management</span>
              </CardTitle>
              <CardDescription>
                Export, import, and manage your business data
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={exportData}
                variant="outline"
                className={`w-full justify-start ${isRTL ? 'flex-row-reverse' : ''}`}
              >
                <Download className="h-4 w-4" />
                <span className="ml-2">Export Data</span>
              </Button>

              <Button
                onClick={importData}
                variant="outline"
                className={`w-full justify-start ${isRTL ? 'flex-row-reverse' : ''}`}
              >
                <Upload className="h-4 w-4" />
                <span className="ml-2">Import Data</span>
              </Button>

              <Button
                onClick={clearCache}
                variant="outline"
                className={`w-full justify-start ${isRTL ? 'flex-row-reverse' : ''}`}
              >
                <Trash2 className="h-4 w-4" />
                <span className="ml-2">Clear Cache</span>
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Security Settings */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                <Shield className="h-5 w-5" />
                <span>Security</span>
              </CardTitle>
              <CardDescription>
                Manage your account security and privacy settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg border bg-muted/50">
                <h4 className="font-medium text-sm mb-2">Two-Factor Authentication</h4>
                <p className="text-xs text-muted-foreground mb-3">
                  Add an extra layer of security to your account
                </p>
                <Button size="sm" variant="outline">
                  Enable 2FA
                </Button>
              </div>

              <div className="p-4 rounded-lg border bg-muted/50">
                <h4 className="font-medium text-sm mb-2">Active Sessions</h4>
                <p className="text-xs text-muted-foreground mb-3">
                  Manage devices that are currently logged in
                </p>
                <Button size="sm" variant="outline">
                  View Sessions
                </Button>
              </div>

              <div className="p-4 rounded-lg border bg-red-50 dark:bg-red-950/20">
                <h4 className="font-medium text-sm mb-2 text-red-600 dark:text-red-400">
                  Danger Zone
                </h4>
                <p className="text-xs text-muted-foreground mb-3">
                  Permanently delete your account and all data
                </p>
                <Button size="sm" variant="destructive">
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Save Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="flex justify-end"
      >
        <Button onClick={saveSettings} size="lg">
          <Save className="h-4 w-4 mr-2" />
          Save All Settings
        </Button>
      </motion.div>
    </div>
  )
}

export default SettingsPage
