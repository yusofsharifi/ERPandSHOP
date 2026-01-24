import React from 'react'
import InvoiceForm from '@/components/invoices/InvoiceForm'
import { useNavigate } from 'react-router-dom'

const NewInvoicePage: React.FC = () => {
  const navigate = useNavigate()
  return <InvoiceForm open={true} onClose={(created?:any) => { if (created && created.id) navigate(`/sales/invoices/${created.id}`); else navigate('/sales/invoices') }} />
}

export default NewInvoicePage
