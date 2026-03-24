# Webhook Patterns Reference

> Extracted from prompts.chat `src/lib/webhook.ts`.

## SSRF Protection

```typescript
import { URL } from "url";
import dns from "dns/promises";
import net from "net";

const PRIVATE_RANGES = [
  /^10\./,                    // 10.0.0.0/8
  /^172\.(1[6-9]|2\d|3[01])\./, // 172.16.0.0/12
  /^192\.168\./,              // 192.168.0.0/16
  /^127\./,                   // 127.0.0.0/8
  /^0\./,                     // 0.0.0.0/8
  /^169\.254\./,              // Link-local
];

export function isPrivateUrl(urlString: string): boolean {
  try {
    const url = new URL(urlString);

    // Block localhost
    if (url.hostname === "localhost" || url.hostname === "::1") return true;

    // Block private IPs
    if (net.isIP(url.hostname)) {
      return PRIVATE_RANGES.some((r) => r.test(url.hostname));
    }

    return false;
  } catch {
    return true; // malformed URLs are blocked
  }
}

// Also resolve DNS to catch DNS rebinding
export async function isPrivateUrlStrict(urlString: string): Promise<boolean> {
  if (isPrivateUrl(urlString)) return true;
  try {
    const url = new URL(urlString);
    const addresses = await dns.resolve4(url.hostname);
    return addresses.some((ip) => PRIVATE_RANGES.some((r) => r.test(ip)));
  } catch {
    return true;
  }
}
```

## Webhook Dispatcher

```typescript
import crypto from "crypto";

export async function triggerWebhooks(
  event: WebhookEvent,
  data: Record<string, any>
) {
  const configs = await prisma.webhookConfig.findMany({
    where: { active: true, events: { has: event } },
  });

  if (configs.length === 0) return;

  const results = await Promise.allSettled(
    configs.map((config) => sendWebhook(config, event, data))
  );

  // Log results
  for (let i = 0; i < results.length; i++) {
    const result = results[i];
    const config = configs[i];
    if (result.status === "rejected") {
      console.error(`Webhook ${config.id} failed:`, result.reason);
    }
  }
}

async function sendWebhook(
  config: WebhookConfig,
  event: WebhookEvent,
  data: Record<string, any>
) {
  if (await isPrivateUrlStrict(config.url)) {
    throw new Error(`SSRF blocked: ${config.url}`);
  }

  const body = config.payloadTemplate
    ? replacePlaceholders(config.payloadTemplate, data)
    : JSON.stringify({ event, data, timestamp: new Date().toISOString() });

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Webhook-Event": event,
    ...JSON.parse(config.headers || "{}"),
  };

  // HMAC signature
  if (config.secret) {
    const signature = crypto
      .createHmac("sha256", config.secret)
      .update(body)
      .digest("hex");
    headers["X-Webhook-Signature"] = `sha256=${signature}`;
  }

  const response = await fetch(config.url, {
    method: "POST",
    headers,
    body,
    signal: AbortSignal.timeout(10_000), // 10s timeout
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }
}
```

## Template Payload System

```typescript
const WEBHOOK_PLACEHOLDERS: Record<string, (data: any) => string> = {
  "{{TITLE}}":       (d) => d.title || "",
  "{{CONTENT}}":     (d) => d.content?.substring(0, 500) || "",
  "{{AUTHOR}}":      (d) => d.author?.name || "Unknown",
  "{{URL}}":         (d) => `https://example.com/items/${d.id}`,
  "{{CREATED_AT}}":  (d) => new Date(d.createdAt).toISOString(),
  "{{EVENT}}":       (d) => d._event || "",
};

export function replacePlaceholders(template: string, data: any): string {
  let result = template;
  for (const [placeholder, resolver] of Object.entries(WEBHOOK_PLACEHOLDERS)) {
    result = result.replaceAll(placeholder, resolver(data));
  }
  return result;
}
```

## Slack Block Kit Preset

```json
{
  "blocks": [
    {
      "type": "header",
      "text": { "type": "plain_text", "text": "{{EVENT}}: {{TITLE}}" }
    },
    {
      "type": "section",
      "text": { "type": "mrkdwn", "text": "{{CONTENT}}" },
      "accessory": {
        "type": "button",
        "text": { "type": "plain_text", "text": "View" },
        "url": "{{URL}}"
      }
    },
    {
      "type": "context",
      "elements": [
        { "type": "mrkdwn", "text": "By *{{AUTHOR}}* at {{CREATED_AT}}" }
      ]
    }
  ]
}
```

## Prisma Model

```prisma
model WebhookConfig {
  id              String   @id @default(cuid())
  url             String
  events          WebhookEvent[]
  headers         String?  // JSON string of custom headers
  payloadTemplate String?  // Template with {{PLACEHOLDERS}}
  active          Boolean  @default(true)
  secret          String?  // For HMAC signing
  userId          String
  user            User     @relation(fields: [userId], references: [id])
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}

enum WebhookEvent {
  PROMPT_CREATED
  PROMPT_UPDATED
  PROMPT_DELETED
}
```
