import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { Camera, Save, Lock, User, Mail, Phone, MapPin, Calendar } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { isValidEmail } from '@/lib/utils'

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().min(1, 'Email is required').refine(isValidEmail, 'Invalid email format'),
  phone: z.string().optional(),
  address: z.string().optional(),
  bio: z.string().optional(),
})

const passwordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type ProfileFormData = z.infer<typeof profileSchema>
type PasswordFormData = z.infer<typeof passwordSchema>

const ProfilePage = () => {
  const [isEditing, setIsEditing] = useState(false)
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { user, updateProfile } = useAuth()
  const { t, i18n } = useTranslation()
  const isRTL = i18n.language === 'fa'

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
    reset: resetProfile,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user?.name || '',
      email: user?.email || '',
      phone: '',
      address: '',
      bio: '',
    },
  })

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors },
    reset: resetPassword,
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  })

  const onProfileSubmit = async (data: ProfileFormData) => {
    try {
      setIsLoading(true)
      await updateProfile(data)
      setIsEditing(false)
    } catch (error) {
      console.error('Profile update failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const onPasswordSubmit = async (data: PasswordFormData) => {
    try {
      setIsLoading(true)
      // Implement password change API call
      console.log('Password change:', data)
      setIsChangingPassword(false)
      resetPassword()
    } catch (error) {
      console.error('Password change failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAvatarUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Implement avatar upload logic
      console.log('Avatar upload:', file)
    }
  }

  const cancelEdit = () => {
    setIsEditing(false)
    resetProfile()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold tracking-tight">{t('userProfile')}</h1>
        <p className="text-muted-foreground">
          Manage your account settings and personal information
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Picture Card */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-center">Profile Picture</CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-4">
              <div className="relative w-32 h-32 mx-auto">
                <div className="w-32 h-32 rounded-full bg-muted flex items-center justify-center overflow-hidden">
                  {user?.avatar ? (
                    <img 
                      src={user.avatar} 
                      alt={user.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <User className="h-16 w-16 text-muted-foreground" />
                  )}
                </div>
                <label 
                  htmlFor="avatar-upload"
                  className="absolute bottom-0 right-0 p-2 bg-primary text-primary-foreground rounded-full cursor-pointer hover:bg-primary/90 transition-colors"
                >
                  <Camera className="h-4 w-4" />
                  <input
                    id="avatar-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                  />
                </label>
              </div>
              <div>
                <h3 className="font-semibold text-lg">{user?.name}</h3>
                <p className="text-sm text-muted-foreground">{user?.email}</p>
                <span className="inline-block px-3 py-1 text-xs bg-primary/10 text-primary rounded-full mt-2">
                  {user?.role}
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Profile Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader>
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div>
                  <CardTitle>{t('editProfile')}</CardTitle>
                  <CardDescription>
                    Update your personal information and contact details
                  </CardDescription>
                </div>
                {!isEditing && (
                  <Button onClick={() => setIsEditing(true)}>
                    Edit Profile
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleProfileSubmit(onProfileSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Name */}
                  <div className="space-y-2">
                    <Label htmlFor="name" className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                      <User className="h-4 w-4" />
                      <span>{t('fullName')}</span>
                    </Label>
                    <Input
                      id="name"
                      disabled={!isEditing}
                      {...registerProfile('name')}
                    />
                    {profileErrors.name && (
                      <p className="text-sm text-destructive">{profileErrors.name.message}</p>
                    )}
                  </div>

                  {/* Email */}
                  <div className="space-y-2">
                    <Label htmlFor="email" className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                      <Mail className="h-4 w-4" />
                      <span>{t('email')}</span>
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      disabled={!isEditing}
                      {...registerProfile('email')}
                    />
                    {profileErrors.email && (
                      <p className="text-sm text-destructive">{profileErrors.email.message}</p>
                    )}
                  </div>

                  {/* Phone */}
                  <div className="space-y-2">
                    <Label htmlFor="phone" className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                      <Phone className="h-4 w-4" />
                      <span>Phone</span>
                    </Label>
                    <Input
                      id="phone"
                      type="tel"
                      disabled={!isEditing}
                      {...registerProfile('phone')}
                    />
                  </div>

                  {/* Address */}
                  <div className="space-y-2">
                    <Label htmlFor="address" className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                      <MapPin className="h-4 w-4" />
                      <span>Address</span>
                    </Label>
                    <Input
                      id="address"
                      disabled={!isEditing}
                      {...registerProfile('address')}
                    />
                  </div>
                </div>

                {/* Bio */}
                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  <textarea
                    id="bio"
                    rows={3}
                    disabled={!isEditing}
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...registerProfile('bio')}
                  />
                </div>

                {/* Action Buttons */}
                {isEditing && (
                  <div className={`flex space-x-4 ${isRTL ? 'space-x-reverse' : ''}`}>
                    <Button type="submit" disabled={isLoading}>
                      <Save className="h-4 w-4 mr-2" />
                      {isLoading ? 'Saving...' : t('save')}
                    </Button>
                    <Button type="button" variant="outline" onClick={cancelEdit}>
                      {t('cancel')}
                    </Button>
                  </div>
                )}
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Change Password */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div>
                <CardTitle className={`flex items-center space-x-2 ${isRTL ? 'space-x-reverse' : ''}`}>
                  <Lock className="h-5 w-5" />
                  <span>{t('changePassword')}</span>
                </CardTitle>
                <CardDescription>
                  Update your password to keep your account secure
                </CardDescription>
              </div>
              {!isChangingPassword && (
                <Button onClick={() => setIsChangingPassword(true)}>
                  Change Password
                </Button>
              )}
            </div>
          </CardHeader>
          {isChangingPassword && (
            <CardContent>
              <form onSubmit={handlePasswordSubmit(onPasswordSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="currentPassword">Current Password</Label>
                  <Input
                    id="currentPassword"
                    type="password"
                    {...registerPassword('currentPassword')}
                  />
                  {passwordErrors.currentPassword && (
                    <p className="text-sm text-destructive">{passwordErrors.currentPassword.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="newPassword">New Password</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    {...registerPassword('newPassword')}
                  />
                  {passwordErrors.newPassword && (
                    <p className="text-sm text-destructive">{passwordErrors.newPassword.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    {...registerPassword('confirmPassword')}
                  />
                  {passwordErrors.confirmPassword && (
                    <p className="text-sm text-destructive">{passwordErrors.confirmPassword.message}</p>
                  )}
                </div>

                <div className={`flex space-x-4 ${isRTL ? 'space-x-reverse' : ''}`}>
                  <Button type="submit" disabled={isLoading}>
                    <Lock className="h-4 w-4 mr-2" />
                    {isLoading ? 'Updating...' : 'Update Password'}
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => {
                      setIsChangingPassword(false)
                      resetPassword()
                    }}
                  >
                    {t('cancel')}
                  </Button>
                </div>
              </form>
            </CardContent>
          )}
        </Card>
      </motion.div>
    </div>
  )
}

export default ProfilePage
