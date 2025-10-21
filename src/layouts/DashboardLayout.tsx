import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion, AnimatePresence } from 'framer-motion'
import SidebarMenu from '@/components/SidebarMenu'
import NavbarHeader from '@/components/NavbarHeader'

const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { i18n } = useTranslation()
  const isRTL = i18n.language === 'fa'

  const shiftClass = sidebarOpen ? (isRTL ? 'mr-64 lg:mr-64' : 'ml-64 lg:ml-64') : ''

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: isRTL ? 300 : -300 }}
            animate={{ x: 0 }}
            exit={{ x: isRTL ? 300 : -300 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className={`fixed top-0 ${isRTL ? 'right-0' : 'left-0'} z-50 h-full w-64 bg-card border-r border-border shadow-lg lg:translate-x-0`}
          >
            <SidebarMenu onClose={() => setSidebarOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className={`transition-all duration-300 ${shiftClass}`}>
        {/* Navbar */}
        <NavbarHeader
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />

        {/* Page Content */}
        <main className="p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
