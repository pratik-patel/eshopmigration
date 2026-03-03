import { Routes, Route, Navigate } from 'react-router-dom'
import { AppShell } from './components/layout/AppShell'
import { CatalogListPage } from './pages/catalog-list/CatalogListPage'
import { CatalogCreatePage } from './pages/catalog-crud/CatalogCreatePage'
import { CatalogEditPage } from './pages/catalog-crud/CatalogEditPage'
import { CatalogDetailsPage } from './pages/catalog-crud/CatalogDetailsPage'
import { CatalogDeletePage } from './pages/catalog-crud/CatalogDeletePage'
import { AboutPage } from './pages/static/AboutPage'
import { ContactPage } from './pages/static/ContactPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}>
        {/* Catalog List */}
        <Route index element={<CatalogListPage />} />

        {/* Catalog CRUD */}
        <Route path="catalog/create" element={<CatalogCreatePage />} />
        <Route path="catalog/edit/:id" element={<CatalogEditPage />} />
        <Route path="catalog/details/:id" element={<CatalogDetailsPage />} />
        <Route path="catalog/delete/:id" element={<CatalogDeletePage />} />

        {/* Static Pages */}
        <Route path="about" element={<AboutPage />} />
        <Route path="contact" element={<ContactPage />} />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
