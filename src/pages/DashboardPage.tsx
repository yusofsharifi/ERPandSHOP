import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { 
  DollarSign, 
  Package, 
  Users, 
  TrendingUp, 
  ShoppingCart,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { useAuth } from '@/contexts/AuthContext'
import SimpleChart from '@/components/ui/SimpleChart'

const DashboardPage = () => {
  const { t, i18n } = useTranslation()
  const { user } = useAuth()
  const isRTL = i18n.language === 'fa'

  // Mock data - in real app, fetch from API
  const stats = [
    {
      title: 'Users',
      value: '1,247',
      change: '+19% from last month',
      icon: Users,
      color: 'text-purple-500'
    },
    {
      title: 'Sales',
      value: '$45,231.89',
      change: '+20.1% from last month',
      icon: DollarSign,
      color: 'text-green-500'
    },
    {
      title: 'Inventory',
      value: '2,350',
      change: '+180 new items',
      icon: Package,
      color: 'text-blue-500'
    },
    {
      title: 'Alerts',
      value: '3',
      change: '2 critical alerts',
      icon: AlertTriangle,
      color: 'text-red-500'
    }
  ]

  const recentOrders = [
    { id: '12345', customer: 'John Doe', amount: '$299.99', status: 'completed', date: '2024-01-15' },
    { id: '12346', customer: 'Jane Smith', amount: '$156.00', status: 'pending', date: '2024-01-15' },
    { id: '12347', customer: 'Bob Johnson', amount: '$89.99', status: 'processing', date: '2024-01-14' },
    { id: '12348', customer: 'Alice Brown', amount: '$445.50', status: 'completed', date: '2024-01-14' },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'processing':
        return <Package className="h-4 w-4 text-blue-500" />
      default:
        return <AlertTriangle className="h-4 w-4 text-red-500" />
    }
  }

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      completed: 'Completed',
      pending: 'Pending',
      processing: 'Processing',
      cancelled: 'Cancelled'
    }
    return statusMap[status] || status
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold tracking-tight">
          {t('welcome')}, {user?.name}!
        </h1>
        <p className="text-muted-foreground">
          Here's what's happening with your business today.
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 + index * 0.1 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Charts & Quick Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monthly Sales Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5" />
                <span>Monthly Sales</span>
              </CardTitle>
              <CardDescription>
                Sales over the last 12 months
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SimpleChart data={[1200,1500,1100,2000,2300,2100,2500,2700,3000,3200,3500,3800]} color="#10b981" />
            </CardContent>
          </Card>
        </motion.div>

        {/* User Growth Chart */}
        <motion.div
          initial={{ opacity: 0, x: 0 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.35 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>User Growth</span>
              </CardTitle>
              <CardDescription>
                New users per month
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SimpleChart data={[20,35,25,40,60,80,90,120,150,200,250,300]} color="#6366f1" />
            </CardContent>
          </Card>
        </motion.div>

        {/* Alerts / Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common tasks you can perform
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="p-4 rounded-lg border bg-card hover:bg-muted transition-colors text-left"
                >
                  <Package className="h-8 w-8 text-blue-500 mb-2" />
                  <h3 className="font-medium text-sm">Add Product</h3>
                  <p className="text-xs text-muted-foreground">Create new inventory item</p>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="p-4 rounded-lg border bg-card hover:bg-muted transition-colors text-left"
                >
                  <Users className="h-8 w-8 text-green-500 mb-2" />
                  <h3 className="font-medium text-sm">New Customer</h3>
                  <p className="text-xs text-muted-foreground">Add customer profile</p>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="p-4 rounded-lg border bg-card hover:bg-muted transition-colors text-left"
                >
                  <ShoppingCart className="h-8 w-8 text-purple-500 mb-2" />
                  <h3 className="font-medium text-sm">Create Order</h3>
                  <p className="text-xs text-muted-foreground">Process new sale</p>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="p-4 rounded-lg border bg-card hover:bg-muted transition-colors text-left"
                >
                  <DollarSign className="h-8 w-8 text-orange-500 mb-2" />
                  <h3 className="font-medium text-sm">Financial Report</h3>
                  <p className="text-xs text-muted-foreground">View revenue analytics</p>
                </motion.button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default DashboardPage
