import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import SimpleChart from '@/components/ui/SimpleChart'
import Modal from '@/components/ui/Modal'
import { useTranslation } from 'react-i18next'

const CashflowPage: React.FC = () => {
  const { i18n, t } = useTranslation()
  const [data, setData] = useState<number[]>([])
  const [labels, setLabels] = useState<string[]>([])
  const [open, setOpen] = useState(false)
  const [detail, setDetail] = useState<any>(null)

  useEffect(() => {
    // fetch cashflow (mock)
    const d = [5000, 4200, 3800, 6000, 7200, 6900, 8000]
    const l = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    setData(d)
    setLabels(l)
  }, [])

  const onPointClick = (idx: number) => {
    setDetail({ label: labels[idx], amount: data[idx], items: [{ id:1, desc:'Invoice 123', amt: data[idx] }]})
    setOpen(true)
  }

  return (
    <div dir={i18n.language === 'fa' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('Cash Flow') || 'Cash Flow'}</h2>
        <div />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('Interactive cash flow') || 'Interactive cash flow'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <SimpleChart data={data} />
          </div>
          <div className="grid grid-cols-3 gap-2">
            {data.map((d, i) => (
              <div key={i} className="p-2 border rounded cursor-pointer" onClick={() => onPointClick(i)}>
                <div className="font-medium">{labels[i]}</div>
                <div className="text-sm text-muted-foreground">{d.toFixed(2)}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Modal open={open} onOpenChange={setOpen} title={detail ? `${detail.label} — ${detail.amount}` : 'Detail'}>
        {detail && (
          <div>
            <h4 className="font-semibold mb-2">Items</h4>
            <div className="space-y-2">
              {detail.items.map((it:any) => (
                <div key={it.id} className="p-2 border rounded">{it.desc} — {it.amt}</div>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default CashflowPage
