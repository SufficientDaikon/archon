# Guard Chain Patterns

> Source: prompts.chat dissection — found in all 61 API route handlers

## Guard Chain Implementation

The guard chain pattern from prompts.chat follows a strict order:
**auth > validate > rate-limit > authorize > execute**

### Guard Type Definition

```typescript
// src/lib/guards/types.ts
export type GuardContext = {
  userId?: string;
  session?: Session;
  data?: unknown;
  [key: string]: unknown;
};

export type GuardResult =
  | { ok: true; context: GuardContext }
  | { ok: false; response: Response };

export type Guard = (
  req: Request,
  context: GuardContext
) => Promise<GuardResult>;
```

### Compose Helper

```typescript
// src/lib/guards/compose.ts
export function composeGuards(...guards: Guard[]) {
  return async (req: Request): Promise<GuardResult> => {
    let context: GuardContext = {};

    for (const guard of guards) {
      const result = await guard(req, context);
      if (!result.ok) return result; // Short-circuit
      context = { ...context, ...result.context };
    }

    return { ok: true, context };
  };
}
```

### Auth Guard

```typescript
// src/lib/guards/auth.ts
import { getServerSession } from "next-auth";
import { authConfig } from "@/lib/auth";

export function authGuard(): Guard {
  return async (req, context) => {
    const session = await getServerSession(authConfig);

    if (!session?.user?.id) {
      return {
        ok: false,
        response: Response.json(
          { error: { code: "UNAUTHORIZED", message: "Authentication required" } },
          { status: 401 }
        ),
      };
    }

    return {
      ok: true,
      context: { ...context, userId: session.user.id, session },
    };
  };
}
```

### Validation Guard (Zod)

```typescript
// src/lib/guards/validate.ts
import { z, ZodSchema } from "zod";

export function validateGuard<T>(schema: ZodSchema<T>): Guard {
  return async (req, context) => {
    const body = await req.json().catch(() => ({}));
    const result = schema.safeParse(body);

    if (!result.success) {
      return {
        ok: false,
        response: Response.json(
          {
            error: {
              code: "VALIDATION_ERROR",
              message: "Invalid request",
              details: result.error.issues.map((i) => ({
                field: i.path.join("."),
                message: i.message,
              })),
            },
          },
          { status: 400 }
        ),
      };
    }

    return { ok: true, context: { ...context, data: result.data } };
  };
}
```

### Rate Limit Guard

```typescript
// src/lib/guards/rate-limit.ts
type RateLimitConfig = {
  action: string;
  cooldownSeconds?: number;
  dailyLimit?: number;
};

export function rateLimitGuard(config: RateLimitConfig): Guard {
  return async (req, context) => {
    const { userId } = context;
    const key = `ratelimit:${config.action}:${userId}`;

    // Check cooldown
    if (config.cooldownSeconds) {
      const lastAction = await redis.get(key);
      if (lastAction) {
        const elapsed = Date.now() - parseInt(lastAction);
        const remaining = config.cooldownSeconds * 1000 - elapsed;
        if (remaining > 0) {
          return {
            ok: false,
            response: Response.json(
              {
                error: {
                  code: "RATE_LIMITED",
                  message: "Too many requests",
                  retryAfter: Math.ceil(remaining / 1000),
                },
              },
              {
                status: 429,
                headers: { "Retry-After": String(Math.ceil(remaining / 1000)) },
              }
            ),
          };
        }
      }
    }

    // Record this action
    await redis.set(key, String(Date.now()), "EX", config.cooldownSeconds || 60);
    return { ok: true, context };
  };
}
```

### Route Handler Usage

```typescript
// src/app/api/prompts/route.ts
import { composeGuards, authGuard, validateGuard, rateLimitGuard } from "@/lib/guards";
import { CreatePromptSchema } from "@/lib/schemas/prompt";

const createGuard = composeGuards(
  authGuard(),
  validateGuard(CreatePromptSchema),
  rateLimitGuard({ action: "create-prompt", cooldownSeconds: 30 })
);

export async function POST(req: Request) {
  const result = await createGuard(req);
  if (!result.ok) return result.response;

  const { userId, data } = result.context;
  // Business logic here — fully validated and authorized
  const prompt = await prisma.prompt.create({
    data: { ...data, authorId: userId },
  });

  return Response.json({ data: prompt }, { status: 201 });
}
```
