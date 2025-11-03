import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Bell, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTranslation } from 'react-i18next'

interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'warning' | 'error' | 'success'
  timestamp: string | Date
  read: boolean
}

const NotificationBell = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const { t, i18n } = useTranslation()
  const isRTL = i18n.language === 'fa'

  const API_BASE = '/api/notifications'

  const fetchNotifications = async () => {
    try {
      const res = await fetch(API_BASE)
      if (!res.ok) throw new Error('Network response was not ok')
      const data = await res.json()
      // Expecting array of notifications
      const list: Notification[] = (data || []).map((n: any) => ({
        ...n,
        timestamp: n.timestamp ? new Date(n.timestamp).toISOString() : new Date().toISOString(),
      }))
      setNotifications(list)
      setUnreadCount(list.filter(n => !n.read).length)
    } catch (err) {
      // Fallback to mock notifications if API not available
      console.warn('Failed to fetch notifications, using fallback', err)
      const mockNotifications: Notification[] = [
        {
          id: '1',
          title: 'New Order',
          message: 'You have received a new order #12345',
          type: 'info',
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          read: false,
        },
        {
          id: '2',
          title: 'Low Stock Alert',
          message: 'Product "Laptop" is running low on stock',
          type: 'warning',
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          read: false,
        },
        {
          id: '3',
          title: 'Payment Received',
          message: 'Payment of $500 has been processed successfully',
          type: 'success',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          read: true,
        },
      ]
      setNotifications(mockNotifications)
      setUnreadCount(mockNotifications.filter(n => !n.read).length)
    }
  }

  useEffect(() => {
    // initial fetch
    fetchNotifications()
  }, [])

  useEffect(() => {
    if (isOpen) {
      // Refresh when opening
      fetchNotifications()
    }
  }, [isOpen])

  const markAsRead = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/${id}/mark-read`, { method: 'POST' })
      if (!res.ok) throw new Error('Failed to mark read')
    } catch (err) {
      console.warn('Mark read API failed, updating locally', err)
    } finally {
      setNotifications(prev => prev.map(n => (n.id === id ? { ...n, read: true } : n)))
      setUnreadCount(prev => Math.max(0, prev - 1))
    }
  }

  const markAllAsRead = async () => {
    try {
      const res = await fetch(`${API_BASE}/mark-all-read`, { method: 'POST' })
      if (!res.ok) throw new Error('Failed')
    } catch (err) {
      console.warn('Mark all read API failed', err)
    } finally {
      setNotifications(prev => prev.map(n => ({ ...n, read: true })))
      setUnreadCount(0)
    }
  }

  const removeNotification = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('Failed')
    } catch (err) {
      console.warn('Delete notification API failed', err)
    } finally {
      const notification = notifications.find(n => n.id === id)
      if (notification && !notification.read) setUnreadCount(prev => Math.max(0, prev - 1))
      setNotifications(prev => prev.filter(n => n.id !== id))
    }
  }

  const getTypeColor = (type: Notification['type']) => {
    switch (type) {
      case 'success': return 'text-green-500'
      case 'warning': return 'text-yellow-500'
      case 'error': return 'text-red-500'
      default: return 'text-blue-500'
    }
  }

  const formatTime = (timestamp: string | Date) => {
    const ts = typeof timestamp === 'string' ? new Date(timestamp) : new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - ts.getTime()
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
  }

  return (
    <div className="relative">
      {/* Notification Bell Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
        className="relative"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </Button>

      {/* Notification Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />
            
            {/* Dropdown Panel */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              transition={{ duration: 0.2 }}
              className={`absolute top-12 ${isRTL ? 'left-0' : 'right-0'} z-50 w-80 bg-card border border-border rounded-lg shadow-lg`}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h3 className="font-semibold text-sm">{t('notifications')}</h3>
                {unreadCount > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={markAllAsRead}
                    className="text-xs"
                  >
                    Mark all read
                  </Button>
                )}
              </div>

              {/* Notifications List */}
              <div className="max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground">
                    <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No notifications</p>
                  </div>
                ) : (
                  <div className="divide-y divide-border">
                    {notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={`p-4 hover:bg-muted/50 transition-colors ${
                          !notification.read ? 'bg-muted/30' : ''
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0 space-y-1">
                            <div className="flex items-center space-x-2">
                              <div className={`w-2 h-2 rounded-full ${getTypeColor(notification.type)}`} />
                              <h4 className="text-sm font-medium truncate">
                                {notification.title}
                              </h4>
                              {!notification.read && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground line-clamp-2">
                              {notification.message}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {formatTime(notification.timestamp)}
                            </p>
                          </div>
                          <div className="flex items-center space-x-1 ml-2">
                            {!notification.read && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => markAsRead(notification.id)}
                                className="h-6 w-6 p-0"
                              >
                                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeNotification(notification.id)}
                              className="h-6 w-6 p-0"
                            >
                              <X className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Footer */}
              {notifications.length > 0 && (
                <div className="p-3 border-t border-border">
                  <Button variant="ghost" size="sm" className="w-full text-xs">
                    View all notifications
                  </Button>
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

export default NotificationBell
