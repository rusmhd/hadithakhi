/*
  # Add Fuzzy Search Capabilities

  1. Extensions
    - Enable pg_trgm (trigram) extension for fuzzy text matching
    - This allows similarity searches and handles typos/incomplete text

  2. Indexes
    - Add GIN indexes using trigram operators for fuzzy search
    - Create indexes on both English and Arabic text fields

  3. Functions
    - Update search function to use similarity ranking
    - Return multiple matches ordered by relevance
*/

-- Enable pg_trgm extension for fuzzy/similarity search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Drop existing full-text search indexes (we'll recreate with better ones)
DROP INDEX IF EXISTS idx_hadiths_text_en_fts;
DROP INDEX IF EXISTS idx_hadiths_text_ar_fts;

-- Create trigram indexes for fuzzy search on English text
CREATE INDEX IF NOT EXISTS idx_hadiths_text_en_trgm ON hadiths USING gin(text_en gin_trgm_ops);

-- Create trigram indexes for fuzzy search on Arabic text
CREATE INDEX IF NOT EXISTS idx_hadiths_text_ar_trgm ON hadiths USING gin(text_ar gin_trgm_ops);

-- Create full-text search indexes (still useful for exact matching)
CREATE INDEX IF NOT EXISTS idx_hadiths_text_en_fts ON hadiths USING gin(to_tsvector('english', text_en));
CREATE INDEX IF NOT EXISTS idx_hadiths_text_ar_fts ON hadiths USING gin(to_tsvector('arabic', text_ar));

-- Create function for advanced fuzzy search with multiple results
CREATE OR REPLACE FUNCTION search_hadiths_fuzzy(
  search_query TEXT,
  search_limit INTEGER DEFAULT 10,
  min_similarity REAL DEFAULT 0.1
)
RETURNS TABLE (
  id BIGINT,
  hadith_id INTEGER,
  source TEXT,
  chapter TEXT,
  hadith_no TEXT,
  text_ar TEXT,
  text_en TEXT,
  relevance_score REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    h.id,
    h.hadith_id,
    h.source,
    h.chapter,
    h.hadith_no,
    h.text_ar,
    h.text_en,
    GREATEST(
      similarity(h.text_en, search_query) * 2.0,
      similarity(h.text_ar, search_query) * 1.5,
      CASE 
        WHEN to_tsvector('english', h.text_en) @@ plainto_tsquery('english', search_query)
        THEN ts_rank(to_tsvector('english', h.text_en), plainto_tsquery('english', search_query)) * 1.5
        ELSE 0
      END,
      CASE 
        WHEN h.text_en ILIKE '%' || search_query || '%' THEN 0.5
        ELSE 0
      END
    )::REAL as relevance_score
  FROM hadiths h
  WHERE 
    similarity(h.text_en, search_query) > min_similarity
    OR similarity(h.text_ar, search_query) > min_similarity
    OR to_tsvector('english', h.text_en) @@ plainto_tsquery('english', search_query)
    OR h.text_en ILIKE '%' || search_query || '%'
    OR h.text_ar ILIKE '%' || search_query || '%'
  ORDER BY relevance_score DESC
  LIMIT search_limit;
END;
$$ LANGUAGE plpgsql;
