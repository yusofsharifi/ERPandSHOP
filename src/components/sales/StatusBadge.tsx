import React from 'react'

const mapStatus = (s: string) => {
  switch ((s || '').toLowerCase()) {
    case 'draft': return 'bg-gray-200 text-gray-800'
    case 'confirmed': return 'bg-indigo-100 text-indigo-800'
    case 'invoiced': return 'bg-blue-100 text-blue-800'
    case 'shipped': return 'bg-yellow-100 text-yellow-800'
    case 'delivered': return 'bg-green-100 text-green-800'
    case 'canceled': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const cls = mapStatus(status)
  const label = status || ''
  return <span className={`px-2 py-1 rounded text-sm font-medium ${cls}`}>{label}</span>
}

export default StatusBadge
