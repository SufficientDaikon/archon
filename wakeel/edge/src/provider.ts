export interface ProviderCfg {
  name: string;
  baseUrl: string;
  model: string;
  apiKey: string;
}

export class ProviderError extends Error {
  constructor(
    public readonly provider: string,
    reason: string,
  ) {
    super(`Provider '${provider}' failed: ${reason}`);
    this.name = "ProviderError";
  }
}

export async function complete(
  cfg: ProviderCfg,
  messages: { role: string; content: string }[],
): Promise<string> {
  const url = `${cfg.baseUrl}/chat/completions`;
  const body = JSON.stringify({ model: cfg.model, messages });
  const headers = {
    Authorization: `Bearer ${cfg.apiKey}`,
    "Content-Type": "application/json",
  };

  let lastErr: Error | null = null;
  for (let attempt = 0; attempt < 2; attempt++) {
    if (attempt > 0) await sleep(1500);
    try {
      const resp = await fetch(url, { method: "POST", body, headers });
      if (!resp.ok) {
        lastErr = new Error(`HTTP ${resp.status}`);
        console.warn(`Provider ${cfg.name} HTTP ${resp.status} (attempt ${attempt + 1}/2)`);
        continue;
      }
      const data = (await resp.json()) as {
        choices: { message: { content: string } }[];
      };
      return data.choices[0].message.content;
    } catch (e) {
      lastErr = e as Error;
      console.warn(`Provider ${cfg.name} error (attempt ${attempt + 1}/2):`, e);
    }
  }
  throw new ProviderError(cfg.name, lastErr?.message ?? "unknown");
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}
