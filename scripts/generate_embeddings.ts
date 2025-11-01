import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import * as path from 'path';
import { pipeline } from '@xenova/transformers';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });

const supabaseUrl = process.env.VITE_SUPABASE_URL!;
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase credentials in .env file');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

interface Hadith {
  id: number;
  text_en: string;
  embedding: number[] | null;
}

let extractor: any;

async function initializeModel() {
  console.log('🤖 Loading FREE local embedding model (one-time download ~25MB)...');
  console.log('⏳ This may take a few minutes on first run...\n');
  
  extractor = await pipeline(
    'feature-extraction', 
    'Xenova/all-MiniLM-L6-v2'
  );
  
  console.log('✅ Model loaded and ready!\n');
}

async function generateEmbedding(text: string): Promise<number[] | null> {
  try {
    if (!text || text.trim().length === 0) {
      throw new Error('Empty text provided');
    }
    
    const output = await extractor(text, { 
      pooling: 'mean', 
      normalize: true 
    });
    
    return Array.from(output.data);
  } catch (error) {
    console.error('Error generating embedding:', error);
    return null;
  }
}

async function generateEmbeddingsForHadiths() {
  console.log('🕌 FREE Hadith Embedding Generator');
  console.log('💰 Cost: $0 (100% free local processing)\n');
  console.log('='.repeat(60));

  try {
    // Initialize the FREE local model
    await initializeModel();

    const { count: totalCount, error: countError } = await supabase
      .from('hadiths')
      .select('*', { count: 'exact', head: true });

    if (countError) {
      console.error('Error counting hadiths:', countError);
      process.exit(1);
    }

    console.log(`📊 Total hadiths in database: ${totalCount?.toLocaleString()}`);

    const { count: withoutEmbedding, error: withoutError } = await supabase
      .from('hadiths')
      .select('*', { count: 'exact', head: true })
      .is('embedding', null);

    if (withoutError) {
      console.error('Error counting hadiths without embeddings:', withoutError);
      process.exit(1);
    }

    console.log(`📝 Hadiths without embeddings: ${withoutEmbedding?.toLocaleString()}`);

    if (!withoutEmbedding || withoutEmbedding === 0) {
      console.log('\n✅ All hadiths already have embeddings!');
      return;
    }

    console.log('\n💡 Processing Information:');
    console.log('   ✅ 100% FREE - No API costs!');
    console.log('   ⚡ Estimated time: 60-120 minutes for 34k hadiths');
    console.log('   🔄 Can be stopped and resumed anytime');
    console.log('   🌐 Works offline after initial model download\n');
    console.log('='.repeat(60));
    console.log('\n🚀 Starting processing...\n');

    const BATCH_SIZE = 50;
    let processed = 0;
    let failed = 0;
    const startTime = Date.now();

    for (let offset = 0; offset < withoutEmbedding; offset += BATCH_SIZE) {
      const { data: batch, error: fetchError } = await supabase
        .from('hadiths')
        .select('id, text_en')
        .is('embedding', null)
        .range(offset, offset + BATCH_SIZE - 1);

      if (fetchError) {
        console.error(`❌ Error fetching batch at offset ${offset}:`, fetchError);
        continue;
      }

      if (!batch || batch.length === 0) {
        console.log('ℹ️  No more hadiths to process');
        break;
      }

      for (const hadith of batch) {
        try {
          const embedding = await generateEmbedding(hadith.text_en);

          if (embedding) {
            const { error: updateError } = await supabase
              .from('hadiths')
              .update({ embedding })
              .eq('id', hadith.id);

            if (updateError) {
              console.error(`❌ Error updating hadith ${hadith.id}:`, updateError);
              failed++;
            } else {
              processed++;
            }
          } else {
            failed++;
          }

          if (processed % 100 === 0) {
            const percentage = ((processed / withoutEmbedding) * 100).toFixed(1);
            const elapsed = ((Date.now() - startTime) / 1000 / 60).toFixed(1);
            const rate = (processed / (Date.now() - startTime) * 60000).toFixed(1);
            const remaining = ((withoutEmbedding - processed) / parseFloat(rate)).toFixed(0);
            
            console.log(`📊 Progress: ${processed.toLocaleString()} / ${withoutEmbedding.toLocaleString()} (${percentage}%)`);
            console.log(`   ⚡ Rate: ${rate} hadiths/min | ⏱️  Elapsed: ${elapsed}min | 🕐 ETA: ~${remaining}min | ❌ Failed: ${failed}\n`);
          }
        } catch (error) {
          console.error(`❌ Error processing hadith ${hadith.id}:`, error);
          failed++;
        }
      }
    }

    const totalTime = ((Date.now() - startTime) / 1000 / 60).toFixed(1);

    console.log('\n' + '='.repeat(60));
    console.log('✨ Embedding generation completed!');
    console.log('='.repeat(60));
    console.log(`✅ Successfully processed: ${processed.toLocaleString()}`);
    console.log(`❌ Failed: ${failed.toLocaleString()}`);
    console.log(`⏱️  Total time: ${totalTime} minutes`);
    console.log(`⚡ Average rate: ${(processed / parseFloat(totalTime)).toFixed(1)} hadiths/min`);
    console.log(`💰 Total cost: $0.00 (FREE!)`);

    const { count: finalWithoutEmbedding } = await supabase
      .from('hadiths')
      .select('*', { count: 'exact', head: true })
      .is('embedding', null);

    console.log(`\n📊 Remaining hadiths without embeddings: ${finalWithoutEmbedding?.toLocaleString() || 0}`);
    
    if (finalWithoutEmbedding === 0) {
      console.log('\n🎉 All hadiths now have embeddings!');
    }

  } catch (error) {
    console.error('\n❌ Process failed:', error);
    process.exit(1);
  }
}

generateEmbeddingsForHadiths();