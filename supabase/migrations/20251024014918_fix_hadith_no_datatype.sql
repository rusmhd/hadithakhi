/*
  # Fix hadith_no Data Type

  1. Schema Changes
    - Change hadith_no from INTEGER to TEXT
    - Some hadith numbers in the source data have suffixes like "815b"
*/

-- Change hadith_no to TEXT to accommodate values like "815b"
ALTER TABLE hadiths ALTER COLUMN hadith_no TYPE TEXT;
