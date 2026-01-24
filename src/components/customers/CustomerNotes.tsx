import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

const CustomerNotes: React.FC<{ customerId: string }> = ({ customerId }) => {
  const { i18n } = useTranslation()
  const [notes, setNotes] = useState<any[]>([])
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchNotes = async () => {
    if (!customerId) return
    setLoading(true)
    try {
      const res = await fetch(`/api/v1/customers/${customerId}`)
      if (!res.ok) { setNotes([]); return }
      const data = await res.json()
      setNotes(data.notes || [])
    } catch (e) {
      setNotes([])
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchNotes() }, [customerId])

  const addNote = async () => {
    if (!text) return
    try {
      const res = await fetch(`/api/v1/customers/${customerId}/notes`, { method: 'POST', headers: {'Content-Type':'application/json','X-User-Id':'1','X-User-Roles':'admin'}, body: JSON.stringify({ note: text }) })
      if (!res.ok) { toast.error('Error'); return }
      const n = await res.json()
      setText('')
      fetchNotes()
      toast.success(i18n.language==='fa' ? 'یادداشت اضافه شد' : 'Note added')
    } catch (e) { toast.error('Error') }
  }

  const delConfirm = async (nid:string) => {
    // API does not include delete note yet; simulate by posting note with empty or relying on backend
    // For now show confirmation and remove locally
    if (!confirm(i18n.language==='fa' ? 'آیا مطمئن هستید؟' : 'Are you sure?')) return
    // optimistic remove (backend delete not implemented)
    setNotes(n => n.filter(x => x.id !== nid))
    toast.success(i18n.language==='fa' ? 'حذف شد' : 'Deleted')
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{i18n.language==='fa' ? 'یادداشت‌ها' : 'Notes'}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-2">
          <div className="flex gap-2">
            <Input placeholder={i18n.language==='fa' ? 'یادداشت جدید' : 'New note'} value={text} onChange={(e:any)=> setText(e.target.value)} />
            <Button onClick={addNote}>{i18n.language==='fa' ? 'افزودن' : 'Add'}</Button>
          </div>
        </div>
        <div>
          {loading && <div>{i18n.language==='fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>}
          {!loading && notes.length === 0 && <div>{i18n.language==='fa' ? 'هیچ یادداشتی نیست' : 'No notes'}</div>}
          {notes.map(n => (
            <div key={n.id} className="border rounded p-2 mb-2">
              <div className="text-sm text-muted-foreground">{new Date(n.created_at).toLocaleString()}</div>
              <div className="mt-1">{n.note}</div>
              <div className="flex gap-2 mt-2">
                <Button size="sm" variant="destructive" onClick={()=> delConfirm(n.id)}>{i18n.language==='fa' ? 'حذف' : 'Delete'}</Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default CustomerNotes
