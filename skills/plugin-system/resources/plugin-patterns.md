# Plugin System Patterns Reference

> Extracted from prompts.chat `src/lib/plugins/` architecture.

## 1. Interface Definitions (`types.ts`)

```typescript
import type { NextAuthConfig } from "next-auth";

// Each plugin category gets its own interface
export interface AuthPlugin {
  id: string;
  name: string;
  getProvider: () => NextAuthConfig["providers"][number];
}

export interface StoragePlugin {
  id: string;
  name: string;
  upload: (file: File | Buffer, options?: UploadOptions) => Promise<UploadResult>;
  delete?: (keyOrUrl: string) => Promise<void>;
  isConfigured: () => boolean;
}

export interface UploadResult {
  url: string;
  key?: string;
  size?: number;
  mimeType?: string;
}

export interface UploadOptions {
  filename?: string;
  mimeType?: string;
  folder?: string;
}

// Registry type maps category names to their plugin Maps
export interface PluginRegistry {
  auth: Map<string, AuthPlugin>;
  storage: Map<string, StoragePlugin>;
}
```

## 2. Registry Implementation (`registry.ts`)

```typescript
import type { AuthPlugin, StoragePlugin, PluginRegistry } from "./types";

// Singleton registry instance
const registry: PluginRegistry = {
  auth: new Map(),
  storage: new Map(),
};

// Auth plugin accessors
export function registerAuthPlugin(plugin: AuthPlugin) {
  registry.auth.set(plugin.id, plugin);
}

export function getAuthPlugin(id: string): AuthPlugin | undefined {
  return registry.auth.get(id);
}

export function getAllAuthPlugins(): AuthPlugin[] {
  return Array.from(registry.auth.values());
}

// Storage plugin accessors
export function registerStoragePlugin(plugin: StoragePlugin) {
  registry.storage.set(plugin.id, plugin);
}

export function getStoragePlugin(id: string): StoragePlugin | undefined {
  return registry.storage.get(id);
}

export function getConfiguredStoragePlugin(): StoragePlugin | undefined {
  return Array.from(registry.storage.values()).find((p) => p.isConfigured());
}
```

## 3. Initialization (`index.ts`)

```typescript
import { getConfig } from "@/lib/config";
import { registerAuthPlugin } from "./registry";

export async function initializePlugins() {
  const config = await getConfig();

  // Register auth plugins based on config
  const providers = config.auth?.providers || [];
  for (const providerId of providers) {
    switch (providerId) {
      case "github": {
        const { githubPlugin } = await import("./auth/github");
        registerAuthPlugin(githubPlugin);
        break;
      }
      case "google": {
        const { googlePlugin } = await import("./auth/google");
        registerAuthPlugin(googlePlugin);
        break;
      }
    }
  }
}

export * from "./types";
export * from "./registry";
```

## 4. Concrete Plugin Example (`auth/github.ts`)

```typescript
import type { AuthPlugin } from "../types";
import GitHub from "next-auth/providers/github";

export const githubPlugin: AuthPlugin = {
  id: "github",
  name: "GitHub",
  getProvider: () =>
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID!,
      clientSecret: process.env.AUTH_GITHUB_SECRET!,
    }),
};
```

## 5. Adding a New Plugin (Extension Guide)

1. Create `plugins/<category>/<name>.ts`
2. Export an object implementing the category interface
3. Add a `case` to `initializePlugins()` (or use a dynamic import map)
4. Add the plugin id to the config file
5. Done — the registry handles the rest

## 6. Generic Plugin Registry (Reusable Template)

```typescript
// For any new plugin category, follow this 3-file pattern:

// types.ts — Add interface
export interface NotificationPlugin {
  id: string;
  name: string;
  send: (to: string, message: string) => Promise<void>;
  isConfigured: () => boolean;
}

// registry.ts — Add Map + accessors
const notifications = new Map<string, NotificationPlugin>();
export const registerNotificationPlugin = (p: NotificationPlugin) => notifications.set(p.id, p);
export const getNotificationPlugin = (id: string) => notifications.get(id);

// index.ts — Add initialization case
case "slack": {
  const { slackPlugin } = await import("./notifications/slack");
  registerNotificationPlugin(slackPlugin);
  break;
}
```
