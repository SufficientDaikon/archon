// Parity check: TS router must select same skills as Python router for golden queries.
// Run: node wakeel/edge/parity_check.mjs
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import path from "path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const indexData = JSON.parse(readFileSync(path.join(__dirname, "src/index.json"), "utf8"));

const STOP_WORDS = new Set([
  "a","an","the","and","or","but","in","on","at","to","for","of","with","by","from",
  "is","are","was","were","be","been","being","have","has","had","do","does","did",
  "will","would","could","should","may","might","shall","can","must","need","this",
  "that","these","those","it","its","you","your","i","we","our","they","their","he",
  "she","his","her","not","no","all","each","every","any","some","most","more","less",
  "very","just","also","so","if","then","than","when","while","as","about","up","out",
  "into","over","after","before","between","through","during","without","against",
  "above","below","skill","guidelines","best","practices","patterns","component",
  "components","design","development","implementation","approach","strategy","framework",
  "use","using","used","based","ensure","provide","create","build","make","work",
  "working","follow","following","include","including","new","expert","focused",
]);

function tokenize(text) {
  const tokens = text.toLowerCase().match(/[a-z][a-z0-9]+/g) ?? [];
  return tokens.filter((t) => !STOP_WORDS.has(t) && t.length >= 2);
}

function selectSkill(query, threshold = 0.3) {
  const idx = indexData.index;
  const skills = indexData.skills;
  const terms = tokenize(query);
  if (!terms.length) return null;

  const scores = {};
  for (const term of terms) {
    const postings = idx[term];
    if (!postings) continue;
    for (const [filename, score] of postings) {
      scores[filename] = (scores[filename] ?? 0) + score;
    }
  }

  let best = null;
  let bestScore = threshold;
  for (const [filename, score] of Object.entries(scores)) {
    if (score > bestScore) {
      bestScore = score;
      best = skills.find((s) => s.filename === filename) ?? null;
    }
  }
  return best ? { ...best, score: bestScore } : null;
}

// Golden anchors from Python router (verified 2026-06-22):
//   DEV Q  → fastmcp (2.235)
//   LENTIL → design-review (1.930)
const CASES = [
  {
    query: "how do I build a REST API in Python?",
    expectedFilename: "fastmcp",
    expectedScoreMin: 2.0,
  },
  {
    query: "what is a good recipe for lentil soup?",
    expectedFilename: "design-review",
    expectedScoreMin: 1.5,
  },
];

let allPassed = true;
for (const { query, expectedFilename, expectedScoreMin } of CASES) {
  const result = selectSkill(query);
  const pass =
    result !== null &&
    result.filename === expectedFilename &&
    result.score >= expectedScoreMin;
  console.log(`Q: "${query}"`);
  console.log(`  → skill: ${result?.filename ?? "none"} (score: ${result?.score?.toFixed(3) ?? "0"})`);
  console.log(`  → expected: ${expectedFilename} (min score: ${expectedScoreMin})`);
  console.log(`  → ${pass ? "PASS ✓" : "FAIL ✗"}`);
  if (!pass) allPassed = false;
}

console.log(allPassed ? "\nPARITY CHECK: PASSED" : "\nPARITY CHECK: FAILED");
process.exit(allPassed ? 0 : 1);
