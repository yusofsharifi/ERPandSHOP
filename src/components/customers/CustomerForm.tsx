import React, { useState, useEffect } from 'react'
import React, { useState, useEffect } from 'react'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

type Contact = { contact_name: string; position?: string; phone?: string; email?: string }

const CustomerForm: React.FC<{ open: boolean; setOpen: (v:boolean)=>void; onCreated?: (c:any)=>void }> = ({ open, setOpen, onCreated }) => {
  const { t, i18n } = useTranslation()
  const [name, setName] = useState('')
  const [companyId, setCompanyId] = useState('00000000-0000-0000-0000-000000000001')
  const [mobile, setMobile] = useState('')
  const [email, setEmail] = useState('')
  const [address, setAddress] = useState('')
  const [nationalId, setNationalId] = useState('')
  const [registrationNo, setRegistrationNo] = useState('')
  const [creditLimit, setCreditLimit] = useState<number | ''>('')
  const [contacts, setContacts] = useState<Contact[]>([])
  const [saving, setSaving] = useState(false)

  useEffect(() => { if (!open) { clearForm() } }, [open])

  const clearForm = () => { setName(''); setMobile(''); setEmail(''); setAddress(''); setNationalId(''); setRegistrationNo(''); setCreditLimit(''); setContacts([]) }

  const addContact = () => setContacts(c => [...c, { contact_name: '' }])
  const removeContact = (idx:number) => setContacts(c => c.filter((_,i)=> i!==idx))
  const updateContact = (idx:number, key:string, val:any) => setContacts(c => { const clone = [...c]; // @ts-ignore
    clone[idx][key]=val; return clone })

  const submit = async () => {
    if (!name) { toast.error(i18n.language==='fa' ? 'نام اجباری است' : 'Name is required'); return }
    setSaving(true)
    try {
      const payload:any = { company_id: companyId, name, mobile, email, address, national_id: nationalId || undefined, registration_no: registrationNo || undefined, credit_limit: creditLimit || 0, contacts }
      const res = await fetch('/api/v1/customers', { method: 'POST', headers: {'Content-Type':'application/json', 'X-User-Id':'1','X-User-Roles':'admin'}, body: JSON.stringify(payload) })
      if (!res.ok) { const err = await res.json().catch(()=>({})); toast.error(err?.detail?.message?.en || 'Error'); return }
      const data = await res.json()
      toast.success(i18n.language==='fa' ? 'مشتری ساخته شد' : 'Customer created')
      setOpen(false)
      onCreated && onCreated(data)
    } catch (e:any) {
      toast.error(i18n.language==='fa' ? 'خطا' : 'Error')
    } finally { setSaving(false) }
  }

  if (!open) return null
  return (
    <Modal open={open} onOpenChange={setOpen} title={i18n.language==='fa' ? 'فرم مشتری' : 'Customer Form'}>
      <div className="grid grid-cols-1 gap-2">
        <Input placeholder={i18n.language==='fa' ? 'نام' : 'Name'} value={name} onChange={(e:any)=> setName(e.target.value)} />
        <Input placeholder={i18n.language==='fa' ? 'تلفن' : 'Mobile'} value={mobile} onChange={(e:any)=> setMobile(e.target.value)} />
        <Input placeholder={i18n.language==='fa' ? 'ایمیل' : 'Email'} value={email} onChange={(e:any)=> setEmail(e.target.value)} />
        <Input placeholder={i18n.language==='fa' ? 'آدرس' : 'Address'} value={address} onChange={(e:any)=> setAddress(e.target.value)} />
        <div className="flex gap-2">
          <Input placeholder={i18n.language==='fa' ? 'شناسه ملی' : 'National ID'} value={nationalId} onChange={(e:any)=> setNationalId(e.target.value)} />
          <Input placeholder={i18n.language==='fa' ? 'شماره ثبت' : 'Registration No'} value={registrationNo} onChange={(e:any)=> setRegistrationNo(e.target.value)} />
        </div>
        <Input placeholder={i18n.language==='fa' ? 'حد اعتباری' : 'Credit Limit'} value={creditLimit as any} onChange={(e:any)=> setCreditLimit(e.target.value ? parseFloat(e.target.value) : '')} />

        <div>
          <div className="flex items-center justify-between">
            <strong>{i18n.language==='fa' ? 'مخاطبان' : 'Contacts'}</strong>
            <Button size="sm" onClick={addContact}>{i18n.language==='fa' ? 'افزودن' : 'Add'}</Button>
          </div>
          {contacts.map((c, idx) => (
            <div key={idx} className="flex gap-2 items-center mt-2">
              <Input placeholder={i18n.language==='fa' ? 'نام مخاطب' : 'Contact name'} value={c.contact_name} onChange={(e:any)=> updateContact(idx,'contact_name',e.target.value)} />
              <Input placeholder={i18n.language==='fa' ? 'تلفن' : 'Phone'} value={c.phone} onChange={(e:any)=> updateContact(idx,'phone',e.target.value)} />
              <Button size="sm" variant="destructive" onClick={()=> removeContact(idx)}>{i18n.language==='fa' ? 'حذف' : 'Remove'}</Button>
            </div>
          ))}
        </div>

        <div className="flex gap-2 justify-end mt-4">
          <Button variant="outline" onClick={()=> setOpen(false)}>{i18n.language==='fa' ? 'انصراف' : 'Cancel'}</Button>
          <Button onClick={submit} disabled={saving}>{saving ? (i18n.language==='fa' ? 'در حال ذخیره...' : 'Saving...') : (i18n.language==='fa' ? 'ذخیره' : 'Save')}</Button>
        </div>
      </div>
    </Modal>
  )
}

export default CustomerForm
