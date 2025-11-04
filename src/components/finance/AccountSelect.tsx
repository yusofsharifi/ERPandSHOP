import React, { useEffect, useState, useMemo } from 'react'
import { Input } from '@/components/ui/Input'
import { cn, API_BASE_URL } from '@/lib/utils'

type Account = { id: string; code: string; name: string }

export default function AccountSelect({ value, onChange, placeholder }: { value?: string | null; onChange: (v: string) => void; placeholder?: string }) {
  const [query, setQuery] = useState('')
  const [options, setOptions] = useState<Account[]>([])
  const [loading, setLoading] = useState(false)

  const fetchAccounts = async (q: string) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/accounts?search=${encodeURIComponent(q || '')}&per_page=20`)
      const data = await res.json()
      setOptions(data.items || [])
    } catch (e) {
      setOptions([])
    } finally {
      setLoading(false)
    }
  }

  // simple debounce using timeout
  useEffect(()=>{
    const t = setTimeout(()=>{ fetchAccounts(query) }, 300)
    return ()=> clearTimeout(t)
  }, [query])

  useEffect(() => { if (!query) fetchAccounts('') }, [])

  return (
    <div className="relative">
      <Input value={query} onChange={(e:any)=> setQuery(e.target.value)} placeholder={placeholder || 'Search account'} />
      <div className="absolute z-10 left-0 right-0 bg-card mt-1 rounded shadow max-h-64 overflow-auto">
        {loading && <div className="p-2">Loading...</div>}
        {!loading && options.length === 0 && <div className="p-2 text-muted-foreground">No accounts</div>}
        {!loading && options.map(a=> (
          <div key={a.id} className={cn('p-2 hover:bg-accent cursor-pointer', a.id === value ? 'bg-accent/60' : '')} onClick={()=> { onChange(a.id); setQuery(`${a.code} - ${a.name}`) }}>
            <div className="text-sm font-medium">{a.code} - {a.name}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
