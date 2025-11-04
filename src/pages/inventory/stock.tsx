import React from 'react'

export default function StockPage(){
  return (
    <div>
      <h1 className="text-xl font-bold">Stock Levels</h1>
      <p className="text-sm text-muted-foreground">Current stock across warehouses (mock)</p>
      <table className="w-full mt-4 table-auto">
        <thead><tr><th>Product</th><th>Warehouse</th><th>Quantity</th></tr></thead>
        <tbody>
          <tr className="border-t"><td className="p-2">Laptop</td><td className="p-2">Main</td><td className="p-2">10</td></tr>
          <tr className="border-t"><td className="p-2">Mouse</td><td className="p-2">Secondary</td><td className="p-2">50</td></tr>
        </tbody>
      </table>
    </div>
  )
}
