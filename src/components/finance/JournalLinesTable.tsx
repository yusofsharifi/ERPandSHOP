import React from 'react'
import AccountSelect from './AccountSelect'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

export default function JournalLinesTable({ lines, setLines }:{ lines:any[]; setLines:(v:any[])=>void }){
  const updateLine = (idx:number, patch: any) => {
    const copy = [...lines]
    copy[idx] = { ...copy[idx], ...patch }
    setLines(copy)
  }
  const addRow = () => setLines([...lines, { line_no: lines.length + 1, account_id: '', description: '', debit: 0, credit: 0 }])
  const removeRow = (idx:number)=> {
    const copy = lines.filter((_,i)=> i!==idx).map((l,i)=> ({...l, line_no: i+1}))
    setLines(copy)
  }

  return (
    <div>
      <table className="w-full table-auto border-collapse">
        <thead>
          <tr className="text-left">
            <th className="p-2">#</th>
            <th className="p-2">Account</th>
            <th className="p-2">Cost Center</th>
            <th className="p-2">Debit</th>
            <th className="p-2">Credit</th>
            <th className="p-2">Desc</th>
            <th className="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {lines.map((ln, idx) => (
            <tr key={idx} className="border-t">
              <td className="p-2 align-top">{ln.line_no}</td>
              <td className="p-2 align-top w-64"><AccountSelect value={ln.account_id} onChange={(v)=> updateLine(idx, { account_id: v })} /></td>
              <td className="p-2 align-top"><Input value={ln.cost_center_id || ''} onChange={(e:any)=> updateLine(idx, { cost_center_id: e.target.value })} /></td>
              <td className="p-2 align-top"><Input type="number" step="0.01" value={ln.debit} onChange={(e:any)=> updateLine(idx, { debit: parseFloat(e.target.value||0) })} /></td>
              <td className="p-2 align-top"><Input type="number" step="0.01" value={ln.credit} onChange={(e:any)=> updateLine(idx, { credit: parseFloat(e.target.value||0) })} /></td>
              <td className="p-2 align-top"><Input value={ln.description || ''} onChange={(e:any)=> updateLine(idx, { description: e.target.value })} /></td>
              <td className="p-2 align-top"><Button variant="ghost" size="sm" onClick={()=> removeRow(idx)}>Remove</Button></td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-2"><Button variant="secondary" onClick={addRow}>Add row</Button></div>
    </div>
  )
}
