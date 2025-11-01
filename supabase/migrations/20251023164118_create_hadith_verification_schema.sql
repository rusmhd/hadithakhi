/*
  # Hadith Verification System Schema

  ## Overview
  This migration creates the database schema for a Hadith verification system that caches
  verified hadiths for faster lookups and better user experience.

  ## Tables Created
  
  ### 1. `hadith_verifications`
  Stores verified hadith results with full details including Arabic text, English translation,
  authenticity grade, and source information.
  
  **Columns:**
  - `id` (uuid, primary key) - Unique identifier for each verification record
  - `search_text` (text) - The original text searched by the user (normalized/lowercase)
  - `hadith_arabic` (text) - The hadith in Arabic script
  - `hadith_english` (text) - The hadith translated to English
  - `authenticity` (text) - Authenticity grade (Sahih, Hasan, Daif, etc.)
  - `source` (text) - The source collection (Bukhari, Muslim, etc.)
  - `reference` (text) - Specific reference (book, hadith number)
  - `narrator` (text) - The chain of narrators if available
  - `found` (boolean) - Whether the hadith was found in authentic sources
  - `created_at` (timestamptz) - When this record was created
  - `search_count` (integer) - Number of times this hadith has been searched
  - `last_searched_at` (timestamptz) - Last time this hadith was searched
  
  ### 2. Indexes
  - Index on `search_text` for fast lookups of previously verified hadiths
  - Index on `last_searched_at` for cleanup of old cache entries
  
  ## Security
  - Enable Row Level Security (RLS) on `hadith_verifications` table
  - Public read access policy: Anyone can read verified hadiths (public knowledge)
  - Service role only write access: Only backend services can write/update records
  
  ## Notes
  - The `search_text` column stores normalized text to improve cache hit rates
  - The `search_count` helps track popular hadiths
  - This schema supports both found and not-found results to avoid repeated API calls
*/

-- Create hadith_verifications table
CREATE TABLE IF NOT EXISTS hadith_verifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  search_text text NOT NULL,
  hadith_arabic text,
  hadith_english text,
  authenticity text,
  source text,
  reference text,
  narrator text,
  found boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  search_count integer DEFAULT 1,
  last_searched_at timestamptz DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_hadith_verifications_search_text 
  ON hadith_verifications(search_text);

CREATE INDEX IF NOT EXISTS idx_hadith_verifications_last_searched 
  ON hadith_verifications(last_searched_at DESC);

-- Enable Row Level Security
ALTER TABLE hadith_verifications ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can read hadith verifications (public religious knowledge)
CREATE POLICY "Anyone can read hadith verifications"
  ON hadith_verifications
  FOR SELECT
  TO anon, authenticated
  USING (true);

-- Policy: Only service role can insert hadith verifications
CREATE POLICY "Service role can insert hadith verifications"
  ON hadith_verifications
  FOR INSERT
  TO service_role
  WITH CHECK (true);

-- Policy: Only service role can update hadith verifications
CREATE POLICY "Service role can update hadith verifications"
  ON hadith_verifications
  FOR UPDATE
  TO service_role
  USING (true)
  WITH CHECK (true);
