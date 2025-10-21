import React, { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { Save, Upload } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Button } from '@/components/ui/Button'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'

const currencies = ['USD', 'EUR', 'IRR']
const timezones = ['UTC', 'Asia/Tehran', 'America/New_York']
const languages = [
  { code: 'en', label: 'English' },
  { code: 'fa', label: 'فارسی' },
]

const generalSchema = z.object({
  companyName: z.string().min(1, 'Company name is required'),
  defaultCurrency: z.string().min(1, 'Default currency is required'),
  timezone: z.string().min(1, 'Timezone is required'),
  language: z.string().min(1, 'Language is required'),
})

const emailSchema = z.object({
  smtpHost: z.string().min(1, 'SMTP host is required'),
  smtpPort: z.number().int().positive('Port must be a positive integer'),
  smtpUser: z.string().min(1, 'SMTP username is required'),
  smtpPassword: z.string().min(1, 'SMTP password is required'),
  senderName: z.string().min(1, 'Sender name is required'),
})

type GeneralForm = z.infer<typeof generalSchema>
type EmailForm = z.infer<typeof emailSchema>

const STORAGE_KEY = 'system_settings_v1'

const SystemSettingsPage = () => {
  const [activeTab, setActiveTab] = useState<'general' | 'email'>('general')
  const [logoPreview, setLogoPreview] = useState<string | null>(null)
  const [logoFile, setLogoFile] = useState<File | null>(null)

  const { register, handleSubmit, setValue, formState: { errors }, reset } = useForm<GeneralForm>({
    resolver: zodResolver(generalSchema),
  })

  const { register: registerEmail, handleSubmit: handleEmailSubmit, setValue: setEmailValue, formState: { errors: emailErrors }, reset: resetEmail } = useForm<EmailForm>({
    resolver: zodResolver(emailSchema),
  })

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      try {
        const parsed = JSON.parse(raw)
        if (parsed.general) {
          const g = parsed.general
          setValue('companyName', g.companyName)
          setValue('defaultCurrency', g.defaultCurrency)
          setValue('timezone', g.timezone)
          setValue('language', g.language)
          if (g.logo) setLogoPreview(g.logo)
        }
        if (parsed.email) {
          const e = parsed.email
          setEmailValue('smtpHost', e.smtpHost)
          setEmailValue('smtpPort', Number(e.smtpPort))
          setEmailValue('smtpUser', e.smtpUser)
          setEmailValue('smtpPassword', e.smtpPassword)
          setEmailValue('senderName', e.senderName)
        }
      } catch (err) {
        console.error('Failed to parse settings', err)
      }
    }
  }, [setValue, setEmailValue])

  const onSaveGeneral = (data: GeneralForm) => {
    const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
    const logoData = logoPreview || null
    const payload = { ...existing, general: { ...data, logo: logoData } }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    toast.success('General settings saved')
  }

  const onSaveEmail = (data: EmailForm) => {
    const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
    const payload = { ...existing, email: data }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    toast.success('Email settings saved')
  }

  const onLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    if (!file) return
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Logo must be smaller than 10MB')
      return
    }
    setLogoFile(file)
    const url = URL.createObjectURL(file)
    setLogoPreview(url)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">System Settings</h1>
        <p className="text-muted-foreground">Configure system-wide settings for the ERP core</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Settings</CardTitle>
          <CardDescription>General system settings and email configuration</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue={activeTab}>
            <TabsList>
              <TabsTrigger value="general">General Settings</TabsTrigger>
              <TabsTrigger value="email">Email Settings</TabsTrigger>
            </TabsList>

            <div className="mt-4">
              <TabsContent value="general">
                <form onSubmit={handleSubmit(onSaveGeneral)} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="companyName">Company Name</Label>
                      <Input id="companyName" {...register('companyName')} />
                      {errors.companyName && <p className="text-sm text-destructive">{errors.companyName.message}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="defaultCurrency">Default Currency</Label>
                      <select id="defaultCurrency" {...register('defaultCurrency')} className="w-full rounded-md border px-3 py-2">
                        <option value="">Select currency</option>
                        {currencies.map((c) => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                      {errors.defaultCurrency && <p className="text-sm text-destructive">{errors.defaultCurrency.message}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="timezone">Timezone</Label>
                      <select id="timezone" {...register('timezone')} className="w-full rounded-md border px-3 py-2">
                        <option value="">Select timezone</option>
                        {timezones.map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                      {errors.timezone && <p className="text-sm text-destructive">{errors.timezone.message}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="language">Language</Label>
                      <select id="language" {...register('language')} className="w-full rounded-md border px-3 py-2">
                        <option value="">Select language</option>
                        {languages.map((l) => (
                          <option key={l.code} value={l.code}>{l.label}</option>
                        ))}
                      </select>
                      {errors.language && <p className="text-sm text-destructive">{errors.language.message}</p>}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Company Logo</Label>
                    <div className="flex items-center space-x-4">
                      <label className="inline-flex items-center cursor-pointer">
                        <input type="file" accept="image/*" onChange={onLogoChange} className="sr-only" />
                        <Button variant="outline" size="sm"><Upload className="h-4 w-4 mr-2" />Upload Logo</Button>
                      </label>
                      {logoPreview && <img src={logoPreview} alt="logo preview" className="h-12 w-12 object-contain rounded" />}
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit" size="lg"><Save className="h-4 w-4 mr-2" />Save Changes</Button>
                  </div>
                </form>
              </TabsContent>

              <TabsContent value="email">
                <form onSubmit={handleEmailSubmit(onSaveEmail)} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="smtpHost">SMTP Host</Label>
                      <Input id="smtpHost" {...registerEmail('smtpHost')} />
                      {emailErrors.smtpHost && <p className="text-sm text-destructive">{emailErrors.smtpHost.message}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="smtpPort">SMTP Port</Label>
                      <Input id="smtpPort" type="number" {...registerEmail('smtpPort', { valueAsNumber: true })} />
                      {emailErrors.smtpPort && <p className="text-sm text-destructive">{String(emailErrors.smtpPort.message)}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="smtpUser">SMTP Username</Label>
                      <Input id="smtpUser" {...registerEmail('smtpUser')} />
                      {emailErrors.smtpUser && <p className="text-sm text-destructive">{emailErrors.smtpUser.message}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="smtpPassword">SMTP Password</Label>
                      <Input id="smtpPassword" type="password" {...registerEmail('smtpPassword')} />
                      {emailErrors.smtpPassword && <p className="text-sm text-destructive">{emailErrors.smtpPassword.message}</p>}
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="senderName">Sender Name</Label>
                      <Input id="senderName" {...registerEmail('senderName')} />
                      {emailErrors.senderName && <p className="text-sm text-destructive">{emailErrors.senderName.message}</p>}
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit" size="lg"><Save className="h-4 w-4 mr-2" />Save Changes</Button>
                  </div>
                </form>
              </TabsContent>
            </div>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

export default SystemSettingsPage
