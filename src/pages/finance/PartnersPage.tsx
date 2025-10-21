import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'

interface Partner { id: string; name: string; partner_type: string; email?: string }

const PartnersPage: React.FC = () => {
  const [partners, setPartners] = useState<Partner[]>([])
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [type, setType] = useState('customer')
  const fetchList = async () => {
    const res = await fetch('/api/v1/arap/partners')
    const data = await res.json()
    setPartners(data)
  }
  useEffect(() => { fetchList() }, [])
  const create = async () => {
    await fetch('/api/v1/arap/partners', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ name, partner_type: type }) })
    setOpen(false)
    setName('')
    fetchList()
  }
  return (
    <div>
      <Card>
        <CardHeader>
          <CardTitle>Partners</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-end mb-4">
            <Button onClick={() => setOpen(true)}>New Partner</Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1">Name</th>
                  <th className="px-2 py-1">Type</th>
                  <th className="px-2 py-1">Email</th>
                </tr>
              </thead>
              <tbody>
                {partners.map(p => (
                  <tr key={p.id} className="border-t">
                    <td className="px-2 py-2">{p.name}</td>
                    <td className="px-2 py-2">{p.partner_type}</td>
                    <td className="px-2 py-2">{p.email || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
        <CardFooter />
      </Card>

      <Modal open={open} onOpenChange={setOpen} title="New Partner">
        <div className="space-y-3">
          <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <div>
            <label className="block text-sm mb-1">Type</label>
            <select value={type} onChange={(e) => setType(e.target.value)} className="w-full p-2 border rounded">
              <option value="customer">Customer</option>
              <option value="supplier">Supplier</option>
            </select>
          </div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={() => setOpen(false)} className="ml-2">Cancel</Button>
            <Button onClick={create} className="ml-2">Create</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default PartnersPage
