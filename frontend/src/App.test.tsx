/**
 * App routing tests.
 *
 * Verifies all routes are configured correctly.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from './App';

// Mock API calls for testing
vi.mock('./api/catalog', () => ({
  listCatalogItems: vi.fn(() =>
    Promise.resolve({
      items: [],
      pagination: { page: 0, limit: 10, total_items: 0, total_pages: 0 },
    })
  ),
  getCatalogItem: vi.fn(() =>
    Promise.resolve({
      id: 1,
      name: 'Test Product',
      price: '19.99',
      picture_file_name: 'test.png',
      picture_uri: '/Pics/test.png',
      catalog_brand_id: 1,
      catalog_type_id: 1,
      brand: { id: 1, brand: 'Test Brand' },
      type: { id: 1, type: 'Test Type' },
      available_stock: 100,
      restock_threshold: 10,
      max_stock_threshold: 200,
    })
  ),
  listBrands: vi.fn(() => Promise.resolve([{ id: 1, brand: 'Test Brand' }])),
  listTypes: vi.fn(() => Promise.resolve([{ id: 1, type: 'Test Type' }])),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

describe('App Routing', () => {
  it('renders catalog list page at root path', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/']}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText(/Catalog Items/i)).toBeInTheDocument();
  });

  it('renders create page at /catalog/create', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/catalog/create']}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText(/Create/i)).toBeInTheDocument();
  });

  it('redirects unknown routes to home', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/unknown-route']}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText(/Catalog Items/i)).toBeInTheDocument();
  });
});
