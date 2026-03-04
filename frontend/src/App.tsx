/**
 * Main App component with routing.
 *
 * Configures React Router for all catalog pages.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Layout } from "./components/layout/Layout";
import { CatalogListPage } from "./pages/catalog/CatalogListPage";
import { CreatePage } from "./pages/catalog/CreatePage";
import { EditPage } from "./pages/catalog/EditPage";
import { DeletePage } from "./pages/catalog/DeletePage";
import { DetailsPage } from "./pages/catalog/DetailsPage";

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60000, // 1 minute
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

/**
 * App root with routing.
 *
 * Routes match ui-specification.json:
 * - / → CatalogListPage (Default.aspx)
 * - /catalog/create → CreatePage (Create.aspx)
 * - /catalog/edit/:id → EditPage (Edit.aspx)
 * - /catalog/delete/:id → DeletePage (Delete.aspx)
 * - /catalog/details/:id → DetailsPage (Details.aspx)
 */
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            {/* Home page - catalog list */}
            <Route path="/" element={<CatalogListPage />} />

            {/* Create new item */}
            <Route path="/catalog/create" element={<CreatePage />} />

            {/* Edit existing item */}
            <Route path="/catalog/edit/:id" element={<EditPage />} />

            {/* Delete item (confirmation) */}
            <Route path="/catalog/delete/:id" element={<DeletePage />} />

            {/* View item details */}
            <Route path="/catalog/details/:id" element={<DetailsPage />} />

            {/* Fallback: redirect to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
