/*
  # Fix Hadiths ID Strategy

  1. Schema Changes
    - Make id auto-increment (use GENERATED ALWAYS AS IDENTITY)
    - Add original_id field to store the JSON file's id
    - This allows importing multiple files without ID conflicts

  2. Updates
    - Recreate table with new structure
*/

-- Drop existing table
DROP TABLE IF EXISTS hadiths CASCADE;

-- Recreate with auto-increment ID
CREATE TABLE hadiths (
  id BIGSERIAL PRIMARY KEY,
  original_id INTEGER NOT NULL,
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
CREATE INDEX idx_hadiths_original_id ON hadiths(original_id);
CREATE INDEX idx_hadiths_source ON hadiths(source);
CREATE INDEX idx_hadiths_hadith_id ON hadiths(hadith_id);
CREATE INDEX idx_hadiths_chapter_no ON hadiths(chapter_no);

-- Create full-text search indexes
CREATE INDEX idx_hadiths_text_en_fts ON hadiths USING gin(to_tsvector('english', text_en));
CREATE INDEX idx_hadiths_text_ar_fts ON hadiths USING gin(to_tsvector('arabic', text_ar));

-- Enable Row Level Security
ALTER TABLE hadiths ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read hadiths
CREATE POLICY "Anyone can read hadiths"
  ON hadiths
  FOR SELECT
  TO anon, authenticated
  USING (true);

-- Allow anon to insert (for initial import)
CREATE POLICY "Allow insert for data import"
  ON hadiths
  FOR INSERT
  TO anon
  WITH CHECK (true);
