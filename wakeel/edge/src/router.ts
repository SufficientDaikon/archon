import indexData from "./index.json";

type SkillMeta = { filename: string; name: string };

// STOP_WORDS and tokenizer must exactly match indexer.py or scores drift.
const STOP_WORDS = new Set([
  "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
  "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
  "being", "have", "has", "had", "do", "does", "did", "will", "would",
  "could", "should", "may", "might", "shall", "can", "must", "need",
  "this", "that", "these", "those", "it", "its", "you", "your", "i",
  "we", "our", "they", "their", "he", "she", "his", "her", "not", "no",
  "all", "each", "every", "any", "some", "most", "more", "less", "very",
  "just", "also", "so", "if", "then", "than", "when", "while", "as",
  "about", "up", "out", "into", "over", "after", "before", "between",
  "through", "during", "without", "against", "above", "below",
  "skill", "guidelines", "best", "practices", "patterns", "component",
  "components", "design", "development", "implementation", "approach",
  "strategy", "framework", "use", "using", "used", "based", "ensure",
  "provide", "create", "build", "make", "work", "working", "follow",
  "following", "include", "including", "new", "expert", "focused",
]);

function tokenize(text: string): string[] {
  const tokens = text.toLowerCase().match(/[a-z][a-z0-9]+/g) ?? [];
  return tokens.filter((t) => !STOP_WORDS.has(t) && t.length >= 2);
}

export function selectSkill(query: string, threshold = 0.3): SkillMeta | null {
  // Cast through unknown: JSON import infers (string|number)[][] but runtime is [string, number][].
  const idx = indexData.index as unknown as Record<string, [string, number][]>;
  const skills = indexData.skills as SkillMeta[];
  const terms = tokenize(query);

  if (!terms.length) return null;

  const scores: Record<string, number> = {};
  for (const term of terms) {
    const postings = idx[term];
    if (!postings) continue;
    for (const [filename, score] of postings) {
      scores[filename] = (scores[filename] ?? 0) + score;
    }
  }

  // Find the max-scoring skill, then gate by threshold.
  // Mirrors Python: max(scores, key=...) filtered by >= threshold.
  let best: SkillMeta | null = null;
  let bestScore = -1;
  for (const [filename, score] of Object.entries(scores)) {
    if (score > bestScore) {
      bestScore = score;
      best = skills.find((s) => s.filename === filename) ?? null;
    }
  }

  return bestScore >= threshold ? best : null;
}