/**
 * Tests for CatalogListPage component.
 *
 * Validates catalog list page behavior against legacy ui-behavior.md specifications.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { CatalogListPage } from './CatalogListPage'
import * as catalogApi from '@/api/catalog'

// Mock the catalog API
vi.mock('@/api/catalog')

// Test data matching runtime-verified data from legacy-golden/grid-data.json
const mockCatalogResponse = {
  page_index: 0,
  page_size: 10,
  total_items: 10,
  total_pages: 1,
  data: [
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
      restock_threshold: 0,
      max_stock_threshold: 0,
      on_reorder: false,
      catalog_brand: {
        id: 2,
        brand: '.NET',
      },
      catalog_type: {
        id: 2,
        type: 'T-Shirt',
      },
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
      restock_threshold: 0,
      max_stock_threshold: 0,
      on_reorder: false,
      catalog_brand: {
        id: 2,
        brand: '.NET',
      },
      catalog_type: {
        id: 1,
        type: 'Mug',
      },
    },
  ],
}

function renderWithProviders(component: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('CatalogListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    vi.mocked(catalogApi.getCatalogItems).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    renderWithProviders(<CatalogListPage />)

    expect(screen.getByText('Loading catalog items...')).toBeInTheDocument()
  })

  it('renders catalog items after loading', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      expect(screen.getByText('.NET Bot Black Hoodie')).toBeInTheDocument()
    })

    expect(screen.getByText('.NET Black & White Mug')).toBeInTheDocument()
  })

  it('renders Create New button with correct CSS classes', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      const createButton = screen.getByText('Create New')
      expect(createButton).toBeInTheDocument()
      expect(createButton).toHaveClass('btn', 'esh-button', 'esh-button-primary')
    })
  })

  it('renders all table columns', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      expect(screen.getByText('Name')).toBeInTheDocument()
    })

    expect(screen.getByText('Description')).toBeInTheDocument()
    expect(screen.getByText('Brand')).toBeInTheDocument()
    expect(screen.getByText('Type')).toBeInTheDocument()
    expect(screen.getByText('Price')).toBeInTheDocument()
    expect(screen.getByText('Picture name')).toBeInTheDocument()
    expect(screen.getByText('Stock')).toBeInTheDocument()
    expect(screen.getByText('Restock')).toBeInTheDocument()
    expect(screen.getByText('Max stock')).toBeInTheDocument()
  })

  it('renders product images with correct paths', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      const images = screen.getAllByRole('img')
      expect(images.length).toBeGreaterThan(0)
    })

    const firstImage = screen.getByAltText('.NET Bot Black Hoodie')
    expect(firstImage).toHaveAttribute('src', '/pics/1.png')
    expect(firstImage).toHaveClass('esh-thumbnail')
  })

  it('renders action links for each product', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      const editLinks = screen.getAllByText('Edit')
      expect(editLinks.length).toBe(2)
    })

    expect(screen.getAllByText('Details').length).toBe(2)
    expect(screen.getAllByText('Delete').length).toBe(2)
  })

  it('does not render pagination when total_pages is 1', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      expect(screen.getByText('.NET Bot Black Hoodie')).toBeInTheDocument()
    })

    expect(screen.queryByText('Previous')).not.toBeInTheDocument()
    expect(screen.queryByText('Next')).not.toBeInTheDocument()
  })

  it('renders pagination when total_pages > 1', async () => {
    const multiPageResponse = {
      ...mockCatalogResponse,
      total_items: 25,
      total_pages: 3,
    }

    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(multiPageResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      expect(screen.getByText('Previous')).toBeInTheDocument()
    })

    expect(screen.getByText('Next')).toBeInTheDocument()
    expect(screen.getByText(/Showing 1 to 10 of 25 products - Page 1 - 3/)).toBeInTheDocument()
  })

  it('renders empty state when no items', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue({
      page_index: 0,
      page_size: 10,
      total_items: 0,
      total_pages: 0,
      data: [],
    })

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      expect(screen.getByText('No data was returned.')).toBeInTheDocument()
    })
  })

  it('renders error state on API failure', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockRejectedValue(
      new Error('Failed to fetch catalog items')
    )

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      expect(screen.getByText(/Error loading catalog items/)).toBeInTheDocument()
    })

    expect(screen.getByText(/Failed to fetch catalog items/)).toBeInTheDocument()
  })

  it('formats prices correctly with esh-price class', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      const priceElements = screen.getAllByText(/19\.50|8\.50/)
      expect(priceElements.length).toBeGreaterThan(0)
    })

    // Check that esh-price class is applied (CSS adds $ via :before)
    const priceSpan = document.querySelector('.esh-price')
    expect(priceSpan).toBeInTheDocument()
  })

  it('displays brand and type from navigation properties', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      expect(screen.getAllByText('.NET').length).toBeGreaterThan(0)
    })

    expect(screen.getByText('T-Shirt')).toBeInTheDocument()
    expect(screen.getByText('Mug')).toBeInTheDocument()
  })

  it('displays stock values', async () => {
    vi.mocked(catalogApi.getCatalogItems).mockResolvedValue(mockCatalogResponse)

    renderWithProviders(<CatalogListPage />)

    await waitFor(() => {
      const stockValues = screen.getAllByText('100')
      expect(stockValues.length).toBeGreaterThan(0)
    })
  })
})
