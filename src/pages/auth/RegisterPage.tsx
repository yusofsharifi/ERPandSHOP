import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useTranslation } from 'react-i18next'
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'

import { useAuth } from '@/contexts/AuthContext'
import AuthCard from '@/components/AuthCard'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { isValidEmail, isValidPassword } from '@/lib/utils'

const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().min(1, 'Email is required').refine(isValidEmail, 'Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters').refine(isValidPassword, 'Password is too weak'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type RegisterFormData = z.infer<typeof registerSchema>

const RegisterPage = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { register: registerUser, isAuthenticated } = useAuth()
  const { t } = useTranslation()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setIsLoading(true)
      await registerUser(data.name, data.email, data.password)
    } catch (error) {
      console.error('Registration failed:', error)
      toast.error('Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const continueWithProvider = async (provider: 'google' | 'github') => {
    toast.loading(`Redirecting to ${provider}...`)
    await new Promise((res) => setTimeout(res, 1000))
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
      title={t('register')}
      description={t('createAccount')}
    >
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

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Name Field */}
        <div className="space-y-2">
          <Label htmlFor="name">{t('fullName')}</Label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              id="name"
              type="text"
              placeholder="John Doe"
              className="pl-10"
              {...register('name')}
            />
          </div>
          {errors.name && (
            <p className="text-sm text-destructive">{errors.name.message}</p>
          )}
        </div>

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

        {/* Confirm Password Field */}
        <div className="space-y-2">
          <Label htmlFor="confirmPassword">{t('confirmPassword')}</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              id="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="••••••••"
              className="pl-10 pr-10"
              {...register('confirmPassword')}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          </div>
          {errors.confirmPassword && (
            <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
          )}
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
            t('signUp')
          )}
        </Button>

        {/* Login Link */}
        <div className="text-center text-sm">
          <span className="text-muted-foreground">{t('alreadyHaveAccount')} </span>
          <Link to="/login" className="text-primary hover:underline font-medium">
            {t('signIn')}
          </Link>
        </div>
      </form>
    </AuthCard>
  )
}

export default RegisterPage
