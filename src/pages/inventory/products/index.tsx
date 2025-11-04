import React from 'react'
import { Link } from 'react-router-dom'

export default function InventoryProductsPage(){
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold">Products</h1>
        <Link to="/inventory/products/new" className="px-3 py-2 bg-primary text-primary-foreground rounded">Add Product</Link>
      </div>
      <p className="text-sm text-muted-foreground">List of products (mock)</p>
      <table className="w-full mt-4 table-auto">
        <thead><tr><th>SKU</th><th>Name</th><th>Stock</th></tr></thead>
        <tbody>
          <tr className="border-t"><td className="p-2">SKU-001</td><td className="p-2">Laptop</td><td className="p-2">12</td></tr>
          <tr className="border-t"><td className="p-2">SKU-002</td><td className="p-2">Mouse</td><td className="p-2">54</td></tr>
        </tbody>
      </table>
    </div>
  )
}
