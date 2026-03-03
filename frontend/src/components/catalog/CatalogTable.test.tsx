/**
 * Tests for CatalogTable component.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { CatalogTable } from './CatalogTable'
import type { CatalogItem } from '@/api/catalog'

// Mock catalog items
const mockItems: CatalogItem[] = [
  {
    id: 1,
    name: '.NET Bot Black Hoodie',
    description: '.NET Bot Black Hoodie',
    price: 19.5,
    picture_file_name: '1.png',
    picture_uri: null,
    catalog_type_id: 2,
    catalog_brand_id: 2,
    available_stock: 100,
    restock_threshold: 10,
    max_stock_threshold: 200,
    on_reorder: false,
    catalog_type: { id: 2, type: 'T-Shirt' },
    catalog_brand: { id: 2, brand: '.NET' },
  },
  {
    id: 2,
    name: '.NET Black & White Mug',
    description: '.NET Black & White Mug',
    price: 8.5,
    picture_file_name: '2.png',
    picture_uri: null,
    catalog_type_id: 1,
    catalog_brand_id: 2,
    available_stock: 100,
    restock_threshold: 10,
    max_stock_threshold: 200,
    on_reorder: false,
    catalog_type: { id: 1, type: 'Mug' },
    catalog_brand: { id: 2, brand: '.NET' },
  },
]

// Wrapper with Router for Link components
function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>)
}

describe('CatalogTable', () => {
  it('renders table with items', () => {
    renderWithRouter(<CatalogTable items={mockItems} />)

    // Check table headers
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Description')).toBeInTheDocument()
    expect(screen.getByText('Brand')).toBeInTheDocument()
    expect(screen.getByText('Type')).toBeInTheDocument()
    expect(screen.getByText('Price')).toBeInTheDocument()

    // Check first item data
    expect(screen.getByText('.NET Bot Black Hoodie')).toBeInTheDocument()
    expect(screen.getByText('T-Shirt')).toBeInTheDocument()

    // Check second item data
    expect(screen.getByText('.NET Black & White Mug')).toBeInTheDocument()
    expect(screen.getByText('Mug')).toBeInTheDocument()
  })

  it('renders action links for each item', () => {
    renderWithRouter(<CatalogTable items={mockItems} />)

    // Check Edit links (2 items = 2 Edit links)
    const editLinks = screen.getAllByText('Edit')
    expect(editLinks).toHaveLength(2)

    // Check Details links
    const detailsLinks = screen.getAllByText('Details')
    expect(detailsLinks).toHaveLength(2)

    // Check Delete links
    const deleteLinks = screen.getAllByText('Delete')
    expect(deleteLinks).toHaveLength(2)
  })

  it('renders product images', () => {
    renderWithRouter(<CatalogTable items={mockItems} />)

    const images = screen.getAllByRole('img')
    expect(images).toHaveLength(2)

    // Check image src attributes
    expect(images[0]).toHaveAttribute('src', '/pics/1.png')
    expect(images[1]).toHaveAttribute('src', '/pics/2.png')

    // Check alt text
    expect(images[0]).toHaveAttribute('alt', '.NET Bot Black Hoodie')
    expect(images[1]).toHaveAttribute('alt', '.NET Black & White Mug')
  })

  it('renders empty state when no items', () => {
    renderWithRouter(<CatalogTable items={[]} />)

    expect(screen.getByText('No data was returned.')).toBeInTheDocument()
  })

  it('renders price with currency formatting', () => {
    renderWithRouter(<CatalogTable items={mockItems} />)

    // Prices should be formatted with 2 decimal places
    // Note: $ symbol is added via CSS (.esh-price:before), not in DOM text
    expect(screen.getByText('19.50')).toBeInTheDocument()
    expect(screen.getByText('8.50')).toBeInTheDocument()

    // Verify esh-price class is applied (CSS adds $ symbol)
    const priceElements = document.querySelectorAll('.esh-price')
    expect(priceElements.length).toBeGreaterThanOrEqual(2)
  })

  it('renders stock values', () => {
    renderWithRouter(<CatalogTable items={mockItems} />)

    // Available stock (appears twice, once for each item)
    const stockValues = screen.getAllByText('100')
    expect(stockValues.length).toBeGreaterThanOrEqual(2)

    // Restock threshold
    expect(screen.getAllByText('10').length).toBeGreaterThanOrEqual(2)

    // Max stock threshold
    expect(screen.getAllByText('200').length).toBeGreaterThanOrEqual(2)
  })
})
