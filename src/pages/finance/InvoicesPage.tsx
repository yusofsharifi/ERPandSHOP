import React, { useEffect, useMemo, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Link } from 'react-router-dom'
import { Input } from '@/components/ui/Input'
import toast from 'react-hot-toast'
import { useAuth } from '@/contexts/AuthContext'

interface Invoice { id: string; invoice_no: string; date: string; due_date?: string | null; total_amount: number | string; balance_amount: number | string; status: string; invoice_type: string; partner_id?: string; partner_name?: string }
interface Partner { id: string; name: string }

const InvoicesPage: React.FC = () => {
  const { user } = useAuth()
  const [items, setItems] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(false)
  const [type, setType] = useState<string | undefined>(undefined)
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [partners, setPartners] = useState<Partner[]>([])
  const [partnerQuery, setPartnerQuery] = useState('')
  const [selectedPartner, setSelectedPartner] = useState<Partner | null>(null)
  const [startDate, setStartDate] = useState<string | undefined>(undefined)
  const [endDate, setEndDate] = useState<string | undefined>(undefined)
  const [selected, setSelected] = useState<Record<string, boolean>>({})
  const [selectAll, setSelectAll] = useState(false)

  const fetchList = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (type) params.set('type', type)
      if (status) params.set('status', status)
      if (selectedPartner) params.set('partner_id', selectedPartner.id)
      const res = await fetch('/api/v1/arap/invoices?' + params.toString())
      if (!res.ok) throw new Error('Failed to load')
      const data = await res.json()
      // ensure numeric amounts
      const normalized = data.map((d: any) => ({
        ...d,
        total_amount: Number(d.total_amount || 0),
        balance_amount: Number(d.balance_amount || 0),
        partner_name: d.partner_name || d.partner_id || '',
      }))
      setItems(normalized)
      setSelected({})
      setSelectAll(false)
    } catch (e) {
      console.error(e)
      toast.error('Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }

  const fetchPartners = async () => {
    try {
      const res = await fetch('/api/v1/arap/partners')
      if (!res.ok) return
      const data = await res.json()
      setPartners(data)
    } catch (e) {
      console.warn('partners fetch failed', e)
    }
  }

  useEffect(() => { fetchPartners() }, [])
  useEffect(() => { fetchList() }, [type, status, selectedPartner])

  // client-side date range filtering
  const visibleItems = useMemo(() => {
    return items.filter(i => {
      if (startDate && i.date < startDate) return false
      if (endDate && i.date > endDate) return false
      return true
    })
  }, [items, startDate, endDate])

  const toggleSelect = (id: string) => {
    setSelected(prev => {
      const next = { ...prev, [id]: !prev[id] }
      const allSelected = visibleItems.length > 0 && visibleItems.every(it => next[it.id])
      setSelectAll(allSelected)
      return next
    })
  }

  const toggleSelectAll = () => {
    const all = !selectAll
    setSelectAll(all)
    const next: Record<string, boolean> = {}
    if (all) {
      visibleItems.forEach(it => next[it.id] = true)
    }
    setSelected(next)
  }

  const exportCSV = (onlySelected = false) => {
    const rows = (onlySelected ? visibleItems.filter(it => selected[it.id]) : visibleItems)
    if (rows.length === 0) {
      toast('No rows to export')
      return
    }
    const header = ['Invoice No','Partner','Date','Due Date','Type','Total','Balance','Status']
    const csv = [header.join(',')]
    rows.forEach(r => {
      const vals = [r.invoice_no, (r.partner_name || ''), r.date || '', r.due_date || '', r.invoice_type || '', Number(r.total_amount || 0).toFixed(2), Number(r.balance_amount || 0).toFixed(2), r.status || '']
      // escape commas
      csv.push(vals.map(v => `"${String(v).replace(/"/g,'""')}"`).join(','))
    })
    const blob = new Blob([csv.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `invoices_export_${new Date().toISOString().slice(0,10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Exported CSV')
  }

  const markCancelled = async () => {
    const ids = visibleItems.filter(it => selected[it.id]).map(it => it.id)
    if (ids.length === 0) return toast('No invoices selected')
    if (!confirm(`Mark ${ids.length} invoice(s) as cancelled?`)) return
    try {
      for (const id of ids) {
        await fetch(`/api/v1/arap/invoices/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: 'cancelled' }) })
      }
      toast.success('Marked cancelled')
      fetchList()
    } catch (e) {
      console.error(e)
      toast.error('Failed to mark cancelled')
    }
  }

  // partner typeahead simple filter
  const partnerSuggestions = useMemo(() => {
    const q = partnerQuery.trim().toLowerCase()
    if (!q) return partners.slice(0,6)
    return partners.filter(p => p.name.toLowerCase().includes(q)).slice(0,8)
  }, [partners, partnerQuery])

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Invoices</h2>
        <div className="flex items-center gap-2">
          <Link to="/finance/invoices/new"><Button>New Invoice</Button></Link>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Invoice list</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-2 mb-4">
            <div className="flex gap-2 items-center">
              <select value={type || ''} onChange={(e)=> setType(e.target.value || undefined)} className="p-2 border rounded" aria-label="Type filter">
                <option value="">All types</option>
                <option value="sale">Sale</option>
                <option value="purchase">Purchase</option>
              </select>
              <select value={status || ''} onChange={(e)=> setStatus(e.target.value || undefined)} className="p-2 border rounded" aria-label="Status filter">
                <option value="">All status</option>
                <option value="draft">Draft</option>
                <option value="open">Open</option>
                <option value="partial">Partial</option>
                <option value="paid">Paid</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div className="flex gap-2 items-center">
              <Input placeholder="Partner..." value={partnerQuery} onChange={(e)=> { setPartnerQuery(e.target.value); setSelectedPartner(null) }} aria-label="Partner search" />
              <div className="relative">
                {partnerQuery && partnerSuggestions.length > 0 && (
                  <div className="absolute z-10 bg-card border rounded mt-1 w-64 max-h-44 overflow-auto">
                    {partnerSuggestions.map(p => (
                      <div key={p.id} className="p-2 hover:bg-muted cursor-pointer" onClick={() => { setSelectedPartner(p); setPartnerQuery(p.name); }}>
                        {p.name}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <Input type="date" value={startDate || ''} onChange={(e)=> setStartDate(e.target.value || undefined)} />
              <Input type="date" value={endDate || ''} onChange={(e)=> setEndDate(e.target.value || undefined)} />

              <Button variant="outline" onClick={fetchList} disabled={loading}>{loading ? 'Loading...' : 'Refresh'}</Button>
            </div>

            <div className="ml-auto flex gap-2 items-center">
              <Button variant="ghost" onClick={() => exportCSV(false)}>Export All</Button>
              <Button variant="ghost" onClick={() => exportCSV(true)}>Export Selected</Button>
              {user && (user.role || '').toLowerCase() === 'admin' && (
                <Button variant="destructive" onClick={markCancelled}>Mark Cancelled</Button>
              )}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full table-auto" role="table" aria-label="Invoices table">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1"><input type="checkbox" checked={selectAll} onChange={toggleSelectAll} aria-label="Select all"/></th>
                  <th className="px-2 py-1">Invoice #</th>
                  <th className="px-2 py-1">Partner</th>
                  <th className="px-2 py-1">Date</th>
                  <th className="px-2 py-1">Due</th>
                  <th className="px-2 py-1">Type</th>
                  <th className="px-2 py-1">Total</th>
                  <th className="px-2 py-1">Balance</th>
                  <th className="px-2 py-1">Status</th>
                  <th className="px-2 py-1">Actions</th>
                </tr>
              </thead>
              <tbody>
                {visibleItems.map((inv, idx) => (
                  <tr key={inv.id} className="border-t hover:bg-muted">
                    <td className="px-2 py-2"><input aria-label={`select-${inv.invoice_no}`} type="checkbox" checked={!!selected[inv.id]} onChange={() => toggleSelect(inv.id)} /></td>
                    <td className="px-2 py-2"><Link to={`/finance/invoices/${inv.id}`} className="text-primary underline">{inv.invoice_no}</Link></td>
                    <td className="px-2 py-2">{inv.partner_name || ''}</td>
                    <td className="px-2 py-2">{inv.date}</td>
                    <td className="px-2 py-2">{inv.due_date || '-'}</td>
                    <td className="px-2 py-2">{inv.invoice_type}</td>
                    <td className="px-2 py-2">{Number(inv.total_amount).toFixed(2)}</td>
                    <td className="px-2 py-2">{Number(inv.balance_amount).toFixed(2)}</td>
                    <td className="px-2 py-2">{inv.status}</td>
                    <td className="px-2 py-2">
                      <div className="flex gap-2">
                        <Link to={`/finance/invoices/${inv.id}`} className="text-primary underline">View</Link>
                        {inv.status !== 'paid' && <Link to={`/finance/invoices/${inv.id}`} className="text-muted underline">Apply Payment</Link>}
                      </div>
                    </td>
                  </tr>
                ))}
                {visibleItems.length === 0 && (
                  <tr><td colSpan={10} className="p-4 text-center text-sm text-muted">No invoices found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default InvoicesPage
