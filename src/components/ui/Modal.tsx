import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: string
  children?: React.ReactNode
}

const Modal: React.FC<ModalProps> = ({ open, onOpenChange, title, children }) => {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-black/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => onOpenChange(false)}
          />

          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
          >
            <div className={cn('w-full max-w-2xl bg-card border border-border rounded-lg shadow-lg') } onClick={(e) => e.stopPropagation()}>
              <div className="p-4 border-b border-border">
                <h3 className="text-lg font-semibold">{title}</h3>
              </div>
              <div className="p-4">
                {children}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default Modal
