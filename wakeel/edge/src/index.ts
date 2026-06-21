import { respond } from "./harness";
import { validateSignature, sendReply } from "./twilio";

export interface Env {
  SESSIONS: KVNamespace;
  SKILLS: KVNamespace;
  GEMINI_API_KEY: string;
  GROQ_API_KEY: string;
  TWILIO_ACCOUNT_SID: string;
  TWILIO_AUTH_TOKEN: string;
  TWILIO_FROM: string;
  DRAFT_PROVIDER?: string;
  VERIFY_PROVIDER?: string;
  OPENROUTER_API_KEY?: string;
  DEV_SKIP_VALIDATION?: string;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({ status: "ok" });
    }

    if (request.method === "POST" && url.pathname === "/webhook") {
      const formData = await request.formData();
      const params: Record<string, string> = {};
      for (const [k, v] of formData.entries()) params[k] = v as string;

      if (env.DEV_SKIP_VALIDATION !== "1") {
        const sig = request.headers.get("X-Twilio-Signature") ?? "";
        if (!(await validateSignature(env.TWILIO_AUTH_TOKEN, request.url, params, sig))) {
          return new Response("Forbidden", { status: 403 });
        }
      }

      const from = params["From"] ?? "";
      const body = params["Body"] ?? "";

      ctx.waitUntil(
        (async () => {
          try {
            const reply = await respond(from, body, env);
            await sendReply(from, reply, env);
          } catch (e) {
            console.error("Pipeline error:", e);
          }
        })(),
      );

      return new Response("<Response/>", { headers: { "Content-Type": "text/xml" } });
    }

    return new Response("Not Found", { status: 404 });
  },
};
