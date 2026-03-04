/**
 * Main layout component matching legacy Site.Master structure.
 *
 * Provides consistent header, hero section, content area, and footer across all pages.
 */

import { ReactNode } from "react";

export interface LayoutProps {
  children: ReactNode;
}

/**
 * Layout component with header, hero, content, and footer.
 *
 * Structure matches legacy Site.Master:
 * - Header with brand logo
 * - Hero section with banner background and title
 * - Main content area (children)
 * - Footer with dark brand logo and footer text image
 */
export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="navbar navbar-light navbar-static-top">
        <div className="esh-header-brand">
          <a href="/">
            <img src="/images/brand.png" alt="eShop Brand" />
          </a>
        </div>
      </header>

      {/* Hero Section */}
      <section className="esh-app-hero">
        <div className="container esh-header">
          <h1 className="esh-header-title">
            Catalog Manager <span>(WebForms)</span>
          </h1>
        </div>
      </section>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="esh-app-footer">
        <div className="container">
          <article className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <section className="flex items-center">
              <img
                className="esh-app-footer-brand"
                src="/images/brand_dark.png"
                alt="eShop Brand"
              />
            </section>
            <section className="flex items-center justify-end">
              <img
                className="esh-app-footer-text hidden sm:block"
                src="/images/main_footer_text.png"
                width="335"
                height="26"
                alt="footer text image"
              />
            </section>
          </article>
        </div>
      </footer>
    </div>
  );
}
