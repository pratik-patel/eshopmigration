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
│   └── lib/
│       ├── utils.ts
│       └── ws.ts                 # WebSocket client wrapper
│
├── tests/{unit,e2e}/
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
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

## Naming Conventions

- Files: `camelCase.ts`, `PascalCase.tsx` for components
- Types/interfaces: `PascalCase`
- Functions/vars: `camelCase`
- React components: `PascalCase`

## Data Conventions

- Channel ID format: Always `PluginId.ChannelName`
- Channel Status: `Good`, `Bad`, `Unknown` (string values, validated with Zod enum)
- Timestamps: ISO 8601 strings (parse with `new Date()` or date library)
