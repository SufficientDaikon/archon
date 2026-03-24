# Prisma ORM Reference Patterns

> Source: prompts.chat dissection — prisma/schema.prisma analysis

## globalThis Singleton

```typescript
// src/lib/db.ts
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development" ? ["query"] : [],
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;
```

**Why**: In serverless environments (Vercel, AWS Lambda), each hot reload creates a new PrismaClient. Without the singleton, you exhaust database connections.

## Cursor Pagination with perPage+1 Trick

```typescript
async function getPaginatedPrompts(cursor?: string, perPage = 20) {
  const items = await prisma.prompt.findMany({
    where: { deletedAt: null },
    take: perPage + 1, // Fetch one extra
    ...(cursor && {
      cursor: { id: cursor },
      skip: 1, // Skip the cursor itself
    }),
    orderBy: { createdAt: "desc" },
    select: {
      id: true,
      title: true,
      content: true,
      createdAt: true,
      author: { select: { name: true, image: true } },
    },
  });

  const hasNextPage = items.length > perPage;
  const data = hasNextPage ? items.slice(0, perPage) : items;

  return {
    data,
    meta: {
      hasNextPage,
      nextCursor: hasNextPage ? data[data.length - 1].id : null,
    },
  };
}
```

**Why**: Avoids a separate COUNT(*) query. Fetching perPage+1 tells you if there's a next page by checking if you got the extra row.

## Soft Deletion Pattern

```prisma
model Prompt {
  id        String    @id @default(cuid())
  title     String
  content   String    @db.Text
  deletedAt DateTime?

  @@index([deletedAt])
  @@index([authorId, deletedAt])
}
```

```typescript
// Always filter deleted records
const prompts = await prisma.prompt.findMany({
  where: { deletedAt: null },
});

// Soft delete
await prisma.prompt.update({
  where: { id },
  data: { deletedAt: new Date() },
});

// Admin hard delete (rare)
await prisma.prompt.delete({ where: { id } });
```

## Strategic Indexing (20+ indexes)

```prisma
model Prompt {
  id          String    @id @default(cuid())
  title       String
  content     String    @db.Text
  slug        String    @unique
  category    String
  locale      String    @default("en")
  authorId    String
  deletedAt   DateTime?
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt

  author      User      @relation(fields: [authorId], references: [id])

  // Single-column indexes for common filters
  @@index([authorId])
  @@index([category])
  @@index([locale])
  @@index([createdAt])
  @@index([deletedAt])

  // Composite indexes for common query combinations
  @@index([category, createdAt])
  @@index([authorId, deletedAt])
  @@index([locale, category])
}

model Vote {
  id       String @id @default(cuid())
  promptId String
  userId   String
  value    Int    // +1 or -1

  // Business invariant: one vote per user per prompt
  @@unique([promptId, userId])
  @@index([promptId])
  @@index([userId])
}
```

## Version History Pattern

```prisma
model Prompt {
  id       String          @id @default(cuid())
  versions PromptVersion[]
}

model PromptVersion {
  id        String   @id @default(cuid())
  promptId  String
  content   String   @db.Text
  version   Int
  createdAt DateTime @default(now())
  prompt    Prompt   @relation(fields: [promptId], references: [id])

  @@unique([promptId, version])
  @@index([promptId, createdAt])
}
```

## Custom NextAuth Adapter

```typescript
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/db";

export const authAdapter = {
  ...PrismaAdapter(prisma),
  async createUser(data: AdapterUser) {
    // Custom: handle unclaimed accounts
    const existing = await prisma.user.findUnique({
      where: { email: data.email },
    });

    if (existing && !existing.claimed) {
      return prisma.user.update({
        where: { id: existing.id },
        data: { ...data, claimed: true },
      });
    }

    return prisma.user.create({ data });
  },
};
```

## Content Fingerprinting for Deduplication

```prisma
model Prompt {
  contentFingerprint String?
  @@index([contentFingerprint])
}
```

```typescript
import { createHash } from "crypto";

function fingerprint(content: string): string {
  const normalized = content
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
  return createHash("sha256").update(normalized).digest("hex").slice(0, 16);
}

// Check before inserting
const fp = fingerprint(newContent);
const exists = await prisma.prompt.findFirst({
  where: { contentFingerprint: fp, deletedAt: null },
});
if (exists) throw new DuplicateContentError(exists.id);
```
