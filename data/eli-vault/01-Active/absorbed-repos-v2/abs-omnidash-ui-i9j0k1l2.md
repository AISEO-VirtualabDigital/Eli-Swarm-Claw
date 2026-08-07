---
absorbedFrom: https://github.com/lalitdotdev/omnidash
absorbedAt: 2026-08-08
chunkType: dashboard-ui-pattern
tags: [omnidash, shadcn-ui, server-components, data-table, resizable-panels, cmdk, recharts, zustand, cookie-persistence, multi-store]
---

# OmniDash — E-Commerce Admin Dashboard UI Patterns

## Core Concept
Multi-vendor e-commerce admin dashboard built with Next.js 13 App Router + shadcn/ui + Prisma + Clerk. Uses server components for data fetching, client components only for interactivity.

## Pattern 1: Server Component Data Fetching (Zero Client JS for Data)
Pages fetch data directly in server components. No loading states needed at page level. Next.js handles streaming via `loading.tsx` Suspense boundaries.

```typescript
const DashboardPage = async ({ params }) => {
  const totalRevenue = await getTotalRevenue(params.storeId);
  const salesCount = await getSalesCount(params.storeId);
  // render with data — zero client JS
};
```

**Absorb into Eli**: Eli's dashboard page already does this partially. Make ALL dashboard stat cards fetch from server actions instead of client-side API calls.

## Pattern 2: Generic Reusable DataTable
Built on TanStack React Table v8. Features: configurable `searchKey` prop, column visibility dropdown, sorting, filtering, pagination. One DataTable serves all CRUD pages with different column definitions.

```typescript
export function DataTable<TData, TValue>({ columns, data, searchKey }: DataTableProps) {
  const table = useReactTable({ data, columns, state: { columnFilters, sorting, columnVisibility } });
}
```

**Absorb into Eli**: Create a generic DataTable for Keywords view and SEO Skills Registry. Currently they use simple lists — a proper DataTable with search/sort/column-visibility would be a major upgrade.

## Pattern 3: Cookie-Persisted Resizable Panels
`react-resizable-panels` with panel sizes persisted to cookies. User's layout survives page refreshes.

```typescript
onLayout={(sizes) => {
  document.cookie = `react-resizable-panels:layout=${JSON.stringify(sizes)}`;
}}
```

**Absorb into Eli**: Apply to the main dashboard layout — let users resize the sidebar vs main content area.

## Pattern 4: Store Switcher with cmdk
Apple-style command palette for quick navigation between multi-tenant stores. Uses `cmdk` library.

**Absorb into Eli**: Add a cmdk command palette (Ctrl+K) for quick navigation between dashboard views (Chat, Knowledge, Keywords, Skills, Settings).

## Pattern 5: KPI Cards + Revenue Chart
Server component fetches 4 data points in parallel. KPI grid (3 cards) + full-width bar chart below. Recharts with `ResponsiveContainer`.

**Absorb into Eli**: Eli's dashboard already has KPI cards. Add a Recharts bar chart showing vault queries over time or knowledge base growth.

## Pattern 6: Owner Authorization in Layout
Dashboard layout does auth check before rendering any child page. All child routes protected by default.

```typescript
const store = await prismadb.store.findFirst({ where: { id: params.storeId, userId } });
if (!store) { redirect('/'); }
```

## Pattern 7: cn() Utility (shadcn pattern)
`twMerge(clsx(inputs))` — safely merge Tailwind classes with conditional logic. Used everywhere.

## Pattern 8: Modal Provider (Client-Only Mount)
Prevents hydration mismatch for Radix Dialog components:

```typescript
const [isMounted, setIsMounted] = useState(false);
useEffect(() => { setIsMounted(true); }, []);
if (!isMounted) return null;
```

## Pattern 9: Dual API Layer
`app/api/` for public REST endpoints + `actions/` directory for direct DB access from dashboard. Clean separation.

**Absorb into Eli**: Eli already has `/api/` routes. Consider adding a `lib/actions/` for dashboard-only data access that skips HTTP overhead.

## Pattern 10: Minimal State Management
Only 2 Zustand stores: `useMailStore` (selected item) and `useStoreModal` (modal open/close). Most state is server-fetched.

**Absorb into Eli**: Keep client state minimal. Dashboard data should come from server components or API routes, not client state.
