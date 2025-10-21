import React from 'react'
import { Button } from '@/components/ui/Button'

export default function PostConfirmationModal({ open, onClose, onConfirm, preview }:{ open:boolean; onClose:()=>void; onConfirm:()=>void; preview?: any }){
  if(!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-card p-4 rounded w-full max-w-md">
        <h3 className="text-lg font-bold">Confirm Post</h3>
        <p className="mt-2 text-sm">Next number: {preview?.number ?? '—'}</p>
        <p className="mt-1 text-sm">Date: {preview?.date ?? '—'}</p>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button variant="default" onClick={onConfirm}>Post</Button>
        </div>
      </div>
    </div>
  )
}
