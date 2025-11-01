/*
  # Create Hadiths Database Schema

  1. New Tables
    - `hadiths`
      - `id` (bigint, primary key) - Sequential ID from JSON
      - `hadith_id` (integer) - Original hadith ID from source
      - `source` (text) - Hadith book name (Sahih Bukhari, Sahih Muslim, etc.)
      - `chapter_no` (integer) - Chapter number
      - `hadith_no` (integer) - Hadith number within source
      - `chapter` (text) - Chapter name in English and Arabic
      - `chain_indx` (text) - Chain of narrators indices
      - `text_ar` (text) - Full Arabic text
      - `text_en` (text) - English translation
      - `created_at` (timestamptz) - Record creation timestamp

  2. Indexes
    - Full-text search on English text
    - Full-text search on Arabic text
    - Index on source for filtering
    - Index on hadith_id for lookups

  3. Security
    - Enable RLS
    - Public read access (no authentication required for hadith reading)
    - No write access from frontend
*/

-- Drop existing table if it exists
DROP TABLE IF EXISTS hadiths CASCADE;

-- Create hadiths table
CREATE TABLE IF NOT EXISTS hadiths (
  id BIGINT PRIMARY KEY,
  hadith_id INTEGER NOT NULL,
  source TEXT NOT NULL,
  chapter_no INTEGER NOT NULL,
  hadith_no INTEGER NOT NULL,
  chapter TEXT NOT NULL,
  chain_indx TEXT,
  text_ar TEXT NOT NULL,
  text_en TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_hadiths_source ON hadiths(source);
CREATE INDEX IF NOT EXISTS idx_hadiths_hadith_id ON hadiths(hadith_id);
CREATE INDEX IF NOT EXISTS idx_hadiths_chapter_no ON hadiths(chapter_no);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_hadiths_text_en_fts ON hadiths USING gin(to_tsvector('english', text_en));
CREATE INDEX IF NOT EXISTS idx_hadiths_text_ar_fts ON hadiths USING gin(to_tsvector('arabic', text_ar));

-- Enable Row Level Security
ALTER TABLE hadiths ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read hadiths (public access)
CREATE POLICY "Anyone can read hadiths"
  ON hadiths
  FOR SELECT
  TO anon, authenticated
  USING (true);

-- Create a function for semantic search
CREATE OR REPLACE FUNCTION search_hadiths(
  search_query TEXT,
  search_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
  id BIGINT,
  hadith_id INTEGER,
  source TEXT,
  chapter TEXT,
  hadith_no INTEGER,
  text_ar TEXT,
  text_en TEXT,
  similarity REAL
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
      similarity(h.text_en, search_query),
      ts_rank(to_tsvector('english', h.text_en), plainto_tsquery('english', search_query))
    ) as similarity
  FROM hadiths h
  WHERE 
    to_tsvector('english', h.text_en) @@ plainto_tsquery('english', search_query)
    OR h.text_en ILIKE '%' || search_query || '%'
  ORDER BY similarity DESC
  LIMIT search_limit;
END;
$$ LANGUAGE plpgsql;
