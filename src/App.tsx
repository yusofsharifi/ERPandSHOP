import { useTranslation } from 'react-i18next'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import DashboardLayout from './layouts/DashboardLayout'

// Pages
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import AccountsPage from './pages/finance/AccountsPage'
import JournalEntriesPage from './pages/finance/JournalEntriesPage'
import JournalEntryNewPage from './pages/finance/JournalEntryNewPage'
import TrialBalancePage from './pages/finance/TrialBalancePage'
import PartnersPage from './pages/finance/PartnersPage'
import InvoicesPage from './pages/finance/InvoicesPage'
import InvoiceNewPage from './pages/finance/InvoiceNewPage'
import InvoiceViewPage from './pages/finance/InvoiceViewPage'
import PaymentsPage from './pages/finance/PaymentsPage'
import ProfilePage from './pages/ProfilePage'
import SettingsPage from './pages/SettingsPage'
import UsersPage from './pages/admin/UsersPage'
import SystemSettingsPage from './pages/admin/SystemSettingsPage'
import RolesPage from './pages/admin/RolesPage'
import NotificationsPage from './pages/admin/NotificationsPage'
import { Routes, Route, Navigate } from 'react-router-dom'

function App() {
  const { i18n } = useTranslation()
  
  return (
    <ThemeProvider>
      <AuthProvider>
        <div className={`min-h-screen bg-background text-foreground ${i18n.language === 'fa' ? 'font-farsi' : ''}`}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Protected Routes */}
            <Route path="/" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="roles" element={<RolesPage />} />
              <Route path="notifications" element={<NotificationsPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="admin/system-settings" element={<SystemSettingsPage />} />
              {/* Finance */}
              <Route path="finance/accounts" element={<AccountsPage />} />
              <Route path="finance/journal-entries" element={<JournalEntriesPage />} />
              <Route path="finance/journal-entries/new" element={<JournalEntryNewPage />} />
              <Route path="finance/reports/trial-balance" element={<TrialBalancePage />} />
            </Route>
            
            {/* Catch all */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
