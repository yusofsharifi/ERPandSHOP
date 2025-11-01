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
import PartnerAgingPage from './pages/finance/PartnerAgingPage'
import TreasuryAccountsPage from './pages/finance/treasury/AccountsPage'
import TreasuryTransferPage from './pages/finance/treasury/TransferPage'
import TreasuryReconciliationPage from './pages/finance/treasury/ReconciliationPage'
import TreasuryCashflowPage from './pages/finance/treasury/CashflowPage'
import EmployeesPage from './pages/hr/EmployeesPage'
import PayrollPage from './pages/hr/PayrollPage'
import PayrollDetailsPage from './pages/hr/PayrollDetailsPage'
import SalaryTemplatesPage from './pages/hr/SalaryTemplatesPage'
import TaxSettingsPage from './pages/hr/TaxSettingsPage'
import PayrollPeriodsPage from './pages/hr/PayrollPeriodsPage'
import PayrollEmployeesPage from './pages/hr/PayrollEmployeesPage'
import PayrollPeriodDetailsPage from './pages/hr/PayrollPeriodDetailsPage'
import PayrollPayslipPage from './pages/hr/PayrollPayslipPage'
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
              <Route path="finance/partners" element={<PartnersPage />} />
              <Route path="finance/partners/:id/aging" element={<PartnerAgingPage />} />
              <Route path="finance/invoices" element={<InvoicesPage />} />
              <Route path="finance/invoices/new" element={<InvoiceNewPage />} />
              <Route path="finance/invoices/:id" element={<InvoiceViewPage />} />
              <Route path="finance/payments" element={<PaymentsPage />} />

              {/* Treasury */}
              <Route path="finance/treasury/accounts" element={<TreasuryAccountsPage />} />
              <Route path="finance/treasury/transfer" element={<TreasuryTransferPage />} />
              <Route path="finance/treasury/reconciliation" element={<TreasuryReconciliationPage />} />
              <Route path="finance/treasury/cashflow" element={<TreasuryCashflowPage />} />

              {/* HR */}
              <Route path="hr" element={<EmployeesPage />} />
              <Route path="hr/employees" element={<EmployeesPage />} />
              <Route path="hr/payroll" element={<PayrollPage />} />
              <Route path="hr/payroll/periods" element={<PayrollPeriodsPage />} />
              <Route path="hr/payroll/employees" element={<PayrollEmployeesPage />} />
              <Route path="hr/payroll/:period_id/details" element={<PayrollPeriodDetailsPage />} />
              <Route path="hr/payroll/:id/payslip" element={<PayrollPayslipPage />} />
              <Route path="hr/payroll/:id" element={<PayrollDetailsPage />} />
              <Route path="hr/salary-templates" element={<SalaryTemplatesPage />} />
              <Route path="hr/tax-settings" element={<TaxSettingsPage />} />
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
