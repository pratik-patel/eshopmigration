/**
 * Unit tests for ProductImage component.
 */

import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { ProductImage } from '@/components/catalog/ProductImage';

describe('ProductImage', () => {
  it('renders with thumbnail size', () => {
    render(
      <ProductImage
        pictureFileName="test.png"
        alt="Test Product"
        size="thumbnail"
      />
    );

    const img = screen.getByAltText('Test Product');
    expect(img).toHaveClass('esh-thumbnail');
  });

  it('renders with full size', () => {
    render(
      <ProductImage
        pictureFileName="test.png"
        alt="Test Product"
        size="full"
      />
    );

    const img = screen.getByAltText('Test Product');
    expect(img).toHaveClass('esh-picture');
  });

  it('uses dummy.png for null filename', () => {
    render(
      <ProductImage
        pictureFileName={null}
        alt="Test Product"
        size="thumbnail"
      />
    );

    const img = screen.getByAltText('Test Product');
    expect(img).toHaveAttribute('src', '/Pics/dummy.png');
  });

  it('uses dummy.png for empty filename', () => {
    render(
      <ProductImage
        pictureFileName=""
        alt="Test Product"
        size="thumbnail"
      />
    );

    const img = screen.getByAltText('Test Product');
    expect(img).toHaveAttribute('src', '/Pics/dummy.png');
  });

  it('constructs correct image URI', () => {
    render(
      <ProductImage
        pictureFileName="product.jpg"
        alt="Test Product"
        size="thumbnail"
      />
    );

    const img = screen.getByAltText('Test Product');
    expect(img).toHaveAttribute('src', '/Pics/product.jpg');
  });

  it('shows loading state initially', () => {
    const { container } = render(
      <ProductImage
        pictureFileName="test.png"
        alt="Test Product"
        size="thumbnail"
      />
    );

    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });
});
