import React from 'react'
import Modal from '@/components/ui/Modal'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

const schema = z.object({
  name: z.string().min(1, { message: 'Name is required' }),
  partner_type: z.enum(['customer', 'supplier']),
  tax_id: z.string().optional(),
  email: z.string().email({ message: 'Invalid email' }).optional(),
  credit_limit: z.preprocess((v) => Number(v), z.number().nonnegative()),
  currency: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

export default function PartnerFormModal({ open, setOpen, onCreated }: { open: boolean; setOpen: (v: boolean) => void; onCreated?: (p: any) => void }) {
  const { t, i18n } = useTranslation()
  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { partner_type: 'customer', credit_limit: 0 } })

  const submit = async (vals: FormValues) => {
    try {
      const res = await fetch('/api/v1/arap/partners', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(vals) })
      if (!res.ok) throw new Error('Failed')
      const data = await res.json()
      toast.success(t('success') || 'Saved')
      setOpen(false)
      reset()
      onCreated && onCreated(data)
    } catch (e) {
      toast.error(t('error') || 'Error')
    }
  }

  return (
    <Modal open={open} onOpenChange={setOpen} title={i18n.language === 'fa' ? 'همکار جدید' : 'New Partner'}>
      <form onSubmit={handleSubmit(submit)} className="space-y-3">
        <div>
          <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'نام' : 'Name'}</label>
          <Input {...register('name')} />
          {errors.name && <div className="text-red-600 text-sm">{errors.name.message}</div>}
        </div>

        <div>
          <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'نوع' : 'Type'}</label>
          <select {...register('partner_type')} className="w-full p-2 border rounded">
            <option value="customer">{i18n.language === 'fa' ? 'مشتری' : 'Customer'}</option>
            <option value="supplier">{i18n.language === 'fa' ? 'تأمین‌کننده' : 'Supplier'}</option>
          </select>
        </div>

        <div>
          <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'شناسه مالیاتی' : 'Tax ID'}</label>
          <Input {...register('tax_id')} />
        </div>

        <div>
          <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'ایمیل' : 'Email'}</label>
          <Input {...register('email')} />
          {errors.email && <div className="text-red-600 text-sm">{errors.email.message}</div>}
        </div>

        <div>
          <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'حد اعتباری' : 'Credit Limit'}</label>
          <Input type="number" step="0.01" {...register('credit_limit')} />
          {errors.credit_limit && <div className="text-red-600 text-sm">{String(errors.credit_limit.message)}</div>}
        </div>

        <div>
          <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'واحد پول' : 'Currency'}</label>
          <Input {...register('currency')} />
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" type="button" onClick={() => setOpen(false)}>{i18n.language === 'fa' ? 'لغو' : 'Cancel'}</Button>
          <Button type="submit" disabled={isSubmitting}>{i18n.language === 'fa' ? 'ذخیره' : 'Save'}</Button>
        </div>
      </form>
    </Modal>
  )
}
