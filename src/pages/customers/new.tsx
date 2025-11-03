import React from 'react'
import CustomerForm from '@/components/customers/CustomerForm'
import { useRouter } from 'react-router-dom'

const NewCustomerPage: React.FC = () => {
  const router = useRouter()
  return (
    <div>
      <CustomerForm open={true} setOpen={() => router.push('/customers')} onCreated={() => router.push('/customers')} />
    </div>
  )
}

export default NewCustomerPage
