import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useTranslation } from 'react-i18next'
import { Eye, EyeOff, Mail, Lock } from 'lucide-react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'

import { useAuth } from '@/contexts/AuthContext'
import AuthCard from '@/components/AuthCard'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { isValidEmail } from '@/lib/utils'

const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').refine(isValidEmail, 'Invalid email format'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [show2FA, setShow2FA] = useState(false)
  const [otp, setOtp] = useState('')
  const [emailFor2FA, setEmailFor2FA] = useState('')

  const { login, isAuthenticated } = useAuth()
  const { t } = useTranslation()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsLoading(true)
      // Try login - AuthContext has fallback in DEV
      await login(data.email, data.password)
      // If backend indicates 2FA required, it should respond accordingly. Here we assume login resolved.
    } catch (error: any) {
      // If backend responded with 2FA requirement, show 2FA input
      if (error && error?.message === '2FA_REQUIRED') {
        setShow2FA(true)
        setEmailFor2FA(data.email)
        toast('Enter your 2FA code', { icon: '🔒' })
        return
      }
      console.error('Login failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const verify2FA = async () => {
    setIsLoading(true)
    try {
      // Call backend 2FA verify endpoint
      const response = await fetch('/api/auth/2fa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailFor2FA, code: otp }),
      })

      if (response.ok) {
        const data = await response.json()
        // store token and user as in AuthContext--but easiest is to call login again or set storage
        // For now, assume backend returns access_token and user
        localStorage.setItem('bizgenius_token', data.access_token)
        localStorage.setItem('bizgenius_user', JSON.stringify(data.user))
        toast.success('2FA verified, logged in')
        window.location.href = '/dashboard'
      } else {
        toast.error('Invalid 2FA code')
      }
    } catch (err) {
      console.error('2FA verify error', err)
      toast.error('2FA verification failed')
    } finally {
      setIsLoading(false)
    }
  }

  const continueWithProvider = async (provider: 'google' | 'github') => {
    toast.loading(`Redirecting to ${provider}...`)
    // Simulate OAuth popup delay
    await new Promise((res) => setTimeout(res, 1000))
    // Simulate successful OAuth login
    const demoEmail = provider === 'google' ? 'google@bizgenius.local' : 'github@bizgenius.local'
    const demoUser = {
      id: `oauth-${provider}-1`,
      email: demoEmail,
      name: `${provider.charAt(0).toUpperCase() + provider.slice(1)} User`,
      role: 'User',
      avatar: '',
    }
    localStorage.setItem('bizgenius_token', `dev-token-${demoEmail}`)
    localStorage.setItem('bizgenius_user', JSON.stringify(demoUser))
    toast.dismiss()
    toast.success('Logged in via ' + provider)
    window.location.href = '/dashboard'
  }

  return (
    <AuthCard
      title={t('login')}
      description={t('welcome')}
    >
      {/* Social Buttons */}
      <div className="space-y-3">
        <Button variant="outline" size="lg" className="w-full flex items-center justify-center" onClick={() => continueWithProvider('google')}>
          Continue with Google
        </Button>
        <Button variant="outline" size="lg" className="w-full flex items-center justify-center" onClick={() => continueWithProvider('github')}>
          Continue with GitHub
        </Button>
      </div>

      <div className="my-4 flex items-center text-sm text-muted-foreground">
        <div className="flex-1 h-px bg-border" />
        <div className="px-3">or continue with email</div>
        <div className="flex-1 h-px bg-border" />
      </div>

      {!show2FA ? (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Email Field */}
          <div className="space-y-2">
            <Label htmlFor="email">{t('email')}</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                id="email"
                type="email"
                placeholder="john@example.com"
                className="pl-10"
                {...register('email')}
              />
            </div>
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>

          {/* Password Field */}
          <div className="space-y-2">
            <Label htmlFor="password">{t('password')}</Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                className="pl-10 pr-10"
                {...register('password')}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
            {errors.password && (
              <p className="text-sm text-destructive">{errors.password.message}</p>
            )}
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <input
                id="remember"
                type="checkbox"
                className="rounded border-gray-300"
              />
              <Label htmlFor="remember" className="text-sm">
                {t('rememberMe')}
              </Label>
            </div>
            <Link
              to="/forgot-password"
              className="text-sm text-primary hover:underline"
            >
              {t('forgotPassword')}
            </Link>
          </div>

          {/* Submit Button */}
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full"
              />
            ) : (
              t('signIn')
            )}
          </Button>

          {/* Register Link */}
          <div className="text-center text-sm">
            <span className="text-muted-foreground">{t('dontHaveAccount')} </span>
            <Link to="/register" className="text-primary hover:underline font-medium">
              {t('signUp')}
            </Link>
          </div>
        </form>
      ) : (
        <div className="space-y-4">
          <Label htmlFor="otp">Two-factor code</Label>
          <Input
            id="otp"
            type="text"
            placeholder="123456"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
          />
          <div className="flex gap-2">
            <Button onClick={verify2FA} className="flex-1">Verify</Button>
            <Button variant="ghost" onClick={() => setShow2FA(false)}>Cancel</Button>
          </div>
        </div>
      )}
    </AuthCard>
  )
}

export default LoginPage
