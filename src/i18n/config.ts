import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import { getStorageItem, setStorageItem, STORAGE_KEYS } from '@/lib/utils'

// Translation resources
const resources = {
  en: {
    translation: {
      // Authentication
      'login': 'Login',
      'register': 'Register',
      'logout': 'Logout',
      'email': 'Email',
      'password': 'Password',
      'confirmPassword': 'Confirm Password',
      'fullName': 'Full Name',
      'forgotPassword': 'Forgot Password?',
      'rememberMe': 'Remember me',
      'signIn': 'Sign In',
      'signUp': 'Sign Up',
      'createAccount': 'Create Account',
      'alreadyHaveAccount': 'Already have an account?',
      'dontHaveAccount': "Don't have an account?",
      
      // Navigation
      'dashboard': 'Dashboard',
      'profile': 'Profile',
      'settings': 'Settings',
      'notifications': 'Notifications',
      
      // Common
      'save': 'Save',
      'cancel': 'Cancel',
      'submit': 'Submit',
      'loading': 'Loading...',
      'error': 'Error',
      'success': 'Success',
      'welcome': 'Welcome',
      'search': 'Search',
      'menu': 'Menu',
      
      // Profile
      'userProfile': 'User Profile',
      'editProfile': 'Edit Profile',
      'changePassword': 'Change Password',
      'uploadAvatar': 'Upload Avatar',
      
      // Theme
      'lightMode': 'Light Mode',
      'darkMode': 'Dark Mode',
      'language': 'Language',
      
      // Messages
      'loginSuccess': 'Login successful!',
      'loginError': 'Login failed. Please check your credentials.',
      'registerSuccess': 'Registration successful!',
      'profileUpdated': 'Profile updated successfully!',
      // Finance GL
      'gl.labels.total_debit': 'Total Debit',
      'gl.labels.total_credit': 'Total Credit',
      'gl.labels.difference': 'Difference',
      'gl.labels.date': 'Date',
      'gl.labels.description': 'Description',
      'gl.labels.debit': 'Debit',
      'gl.labels.credit': 'Credit',
      'gl.labels.account': 'Account',
      'gl.error.not_balanced': 'Total debit and credit must match',
      'gl.success.entry_saved': 'Journal entry saved',
      'finance.journal_new': 'New Journal Entry',
      'finance.journal_list': 'Journal Entries'
    }
  },
  fa: {
    translation: {
      // Authentication
      'login': 'ورود',
      'register': 'ثبت‌نام',
      'logout': 'خروج',
      'email': 'ایمیل',
      'password': 'رمز عبور',
      'confirmPassword': 'تأیید رمز عبور',
      'fullName': 'نام کامل',
      'forgotPassword': 'رمز عبور را فراموش کرده‌اید؟',
      'rememberMe': 'مرا به خاطر بسپار',
      'signIn': 'ورود',
      'signUp': 'ثبت‌نام',
      'createAccount': 'ایجاد حساب کاربری',
      'alreadyHaveAccount': 'حساب کاربری دارید؟',
      'dontHaveAccount': 'حساب کاربری ندارید؟',
      
      // Navigation
      'dashboard': 'داشبورد',
      'profile': 'پروفایل کاربر',
      'settings': 'تنظیمات',
      'notifications': 'اعلان‌ها',
      
      // Common
      'save': 'ذخیره',
      'cancel': 'لغو',
      'submit': 'ارسال',
      'loading': 'در حال بارگذاری...',
      'error': 'خطا',
      'success': 'موفقیت‌آمیز',
      'welcome': 'خوش‌آمدید',
      'search': 'جستجو',
      'menu': 'منو',
      
      // Profile
      'userProfile': 'پروفایل کاربر',
      'editProfile': 'ویرایش پروفایل',
      'changePassword': 'تغییر رمز عبور',
      'uploadAvatar': 'آپلود تصویر',
      
      // Theme
      'lightMode': 'حالت روشن',
      'darkMode': 'حالت تاریک',
      'language': 'زبان',
      
      // Messages
      'loginSuccess': 'ورود موفقیت‌آمیز بود!',
      'loginError': 'ورود ناموفق. لطفا اطلاعات ورود را بررسی کنید.',
      'registerSuccess': 'ثبت‌نام موفقیت‌آمیز بود!',
      'profileUpdated': 'پروفایل با موفقیت بروزرسانی شد!',
      // Finance GL
      'gl.labels.total_debit': 'جمع بدهکار',
      'gl.labels.total_credit': 'جمع بستانکار',
      'gl.labels.difference': 'تفاضل',
      'gl.labels.date': 'تاریخ',
      'gl.labels.description': 'شرح',
      'gl.labels.debit': 'بدهکار',
      'gl.labels.credit': 'بستانکار',
      'gl.labels.account': 'سرفصل',
      'gl.error.not_balanced': 'جمع بدهکاری و بستانکاری برابر نیست',
      'gl.success.entry_saved': 'سند ذخیره شد',
      'finance.journal_new': 'سند جدید',
      'finance.journal_list': 'اسناد حسابداری'
    }
  }
}

// Get saved language or default to 'en'
const savedLanguage = getStorageItem(STORAGE_KEYS.LANGUAGE) || 'en'

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage,
    fallbackLng: 'en',
    
    interpolation: {
      escapeValue: false, // react already does escaping
    },
    
    // Auto-detect RTL
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  })

// Save language changes to localStorage
i18n.on('languageChanged', (lng) => {
  setStorageItem(STORAGE_KEYS.LANGUAGE, lng)
  
  // Set document direction for RTL
  const direction = lng === 'fa' ? 'rtl' : 'ltr'
  document.documentElement.setAttribute('dir', direction)
  document.documentElement.setAttribute('lang', lng)
})

// Set initial direction
const direction = savedLanguage === 'fa' ? 'rtl' : 'ltr'
document.documentElement.setAttribute('dir', direction)
document.documentElement.setAttribute('lang', savedLanguage)

export default i18n
