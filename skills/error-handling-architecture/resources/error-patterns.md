# Error Handling Patterns

> Source: prompts.chat dissection — error handling across API routes and React components

## Error Code Enum

```typescript
// src/lib/errors/codes.ts
export enum ErrorCode {
  VALIDATION_ERROR = "VALIDATION_ERROR",
  UNAUTHORIZED = "UNAUTHORIZED",
  FORBIDDEN = "FORBIDDEN",
  NOT_FOUND = "NOT_FOUND",
  CONFLICT = "CONFLICT",
  RATE_LIMITED = "RATE_LIMITED",
  PAYMENT_FAILED = "PAYMENT_FAILED",
  SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE",
  INTERNAL = "INTERNAL",
}

export const STATUS_MAP: Record<ErrorCode, number> = {
  [ErrorCode.VALIDATION_ERROR]: 400,
  [ErrorCode.UNAUTHORIZED]: 401,
  [ErrorCode.FORBIDDEN]: 403,
  [ErrorCode.NOT_FOUND]: 404,
  [ErrorCode.CONFLICT]: 409,
  [ErrorCode.RATE_LIMITED]: 429,
  [ErrorCode.PAYMENT_FAILED]: 402,
  [ErrorCode.SERVICE_UNAVAILABLE]: 503,
  [ErrorCode.INTERNAL]: 500,
};
```

## AppError Base Class

```typescript
// src/lib/errors/app-error.ts
import { ErrorCode, STATUS_MAP } from "./codes";

export class AppError extends Error {
  readonly code: ErrorCode;
  readonly statusCode: number;
  readonly details?: unknown;
  readonly isOperational: boolean;

  constructor(
    code: ErrorCode,
    message: string,
    options?: { details?: unknown; isOperational?: boolean }
  ) {
    super(message);
    this.code = code;
    this.statusCode = STATUS_MAP[code];
    this.details = options?.details;
    this.isOperational = options?.isOperational ?? true;
    this.name = "AppError";
  }

  // Factory methods
  static unauthorized(message = "Authentication required") {
    return new AppError(ErrorCode.UNAUTHORIZED, message);
  }

  static validation(details: Array<{ field: string; message: string }>) {
    return new AppError(ErrorCode.VALIDATION_ERROR, "Invalid request", { details });
  }

  static notFound(resource: string) {
    return new AppError(ErrorCode.NOT_FOUND, `${resource} not found`);
  }

  static forbidden(message = "Insufficient permissions") {
    return new AppError(ErrorCode.FORBIDDEN, message);
  }

  static conflict(message: string) {
    return new AppError(ErrorCode.CONFLICT, message);
  }

  static rateLimited(retryAfter: number) {
    return new AppError(ErrorCode.RATE_LIMITED, "Too many requests", {
      details: { retryAfter },
    });
  }

  static internal(message = "Internal server error") {
    return new AppError(ErrorCode.INTERNAL, message, { isOperational: false });
  }

  toJSON() {
    return {
      error: {
        code: this.code,
        message: this.message,
        ...(this.details ? { details: this.details } : {}),
      },
    };
  }

  toResponse() {
    return Response.json(this.toJSON(), {
      status: this.statusCode,
      ...(this.code === ErrorCode.RATE_LIMITED
        ? { headers: { "Retry-After": String((this.details as any)?.retryAfter ?? 60) } }
        : {}),
    });
  }
}
```

## Prisma Error Mapper

```typescript
// src/lib/errors/mappers.ts
import { Prisma } from "@prisma/client";
import { AppError } from "./app-error";

export function mapPrismaError(error: unknown): AppError {
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    switch (error.code) {
      case "P2002": // Unique constraint violation
        return AppError.conflict("Resource already exists");
      case "P2025": // Record not found
        return AppError.notFound("Resource");
      case "P2003": // Foreign key constraint failed
        return AppError.validation([{ field: "relation", message: "Related resource not found" }]);
      default:
        return AppError.internal(`Database error: ${error.code}`);
    }
  }

  if (error instanceof Prisma.PrismaClientValidationError) {
    return AppError.validation([{ field: "query", message: "Invalid query parameters" }]);
  }

  return AppError.internal("Unexpected database error");
}
```

## Global Error Handler Middleware

```typescript
// src/lib/errors/middleware.ts
import { AppError } from "./app-error";
import { mapPrismaError } from "./mappers";
import { logger } from "@/lib/logger";

export function withErrorHandler(
  handler: (req: Request) => Promise<Response>
) {
  return async (req: Request): Promise<Response> => {
    try {
      return await handler(req);
    } catch (error) {
      if (error instanceof AppError) {
        if (!error.isOperational) {
          logger.error("Programming error", { error, stack: error.stack });
        }
        return error.toResponse();
      }

      // Map known external errors
      const mapped = mapPrismaError(error);
      if (mapped.code !== "INTERNAL") return mapped.toResponse();

      // Unknown error — log and return generic 500
      logger.error("Unhandled error", {
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      });

      return AppError.internal().toResponse();
    }
  };
}
```

## React Error Boundaries

```tsx
// app/error.tsx — Global error boundary
"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <h2>Something went wrong</h2>
        <p>Error reference: {error.digest}</p>
        <button onClick={reset}>Try again</button>
      </body>
    </html>
  );
}
```

```tsx
// app/[route]/error.tsx — Route-level error boundary
"use client";

export default function RouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="error-container">
      <h2>Failed to load this page</h2>
      <p>Reference: {error.digest}</p>
      <button onClick={reset}>Retry</button>
    </div>
  );
}
```

## Graceful Degradation Pattern

```typescript
// Optional feature with graceful fallback
async function getAIEmbedding(text: string): Promise<number[] | null> {
  if (!process.env.OPENAI_API_KEY) {
    logger.warn("AI embeddings disabled — OPENAI_API_KEY not set");
    return null;
  }

  try {
    const response = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: text,
    });
    return response.data[0].embedding;
  } catch (error) {
    logger.warn("AI embedding failed, continuing without", { error });
    return null; // Graceful degradation — feature is optional
  }
}
```
