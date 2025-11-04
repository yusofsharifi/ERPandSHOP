import React from 'react'
import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import {
  Home,
  User,
  Settings,
  LogOut,
  X,
  DollarSign,
  Package,
  Users,
  BarChart3,
  Store,
  Building2,
  Bell,
  ChevronDown,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/Button'

interface SidebarMenuProps {
  onClose: () => void
}

const SidebarMenu = ({ onClose }: SidebarMenuProps) => {
  const { logout, user } = useAuth()
  const { t, i18n } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const isRTL = i18n.language === 'fa'

  const menuItems: any[] = [
    { icon: Home, label: t('nav.dashboard', 'Dashboard'), path: '/dashboard' },
    { icon: Users, label: t('nav.users', 'Users'), path: '/users' },
    { icon: Users, label: t('nav.roles', 'Roles'), path: '/roles', adminOnly: true },
    {
      icon: DollarSign,
      label: t('nav.finance', 'Finance'),
      children: [
        { label: t('nav.finance', 'Finance'), path: '/finance' },
        { label: 'Accounts', path: '/finance/accounts' },
        { label: 'Journal Entries', path: '/finance/journal-entries' },
        { label: 'Invoices', path: '/finance/invoices' },
      ],
    },
    {
      icon: Package,
      label: t('nav.inventory', 'Inventory'),
      children: [
        { label: 'Products', path: '/inventory/products' },
        { label: 'Stock Levels', path: '/inventory/stock' },
      ],
    },
    { icon: Users, label: t('nav.crm', 'CRM'), path: '/crm' },
    {
      icon: Building2,
      label: t('nav.hr', 'HR'),
      children: [
        { label: 'Employees', path: '/hr/employees' },
        { label: 'Payroll', path: '/hr/payroll' },
      ],
    },
    { icon: BarChart3, label: t('nav.analytics', 'Analytics'), path: '/analytics' },
    { icon: Bell, label: t('nav.notifications', 'Notifications'), path: '/notifications' },
    { icon: Store, label: t('nav.ecommerce', 'E-Commerce'), path: '/ecommerce' },
    // Sales group
    {
      icon: DollarSign,
      label: t('nav.sales', 'Sales'),
      children: [
        { label: t('nav.sales_orders', 'Sales Orders'), path: '/sales/orders' },
        { label: t('nav.sales_invoices', 'Sales Invoices'), path: '/sales/invoices' },
      ],
    },
  ]

  const settingsItems = [
    { icon: User, label: t('nav.profile', 'Profile'), path: '/profile' },
    { icon: Settings, label: t('nav.settings', 'Settings'), path: '/settings' },
    // System Settings - visible to admins
    { icon: Settings, label: t('nav.system_settings', 'System Settings'), path: '/admin/system-settings', adminOnly: true },
  ]

  const handleLogout = () => {
    logout()
    onClose()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className={`flex items-center justify-between p-4 border-b border-border ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">BG</span>
          </div>
          <div>
            <h2 className="font-semibold text-sm">BizGenius</h2>
            <p className="text-xs text-muted-foreground">ERP & E-Commerce</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="lg:hidden h-8 w-8">
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* User Info */}
      {user && (
        <div className="p-4 border-b border-border">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center overflow-hidden">
              {user.avatar ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={user.avatar} alt={user.name} className="w-10 h-10 rounded-full object-cover" />
              ) : (
                <User className="h-5 w-5 text-muted-foreground" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">{user.name}</p>
              <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              <p className="text-xs text-primary">{user.role}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        <div className="space-y-1">
          {menuItems.map((item) => {
            const active = location.pathname === item.path || location.pathname.startsWith(item.path + '/')
            return (
              <button
                key={item.path}
                onClick={() => {
                  const nav = navigate || ((p:string)=>{ window.history.pushState({}, '', p); window.dispatchEvent(new PopStateEvent('popstate')) })
                  nav(item.path)
                  // close sidebar only on small screens
                  if (typeof window !== 'undefined' && window.innerWidth < 1024) onClose()
                }}
                className={`w-full text-left flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${isRTL ? 'space-x-reverse' : ''} ${active ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted'}`}
              >
                <item.icon className="h-4 w-4" />
                <span className="text-sm font-medium">{item.label}</span>
              </button>
            )
          })}
        </div>

        <div className="pt-4 border-t border-border">
          <div className="space-y-1">
            {settingsItems.map((item) => {
              if ((item as any).adminOnly && user?.role !== 'Admin') return null
              const active = location.pathname === item.path || location.pathname.startsWith(item.path + '/')
              return (
                <button
                  key={item.path}
                  onClick={() => {
                    const nav = navigate || ((p:string)=>{ window.history.pushState({}, '', p); window.dispatchEvent(new PopStateEvent('popstate')) })
                    nav(item.path)
                    if (typeof window !== 'undefined' && window.innerWidth < 1024) onClose()
                  }}
                  className={`w-full text-left flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${isRTL ? 'space-x-reverse' : ''} ${active ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted'}`}
                >
                  <item.icon className="h-4 w-4" />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-border">
        <Button variant="ghost" onClick={handleLogout} className={`w-full justify-start ${isRTL ? 'flex-row-reverse' : ''}`}>
          <LogOut className="h-4 w-4" />
          <span className="ml-3">{t('logout')}</span>
        </Button>
      </div>
    </div>
  )
}

export default SidebarMenu
