# Similarity Algorithms Reference

> Extracted from prompts.chat `packages/prompts.chat/src/similarity/index.ts`.

## Complete Implementation

```typescript
import crypto from "crypto";

// ── Normalization ──────────────────────────────────────────

const STOP_WORDS = new Set([
  "the", "a", "an", "is", "are", "was", "were", "be", "been",
  "being", "have", "has", "had", "do", "does", "did", "will",
  "would", "could", "should", "may", "might", "shall", "can",
  "to", "of", "in", "for", "on", "with", "at", "by", "from",
  "as", "into", "about", "like", "through", "after", "between",
  "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
  "it", "its", "this", "that", "these", "those",
]);

export function normalizeContent(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, " ")    // strip punctuation
    .split(/\s+/)
    .filter((w) => w.length > 1 && !STOP_WORDS.has(w))
    .join(" ")
    .trim();
}

// ── Fingerprinting ─────────────────────────────────────────

export function getContentFingerprint(text: string): string {
  const normalized = normalizeContent(text);
  return crypto.createHash("sha256").update(normalized).digest("hex");
}

// ── Bigram Generation ──────────────────────────────────────

function getBigrams(text: string): Set<string> {
  const normalized = normalizeContent(text);
  const bigrams = new Set<string>();
  for (let i = 0; i < normalized.length - 1; i++) {
    bigrams.add(normalized.substring(i, i + 2));
  }
  return bigrams;
}

// ── Similarity Scoring ─────────────────────────────────────

export function calculateSimilarity(a: string, b: string): number {
  const bigramsA = getBigrams(a);
  const bigramsB = getBigrams(b);

  if (bigramsA.size === 0 && bigramsB.size === 0) return 1;
  if (bigramsA.size === 0 || bigramsB.size === 0) return 0;

  let intersection = 0;
  for (const bg of bigramsA) {
    if (bigramsB.has(bg)) intersection++;
  }

  const union = bigramsA.size + bigramsB.size - intersection;
  return union === 0 ? 0 : intersection / union; // Jaccard index
}

export function isSimilarContent(
  a: string,
  b: string,
  threshold = 0.8
): boolean {
  return calculateSimilarity(a, b) >= threshold;
}

// ── Batch Deduplication ────────────────────────────────────

interface DuplicateGroup<T> {
  original: T;
  duplicates: Array<{ item: T; similarity: number }>;
}

export function findDuplicates<T extends { content: string }>(
  items: T[],
  threshold = 0.8
): DuplicateGroup<T>[] {
  const groups: DuplicateGroup<T>[] = [];
  const seen = new Set<number>();

  // Phase 1: Exact match via fingerprint
  const fingerprints = new Map<string, number>();
  for (let i = 0; i < items.length; i++) {
    const fp = getContentFingerprint(items[i].content);
    if (fingerprints.has(fp)) {
      const origIdx = fingerprints.get(fp)!;
      seen.add(i);
      // Add to existing group or create new
      let group = groups.find((g) => g.original === items[origIdx]);
      if (!group) {
        group = { original: items[origIdx], duplicates: [] };
        groups.push(group);
      }
      group.duplicates.push({ item: items[i], similarity: 1.0 });
    } else {
      fingerprints.set(fp, i);
    }
  }

  // Phase 2: Fuzzy match on remaining items
  const remaining = items.filter((_, i) => !seen.has(i));
  for (let i = 0; i < remaining.length; i++) {
    if (seen.has(i)) continue;
    for (let j = i + 1; j < remaining.length; j++) {
      if (seen.has(j)) continue;
      const sim = calculateSimilarity(remaining[i].content, remaining[j].content);
      if (sim >= threshold) {
        seen.add(j);
        let group = groups.find((g) => g.original === remaining[i]);
        if (!group) {
          group = { original: remaining[i], duplicates: [] };
          groups.push(group);
        }
        group.duplicates.push({ item: remaining[j], similarity: sim });
      }
    }
  }

  return groups;
}

export function deduplicate<T extends { content: string }>(
  items: T[],
  threshold = 0.8
): T[] {
  const groups = findDuplicates(items, threshold);
  const duplicateItems = new Set(
    groups.flatMap((g) => g.duplicates.map((d) => d.item))
  );
  return items.filter((item) => !duplicateItems.has(item));
}
```

## Algorithm Comparison

| Algorithm | Speed | Accuracy | Best For |
|-----------|-------|----------|----------|
| **Fingerprint (SHA-256)** | O(1) lookup | Exact only | Pre-filter for exact duplicates |
| **Bigram Jaccard** | O(n*m) | Good for short text | Prompts, titles, short paragraphs |
| **Trigram Jaccard** | O(n*m) | Better for longer text | Articles, documentation |
| **Cosine TF-IDF** | O(n*d) | Best for documents | Long-form content, embeddings |
| **Levenshtein** | O(n*m) | Character-level | Typo detection, near-identical |
| **Min-Hash LSH** | O(n*b) | Approximate | Millions of items at scale |

## Threshold Guidelines

| Use Case | Recommended Threshold |
|----------|----------------------|
| Exact duplicate removal | 0.95 |
| Near-duplicate detection | 0.80 (default) |
| Topic-level grouping | 0.60 |
| Broad similarity search | 0.40 |
