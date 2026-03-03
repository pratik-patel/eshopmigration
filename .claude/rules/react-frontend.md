# React Frontend Code Generation Rules

Apply these rules when generating any React/TypeScript frontend code for this migration project.

## Framework & Stack

- **React 18** with **TypeScript** (strict mode)
- **Vite** — build tool
- **React Router v6** — routing; one route per seam
- **TanStack Query (React Query) v5** — server state, caching, polling
- **Zustand** — client-only UI state (not for server data)
- **shadcn/ui + Tailwind CSS** — component library and styling
- **Zod** — runtime schema validation of API responses
- **openapi-typescript** — generate TypeScript types from OpenAPI spec

## Project Structure Convention

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx                   # Router root
│   │
│   ├── api/
│   │   ├── client.ts             # Base fetch wrapper
│   │   ├── channels.ts           # Channel API calls
│   │   └── archiver.ts           # History API calls
│   │
│   ├── hooks/
│   │   ├── useChannel.ts         # TanStack Query hooks
│   │   ├── useChannelStream.ts   # WebSocket hook
│   │   └── useArchiverHistory.ts
│   │
│   ├── components/
│   │   ├── ui/                   # shadcn base components (do not modify)
│   │   ├── channels/             # Channel-specific components
│   │   │   ├── ChannelValue.tsx
│   │   │   ├── ChannelStatus.tsx
│   │   │   └── ChannelList.tsx
│   │   └── layout/
│   │       ├── AppShell.tsx
│   │       └── Sidebar.tsx
│   │
│   ├── pages/                    # One folder per seam route
│   │   ├── channels/
│   │   │   └── ChannelsPage.tsx
│   │   ├── archiver/
│   │   │   └── ArchiverPage.tsx
│   │   └── designer/
│   │       └── DesignerPage.tsx
│   │
│   ├── stores/                   # Zustand stores (UI state only)
│   │   └── uiStore.ts
│   │
│   ├── types/                    # Generated + hand-written types
│   │   └── api.d.ts              # Generated from OpenAPI spec
│   │
│   ├── assets/                   # Static assets (imported in code)
│   │   ├── catalog/              # Seam-specific assets
│   │   │   ├── index.ts          # Typed exports
│   │   │   └── *.png|svg|jpg
│   │   └── orders/
│   │       └── ...
│   │
│   └── lib/
│       ├── utils.ts
│       └── ws.ts                 # WebSocket client wrapper
│
├── public/                       # Static assets (served directly)
│   ├── favicon.ico
│   └── shared/                   # Shared assets
│       └── *.png|svg|jpg
│
├── tests/{unit,e2e}/
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

## Static Asset Management

### Directory Structure

```
frontend/
├── public/                      # Static assets served directly
│   ├── favicon.ico
│   ├── logo.png                 # App-wide logo
│   └── shared/                  # Shared across multiple seams
│       ├── company-logo.png
│       └── icons/
│           └── common-icon.svg
│
└── src/
    └── assets/                  # Assets imported in code
        ├── catalog/             # Seam-specific assets
        │   ├── index.ts         # Typed exports
        │   ├── product-placeholder.png
        │   └── icons/
        │       └── save.svg
        └── orders/              # Another seam
            ├── index.ts
            └── ...
```

### Asset Import Pattern

**Always use typed imports** — never hardcode paths in components.

```typescript
// src/assets/catalog/index.ts
export const catalogAssets = {
  productPlaceholder: new URL('./product-placeholder.png', import.meta.url).href,
  saveIcon: new URL('./icons/save.svg', import.meta.url).href,
  // Shared assets (in public/)
  companyLogo: '/shared/company-logo.png',
} as const;

export type CatalogAsset = keyof typeof catalogAssets;
```

```typescript
// In component: src/components/catalog/ProductCard.tsx
import { catalogAssets } from '@/assets/catalog';

export function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="card">
      <img
        src={product.imageUrl || catalogAssets.productPlaceholder}
        alt={product.name}
        className="w-full h-48 object-cover"
      />
      <button className="btn">
        <img src={catalogAssets.saveIcon} alt="" className="w-4 h-4" />
        Save
      </button>
    </div>
  );
}
```

### Asset Optimization Rules

**Before copying assets:**
- Compress images > 500KB (use `sharp`, `imagemin`, or online tools)
- Convert icons to SVG where possible (better scaling, smaller size)
- Use WebP format for photos where browser support allows (with fallback)
- Remove unused assets (verify usage in `ui-behavior.md`)

**Image format guidelines:**
- **Icons/logos with simple shapes** → SVG (infinitely scalable, small size)
- **Photos with transparency** → PNG (or WebP with PNG fallback)
- **Photos without transparency** → JPG or WebP (smaller than PNG)
- **Favicons** → ICO (multi-size) or PNG (single size)

### Vite Asset Handling

Vite automatically processes assets:

```typescript
// Imported assets get content hash in filename
import logo from './logo.png'; // → /assets/logo-a3b2c1d4.png

// Public folder assets keep original path
<img src="/shared/logo.png" /> // → /shared/logo.png (no hash)
```

**Rules:**
- Use `public/` for assets that need stable URLs (SEO images, favicons, robots.txt)
- Use `src/assets/` for component-specific assets (gets optimized and hashed)
- Never put large files (> 1MB) in `src/assets/` — use `public/` or CDN

### Forbidden Asset Patterns

- ❌ No hardcoded paths in components: `<img src="/assets/catalog/product.png" />`
- ❌ No direct references to legacy paths: `<img src="C:\Legacy\Images\product.png" />`
- ❌ No inline data URIs for large images (> 10KB)
- ❌ No unoptimized assets (compress images before copying)
- ❌ No assets without alt text (accessibility requirement)

### Asset Loading States

Always handle loading states for images:

```typescript
import { useState } from 'react';

export function ProductImage({ src, alt }: { src: string; alt: string }) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  return (
    <div className="relative">
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
      <img
        src={src}
        alt={alt}
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setIsLoading(false);
          setHasError(true);
        }}
        className={`transition-opacity ${isLoading ? 'opacity-0' : 'opacity-100'}`}
      />
      {hasError && (
        <div className="text-red-500">Failed to load image</div>
      )}
    </div>
  );
}
```

## TypeScript Rules

- `strict: true` in tsconfig — no exceptions
- **No `any`** — use `unknown` and narrow explicitly
- All API response shapes must be validated with Zod at the boundary
- Types for API responses come from `openapi-typescript` output — do not hand-write what can be generated

```typescript
// Bad
const data: any = await fetch(...).then(r => r.json());

// Good
import { z } from "zod";
import type { components } from "@/types/api";

type ChannelState = components["schemas"]["ChannelStateDto"];

const ChannelStateSchema = z.object({
  channelId: z.string(),
  value: z.string(),
  type: z.string(),
  modifyTime: z.string().datetime(),
  status: z.enum(["Good", "Bad", "Unknown"]),
});
```

## Data Fetching

- All server state via TanStack Query — **no `useEffect` + `useState` for API calls**
- Polling interval for channel values: configurable, default 2s (matching legacy OPC timer)
- WebSocket connection for real-time updates: use a custom `useChannelStream` hook

```typescript
// Real-time channel updates
function useChannelStream(channelIds: string[]) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/ws/channels`);
    ws.onmessage = (event) => {
      const update = ChannelUpdateSchema.parse(JSON.parse(event.data));
      queryClient.setQueryData(["channel", update.channelId], update);
    };
    return () => ws.close();
  }, [channelIds, queryClient]);
}
```

## Component Rules

- Components are function components with **named exports** — no default exports from component files
- Props must be typed with explicit interfaces — no inline object types for props
- UI components in `components/` are pure/presentational — no API calls inside them
- Data fetching happens in page-level components or dedicated hooks
- Use `React.memo` only when there is a measured performance problem

## Real-time Display (Channel Values)

The legacy system used WPF bindings and `INotifyPropertyChanged`. In React:

- Channel values live in TanStack Query cache, updated via WebSocket messages
- `ChannelValue` component subscribes to the query cache key `["channel", channelId]`
- Status colors: `Good → green`, `Bad → red`, `Unknown → gray` — defined as Tailwind classes, not inline styles

## Routing

One route per seam workflow:

```typescript
// App.tsx
<Routes>
  <Route path="/" element={<AppShell />}>
    <Route index element={<Navigate to="/channels" />} />
    <Route path="channels" element={<ChannelsPage />} />
    <Route path="archiver" element={<ArchiverPage />} />
    <Route path="designer" element={<DesignerPage />} />
  </Route>
</Routes>
```

Route paths must match the seam name in `seams/`.

## Error Handling

- All API errors must be caught and displayed — **never silently swallow errors**
- Use TanStack Query's `onError` and `error` state
- Global error boundary at `AppShell` level

## Testing

- **Unit/component tests** — Vitest + React Testing Library
- **E2E tests** — Playwright; cover the happy path of each seam
- Test files co-located with source: `ChannelValue.test.tsx` next to `ChannelValue.tsx`

## Forbidden Patterns

- ❌ No class components
- ❌ No `useEffect` for data fetching — always TanStack Query
- ❌ No inline styles — Tailwind only
- ❌ No `any` types
- ❌ No direct `window.location` manipulation — use React Router's `useNavigate`
- ❌ No business logic in components — extract to hooks or services
- ❌ No hardcoded asset paths — always import from typed asset index
- ❌ No unoptimized or uncompressed assets — compress before copying
- ❌ No images without alt text — accessibility requirement

## Naming Conventions

- Files: `camelCase.ts`, `PascalCase.tsx` for components
- Types/interfaces: `PascalCase`
- Functions/vars: `camelCase`
- React components: `PascalCase`

## Data Conventions

- Channel ID format: Always `PluginId.ChannelName`
- Channel Status: `Good`, `Bad`, `Unknown` (string values, validated with Zod enum)
- Timestamps: ISO 8601 strings (parse with `new Date()` or date library)
