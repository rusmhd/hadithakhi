// cluster-matcher.ts
// Pure-JS semantic similarity inside a category
// Works stand-alone – no external deps

import { CLUSTER_MAP} from "./hadith-clusters";

/* ---------- helpers ---------- */
const STOP_WORDS = new Set(
  "the is and of a in to for with on that this it he she they you we be are was were will would could should has had have do does did but not so if then than as at by an or from".split(" ")
);

function tokenize(text: string): Map<string, number> {
  const bag = new Map<string, number>();
  text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .split(" ")
    .filter((t) => t.length > 2 && !STOP_WORDS.has(t))
    .forEach((t) => bag.set(t, (bag.get(t) || 0) + 1));
  return bag;
}

function tfidf(bag: Map<string, number>, docFreq: Map<string, number>, totalDocs: number): Map<string, number> {
  const vec = new Map<string, number>();
  const maxTf = Math.max(1, ...bag.values());
  for (const [term, tf] of bag) {
    const idf = Math.log(totalDocs / (docFreq.get(term) || 1));
    vec.set(term, (tf / maxTf) * idf);
  }
  return vec;
}

function cosine(a: Map<string, number>, b: Map<string, number>): number {
  let dot = 0,
    normA = 0,
    normB = 0;
  for (const [t, w] of a) {
    dot += w * (b.get(t) || 0);
    normA += w * w;
  }
  for (const w of b.values()) normB += w * w;
  return normA && normB ? dot / (Math.sqrt(normA) * Math.sqrt(normB)) : 0;
}

/* ---------- build tf-idf fingerprints per category ---------- */
interface FingerPrint {
  clusterId: string;
  vec: Map<string, number>;
}
const INDEX_CACHE = new Map<string, FingerPrint[]>();

function buildIndex(categoryId: string): FingerPrint[] {
  if (INDEX_CACHE.has(categoryId)) return INDEX_CACHE.get(categoryId)!;

  const clusters = CLUSTER_MAP[categoryId];
  const docFreq = new Map<string, number>();
  const totalDocs = clusters.reduce((s, c) => s + c.examples.length, 0);

  // pass 1 – df
  for (const c of clusters) {
    const docTerms = new Set<string>();
    c.examples.forEach((e) => tokenize(e).forEach((_, t) => docTerms.add(t)));
    docTerms.forEach((t) => docFreq.set(t, (docFreq.get(t) || 0) + 1));
  }

  // pass 2 – tf-idf
  const fingerprints: FingerPrint[] = [];
  for (const c of clusters) {
    const merged = new Map<string, number>();
    c.examples.forEach((e) => {
      const bag = tokenize(e);
      const tfidfVec = tfidf(bag, docFreq, totalDocs);
      tfidfVec.forEach((w, t) => merged.set(t, (merged.get(t) || 0) + w));
    });
    fingerprints.push({ clusterId: c.id, vec: merged });
  }

  INDEX_CACHE.set(categoryId, fingerprints);
  return fingerprints;
}

/* ---------- public API ---------- */
export interface ClusterMatch {
  clusterId: string;
  similarity: number; // 0-1
}

export function bestCluster(text: string, categoryId: string): ClusterMatch | null {
  const fps = buildIndex(categoryId);
  const q = tfidf(tokenize(text), new Map(), 1); // query only
  let best: ClusterMatch | null = null;
  for (const fp of fps) {
    const sim = cosine(q, fp.vec);
    if (!best || sim > best.similarity) best = { clusterId: fp.clusterId, similarity: sim };
  }
  return best;
}