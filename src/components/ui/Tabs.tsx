import React, { createContext, useContext, useState } from 'react'

type TabsContextValue = {
  value: string
  setValue: (v: string) => void
}

const TabsContext = createContext<TabsContextValue | undefined>(undefined)

export const Tabs = ({ defaultValue, children }: { defaultValue?: string; children: React.ReactNode }) => {
  const [value, setValue] = useState(defaultValue || 'general')
  return (
    <TabsContext.Provider value={{ value, setValue }}>{children}</TabsContext.Provider>
  )
}

export const TabsList = ({ children }: { children: React.ReactNode }) => {
  return <div className="flex space-x-2" role="tablist">{children}</div>
}

export const TabsTrigger = ({ value, children }: { value: string; children: React.ReactNode }) => {
  const ctx = useContext(TabsContext)
  if (!ctx) return null
  const active = ctx.value === value
  return (
    <button
      role="tab"
      aria-selected={active}
      onClick={() => ctx.setValue(value)}
      className={`px-3 py-2 rounded-md text-sm font-medium ${active ? 'bg-primary text-white' : 'bg-transparent text-muted-foreground hover:bg-accent'}`}
    >
      {children}
    </button>
  )
}

export const TabsContent = ({ value, children }: { value: string; children: React.ReactNode }) => {
  const ctx = useContext(TabsContext)
  if (!ctx) return null
  return <div hidden={ctx.value !== value}>{children}</div>
}
