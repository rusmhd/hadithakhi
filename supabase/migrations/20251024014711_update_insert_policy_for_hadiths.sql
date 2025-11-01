/*
  # Update Insert Policy for Hadith Import

  1. Security Updates
    - Drop previous insert policy
    - Add policy to allow anon role to insert hadiths (for initial data import)
    - Note: This should be removed after import is complete for production
*/

-- Drop existing insert policy if exists
DROP POLICY IF EXISTS "Service role can insert hadiths" ON hadiths;

-- Allow anon role to insert hadiths (for data import)
CREATE POLICY "Allow insert for data import"
  ON hadiths
  FOR INSERT
  TO anon
  WITH CHECK (true);
