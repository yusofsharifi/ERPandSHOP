import React from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

const NotificationsPage = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Notifications</h1>
      <Card>
        <CardHeader>
          <CardTitle>All Notifications</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">A full notifications management UI will be available here.</p>
        </CardContent>
      </Card>
    </div>
  )
}

export default NotificationsPage
