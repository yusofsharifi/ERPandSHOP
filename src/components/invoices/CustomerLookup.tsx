import React, { useState, useEffect } from 'react'
import React, { useState, useEffect } from 'react'
import { Input } from '@/components/ui/Input'

const CustomerLookup: React.FC<{ onSelect: (id:string, name:string)=>void }> = ({ onSelect }) => {
  const [q, setQ] = useState('')
  const [results, setResults] = useState<any[]>([])

  useEffect(() => {
    const id = setTimeout(async () => {
      if (!q) { setResults([]); return }
      try {
        const res = await fetch('/api/v1/arap/partners?search=' + encodeURIComponent(q))
        if (!res.ok) { setResults([]); return }
        const data = await res.json()
        setResults(Array.isArray(data) ? data : (data.items || data))
      } catch (e) { setResults([]) }
    }, 250)
    return () => clearTimeout(id)
  }, [q])

  return (
    <div>
      <Input placeholder="مشتری را جستجو کنید" value={q} onChange={(e:any)=> setQ(e.target.value)} />
      {results.length > 0 && (
        <div className="border rounded mt-1 max-h-48 overflow-auto bg-white z-50">
          {results.map(r => (
            <div key={r.id} className="p-2 hover:bg-gray-100 cursor-pointer" onClick={()=> { onSelect(r.id, r.name); setResults([]); setQ('') }}>
              <div className="font-medium">{r.name}</div>
              <div className="text-sm text-muted-foreground">{r.email || r.phone}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CustomerLookup
