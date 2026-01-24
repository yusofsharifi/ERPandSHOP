import React from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

const LineItem: React.FC<{ idx:number, item:any, onChange:(idx:number, key:string, val:any)=>void, onRemove:(idx:number)=>void }> = ({ idx, item, onChange, onRemove }) => {
  return (
    <div className="grid grid-cols-12 gap-2 items-center w-full">
      <input className="col-span-4 p-2 border rounded" placeholder="Description" value={item.description || ''} onChange={(e)=> onChange(idx, 'description', e.target.value)} />
      <input className="col-span-2 p-2 border rounded" type="number" step="0.0001" value={item.qty} onChange={(e)=> onChange(idx, 'qty', e.target.value)} />
      <input className="col-span-2 p-2 border rounded" type="number" step="0.01" value={item.unit_price} onChange={(e)=> onChange(idx, 'unit_price', e.target.value)} />
      <input className="col-span-2 p-2 border rounded" type="number" step="0.01" value={item.tax_rate} onChange={(e)=> onChange(idx, 'tax_rate', e.target.value)} />
      <div className="col-span-1 text-right">{item.line_total ?? '-'}</div>
      <div className="col-span-1"><Button size="sm" variant="destructive" onClick={()=> onRemove(idx)}>حذف</Button></div>
    </div>
  )
}

export default LineItem
