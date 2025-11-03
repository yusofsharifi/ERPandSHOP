import React from 'react'
import OrderForm from '@/components/sales/OrderForm'
import { useNavigate } from 'react-router-dom'

const NewOrderPage: React.FC = () => {
  const navigate = useNavigate()
  return <OrderForm open={true} onClose={(created?:any) => { if (created && created.id) navigate(`/sales/orders/${created.id}`); else navigate('/sales/orders') }} />
}

export default NewOrderPage
