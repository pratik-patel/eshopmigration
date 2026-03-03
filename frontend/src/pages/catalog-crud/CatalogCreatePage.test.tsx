/**
 * Unit tests for CatalogCreatePage.
 *
 * Tests validation, form submission, and error handling.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { CatalogCreatePage } from './CatalogCreatePage'
import * as catalogApi from '@/api/catalog'

// Mock the API module
vi.mock('@/api/catalog', () => ({
  createCatalogItem: vi.fn(),
  getCatalogBrands: vi.fn(),
  getCatalogTypes: vi.fn(),
}))

const mockBrands = [
  { id: 1, brand: '.NET' },
  { id: 2, brand: 'Other' },
  { id: 3, brand: 'Azure' },
  { id: 4, brand: 'Visual Studio' },
  { id: 5, brand: 'SQL Server' },
]

const mockTypes = [
  { id: 1, type: 'Mug' },
  { id: 2, type: 'T-Shirt' },
  { id: 3, type: 'Sheet' },
  { id: 4, type: 'USB Memory Stick' },
]

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {ui}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('CatalogCreatePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock brands and types API calls
    vi.mocked(catalogApi.getCatalogBrands).mockResolvedValue(mockBrands)
    vi.mocked(catalogApi.getCatalogTypes).mockResolvedValue(mockTypes)
  })

  it('renders create form with all fields', async () => {
    renderWithProviders(<CatalogCreatePage />)

    // Check title
    expect(screen.getByText('Create')).toBeInTheDocument()

    // Check form fields
    await waitFor(() => {
      expect(screen.getByLabelText('Name')).toBeInTheDocument()
    })
    expect(screen.getByLabelText('Description')).toBeInTheDocument()
    expect(screen.getByLabelText('Brand')).toBeInTheDocument()
    expect(screen.getByLabelText('Type')).toBeInTheDocument()
    expect(screen.getByLabelText('Price')).toBeInTheDocument()
    expect(screen.getByLabelText('Stock')).toBeInTheDocument()
    expect(screen.getByLabelText('Restock')).toBeInTheDocument()
    expect(screen.getByLabelText('Max stock')).toBeInTheDocument()

    // Check buttons
    expect(screen.getByText('[ Create ]')).toBeInTheDocument()
    expect(screen.getByText('[ Cancel ]')).toBeInTheDocument()
  })

  it('shows validation error when name is empty', async () => {
    const user = userEvent.setup()
    renderWithProviders(<CatalogCreatePage />)

    await waitFor(() => {
      expect(screen.getByLabelText('Name')).toBeInTheDocument()
    })

    // Try to submit without filling name
    const submitButton = screen.getByText('[ Create ]')
    await user.click(submitButton)

    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText('The Name field is required.')).toBeInTheDocument()
    })
  })

  it('shows validation error for invalid price', async () => {
    const user = userEvent.setup()
    renderWithProviders(<CatalogCreatePage />)

    await waitFor(() => {
      expect(screen.getByLabelText('Name')).toBeInTheDocument()
    })

    // Fill name and invalid price
    const nameInput = screen.getByLabelText('Name')
    const priceInput = screen.getByLabelText('Price')

    await user.type(nameInput, 'Test Product')
    await user.clear(priceInput)
    await user.type(priceInput, '-5')

    // Submit form
    const submitButton = screen.getByText('[ Create ]')
    await user.click(submitButton)

    // Check for validation error
    await waitFor(() => {
      expect(
        screen.getByText('The Price must be a positive number with maximum two decimals between 0 and 1 million.')
      ).toBeInTheDocument()
    })
  })

  it('successfully creates catalog item with valid data', async () => {
    const user = userEvent.setup()

    const mockCreatedItem = {
      id: 13,
      name: 'Test Product',
      description: 'Test Description',
      price: 19.99,
      picture_file_name: 'dummy.png',
      picture_uri: null,
      catalog_type_id: 2,
      catalog_brand_id: 1,
      available_stock: 100,
      restock_threshold: 10,
      max_stock_threshold: 200,
      on_reorder: false,
      catalog_type: { id: 2, type: 'T-Shirt' },
      catalog_brand: { id: 1, brand: '.NET' },
    }

    vi.mocked(catalogApi.createCatalogItem).mockResolvedValue(mockCreatedItem)

    renderWithProviders(<CatalogCreatePage />)

    await waitFor(() => {
      expect(screen.getByLabelText('Name')).toBeInTheDocument()
    })

    // Fill form with valid data
    await user.type(screen.getByLabelText('Name'), 'Test Product')
    await user.type(screen.getByLabelText('Description'), 'Test Description')
    await user.selectOptions(screen.getByLabelText('Brand'), '1')
    await user.selectOptions(screen.getByLabelText('Type'), '2')
    await user.clear(screen.getByLabelText('Price'))
    await user.type(screen.getByLabelText('Price'), '19.99')
    await user.clear(screen.getByLabelText('Stock'))
    await user.type(screen.getByLabelText('Stock'), '100')
    await user.clear(screen.getByLabelText('Restock'))
    await user.type(screen.getByLabelText('Restock'), '10')
    await user.clear(screen.getByLabelText('Max stock'))
    await user.type(screen.getByLabelText('Max stock'), '200')

    // Submit form
    const submitButton = screen.getByText('[ Create ]')
    await user.click(submitButton)

    // Verify API was called
    await waitFor(() => {
      expect(catalogApi.createCatalogItem).toHaveBeenCalledWith({
        name: 'Test Product',
        description: 'Test Description',
        catalog_brand_id: 1,
        catalog_type_id: 2,
        price: 19.99,
        available_stock: 100,
        restock_threshold: 10,
        max_stock_threshold: 200,
        picture_file_name: 'dummy.png',
      })
    })
  })

  it('displays server validation errors from 400 response', async () => {
    const user = userEvent.setup()

    // Mock API to return validation error
    const apiError = {
      name: 'ApiError',
      message: 'Validation failed',
      status: 400,
      details: {
        code: 'validation_error',
        message: 'Validation failed',
        detail: {
          price: 'The Price must be a positive number with maximum two decimals between 0 and 1 million.',
        },
      },
    }

    vi.mocked(catalogApi.createCatalogItem).mockRejectedValue(apiError)

    renderWithProviders(<CatalogCreatePage />)

    await waitFor(() => {
      expect(screen.getByLabelText('Name')).toBeInTheDocument()
    })

    // Fill form with data that will trigger server error
    await user.type(screen.getByLabelText('Name'), 'Test Product')
    await user.selectOptions(screen.getByLabelText('Brand'), '1')
    await user.selectOptions(screen.getByLabelText('Type'), '2')
    await user.clear(screen.getByLabelText('Price'))
    await user.type(screen.getByLabelText('Price'), '2000000')

    // Submit form
    const submitButton = screen.getByText('[ Create ]')
    await user.click(submitButton)

    // Wait for server error to be displayed
    await waitFor(() => {
      expect(
        screen.getByText('The Price must be a positive number with maximum two decimals between 0 and 1 million.')
      ).toBeInTheDocument()
    })
  })

  it('loads brands and types dropdowns', async () => {
    renderWithProviders(<CatalogCreatePage />)

    // Wait for dropdowns to be populated
    await waitFor(() => {
      const brandSelect = screen.getByLabelText('Brand')
      expect(brandSelect).toBeInTheDocument()

      // Check that brands are loaded (5 brands + 1 "Select Brand" option)
      const brandOptions = within(brandSelect as HTMLSelectElement).getAllByRole('option')
      expect(brandOptions).toHaveLength(6)
      expect(brandOptions[1]).toHaveTextContent('.NET')
    })

    await waitFor(() => {
      const typeSelect = screen.getByLabelText('Type')
      expect(typeSelect).toBeInTheDocument()

      // Check that types are loaded (4 types + 1 "Select Type" option)
      const typeOptions = within(typeSelect as HTMLSelectElement).getAllByRole('option')
      expect(typeOptions).toHaveLength(5)
      expect(typeOptions[1]).toHaveTextContent('Mug')
    })
  })
})
