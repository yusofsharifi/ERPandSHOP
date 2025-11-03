import React from 'react'

const mapStatus = (s: string) => {
  switch ((s || '').toLowerCase()) {
    case 'draft': return 'bg-gray-200 text-gray-800'
    case 'open':
    case 'posted': return 'bg-blue-100 text-blue-800'
    case 'partial':
    case 'paid': return 'bg-green-100 text-green-800'
    case 'cancelled':
    case 'canceled': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const InvoiceStatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const cls = mapStatus(status)
  return <span className={`px-2 py-1 rounded text-sm font-medium ${cls}`}>{status}</span>
}

export default InvoiceStatusBadge
