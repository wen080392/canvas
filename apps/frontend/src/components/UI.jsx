import React from 'react'

export function Button({ children, onClick, className = '', variant = 'primary', ...props }) {
  const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-all'
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    success: 'bg-green-600 text-white hover:bg-green-700',
  }

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${className}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  )
}

export function Card({ children, className = '', ...props }) {
  return (
    <div
      className={`bg-white rounded-lg shadow-md p-6 ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export function Modal({ isOpen, onClose, title, children }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

export function Loading() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin">
        <div className="w-8 h-8 border-4 border-gray-200 border-t-blue-600 rounded-full" />
      </div>
      <span className="ml-3 text-gray-600">Carregando...</span>
    </div>
  )
}

export function Alert({ type = 'info', title, message }) {
  const colors = {
    success: 'bg-green-100 border-green-400 text-green-800',
    error: 'bg-red-100 border-red-400 text-red-800',
    warning: 'bg-yellow-100 border-yellow-400 text-yellow-800',
    info: 'bg-blue-100 border-blue-400 text-blue-800',
  }

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  }

  return (
    <div className={`border-l-4 p-4 mb-4 ${colors[type]}`}>
      <div className="flex">
        <span className="text-xl font-bold mr-2">{icons[type]}</span>
        <div>
          {title && <div className="font-bold">{title}</div>}
          <div className="text-sm">{message}</div>
        </div>
      </div>
    </div>
  )
}

export function Badge({ label, variant = 'primary' }) {
  const variants = {
    primary: 'bg-blue-100 text-blue-800',
    secondary: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${variants[variant]}`}>
      {label}
    </span>
  )
}

export function Spinner({ size = 'md' }) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <div className={`${sizes[size]} border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin`} />
  )
}

export function EmptyState({ icon = '📭', title, description, action }) {
  return (
    <div className="text-center py-12">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6">{description}</p>
      {action && action}
    </div>
  )
}
