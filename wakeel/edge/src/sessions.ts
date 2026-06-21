type Message = { role: string; content: string };

const MAX_MESSAGES = 20; // 10 turns × 2

export async function getHistory(kv: KVNamespace, sessionId: string): Promise<Message[]> {
  const raw = await kv.get(sessionId);
  if (!raw) return [];
  try {
    return JSON.parse(raw) as Message[];
  } catch {
    return [];
  }
}

export async function appendTurn(
  kv: KVNamespace,
  sessionId: string,
  userText: string,
  assistantText: string,
): Promise<void> {
  const history = await getHistory(kv, sessionId);
  history.push({ role: "user", content: userText });
  history.push({ role: "assistant", content: assistantText });
  const trimmed = history.slice(-MAX_MESSAGES);
  await kv.put(sessionId, JSON.stringify(trimmed), { expirationTtl: 86400 });
}
