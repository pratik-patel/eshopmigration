/**
 * Unit tests for Pagination component.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Pagination } from '@/components/catalog/Pagination';
import type { PaginationMetadata } from '@/types/api';

describe('Pagination', () => {
  const mockOnPageChange = vi.fn();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders Previous and Next buttons', () => {
    const pagination: PaginationMetadata = {
      page: 1,
      limit: 10,
      total_items: 30,
      total_pages: 3,
    };

    render(<Pagination pagination={pagination} onPageChange={mockOnPageChange} />);

    expect(screen.getByText('Previous')).toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
  });

  it('shows current page indicator', () => {
    const pagination: PaginationMetadata = {
      page: 1,
      limit: 10,
      total_items: 30,
      total_pages: 3,
    };

    render(<Pagination pagination={pagination} onPageChange={mockOnPageChange} />);

    expect(screen.getByText('Page 2 of 3')).toBeInTheDocument();
  });

  it('disables Previous button on first page', () => {
    const pagination: PaginationMetadata = {
      page: 0,
      limit: 10,
      total_items: 30,
      total_pages: 3,
    };

    render(<Pagination pagination={pagination} onPageChange={mockOnPageChange} />);

    const prevButton = screen.getByText('Previous');
    expect(prevButton).toBeDisabled();
    expect(prevButton).toHaveClass('esh-pager-item--disabled');
  });

  it('disables Next button on last page', () => {
    const pagination: PaginationMetadata = {
      page: 2,
      limit: 10,
      total_items: 30,
      total_pages: 3,
    };

    render(<Pagination pagination={pagination} onPageChange={mockOnPageChange} />);

    const nextButton = screen.getByText('Next');
    expect(nextButton).toBeDisabled();
    expect(nextButton).toHaveClass('esh-pager-item--disabled');
  });

  it('calls onPageChange with previous page', () => {
    const pagination: PaginationMetadata = {
      page: 1,
      limit: 10,
      total_items: 30,
      total_pages: 3,
    };

    render(<Pagination pagination={pagination} onPageChange={mockOnPageChange} />);

    const prevButton = screen.getByText('Previous');
    fireEvent.click(prevButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(0);
  });

  it('calls onPageChange with next page', () => {
    const pagination: PaginationMetadata = {
      page: 1,
      limit: 10,
      total_items: 30,
      total_pages: 3,
    };

    render(<Pagination pagination={pagination} onPageChange={mockOnPageChange} />);

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(2);
  });

  it('hides when only one page', () => {
    const pagination: PaginationMetadata = {
      page: 0,
      limit: 10,
      total_items: 5,
      total_pages: 1,
    };

    const { container } = render(
      <Pagination pagination={pagination} onPageChange={mockOnPageChange} />
    );

    expect(container.firstChild).toBeNull();
  });

  it('hides when no items', () => {
    const pagination: PaginationMetadata = {
      page: 0,
      limit: 10,
      total_items: 0,
      total_pages: 0,
    };

    const { container } = render(
      <Pagination pagination={pagination} onPageChange={mockOnPageChange} />
    );

    expect(container.firstChild).toBeNull();
  });
});
