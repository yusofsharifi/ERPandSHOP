import React from 'react'
import CustomerForm from '@/components/customers/CustomerForm'
import { useNavigate } from 'react-router-dom'

const NewCustomerPage: React.FC = () => {
  const navigate = useNavigate()
  return (
    <div>
      <CustomerForm open={true} setOpen={() => navigate('/customers')} onCreated={() => navigate('/customers')} />
    </div>
  )
}

export default NewCustomerPage
