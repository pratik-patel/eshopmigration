/**
 * Unit tests for Layout component.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Layout } from "./Layout";

describe("Layout", () => {
  it("renders header with brand logo", () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const brandImages = screen.getAllByAltText("eShop Brand");
    expect(brandImages.length).toBeGreaterThan(0);
  });

  it("renders hero section with title", () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(screen.getByText("Catalog Manager")).toBeInTheDocument();
    expect(screen.getByText("(WebForms)")).toBeInTheDocument();
  });

  it("renders children content", () => {
    render(
      <Layout>
        <div data-testid="test-content">Test Content</div>
      </Layout>
    );

    expect(screen.getByTestId("test-content")).toBeInTheDocument();
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  it("renders footer with brand and footer text images", () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const footerTextImage = screen.getByAltText("footer text image");
    expect(footerTextImage).toBeInTheDocument();
  });

  it("has correct semantic structure", () => {
    const { container } = render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(container.querySelector("header")).toBeInTheDocument();
    expect(container.querySelector("main")).toBeInTheDocument();
    expect(container.querySelector("footer")).toBeInTheDocument();
  });

  it("applies layout classes correctly", () => {
    const { container } = render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(container.querySelector(".esh-header-brand")).toBeInTheDocument();
    expect(container.querySelector(".esh-app-hero")).toBeInTheDocument();
    expect(container.querySelector(".esh-header-title")).toBeInTheDocument();
    expect(container.querySelector(".esh-app-footer")).toBeInTheDocument();
  });
});
