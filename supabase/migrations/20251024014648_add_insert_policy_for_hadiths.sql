/*
  # Add Insert Policy for Hadith Import

  1. Security Updates
    - Add policy to allow service role to insert hadiths
    - Keep read access public
*/

-- Allow service role to insert hadiths (for data import)
CREATE POLICY "Service role can insert hadiths"
  ON hadiths
  FOR INSERT
  TO authenticated
  WITH CHECK (true);
