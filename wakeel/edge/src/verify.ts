import { complete } from "./provider";
import type { ProviderCfg } from "./provider";

const VERIFY_SYSTEM = `You are a disciplined verifier enforcing Iron Law #7: VERIFY, DON'T TRUST.

Review the draft response below. Check:
1. Is it factually accurate (no hallucinated claims)?
2. Is it honest about uncertainty?
3. Is it responsive to the user's question?

If the draft is acceptable, output it verbatim.
If you find a specific factual error, produce a corrected version.
Do NOT add new content, expand scope, or change the style.
Return the final response text only — no preamble, no explanation.`;

export async function verify(draft: string, question: string, cfg: ProviderCfg): Promise<string> {
  const messages = [
    { role: "system", content: VERIFY_SYSTEM },
    { role: "user", content: `User question: ${question}\n\nDraft response:\n${draft}` },
  ];
  try {
    return await complete(cfg, messages);
  } catch (e) {
    console.warn("Verify degraded to draft:", e);
    return draft;
  }
}
