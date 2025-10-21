import React, { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { API_BASE_URL } from '@/lib/utils'
import toast from 'react-hot-toast'

export default function AttachmentUploader({ entryId, onUploaded }:{ entryId: string; onUploaded?: (a:any)=>void }){
  const [files, setFiles] = useState<FileList | null>(null)
  const upload = async ()=>{
    if(!files || files.length === 0) { toast.error('No files'); return }
    for(let i=0;i<files.length;i++){
      const f = files[i]
      const fd = new FormData()
      fd.append('file', f)
      try{
        const res = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries/${entryId}/attachments`, { method: 'POST', headers: {'X-User-Id':'admin@local'}, body: fd })
        const d = await res.json()
        if(!res.ok) { toast.error(d?.detail?.message?.fa || d?.detail?.message?.en || 'Upload failed'); continue }
        toast.success('Uploaded')
        onUploaded && onUploaded(d.attachment)
      }catch(e){ toast.error('Upload error') }
    }
  }
  return (
    <div className="space-y-2">
      <input type="file" multiple onChange={(e)=> setFiles(e.target.files)} />
      <div className="flex gap-2"><Button onClick={upload}>Upload</Button></div>
    </div>
  )
}
