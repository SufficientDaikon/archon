import { complete } from "./provider";
import { verify } from "./verify";
import { selectSkill } from "./router";
import { getHistory, appendTurn } from "./sessions";
import { SYNAPSES } from "./synapses";
import type { Env } from "./index";

const FALLBACK_REPLY = "النظام مزحوم دلوقتي، جرّب تاني بعد شوية.";

const PERSONA = `You are Wakeel — a disciplined, friendly assistant running on the Archon Harness.

WhatsApp reply guidelines:
- Keep responses short and conversational (3-5 sentences max).
- Never use markdown tables or heavy formatting — plain text only.
- Use simple bullet points (• or -) sparingly when needed.
- Respond in the same language the user wrote in.
- Be warm, direct, and precise.`;

const PROVIDERS: Record<string, { baseUrl: string; model: string; role: string }> = {
  gemini: {
    baseUrl: "https://generativelanguage.googleapis.com/v1beta/openai",
    model: "gemini-2.5-flash",
    role: "draft",
  },
  groq: {
    baseUrl: "https://api.groq.com/openai/v1",
    model: "llama-3.3-70b-versatile",
    role: "verify",
  },
  openrouter: {
    baseUrl: "https://openrouter.ai/api/v1",
    model: "deepseek/deepseek-r1:free",
    role: "swap_demo",
  },
};

function getProviderCfg(env: Env, role: "draft" | "verify") {
  const override = role === "draft" ? env.DRAFT_PROVIDER : env.VERIFY_PROVIDER;
  const key = override ?? Object.keys(PROVIDERS).find((k) => PROVIDERS[k].role === role)!;
  const p = PROVIDERS[key];
  if (!p) throw new Error(`Unknown provider: ${key}`);
  const apiKey = getApiKey(env, key);
  return { name: key, baseUrl: p.baseUrl, model: p.model, apiKey };
}

function getApiKey(env: Env, provider: string): string {
  if (provider === "gemini") return env.GEMINI_API_KEY;
  if (provider === "groq") return env.GROQ_API_KEY;
  if (provider === "openrouter") return env.OPENROUTER_API_KEY ?? "";
  return "";
}

function buildSystemPrompt(skillName: string | null, skillContent: string): string {
  const parts = [PERSONA, "\n\n<!-- COGNITIVE DISCIPLINE -->\n" + SYNAPSES];
  if (skillName && skillContent) {
    parts.push(`\n\n<!-- DOMAIN SKILL: ${skillName} -->\n${skillContent}`);
  }
  return parts.join("\n");
}

export async function respond(sessionId: string, text: string, env: Env): Promise<string> {
  const skill = selectSkill(text);
  let skillContent = "";
  if (skill) {
    try {
      skillContent = (await env.SKILLS.get(skill.filename)) ?? "";
    } catch (e) {
      console.warn("Skill KV load failed, continuing without skill:", e);
    }
  }

  const systemPrompt = buildSystemPrompt(skill?.name ?? null, skillContent);
  const history = await getHistory(env.SESSIONS, sessionId);
  const messages = [
    { role: "system", content: systemPrompt },
    ...history,
    { role: "user", content: text },
  ];

  const draftCfg = getProviderCfg(env, "draft");
  let draft: string;
  try {
    draft = await complete(draftCfg, messages);
  } catch (e) {
    console.error("Draft failed after retry:", e);
    return FALLBACK_REPLY;
  }

  const verifyCfg = getProviderCfg(env, "verify");
  const final = await verify(draft, text, verifyCfg);

  await appendTurn(env.SESSIONS, sessionId, text, final);
  return final;
}
