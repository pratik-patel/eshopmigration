import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with proper precedence.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format price as number (without $ sign).
 * The $ sign is added via CSS (.esh-price:before) for legacy parity.
 */
export function formatPrice(price: number): string {
  return price.toFixed(2)
}

/**
 * Format date to ISO string.
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-US')
}
