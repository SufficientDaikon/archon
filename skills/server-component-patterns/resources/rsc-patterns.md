# RSC Patterns Reference

Practical code examples for Server Component architecture in Next.js App Router.

---

## 1. Server/Client Boundary Patterns

### Pattern A: Server Component with Direct Data Fetching

Server Components can be `async` and fetch data directly — no `useEffect`, no `useState`, no loading state management.

```tsx
// app/products/page.tsx — SERVER COMPONENT (default, no directive)
import { db } from "@/lib/db";
import { ProductCard } from "@/components/ProductCard";

export default async function ProductsPage() {
  const products = await db.product.findMany({
    where: { published: true },
    orderBy: { createdAt: "desc" },
  });

  return (
    <main>
      <h1>Products</h1>
      <div className="grid grid-cols-3 gap-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </main>
  );
}
```

### Pattern B: Extracting a Minimal Client Component

Only the interactive part gets `"use client"`. The parent stays on the server.

```tsx
// components/ProductCard.tsx — SERVER COMPONENT
// No directive needed. Pure display, receives data as props.
import { AddToCartButton } from "./AddToCartButton";

interface Product {
  id: string;
  name: string;
  price: number;
  imageUrl: string;
}

export function ProductCard({ product }: { product: Product }) {
  return (
    <div className="rounded-lg border p-4">
      <img src={product.imageUrl} alt={product.name} className="w-full" />
      <h2 className="text-lg font-semibold">{product.name}</h2>
      <p className="text-gray-600">${product.price.toFixed(2)}</p>
      {/* Only the button is a Client Component */}
      <AddToCartButton productId={product.id} />
    </div>
  );
}
```

```tsx
// components/AddToCartButton.tsx — CLIENT COMPONENT
"use client";

import { useState } from "react";
import { addToCart } from "@/app/actions/cart";

export function AddToCartButton({ productId }: { productId: string }) {
  const [pending, setPending] = useState(false);

  async function handleClick() {
    setPending(true);
    await addToCart(productId);
    setPending(false);
  }

  return (
    <button onClick={handleClick} disabled={pending} className="btn-primary">
      {pending ? "Adding..." : "Add to Cart"}
    </button>
  );
}
```

### Pattern C: Composition — Server Component Children Inside Client Component

Client Components can render Server Component children via the `children` prop. This keeps the client boundary small.

```tsx
// components/Sidebar.tsx — CLIENT COMPONENT (needs toggle state)
"use client";

import { useState } from "react";

export function Sidebar({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <aside className={isOpen ? "w-64" : "w-0 overflow-hidden"}>
      <button onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? "Close" : "Open"}
      </button>
      {isOpen && children}
    </aside>
  );
}
```

```tsx
// app/dashboard/page.tsx — SERVER COMPONENT
import { Sidebar } from "@/components/Sidebar";
import { db } from "@/lib/db";

export default async function DashboardPage() {
  const recentItems = await db.item.findMany({ take: 10 });

  return (
    <div className="flex">
      <Sidebar>
        {/* This entire list renders on the server, streamed into the client shell */}
        <ul>
          {recentItems.map((item) => (
            <li key={item.id}>{item.name}</li>
          ))}
        </ul>
      </Sidebar>
      <main>{/* ... */}</main>
    </div>
  );
}
```

### Pattern D: Avoiding Barrel File Contamination

Barrel files (`index.ts`) that re-export both server and client modules force the entire file into the client bundle.

```tsx
// BAD — barrel file mixes server and client exports
// components/index.ts
export { ProductCard } from "./ProductCard";       // Server Component
export { AddToCartButton } from "./AddToCartButton"; // Client Component
// Importing ProductCard from this barrel makes it a Client Component!

// GOOD — import directly from the component file
import { ProductCard } from "@/components/ProductCard";
import { AddToCartButton } from "@/components/AddToCartButton";
```

---

## 2. Streaming with Suspense

### Pattern E: Route-Level Streaming with loading.tsx

The simplest streaming pattern. Next.js automatically wraps `page.tsx` in a Suspense boundary using `loading.tsx` as the fallback.

```tsx
// app/products/loading.tsx — SERVER COMPONENT
export default function ProductsLoading() {
  return (
    <main>
      <h1>Products</h1>
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-64 animate-pulse rounded-lg bg-gray-200" />
        ))}
      </div>
    </main>
  );
}
```

### Pattern F: Nested Suspense for Independent Data

When a page has multiple independent data requirements, wrap each in its own Suspense boundary. The fast ones render first.

```tsx
// app/dashboard/page.tsx — SERVER COMPONENT
import { Suspense } from "react";
import { RevenueChart } from "@/components/RevenueChart";
import { RecentOrders } from "@/components/RecentOrders";
import { TopProducts } from "@/components/TopProducts";

export default function DashboardPage() {
  return (
    <main className="grid grid-cols-2 gap-6">
      {/* Each section streams independently */}
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />
      </Suspense>

      <Suspense fallback={<OrdersSkeleton />}>
        <RecentOrders />
      </Suspense>

      <Suspense fallback={<ProductsSkeleton />}>
        <TopProducts />
      </Suspense>
    </main>
  );
}

function ChartSkeleton() {
  return <div className="h-80 animate-pulse rounded-lg bg-gray-200" />;
}

function OrdersSkeleton() {
  return <div className="h-96 animate-pulse rounded-lg bg-gray-200" />;
}

function ProductsSkeleton() {
  return <div className="h-64 animate-pulse rounded-lg bg-gray-200" />;
}
```

```tsx
// components/RevenueChart.tsx — SERVER COMPONENT (async)
import { db } from "@/lib/db";

export async function RevenueChart() {
  // This query might be slow — Suspense handles the wait
  const revenue = await db.order.aggregate({
    _sum: { total: true },
    where: { createdAt: { gte: thirtyDaysAgo() } },
  });

  return (
    <div className="rounded-lg border p-4">
      <h2>Revenue (30 days)</h2>
      <p className="text-3xl font-bold">${revenue._sum.total?.toFixed(2)}</p>
    </div>
  );
}
```

### Pattern G: Streaming a List with Sequential Reveal

Use Suspense to show items as they resolve, rather than waiting for all data.

```tsx
// app/feed/page.tsx — SERVER COMPONENT
import { Suspense } from "react";
import { FeedItem } from "@/components/FeedItem";
import { getFeedIds } from "@/lib/feed";

export default async function FeedPage() {
  const feedIds = await getFeedIds(); // Fast: just IDs

  return (
    <ul>
      {feedIds.map((id) => (
        <Suspense key={id} fallback={<FeedItemSkeleton />}>
          {/* Each item fetches its own detailed data independently */}
          <FeedItem id={id} />
        </Suspense>
      ))}
    </ul>
  );
}
```

---

## 3. Server Actions

### Pattern H: Form with Server Action (Progressive Enhancement)

Forms using the `action` prop work even with JavaScript disabled.

```tsx
// app/actions/contact.ts
"use server";

import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";
import { z } from "zod";

const ContactSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email"),
  message: z.string().min(10, "Message must be at least 10 characters"),
});

export type ContactState = {
  errors?: Record<string, string[]>;
  success?: boolean;
};

export async function submitContact(
  prevState: ContactState,
  formData: FormData
): Promise<ContactState> {
  const parsed = ContactSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
    message: formData.get("message"),
  });

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors };
  }

  await db.contactSubmission.create({ data: parsed.data });
  revalidatePath("/contact");

  return { success: true };
}
```

```tsx
// components/ContactForm.tsx — CLIENT COMPONENT (needs useActionState)
"use client";

import { useActionState } from "react";
import { submitContact, type ContactState } from "@/app/actions/contact";

export function ContactForm() {
  const [state, formAction, pending] = useActionState<ContactState, FormData>(
    submitContact,
    {}
  );

  if (state.success) {
    return <p className="text-green-600">Message sent successfully!</p>;
  }

  return (
    <form action={formAction} className="space-y-4">
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" name="name" required className="input" />
        {state.errors?.name && (
          <p className="text-red-500 text-sm">{state.errors.name[0]}</p>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" required className="input" />
        {state.errors?.email && (
          <p className="text-red-500 text-sm">{state.errors.email[0]}</p>
        )}
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea id="message" name="message" required className="input" />
        {state.errors?.message && (
          <p className="text-red-500 text-sm">{state.errors.message[0]}</p>
        )}
      </div>

      <button type="submit" disabled={pending} className="btn-primary">
        {pending ? "Sending..." : "Send Message"}
      </button>
    </form>
  );
}
```

### Pattern I: Optimistic Updates with useOptimistic

Show the result immediately while the server processes the mutation.

```tsx
// components/LikeButton.tsx — CLIENT COMPONENT
"use client";

import { useOptimistic, useTransition } from "react";
import { toggleLike } from "@/app/actions/likes";

interface Props {
  postId: string;
  initialLiked: boolean;
  initialCount: number;
}

export function LikeButton({ postId, initialLiked, initialCount }: Props) {
  const [isPending, startTransition] = useTransition();

  const [optimistic, setOptimistic] = useOptimistic(
    { liked: initialLiked, count: initialCount },
    (current, newLiked: boolean) => ({
      liked: newLiked,
      count: current.count + (newLiked ? 1 : -1),
    })
  );

  function handleClick() {
    startTransition(async () => {
      const newLiked = !optimistic.liked;
      setOptimistic(newLiked);
      await toggleLike(postId);
    });
  }

  return (
    <button onClick={handleClick} disabled={isPending} className="flex items-center gap-1">
      <span>{optimistic.liked ? "❤️" : "🤍"}</span>
      <span>{optimistic.count}</span>
    </button>
  );
}
```

```tsx
// app/actions/likes.ts
"use server";

import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";
import { auth } from "@/lib/auth";

export async function toggleLike(postId: string) {
  const session = await auth();
  if (!session?.user?.id) throw new Error("Unauthorized");

  const existing = await db.like.findUnique({
    where: { userId_postId: { userId: session.user.id, postId } },
  });

  if (existing) {
    await db.like.delete({ where: { id: existing.id } });
  } else {
    await db.like.create({ data: { userId: session.user.id, postId } });
  }

  revalidatePath("/feed");
}
```

### Pattern J: Server Action with Revalidation Tags

Use `fetch` with `next.revalidate` tags for fine-grained cache invalidation.

```tsx
// lib/data.ts — runs on server only
import { unstable_cache } from "next/cache";
import { db } from "@/lib/db";

export const getProducts = unstable_cache(
  async (categoryId?: string) => {
    return db.product.findMany({
      where: categoryId ? { categoryId } : undefined,
      orderBy: { createdAt: "desc" },
    });
  },
  ["products"],
  { tags: ["products"], revalidate: 3600 }
);

export const getProduct = unstable_cache(
  async (id: string) => {
    return db.product.findUnique({ where: { id } });
  },
  ["product"],
  { tags: ["products"], revalidate: 3600 }
);
```

```tsx
// app/actions/products.ts
"use server";

import { revalidateTag } from "next/cache";
import { db } from "@/lib/db";

export async function updateProduct(id: string, formData: FormData) {
  await db.product.update({
    where: { id },
    data: {
      name: formData.get("name") as string,
      price: parseFloat(formData.get("price") as string),
    },
  });

  // Invalidate all cached queries tagged with "products"
  revalidateTag("products");
}
```

---

## 4. Error Handling

### Pattern K: error.tsx Boundary

`error.tsx` files must be Client Components (they need `useState` for retry logic).

```tsx
// app/products/error.tsx — CLIENT COMPONENT (required)
"use client";

import { useEffect } from "react";

export default function ProductsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Products error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center gap-4 p-8">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="text-gray-600">Failed to load products.</p>
      <button onClick={reset} className="btn-primary">
        Try Again
      </button>
    </div>
  );
}
```

---

## 5. Anti-Patterns to Avoid

### Anti-Pattern: "use client" on a Page

```tsx
// BAD — makes entire page tree client-rendered
"use client";

import { useEffect, useState } from "react";

export default function ProductsPage() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch("/api/products").then(r => r.json()).then(setProducts);
  }, []);

  return <div>{/* ... */}</div>;
}

// GOOD — Server Component page, Client Components only where needed
// (see Pattern A and Pattern B above)
```

### Anti-Pattern: Passing Functions Across the Boundary

```tsx
// BAD — functions are not serializable across server/client boundary
// app/page.tsx (Server Component)
import { ClientList } from "./ClientList";

export default async function Page() {
  const items = await getItems();
  return (
    <ClientList
      items={items}
      onDelete={(id) => deleteItem(id)} // ERROR: not serializable
    />
  );
}

// GOOD — use Server Actions instead
// app/page.tsx (Server Component)
import { ClientList } from "./ClientList";

export default async function Page() {
  const items = await getItems();
  return <ClientList items={items} />;
}

// components/ClientList.tsx
"use client";
import { deleteItem } from "@/app/actions/items"; // Server Action

export function ClientList({ items }) {
  return items.map((item) => (
    <div key={item.id}>
      {item.name}
      <button onClick={() => deleteItem(item.id)}>Delete</button>
    </div>
  ));
}
```

### Anti-Pattern: Wrapping Root Layout in Providers

```tsx
// BAD — makes everything client
"use client";
export default function RootLayout({ children }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <CartProvider>
          {children}
        </CartProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

// GOOD — push providers to a dedicated Client Component, keep layout as Server
// app/layout.tsx (Server Component)
import { Providers } from "./providers";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

// app/providers.tsx (Client Component — small boundary)
"use client";
import { ThemeProvider } from "@/components/ThemeProvider";

export function Providers({ children }: { children: React.ReactNode }) {
  return <ThemeProvider>{children}</ThemeProvider>;
}
```
