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
      'finance.journal_list': 'Journal Entries',
      // Treasury
      'treasury.accounts': 'Treasury Accounts',
      'treasury.cash_accounts': 'Cash Accounts',
      'treasury.bank_accounts': 'Bank Accounts',
      'treasury.low_balance': 'Low balance',
      'treasury.transfer': 'Transfer',
      'treasury.new_transfer': 'New Transfer',
      'treasury.from_type': 'From Type',
      'treasury.from_account': 'From Account',
      'treasury.to_type': 'To Type',
      'treasury.to_account': 'To Account',
      'treasury.amount': 'Amount',
      'treasury.preview_balance': 'Preview balance after transfer',
      'treasury.reset': 'Reset',
      'treasury.confirm_transfer': 'Confirm Transfer',
      'treasury.are_you_sure_transfer': 'Are you sure you want to transfer',
      'treasury.suggest_matches': 'Suggest matches',
      'treasury.matches': 'Matches',
      'treasury.apply': 'Apply',
      'treasury.upload_statement': 'Upload Statement',
      'treasury.selected': 'Selected',
      'treasury.field_mapping': 'Field mapping',
      'treasury.date_field': 'Date field',
      'treasury.description_field': 'Description field',
      'treasury.amount_field': 'Amount field',
      'treasury.cashflow': 'Cash Flow',
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
      'finance.journal_list': 'اسناد حسابداری',
      // Treasury
      'treasury.accounts': 'حساب‌های خزانه',
      'treasury.cash_accounts': 'حساب‌های نقدی',
      'treasury.bank_accounts': 'حساب‌های بانکی',
      'treasury.low_balance': 'موجودی کم',
      'treasury.transfer': 'انتقال',
      'treasury.new_transfer': 'انتقال جدید',
      'treasury.from_type': 'نوع مبدا',
      'treasury.from_account': 'حساب مبدا',
      'treasury.to_type': 'نوع مقصد',
      'treasury.to_account': 'حساب مقصد',
      'treasury.amount': 'مبلغ',
      'treasury.preview_balance': 'پیش‌نمایش موجودی پس از انتقال',
      'treasury.reset': 'بازنشانی',
      'treasury.confirm_transfer': 'تأیید انتقال',
      'treasury.are_you_sure_transfer': 'آیا از انجام انتقال مطمئن هستید؟',
      'treasury.suggest_matches': 'پیشنهاد تطبیق‌ها',
      'treasury.matches': 'تطبیق‌ها',
      'treasury.apply': 'اعمال',
      'treasury.upload_statement': 'بارگذاری صورت‌حساب',
      'treasury.selected': 'انتخاب شده',
      'treasury.field_mapping': 'نگاشت فیلدها',
      'treasury.date_field': 'فیلد تاریخ',
      'treasury.description_field': 'فیلد شرح',
      'treasury.amount_field': 'فیلد مبلغ',
      'treasury.cashflow': 'جریان نقدی'
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
