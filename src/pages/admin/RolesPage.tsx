import React from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

const RolesPage = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Roles Management</h1>
      <Card>
        <CardHeader>
          <CardTitle>Roles</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Role CRUD and permissions will be implemented here.</p>
        </CardContent>
      </Card>
    </div>
  )
}

export default RolesPage
