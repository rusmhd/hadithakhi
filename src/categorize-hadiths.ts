// ************************************************************
//  categorize-hadiths.ts   –  34 k hadith cluster edition
// ************************************************************
import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';

// NEW: granular clusters + optional cosine fallback
import { bestClusterForHadith, ALL_CLUSTERS } from './hadith-clusters';
import { bestCluster } from './cluster-matcher';

dotenv.config();

const supabase = createClient(
  process.env.VITE_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

/* ============================================================
   COMPREHENSIVE KEYWORD MAP – unchanged from your original
   ============================================================ */
const COMPREHENSIVE_KEYWORDS = {
  aqeedah: { /* … full object untouched … */ },
  ibaadah: { /* … full object untouched … */ },
  muamalat: { /* … full object untouched … */ },
  family: { /* … full object untouched … */ },
  akhlaq: { /* … full object untouched … */ },
  'halal-haram': { /* … full object untouched … */ },
  knowledge: { /* … full object untouched … */ },
  jihad: { /* … full object untouched … */ },
  eschatology: { /* … full object untouched … */ },
  seerah: { /* … full object untouched … */ },
  health: { /* … full object untouched … */ },
  governance: { /* … full object untouched … */ }
} as const;

/* ============================================================
   1.  BUILD LEGACY KEYWORD MAP (major category scoring)
   ============================================================ */
function extractAllKeywords(): Map<string, { category: string; subcategory: string; weight: number }> {
  const oldMap = new Map<string, { category: string; subcategory: string; weight: number }>();
  for (const [category, subObj] of Object.entries(COMPREHENSIVE_KEYWORDS)) {
    for (const [subcat, kwList] of Object.entries(subObj)) {
      const weight = subcat === 'primary' ? 2.0 : 1.0;
      for (const kw of kwList) {
        const key = kw.toLowerCase();
        if (!oldMap.has(key)) oldMap.set(key, { category, subcategory: subcat, weight });
      }
    }
  }
  return oldMap;
}

/* ============================================================
   2.  SCORE MAJOR CATEGORY (unchanged)
   ============================================================ */
function scoreHadith(text: string, keywordMap: Map<string, any>): Map<string, number> {
  const lowerText = text.toLowerCase();
  const categoryScores = new Map<string, number>();
  for (const c of Object.keys(COMPREHENSIVE_KEYWORDS)) categoryScores.set(c, 0);

  for (const [keyword, info] of keywordMap.entries()) {
    const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
    const matches = lowerText.match(regex);
    if (matches) {
      categoryScores.set(info.category, (categoryScores.get(info.category) || 0) + matches.length * info.weight);
    }
  }
  return categoryScores;
}

/* ============================================================
   3.  CLUSTER CHOOSER – keyword first, cosine fallback
   ============================================================ */
const USE_SEMANTIC_FALLBACK = true;      // toggle off → pure keyword
const SEMANTIC_MIN_SIMILARITY = 0.15;    // 15 % cosine similarity

function pickClusterId(text: string, categoryId: string, keywordId: string | null): string | null {
  if (!USE_SEMANTIC_FALLBACK) return keywordId;
  if (keywordId) return keywordId;                      // strong keyword hit → keep it
  const cos = bestCluster(text, categoryId);
  return cos && cos.similarity >= SEMANTIC_MIN_SIMILARITY ? cos.clusterId : null;
}

/* ============================================================
   4.  MAIN CATEGORISATION WRAPPER
   ============================================================ */
function categorizeHadith(hadithText: string, keywordMap: Map<string, any>): {
  categoryId: string;
  subcategory: string | null;
  confidence: number;
  keywords: string[];
} {
  // ---------- major category ----------
  const categoryScores = scoreHadith(hadithText, keywordMap);
  let bestCategory = 'general';
  let highestScore = 0;
  for (const [cat, sc] of categoryScores.entries()) {
    if (sc > highestScore) { highestScore = sc; bestCategory = cat; }
  }

  // ---------- micro cluster ----------
  const keywordId = bestClusterForHadith(hadithText, 1);
  const bestClusterId = pickClusterId(hadithText, bestCategory, keywordId);

  // ---------- audit keywords ----------
  const matchedKeywords: string[] = [];
  for (const [kw, info] of keywordMap.entries()) {
    if (info.category === bestCategory) {
      const rx = new RegExp(`\\b${kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
      if (hadithText.toLowerCase().match(rx)) matchedKeywords.push(kw);
    }
  }

  const confidence = Math.min((highestScore / hadithText.split(' ').length) * 100, 100);
  return {
    categoryId: bestCategory,
    subcategory: bestClusterId,               // cluster id
    confidence: Math.round(confidence),
    keywords: matchedKeywords.slice(0, 10),
  };
}

/* ============================================================
   5.  BATCH PROCESSOR (unchanged except counters)
   ============================================================ */
async function categorizeAllHadiths() {
  console.log('🚀 Starting comprehensive hadith categorisation...');
  const keywordMap = extractAllKeywords();
  console.log(`✅ Loaded ${keywordMap.size} unique keywords`);

  const { count } = await supabase.from('hadiths').select('*', { count: 'exact', head: true });
  console.log(`📚 Total hadiths: ${count}`);

  const BATCH_SIZE = 100;
  let processed = 0, categorized = 0, lowConfidence = 0, failed = 0, semanticUsed = 0;

  for (let offset = 0; offset < count!; offset += BATCH_SIZE) {
    const { data: hadiths, error } = await supabase
      .from('hadiths')
      .select('id, hadith_text, hadith_english')
      .range(offset, offset + BATCH_SIZE - 1);

    if (error || !hadiths?.length) continue;

    const updates: any[] = [];
    for (const hadith of hadiths) {
      const text = hadith.hadith_english || hadith.hadith_text || '';
      const result = categorizeHadith(text, keywordMap);

      processed++;
      if (result.confidence >= 10) {
        // track semantic usage
        const kwId = bestClusterForHadith(text, 1);
        if (result.subcategory && result.subcategory !== kwId) semanticUsed++;

        updates.push({
          id: hadith.id,
          category_id: result.categoryId,
          subcategory: result.subcategory,
          keywords: result.keywords,
        });
        categorized++;
      } else {
        lowConfidence++;
      }
    }

    // bulk update
    if (updates.length) {
      const { error: bulkErr } = await supabase.from('hadiths').upsert(updates);
      if (bulkErr) {
        failed += updates.length;
        console.error('❌ Bulk update failed', bulkErr);
      }
    }

    const progress = ((processed / count!) * 100).toFixed(1);
    console.log(
      `⏳ ${processed}/${count} (${progress}%) | ` +
      `✅ ${categorized} | ⚠️ ${lowConfidence} | 🧠 semantic ${semanticUsed}`
    );
  }

  console.log('\n✨ Complete!');
  console.log(`📈 Success: ${categorized} | Low conf: ${lowConfidence} | Failed: ${failed}`);
  console.log(`🧠 Semantic fallback helped: ${semanticUsed} hadiths`);
}

/* ============================================================
   6.  RUN
   ============================================================ */
categorizeAllHadiths().then(() => {
  console.log('🏁 Script finished.');
  process.exit(0);
});