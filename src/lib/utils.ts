import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// API Base URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Storage keys
export const STORAGE_KEYS = {
  TOKEN: 'bizgenius_token',
  REFRESH_TOKEN: 'bizgenius_refresh_token',
  LANGUAGE: 'bizgenius_language',
  THEME: 'bizgenius_theme',
  USER: 'bizgenius_user',
} as const

// Helper functions
export const getStorageItem = (key: string) => {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

export const setStorageItem = (key: string, value: string) => {
  try {
    localStorage.setItem(key, value)
  } catch {
    // Handle localStorage errors silently
  }
}

export const removeStorageItem = (key: string) => {
  try {
    localStorage.removeItem(key)
  } catch {
    // Handle localStorage errors silently
  }
}

// Validation helpers
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const isValidPassword = (password: string): boolean => {
  return password.length >= 8
}
