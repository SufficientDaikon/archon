# Config Patterns Reference

> Extracted from prompts.chat `prompts.config.ts` + `src/lib/config/index.ts`.

## 1. User-Facing Config File

```typescript
// app.config.ts (at project root)
import { defineConfig } from "@/lib/config";

export default defineConfig({
  branding: {
    name: "My Prompt Library",
    description: "A curated collection of AI prompts",
    logo: "/logo.svg",
    darkLogo: "/logo-dark.svg",
    favicon: "/favicon.ico",
  },
  theme: {
    primaryColor: "#6366f1",
    radius: 0.5,
    variant: "default",   // "flat" | "default" | "brutal"
    density: "comfortable", // "compact" | "comfortable" | "spacious"
  },
  auth: {
    providers: ["github", "google", "credentials"],
  },
  i18n: {
    defaultLocale: "en",
    locales: ["en", "es", "fr", "de", "ja", "zh"],
  },
  features: {
    privatePrompts: true,
    changeRequests: true,
    categories: true,
    tags: true,
    aiSearch: true,
    aiGeneration: false,
    comments: true,
  },
});
```

## 2. Config Type Definitions

```typescript
// types.ts
export interface BrandingConfig {
  name: string;
  description: string;
  logo?: string;
  darkLogo?: string;
  favicon?: string;
}

export interface ThemeConfig {
  primaryColor: string;
  radius: number;
  variant: "flat" | "default" | "brutal";
  density: "compact" | "comfortable" | "spacious";
}

export interface AuthConfig {
  providers: string[];
}

export interface I18nConfig {
  defaultLocale: string;
  locales: string[];
}

export interface FeaturesConfig {
  [key: string]: boolean;
}

export interface AppConfig {
  branding: BrandingConfig;
  theme: ThemeConfig;
  auth: AuthConfig;
  i18n: I18nConfig;
  features: FeaturesConfig;
}
```

## 3. Core Implementation

```typescript
// index.ts
import { AppConfig } from "./types";
import { defaults } from "./defaults";

// Identity function for TypeScript autocomplete
export function defineConfig(config: Partial<AppConfig>): AppConfig {
  return deepMerge(defaults, config) as AppConfig;
}

// Cached config singleton
let cachedConfig: AppConfig | null = null;

export async function getConfig(): Promise<AppConfig> {
  if (cachedConfig) return cachedConfig;

  let userConfig: Partial<AppConfig> = {};
  try {
    const mod = await import(/* webpackIgnore: true */ "../../app.config");
    userConfig = mod.default || mod;
  } catch {
    // No user config — use defaults
  }

  const config = deepMerge(defaults, userConfig) as AppConfig;
  cachedConfig = applyEnvOverrides(config);
  return cachedConfig;
}

export function getConfigSync(): AppConfig {
  if (!cachedConfig) throw new Error("Config not loaded. Call getConfig() first.");
  return cachedConfig;
}
```

## 4. Environment Override Layer

```typescript
// Env var prefix: APP_
export function applyEnvOverrides(config: AppConfig): AppConfig {
  const result = structuredClone(config);

  // Branding
  if (process.env.APP_BRANDING_NAME) result.branding.name = process.env.APP_BRANDING_NAME;
  if (process.env.APP_BRANDING_LOGO) result.branding.logo = process.env.APP_BRANDING_LOGO;

  // Auth
  if (process.env.APP_AUTH_PROVIDERS) {
    result.auth.providers = process.env.APP_AUTH_PROVIDERS.split(",").map(s => s.trim());
  }

  // Features (boolean coercion)
  for (const key of Object.keys(result.features)) {
    const envKey = `APP_FEATURE_${key.replace(/([A-Z])/g, "_$1").toUpperCase()}`;
    if (process.env[envKey] !== undefined) {
      result.features[key] = process.env[envKey] === "true";
    }
  }

  // Theme
  if (process.env.APP_THEME_PRIMARY_COLOR) result.theme.primaryColor = process.env.APP_THEME_PRIMARY_COLOR;

  return result;
}
```

## 5. Feature Flag Usage

```tsx
// In React components (UI gating)
const config = getConfigSync();
return (
  <div>
    {config.features.comments && <CommentSection promptId={id} />}
    {config.features.aiSearch && <AISearchBar />}
  </div>
);

// In API routes (endpoint gating)
export async function POST(req: Request) {
  const config = await getConfig();
  if (!config.features.aiGeneration) {
    return Response.json({ error: "AI generation is disabled" }, { status: 403 });
  }
  // ... handle request
}
```

## 6. Deep Merge Utility

```typescript
function deepMerge(target: any, source: any): any {
  const result = { ...target };
  for (const key of Object.keys(source)) {
    if (source[key] && typeof source[key] === "object" && !Array.isArray(source[key])) {
      result[key] = deepMerge(target[key] || {}, source[key]);
    } else if (source[key] !== undefined) {
      result[key] = source[key];
    }
  }
  return result;
}
```
