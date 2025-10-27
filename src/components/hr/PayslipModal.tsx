import React from 'react'
import Modal from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'

type Props = { open: boolean, onOpenChange: (v:boolean)=>void, payslip: any }

export default function PayslipModal({ open, onOpenChange, payslip }: Props){
  if (!payslip) return null

  const printPayslip = ()=>{
    const w = window.open('', '_blank')
    if (!w) return
    w.document.write(`<html><head><title>Payslip</title></head><body><pre>${JSON.stringify(payslip, null, 2)}</pre></body></html>`)
    w.document.close()
    w.print()
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title={`Payslip - ${payslip.name}`}>
      <div className="space-y-2">
        <div><strong>Employee:</strong> {payslip.name}</div>
        <div><strong>Gross:</strong> {payslip.gross}</div>
        <div><strong>Tax:</strong> {payslip.tax}</div>
        <div><strong>Net:</strong> {payslip.net}</div>
        <div className="flex gap-2 justify-end mt-4">
          <Button variant="outline" onClick={()=> onOpenChange(false)}>Close</Button>
          <Button onClick={printPayslip}>Print / Save PDF</Button>
        </div>
      </div>
    </Modal>
  )
}
