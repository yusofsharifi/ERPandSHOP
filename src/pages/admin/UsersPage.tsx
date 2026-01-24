import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import toast from 'react-hot-toast'

interface UserRow {
  id: string
  name: string
  email: string
  role: string
  status: string
}

const fetchUsers = async (page = 1, per_page = 10, search = '', role = '', status = '') => {
  try {
    const params = new URLSearchParams({ page: String(page), per_page: String(per_page) })
    if (search) params.set('search', search)
    if (role) params.set('role', role)
    if (status) params.set('status', status)
    const res = await fetch(`/api/users?${params.toString()}`)
    if (!res.ok) throw new Error('Failed to fetch users')
    return res.json()
  } catch (err) {
    console.error('fetchUsers error', err)
    throw new Error('Failed to fetch users')
  }
}

const createUserApi = async (payload: any) => {
  try {
    const res = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error('Create user failed')
    return res.json()
  } catch (err) {
    console.error('createUserApi error', err)
    throw new Error('Create user failed')
  }
}

const updateUserApi = async (id: string, payload: any) => {
  try {
    const res = await fetch(`/api/users/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error('Update user failed')
    return res.json()
  } catch (err) {
    console.error('updateUserApi error', err)
    throw new Error('Update user failed')
  }
}

const deleteUserApi = async (id: string) => {
  try {
    const res = await fetch(`/api/users/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Delete user failed')
    return res.json()
  } catch (err) {
    console.error('deleteUserApi error', err)
    throw new Error('Delete user failed')
  }
}

const UsersPage: React.FC = () => {
  const { user } = useAuth()
  const isAdmin = user?.role === 'Admin'
  const queryClient = useQueryClient()

  const [page, setPage] = useState(1)
  const [perPage] = useState(10)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<UserRow | null>(null)

  const { data, isLoading } = useQuery(['users', page, perPage, search, roleFilter, statusFilter], () => fetchUsers(page, perPage, search, roleFilter, statusFilter), { keepPreviousData: true })

  const createUser = useMutation(createUserApi, {
    onSuccess: () => {
      toast.success('User created')
      queryClient.invalidateQueries(['users'])
      setModalOpen(false)
    },
    onError: () => toast.error('Create user failed'),
  })

  const updateUser = useMutation(({ id, payload }: any) => updateUserApi(id, payload), {
    onSuccess: () => {
      toast.success('User updated')
      queryClient.invalidateQueries(['users'])
      setModalOpen(false)
      setEditingUser(null)
    },
    onError: () => toast.error('Update failed'),
  })

  const deleteUser = useMutation((id: string) => deleteUserApi(id), {
    onSuccess: () => {
      toast.success('User deleted')
      queryClient.invalidateQueries(['users'])
    },
    onError: () => toast.error('Delete failed'),
  })

  const users: UserRow[] = data?.data || []
  const total = data?.meta?.total || 0
  const totalPages = Math.max(1, Math.ceil(total / perPage))

  const openCreateModal = () => {
    setEditingUser(null)
    setModalOpen(true)
  }

  const openEditModal = (u: UserRow) => {
    setEditingUser(u)
    setModalOpen(true)
  }

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const formData = new FormData(form)
    const payload: any = {
      name: formData.get('name'),
      email: formData.get('email'),
      role: formData.get('role'),
      status: formData.get('status') || 'Active',
    }
    if ((formData.get('password') as string) && (formData.get('password') as string).length > 0) payload.password = formData.get('password')

    if (editingUser) {
      updateUser.mutate({ id: editingUser.id, payload })
    } else {
      createUser.mutate(payload)
    }
  }

  const handleDelete = (id: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return
    deleteUser.mutate(id)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Users</CardTitle>
          <div className="flex items-center gap-2">
            <Input placeholder="Search by name or email" value={search} onChange={(e:any) => { setSearch(e.target.value); setPage(1) }} />
            <select value={roleFilter} onChange={(e)=> setRoleFilter(e.target.value)} className="rounded border border-input px-2 py-1">
              <option value="">All roles</option>
              <option value="Admin">Admin</option>
              <option value="User">User</option>
              <option value="Manager">Manager</option>
            </select>
            <select value={statusFilter} onChange={(e)=> setStatusFilter(e.target.value)} className="rounded border border-input px-2 py-1">
              <option value="">All status</option>
              <option value="Active">Active</option>
              <option value="Suspended">Suspended</option>
            </select>
            {isAdmin && (
              <Button onClick={openCreateModal}>Add New User</Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left text-sm text-muted-foreground">
                  <th className="p-2">ID</th>
                  <th className="p-2">Name</th>
                  <th className="p-2">Email</th>
                  <th className="p-2">Role</th>
                  <th className="p-2">Status</th>
                  <th className="p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={6} className="p-4 text-center">Loading...</td></tr>
                ) : users.length === 0 ? (
                  <tr><td colSpan={6} className="p-4 text-center">No users</td></tr>
                ) : users.map(u => (
                  <tr key={u.id} className="border-t">
                    <td className="p-2 text-sm">{u.id}</td>
                    <td className="p-2 text-sm">{u.name}</td>
                    <td className="p-2 text-sm">{u.email}</td>
                    <td className="p-2 text-sm">{u.role}</td>
                    <td className="p-2 text-sm">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${u.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>{u.status}</span>
                    </td>
                    <td className="p-2 text-sm">
                      <div className="flex items-center gap-2">
                        {isAdmin ? (
                          <>
                            <Button size="sm" onClick={() => openEditModal(u)}>Edit</Button>
                            <Button size="sm" variant="destructive" onClick={() => handleDelete(u.id)}>Delete</Button>
                          </>
                        ) : (
                          <span className="text-muted-foreground">Read</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-muted-foreground">Page {page} of {totalPages}</div>
            <div className="flex items-center gap-2">
              <Button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
              <Button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Modal */}
      <Modal open={modalOpen} onOpenChange={setModalOpen} title={editingUser ? 'Edit User' : 'Add New User'}>
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Name</Label>
              <Input name="name" defaultValue={editingUser?.name || ''} required />
            </div>
            <div>
              <Label>Email</Label>
              <Input name="email" defaultValue={editingUser?.email || ''} type="email" required />
            </div>
            <div>
              <Label>Password</Label>
              <Input name="password" type="password" placeholder="Leave blank to keep existing" />
            </div>
            <div>
              <Label>Role</Label>
              <select name="role" defaultValue={editingUser?.role || 'User'} className="w-full rounded border border-input px-2 py-1">
                <option value="User">User</option>
                <option value="Admin">Admin</option>
                <option value="Manager">Manager</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => { setModalOpen(false); setEditingUser(null) }}>Cancel</Button>
            <Button type="submit">{editingUser ? 'Save' : 'Create'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default UsersPage
