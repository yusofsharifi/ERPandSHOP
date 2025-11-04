import React, { useState } from 'react'

export default function NewProductPage(){
  const [name, setName] = useState('')
  const [sku, setSku] = useState('')
  const [stock, setStock] = useState(0)
  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Add Product</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        <input className="input" placeholder="SKU" value={sku} onChange={(e)=> setSku(e.target.value)} />
        <input className="input" placeholder="Name" value={name} onChange={(e)=> setName(e.target.value)} />
        <input className="input" placeholder="Stock" type="number" value={stock} onChange={(e)=> setStock(parseInt(e.target.value||'0'))} />
      </div>
      <div className="mt-4"><button className="px-3 py-2 bg-primary text-primary-foreground rounded">Save</button></div>
    </div>
  )
}
