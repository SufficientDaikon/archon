# Vitest Reference

Practical code examples for Vitest configuration, mock patterns, route handler testing, and React hook testing.

---

## 1. Vitest Configuration

### vitest.config.ts

```ts
import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    include: ["**/*.{test,spec}.{ts,tsx}"],
    exclude: ["node_modules", "dist", ".next", "build"],
    pool: "forks",
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json-summary"],
      reportsDirectory: "./coverage",
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/**/*.d.ts",
        "src/**/*.test.{ts,tsx}",
        "src/**/index.ts",
        "src/types/**",
      ],
      thresholds: {
        statements: 80,
        branches: 70,
        functions: 75,
        lines: 80,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@/lib": path.resolve(__dirname, "./src/lib"),
      "@/components": path.resolve(__dirname, "./src/components"),
    },
  },
});
```

### vitest.setup.ts

```ts
import { vi, beforeEach } from "vitest";

// Clear all mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
});

// Global mocks that apply to all test files
vi.mock("next/navigation", () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  })),
  useSearchParams: vi.fn(() => new URLSearchParams()),
  usePathname: vi.fn(() => "/"),
}));
```

### package.json scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest --watch",
    "test:coverage": "vitest run --coverage",
    "test:ci": "vitest run --coverage --reporter=junit --outputFile=test-results.xml"
  }
}
```

---

## 2. Mock Patterns

### Module-Level Mocking (Prisma)

```ts
// tests/__mocks__/prisma.ts
import { vi } from "vitest";

export const prisma = {
  user: {
    findMany: vi.fn(),
    findUnique: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  post: {
    findMany: vi.fn(),
    findUnique: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  $transaction: vi.fn((callback: any) => callback(prisma)),
};

// Usage in test files:
vi.mock("@/lib/prisma", () => ({
  prisma,
}));
```

### Auth Mocking (NextAuth)

```ts
// tests/__mocks__/next-auth.ts
import { vi } from "vitest";

export const mockSession = {
  user: {
    id: "user-1",
    name: "Test User",
    email: "test@example.com",
    role: "admin",
  },
  expires: "2099-01-01T00:00:00.000Z",
};

export const getServerSession = vi.fn(() => Promise.resolve(mockSession));

// Usage in test files:
vi.mock("next-auth", () => ({
  getServerSession,
}));
```

### External Service Mocking (S3)

```ts
import { vi } from "vitest";

vi.mock("@aws-sdk/client-s3", () => ({
  S3Client: vi.fn(() => ({
    send: vi.fn(),
  })),
  PutObjectCommand: vi.fn(),
  GetObjectCommand: vi.fn(),
  DeleteObjectCommand: vi.fn(),
}));
```

### Typed Mock Helpers

```ts
import { vi, type Mock } from "vitest";
import { prisma } from "@/lib/prisma";

// Type-safe mock setup
function mockPrismaReturn<T>(
  method: Mock,
  data: T
): void {
  method.mockResolvedValueOnce(data);
}

// Usage:
mockPrismaReturn(vi.mocked(prisma.user.findUnique), {
  id: "user-1",
  name: "Alice",
  email: "alice@example.com",
});
```

### Spy on Specific Methods

```ts
import { vi, describe, it, expect } from "vitest";

describe("Logger", () => {
  it("calls console.error on failure", () => {
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    doSomethingThatFails();

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining("failed")
    );

    consoleSpy.mockRestore();
  });
});
```

---

## 3. Route Handler Testing (Next.js App Router)

### GET Route Handler

```ts
// src/app/api/users/route.ts
import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth";

export async function GET() {
  const session = await getServerSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const users = await prisma.user.findMany({
    select: { id: true, name: true, email: true },
  });

  return NextResponse.json(users);
}
```

```ts
// tests/unit/api/users.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { GET } from "@/app/api/users/route";

// Module-level mocks
vi.mock("@/lib/prisma", () => ({
  prisma: {
    user: {
      findMany: vi.fn(),
    },
  },
}));

vi.mock("next-auth", () => ({
  getServerSession: vi.fn(),
}));

import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("GET /api/users", () => {
  it("returns 401 when not authenticated", async () => {
    vi.mocked(getServerSession).mockResolvedValueOnce(null);

    const response = await GET();
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.error).toBe("Unauthorized");
  });

  it("returns users when authenticated", async () => {
    const mockUsers = [
      { id: "1", name: "Alice", email: "alice@test.com" },
      { id: "2", name: "Bob", email: "bob@test.com" },
    ];

    vi.mocked(getServerSession).mockResolvedValueOnce({
      user: { id: "1", name: "Alice", email: "alice@test.com" },
    });
    vi.mocked(prisma.user.findMany).mockResolvedValueOnce(mockUsers);

    const response = await GET();
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data).toEqual(mockUsers);
    expect(prisma.user.findMany).toHaveBeenCalledWith({
      select: { id: true, name: true, email: true },
    });
  });
});
```

### POST Route Handler with Request Body

```ts
// tests/unit/api/users-create.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { POST } from "@/app/api/users/route";

vi.mock("@/lib/prisma", () => ({
  prisma: {
    user: { create: vi.fn() },
  },
}));

vi.mock("next-auth", () => ({
  getServerSession: vi.fn(),
}));

import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth";

beforeEach(() => {
  vi.clearAllMocks();
});

function createRequest(body: object): Request {
  return new Request("http://localhost/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

describe("POST /api/users", () => {
  it("creates a user with valid data", async () => {
    const input = { name: "Charlie", email: "charlie@test.com" };
    const created = { id: "3", ...input };

    vi.mocked(getServerSession).mockResolvedValueOnce({ user: { id: "1" } });
    vi.mocked(prisma.user.create).mockResolvedValueOnce(created);

    const response = await POST(createRequest(input));
    const data = await response.json();

    expect(response.status).toBe(201);
    expect(data).toEqual(created);
  });

  it("returns 400 for missing required fields", async () => {
    vi.mocked(getServerSession).mockResolvedValueOnce({ user: { id: "1" } });

    const response = await POST(createRequest({ name: "" }));
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toBeDefined();
  });
});
```

---

## 4. Business Logic Testing

### Pure Function Testing

```ts
// src/lib/utils.ts
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function calculateDiscount(
  price: number,
  discountPercent: number
): number {
  if (price < 0 || discountPercent < 0 || discountPercent > 100) {
    throw new Error("Invalid input");
  }
  return Math.round(price * (1 - discountPercent / 100) * 100) / 100;
}
```

```ts
// tests/unit/lib/utils.test.ts
import { describe, it, expect } from "vitest";
import { slugify, calculateDiscount } from "@/lib/utils";

describe("slugify", () => {
  it.each([
    ["Hello World", "hello-world"],
    ["  Spaces  Around  ", "spaces-around"],
    ["Special! @Characters#", "special-characters"],
    ["already-slugged", "already-slugged"],
    ["UPPER CASE", "upper-case"],
    ["multiple   spaces", "multiple-spaces"],
  ])("converts %s to %s", (input, expected) => {
    expect(slugify(input)).toBe(expected);
  });

  it("handles empty string", () => {
    expect(slugify("")).toBe("");
  });
});

describe("calculateDiscount", () => {
  it("calculates correct discount", () => {
    expect(calculateDiscount(100, 20)).toBe(80);
    expect(calculateDiscount(49.99, 10)).toBe(44.99);
  });

  it("returns full price for 0% discount", () => {
    expect(calculateDiscount(100, 0)).toBe(100);
  });

  it("returns 0 for 100% discount", () => {
    expect(calculateDiscount(100, 100)).toBe(0);
  });

  it("throws for negative price", () => {
    expect(() => calculateDiscount(-10, 20)).toThrow("Invalid input");
  });

  it("throws for discount over 100", () => {
    expect(() => calculateDiscount(100, 150)).toThrow("Invalid input");
  });
});
```

### Validator Testing

```ts
// tests/unit/lib/validators.test.ts
import { describe, it, expect } from "vitest";
import { validateEmail, validatePassword } from "@/lib/validators";

describe("validateEmail", () => {
  it.each([
    "user@example.com",
    "name+tag@domain.org",
    "first.last@sub.domain.com",
  ])("accepts valid email: %s", (email) => {
    expect(validateEmail(email)).toEqual({ valid: true });
  });

  it.each([
    ["", "Email is required"],
    ["not-an-email", "Invalid email format"],
    ["@no-local.com", "Invalid email format"],
    ["no-domain@", "Invalid email format"],
  ])("rejects invalid email %s with message: %s", (email, message) => {
    const result = validateEmail(email);
    expect(result.valid).toBe(false);
    expect(result.error).toBe(message);
  });
});
```

---

## 5. React Hook Testing

### Custom Hook with State

```ts
// src/hooks/useCounter.ts
import { useState, useCallback } from "react";

export function useCounter(initial = 0) {
  const [count, setCount] = useState(initial);

  const increment = useCallback(() => setCount((c) => c + 1), []);
  const decrement = useCallback(() => setCount((c) => c - 1), []);
  const reset = useCallback(() => setCount(initial), [initial]);

  return { count, increment, decrement, reset };
}
```

```ts
// tests/unit/hooks/useCounter.test.ts
import { describe, it, expect } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useCounter } from "@/hooks/useCounter";

describe("useCounter", () => {
  it("starts at 0 by default", () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  it("starts at custom initial value", () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });

  it("increments", () => {
    const { result } = renderHook(() => useCounter());
    act(() => result.current.increment());
    expect(result.current.count).toBe(1);
  });

  it("decrements", () => {
    const { result } = renderHook(() => useCounter(5));
    act(() => result.current.decrement());
    expect(result.current.count).toBe(4);
  });

  it("resets to initial value", () => {
    const { result } = renderHook(() => useCounter(3));
    act(() => {
      result.current.increment();
      result.current.increment();
    });
    expect(result.current.count).toBe(5);
    act(() => result.current.reset());
    expect(result.current.count).toBe(3);
  });
});
```

### Async Hook with API Call

```ts
// src/hooks/useUser.ts
import { useState, useEffect } from "react";

interface User {
  id: string;
  name: string;
  email: string;
}

export function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchUser() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/users/${userId}`);
        if (!res.ok) throw new Error("Failed to fetch user");
        const data = await res.json();
        if (!cancelled) setUser(data);
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchUser();
    return () => { cancelled = true; };
  }, [userId]);

  return { user, loading, error };
}
```

```ts
// tests/unit/hooks/useUser.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useUser } from "@/hooks/useUser";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useUser", () => {
  it("fetches and returns user data", async () => {
    const mockUser = { id: "1", name: "Alice", email: "alice@test.com" };

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });

    const { result } = renderHook(() => useUser("1"));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.error).toBeNull();
  });

  it("handles fetch error", async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    const { result } = renderHook(() => useUser("999"));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toBeNull();
    expect(result.current.error).toBe("Failed to fetch user");
  });

  it("handles network failure", async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useUser("1"));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe("Network error");
  });
});
```

### Hook with Context Provider Wrapper

```ts
// tests/unit/hooks/useAuth.test.ts
import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAuth } from "@/hooks/useAuth";
import { AuthProvider } from "@/contexts/AuthContext";
import type { ReactNode } from "react";

function createWrapper(user: any = null) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <AuthProvider value={{ user, isLoggedIn: !!user }}>{children}</AuthProvider>;
  };
}

describe("useAuth", () => {
  it("returns user from context when logged in", () => {
    const mockUser = { id: "1", name: "Alice" };

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(mockUser),
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isLoggedIn).toBe(true);
  });

  it("returns null user when not logged in", () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(null),
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isLoggedIn).toBe(false);
  });
});
```

---

## 6. Common Assertion Patterns

```ts
// Object shape matching
expect(result).toMatchObject({
  id: expect.any(String),
  createdAt: expect.any(Date),
  name: "Alice",
});

// Array containing specific items
expect(items).toEqual(
  expect.arrayContaining([
    expect.objectContaining({ name: "Alice" }),
  ])
);

// Error assertions
expect(() => riskyFunction()).toThrow("specific message");
expect(() => riskyFunction()).toThrowError(/pattern/);

// Async error assertions
await expect(asyncRiskyFunction()).rejects.toThrow("async error");

// Snapshot testing (use sparingly)
expect(result).toMatchInlineSnapshot(`
  {
    "id": "1",
    "name": "Alice",
  }
`);

// Mock call assertions
expect(mockFn).toHaveBeenCalledTimes(1);
expect(mockFn).toHaveBeenCalledWith("arg1", expect.objectContaining({ key: "value" }));
expect(mockFn).toHaveBeenNthCalledWith(1, "first-call-arg");
```

---

## 7. CI Configuration Example

### GitHub Actions

```yaml
name: Unit Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"
      - run: npm ci
      - run: npx vitest run --coverage --reporter=junit --outputFile=test-results.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: coverage/
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: test-results.xml
```
