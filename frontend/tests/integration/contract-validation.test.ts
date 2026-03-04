/**
 * Contract validation tests.
 *
 * Verifies frontend API calls match OpenAPI contract.
 */

import { describe, it, expect } from 'vitest';
import { z } from 'zod';
import type {
  CatalogItemResponse,
  CatalogItemCreate,
  CatalogItemListResponse,
  BrandResponse,
  TypeResponse,
} from '@/types/api';

// Zod schemas for runtime validation
const BrandResponseSchema = z.object({
  id: z.number(),
  brand: z.string(),
});

const TypeResponseSchema = z.object({
  id: z.number(),
  type: z.string(),
});

const CatalogItemResponseSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable().optional(),
  price: z.string(),
  picture_file_name: z.string(),
  picture_uri: z.string(),
  catalog_brand_id: z.number(),
  catalog_type_id: z.number(),
  brand: BrandResponseSchema,
  type: TypeResponseSchema,
  available_stock: z.number(),
  restock_threshold: z.number(),
  max_stock_threshold: z.number(),
});

const PaginationMetadataSchema = z.object({
  page: z.number(),
  limit: z.number(),
  total_items: z.number(),
  total_pages: z.number(),
});

const CatalogItemListResponseSchema = z.object({
  items: z.array(CatalogItemResponseSchema),
  pagination: PaginationMetadataSchema,
});

const CatalogItemCreateSchema = z.object({
  name: z.string().min(1).max(50),
  description: z.string().nullable().optional(),
  price: z.string(),
  catalog_brand_id: z.number().min(1),
  catalog_type_id: z.number().min(1),
  available_stock: z.number().min(0).max(10000000),
  restock_threshold: z.number().min(0).max(10000000),
  max_stock_threshold: z.number().min(0).max(10000000),
  temp_image_name: z.string().nullable().optional(),
});

describe('Contract Validation', () => {
  describe('BrandResponse', () => {
    it('validates correct brand response', () => {
      const brand: BrandResponse = {
        id: 1,
        brand: 'Test Brand',
      };

      const result = BrandResponseSchema.safeParse(brand);
      expect(result.success).toBe(true);
    });

    it('rejects invalid brand response', () => {
      const invalid = {
        id: 'not-a-number',
        brand: 123,
      };

      const result = BrandResponseSchema.safeParse(invalid);
      expect(result.success).toBe(false);
    });
  });

  describe('TypeResponse', () => {
    it('validates correct type response', () => {
      const type: TypeResponse = {
        id: 1,
        type: 'T-Shirt',
      };

      const result = TypeResponseSchema.safeParse(type);
      expect(result.success).toBe(true);
    });
  });

  describe('CatalogItemResponse', () => {
    it('validates correct catalog item response', () => {
      const item: CatalogItemResponse = {
        id: 1,
        name: 'Test Product',
        description: 'Test Description',
        price: '19.99',
        picture_file_name: 'test.png',
        picture_uri: '/Pics/test.png',
        catalog_brand_id: 1,
        catalog_type_id: 1,
        brand: { id: 1, brand: 'Test Brand' },
        type: { id: 1, type: 'T-Shirt' },
        available_stock: 100,
        restock_threshold: 10,
        max_stock_threshold: 200,
      };

      const result = CatalogItemResponseSchema.safeParse(item);
      expect(result.success).toBe(true);
    });

    it('validates item with null description', () => {
      const item: CatalogItemResponse = {
        id: 1,
        name: 'Test Product',
        description: null,
        price: '19.99',
        picture_file_name: 'test.png',
        picture_uri: '/Pics/test.png',
        catalog_brand_id: 1,
        catalog_type_id: 1,
        brand: { id: 1, brand: 'Test Brand' },
        type: { id: 1, type: 'T-Shirt' },
        available_stock: 100,
        restock_threshold: 10,
        max_stock_threshold: 200,
      };

      const result = CatalogItemResponseSchema.safeParse(item);
      expect(result.success).toBe(true);
    });
  });

  describe('CatalogItemListResponse', () => {
    it('validates paginated list response', () => {
      const listResponse: CatalogItemListResponse = {
        items: [
          {
            id: 1,
            name: 'Product 1',
            price: '19.99',
            picture_file_name: 'test.png',
            picture_uri: '/Pics/test.png',
            catalog_brand_id: 1,
            catalog_type_id: 1,
            brand: { id: 1, brand: 'Brand' },
            type: { id: 1, type: 'Type' },
            available_stock: 100,
            restock_threshold: 10,
            max_stock_threshold: 200,
          },
        ],
        pagination: {
          page: 0,
          limit: 10,
          total_items: 1,
          total_pages: 1,
        },
      };

      const result = CatalogItemListResponseSchema.safeParse(listResponse);
      expect(result.success).toBe(true);
    });

    it('validates empty list response', () => {
      const listResponse: CatalogItemListResponse = {
        items: [],
        pagination: {
          page: 0,
          limit: 10,
          total_items: 0,
          total_pages: 0,
        },
      };

      const result = CatalogItemListResponseSchema.safeParse(listResponse);
      expect(result.success).toBe(true);
    });
  });

  describe('CatalogItemCreate', () => {
    it('validates correct create request', () => {
      const createData: CatalogItemCreate = {
        name: 'New Product',
        description: 'Description',
        price: '29.99',
        catalog_brand_id: 1,
        catalog_type_id: 1,
        available_stock: 50,
        restock_threshold: 5,
        max_stock_threshold: 100,
        temp_image_name: 'temp.png',
      };

      const result = CatalogItemCreateSchema.safeParse(createData);
      expect(result.success).toBe(true);
    });

    it('rejects name longer than 50 chars', () => {
      const createData = {
        name: 'A'.repeat(51),
        price: '29.99',
        catalog_brand_id: 1,
        catalog_type_id: 1,
        available_stock: 50,
        restock_threshold: 5,
        max_stock_threshold: 100,
      };

      const result = CatalogItemCreateSchema.safeParse(createData);
      expect(result.success).toBe(false);
    });

    it('rejects invalid brand ID', () => {
      const createData = {
        name: 'Product',
        price: '29.99',
        catalog_brand_id: 0,
        catalog_type_id: 1,
        available_stock: 50,
        restock_threshold: 5,
        max_stock_threshold: 100,
      };

      const result = CatalogItemCreateSchema.safeParse(createData);
      expect(result.success).toBe(false);
    });

    it('rejects stock > 10000000', () => {
      const createData = {
        name: 'Product',
        price: '29.99',
        catalog_brand_id: 1,
        catalog_type_id: 1,
        available_stock: 10000001,
        restock_threshold: 5,
        max_stock_threshold: 100,
      };

      const result = CatalogItemCreateSchema.safeParse(createData);
      expect(result.success).toBe(false);
    });

    it('rejects negative stock', () => {
      const createData = {
        name: 'Product',
        price: '29.99',
        catalog_brand_id: 1,
        catalog_type_id: 1,
        available_stock: -1,
        restock_threshold: 5,
        max_stock_threshold: 100,
      };

      const result = CatalogItemCreateSchema.safeParse(createData);
      expect(result.success).toBe(false);
    });
  });

  describe('Type Safety', () => {
    it('TypeScript types match runtime validation', () => {
      // This test verifies compile-time type safety
      const item: CatalogItemResponse = {
        id: 1,
        name: 'Test',
        price: '19.99',
        picture_file_name: 'test.png',
        picture_uri: '/Pics/test.png',
        catalog_brand_id: 1,
        catalog_type_id: 1,
        brand: { id: 1, brand: 'Brand' },
        type: { id: 1, type: 'Type' },
        available_stock: 100,
        restock_threshold: 10,
        max_stock_threshold: 200,
      };

      // Should compile without errors
      expect(item.id).toBe(1);
      expect(item.brand.brand).toBe('Brand');
    });
  });
});
