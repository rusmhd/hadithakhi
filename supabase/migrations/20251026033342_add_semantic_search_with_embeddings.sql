/*
  # Add Semantic Search with Vector Embeddings

  1. Extensions
    - Enable pgvector extension for semantic/contextual search
    - This allows understanding meaning and context, not just keywords

  2. Schema Changes
    - Add embedding column to store text vectors
    - Create vector indexes for fast similarity search

  3. Functions
    - Create enhanced search function that combines:
      * Semantic similarity (contextual understanding)
      * Fuzzy text matching (typo tolerance)
      * Full-text search (keyword matching)
    - Weight semantic results higher for better context understanding

  4. Notes
    - Embeddings will be generated via edge function using AI
    - This enables searches like "hadith about being kind" to find relevant hadiths
      even if they don't contain exact words
*/

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column for semantic search (384 dimensions for sentence transformers)
ALTER TABLE hadiths 
ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Create index for fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_hadiths_embedding ON hadiths 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Enhanced search function with semantic understanding
CREATE OR REPLACE FUNCTION search_hadiths_semantic(
  search_query TEXT,
  query_embedding vector(384) DEFAULT NULL,
  search_limit INTEGER DEFAULT 10,
  min_similarity REAL DEFAULT 0.05
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
  -- If embedding is provided, use semantic search with other methods
  IF query_embedding IS NOT NULL THEN
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
        -- Semantic similarity (highest weight for context)
        CASE 
          WHEN h.embedding IS NOT NULL 
          THEN (1 - (h.embedding <=> query_embedding)) * 3.0
          ELSE 0
        END,
        -- Fuzzy text matching
        similarity(h.text_en, search_query) * 2.0,
        similarity(h.text_ar, search_query) * 1.5,
        -- Full-text search
        CASE 
          WHEN to_tsvector('english', h.text_en) @@ plainto_tsquery('english', search_query)
          THEN ts_rank(to_tsvector('english', h.text_en), plainto_tsquery('english', search_query)) * 1.5
          ELSE 0
        END,
        -- Exact substring match
        CASE 
          WHEN h.text_en ILIKE '%' || search_query || '%' THEN 0.5
          ELSE 0
        END
      )::REAL as relevance_score
    FROM hadiths h
    WHERE 
      (h.embedding IS NOT NULL AND (1 - (h.embedding <=> query_embedding)) > 0.3)
      OR similarity(h.text_en, search_query) > min_similarity
      OR similarity(h.text_ar, search_query) > min_similarity
      OR to_tsvector('english', h.text_en) @@ plainto_tsquery('english', search_query)
      OR h.text_en ILIKE '%' || search_query || '%'
      OR h.text_ar ILIKE '%' || search_query || '%'
    ORDER BY relevance_score DESC
    LIMIT search_limit;
  ELSE
    -- Fallback to fuzzy search if no embedding
    RETURN QUERY
    SELECT * FROM search_hadiths_fuzzy(search_query, search_limit, min_similarity);
  END IF;
END;
$$ LANGUAGE plpgsql;
