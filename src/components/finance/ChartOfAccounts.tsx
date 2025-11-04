import React, { useMemo } from 'react'

type Account = { id: string; code: string; name: string; type?: string; disabled?: boolean; currency?: string; company_id?: string; status?: string; description?: string }

const buildTree = (accounts: Account[]) => {
  const map: Record<string, any> = {}
  const roots: any[] = []
  // sort by code for predictable order
  const sorted = [...accounts].sort((a,b)=> (a.code||'').localeCompare(b.code||''))
  for (const acc of sorted) {
    const node = { ...acc, children: [] }
    map[acc.code] = node
  }
  for (const acc of sorted) {
    const code = acc.code || ''
    const parts = code.split('.')
    if (parts.length > 1) {
      const parentCode = parts.slice(0, -1).join('.')
      if (map[parentCode]) {
        map[parentCode].children.push(map[code])
        continue
      }
    }
    roots.push(map[code])
  }
  return roots
}

const AccountNode: React.FC<{ node:any; depth?:number; onToggle:(id:string)=>void; onEdit?: (id:string)=>void }>= ({ node, depth=0, onToggle, onEdit }) => {
  return (
    <div className={`pl-${Math.min(depth*4, 24)} py-1`}> 
      <div className="flex items-center justify-between gap-2">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <div className={`text-sm font-medium${node.disabled ? ' line-through text-muted-foreground' : ''}`}>{node.code} {node.name}</div>
            <div className="text-xs text-muted-foreground">{node.type}</div>
          </div>
          {node.description && <div className="text-xs text-muted-foreground mt-1">{node.description}</div>}
        </div>
        <div className="flex items-center gap-2">
          <button className="text-xs px-2 py-1 border rounded" onClick={()=> onToggle(node.id)}>{node.disabled ? 'Enable' : 'Disable'}</button>
          <button className="text-xs px-2 py-1 border rounded" onClick={()=> onEdit && onEdit(node.id)}>Edit</button>
        </div>
      </div>
      {node.children && node.children.length > 0 && (
        <div className="mt-1">
          {node.children.map((c:any)=> <AccountNode key={c.id} node={c} depth={depth+1} onToggle={onToggle} onEdit={onEdit} />)}
        </div>
      )}
    </div>
  )
}

const ChartOfAccounts: React.FC<{ accounts: Account[]; onToggle: (id:string)=>void; onEdit?: (id:string)=>void }> = ({ accounts, onToggle, onEdit }) => {
  const tree = useMemo(()=> buildTree(accounts), [accounts])
  return (
    <div>
      {tree.map((n:any)=> <AccountNode key={n.id} node={n} onToggle={onToggle} onEdit={onEdit} />)}
    </div>
  )
}

export default ChartOfAccounts
