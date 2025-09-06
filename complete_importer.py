# complete_importer.py - Import your complete hadith JSON collection

import json
import sqlite3
import os
from pathlib import Path
import re

class CompleteHadithImporter:
    def __init__(self, db_path: str = "hadith_database.db"):
        self.db_path = db_path
        self.theme_map = self.build_theme_mapping()
        self.setup_database()
    
    def setup_database(self):
        """Create optimized database structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing table if you want to start fresh
        # cursor.execute("DROP TABLE IF EXISTS hadiths")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hadiths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arabic_text TEXT NOT NULL,
                english_translation TEXT NOT NULL,
                narrator TEXT,
                collection TEXT NOT NULL,
                book TEXT,
                book_number INTEGER,
                chapter TEXT,
                chapter_number INTEGER,
                hadith_number TEXT,
                volume_number INTEGER,
                authenticity TEXT DEFAULT 'Sahih',
                theme TEXT,
                explanation TEXT,
                application TEXT,
                grade TEXT,
                reference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(collection, book_number, hadith_number)
            )
        ''')
        
        # Create comprehensive indexes for fast searching
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_arabic_full_text ON hadiths(arabic_text)",
            "CREATE INDEX IF NOT EXISTS idx_english_full_text ON hadiths(english_translation)",
            "CREATE INDEX IF NOT EXISTS idx_collection_book ON hadiths(collection, book_number)",
            "CREATE INDEX IF NOT EXISTS idx_theme_search ON hadiths(theme)",
            "CREATE INDEX IF NOT EXISTS idx_narrator ON hadiths(narrator)",
            "CREATE INDEX IF NOT EXISTS idx_hadith_number ON hadiths(collection, hadith_number)"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        conn.commit()
        conn.close()
        print("✅ Database structure ready")
    
    def build_theme_mapping(self):
        """Build comprehensive theme mapping for auto-categorization"""
        return {
            # Worship & Prayer
            'Prayer': [
                'prayer', 'salah', 'salat', 'mosque', 'masjid', 'qibla', 'imam', 
                'congregation', 'ablution', 'wudu', 'adhan', 'call to prayer',
                'prostration', 'sujud', 'rukuh', 'witr', 'tahajjud', 'fajr'
            ],
            'Fasting': [
                'fast', 'fasting', 'sawm', 'ramadan', 'iftar', 'suhur', 'break fast'
            ],
            'Pilgrimage': [
                'hajj', 'umrah', 'pilgrimage', 'kaaba', 'mecca', 'medina', 'tawaf'
            ],
            'Zakat': [
                'zakat', 'charity', 'alms', 'sadaqah', 'wealth', 'poor', 'needy'
            ],
            
            # Faith & Belief
            'Faith': [
                'faith', 'belief', 'iman', 'islam', 'muslim', 'believer', 'disbelief',
                'shirk', 'monotheism', 'tawhid', 'allah', 'god'
            ],
            'Quran': [
                'quran', 'quranic', 'recitation', 'revelation', 'book of allah',
                'verses', 'surah', 'ayah'
            ],
            'Prophets': [
                'prophet', 'messenger', 'muhammad', 'moses', 'jesus', 'abraham',
                'noah', 'david', 'solomon'
            ],
            
            # Character & Morals
            'Character': [
                'character', 'manner', 'behavior', 'conduct', 'ethics', 'moral',
                'virtue', 'righteousness', 'good deed', 'sin'
            ],
            'Honesty': [
                'honest', 'truth', 'truthful', 'lie', 'lying', 'deceive', 'trust'
            ],
            'Kindness': [
                'kind', 'kindness', 'mercy', 'compassion', 'gentle', 'soft',
                'harsh', 'cruel'
            ],
            'Patience': [
                'patience', 'patient', 'sabr', 'perseverance', 'endurance',
                'hardship', 'trial', 'test', 'difficulty'
            ],
            'Humility': [
                'humble', 'humility', 'pride', 'arrogant', 'modest', 'ego'
            ],
            
            # Relationships
            'Family': [
                'family', 'parent', 'mother', 'father', 'child', 'son', 'daughter',
                'wife', 'husband', 'marriage', 'divorce', 'relative'
            ],
            'Brotherhood': [
                'brother', 'sister', 'brotherhood', 'community', 'ummah', 'neighbor',
                'friendship', 'companion'
            ],
            'Leadership': [
                'leader', 'leadership', 'ruler', 'authority', 'obey', 'command',
                'government', 'justice'
            ],
            
            # Knowledge & Education
            'Knowledge': [
                'knowledge', 'learn', 'teach', 'scholar', 'student', 'education',
                'wisdom', 'ignorance', 'study'
            ],
            
            # Business & Finance
            'Business': [
                'business', 'trade', 'trading', 'transaction', 'money', 'wealth',
                'rich', 'poor', 'debt', 'loan', 'interest', 'riba'
            ],
            
            # Life Situations
            'Death': [
                'death', 'die', 'grave', 'burial', 'funeral', 'afterlife',
                'paradise', 'hell', 'judgment'
            ],
            'Health': [
                'health', 'illness', 'sick', 'medicine', 'cure', 'treatment',
                'disease', 'healing'
            ],
            'Travel': [
                'travel', 'journey', 'trip', 'road', 'path'
            ],
            
            # Speech & Communication
            'Speech': [
                'speak', 'speech', 'word', 'tongue', 'silent', 'quiet',
                'gossip', 'backbite', 'slander'
            ],
            
            # Emotions
            'Anger': [
                'anger', 'angry', 'rage', 'fury', 'temper', 'calm'
            ],
            'Fear': [
                'fear', 'afraid', 'scared', 'anxiety', 'worry', 'concern'
            ],
            'Hope': [
                'hope', 'optimism', 'despair', 'hopeless', 'expect'
            ],
            'Gratitude': [
                'grateful', 'gratitude', 'thank', 'appreciate', 'blessing'
            ]
        }
    
    def auto_assign_theme(self, arabic: str, english: str, book: str = "", chapter: str = "") -> str:
        """Intelligently assign theme based on content analysis"""
        
        # Combine all text for analysis
        content = f"{english} {book} {chapter} {arabic}".lower()
        
        # Score each theme
        theme_scores = {}
        
        for theme, keywords in self.theme_map.items():
            score = 0
            for keyword in keywords:
                # Count occurrences with different weights
                if keyword in content:
                    # Higher weight for exact matches
                    score += content.count(keyword) * 2
                    # Bonus for book/chapter matches
                    if keyword in f"{book} {chapter}".lower():
                        score += 5
        
            if score > 0:
                theme_scores[theme] = score
        
        # Return highest scoring theme, or 'General' if no matches
        if theme_scores:
            return max(theme_scores.items(), key=lambda x: x[1])[0]
        
        # Fallback theme assignment based on common patterns
        if 'book of' in book.lower():
            book_name = book.lower().replace('book of', '').strip()
            if 'prayer' in book_name or 'salah' in book_name:
                return 'Prayer'
            elif 'faith' in book_name or 'belief' in book_name:
                return 'Faith'
            elif 'marriage' in book_name or 'family' in book_name:
                return 'Family'
        
        return 'General'
    
    def generate_contextual_explanation(self, theme: str, english: str) -> str:
        """Generate context-aware explanations"""
        
        base_explanations = {
            'Prayer': "This hadith emphasizes the importance of prayer in Islam and provides guidance on proper worship practices.",
            'Faith': "This hadith teaches fundamental aspects of Islamic belief and what it means to be a true believer.",
            'Character': "This hadith guides us in developing excellent character and moral conduct as prescribed in Islam.",
            'Knowledge': "This hadith highlights the Islamic emphasis on seeking and sharing beneficial knowledge.",
            'Family': "This hadith provides essential guidance on family relationships and responsibilities in Islam.",
            'Business': "This hadith offers guidance on conducting business with Islamic ethics and principles.",
            'Charity': "This hadith encourages generosity and emphasizes the importance of helping those in need.",
            'Patience': "This hadith teaches the virtue of patience (sabr) during trials and difficulties.",
            'Brotherhood': "This hadith emphasizes the bonds of brotherhood and community in Islam.",
            'Speech': "This hadith provides guidance on proper speech and communication in Islamic conduct."
        }
        
        # Add specific context based on hadith content
        explanation = base_explanations.get(theme, "This hadith provides important Islamic guidance and wisdom.")
        
        # Enhance with specific details if found
        if 'paradise' in english.lower():
            explanation += " It also mentions the rewards in Paradise for following this guidance."
        elif 'allah' in english.lower():
            explanation += " It reminds us of Allah's wisdom and mercy in this matter."
        
        return explanation
    
    def generate_practical_application(self, theme: str, english: str) -> str:
        """Generate practical, actionable applications"""
        
        applications = {
            'Prayer': "Establish regular prayers, maintain focus during worship, and make prayer a cornerstone of your daily routine.",
            'Faith': "Strengthen your relationship with Allah through regular worship, dhikr, and reflection on His attributes.",
            'Character': "Practice good manners in all interactions, be honest in your dealings, and strive to embody Islamic values.",
            'Knowledge': "Seek beneficial knowledge throughout your life, share what you learn with others, and apply Islamic teachings.",
            'Family': "Honor your parents, maintain strong family bonds, and fulfill your responsibilities to family members.",
            'Business': "Conduct all business with complete honesty, avoid interest (riba), and ensure fairness in all transactions.",
            'Charity': "Give regularly to charity, help those in need in your community, and share your blessings with others.",
            'Patience': "Practice patience during difficult times, trust in Allah's wisdom, and maintain hope during trials.",
            'Brotherhood': "Be a supportive member of your community, help your neighbors, and strengthen bonds with fellow Muslims.",
            'Speech': "Think before speaking, choose words that bring benefit, avoid gossip and harmful speech."
        }
        
        base_app = applications.get(theme, "Apply this Islamic wisdom in your daily life to become a better Muslim.")
        
        # Add specific actions based on content
        if 'charity' in english.lower() or 'give' in english.lower():
            base_app += " Look for opportunities to give charity regularly."
        elif 'pray' in english.lower():
            base_app += " Make this a part of your daily prayer routine."
        
        return base_app
    
    def detect_json_structure(self, file_path: str):
        """Analyze your JSON file structure"""
        print(f"🔍 Analyzing {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📊 File type: {type(data).__name__}")
            
            if isinstance(data, list):
                print(f"📋 Total items: {len(data)}")
                if len(data) > 0:
                    print("🔑 Sample item structure:")
                    sample = data[0]
                    for key, value in sample.items():
                        print(f"   {key}: {type(value).__name__} - {str(value)[:50]}...")
                return data, 'list'
                
            elif isinstance(data, dict):
                print("🔑 Top-level keys:")
                for key in data.keys():
                    value = data[key]
                    print(f"   {key}: {type(value).__name__}")
                    if isinstance(value, list):
                        print(f"      └─ Contains {len(value)} items")
                
                # Find the hadith data
                hadith_keys = ['hadiths', 'data', 'bukhari', 'muslim', 'collection', 'items']
                for key in hadith_keys:
                    if key in data and isinstance(data[key], list):
                        print(f"✅ Found hadith data in key: '{key}'")
                        return data[key], 'nested'
                
                return data, 'dict'
            
        except Exception as e:
            print(f"❌ Error analyzing file: {e}")
            return None, None
    
    def import_complete_collection(self, json_file: str):
        """Import your complete hadith collection"""
        
        if not os.path.exists(json_file):
            print(f"❌ File not found: {json_file}")
            print("Available JSON files:")
            for file in Path('.').glob('*.json'):
                print(f"   - {file}")
            return
        
        # Analyze structure
        data, structure_type = self.detect_json_structure(json_file)
        if not data:
            return
        
        print(f"\n🚀 Starting import of {len(data)} hadiths...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported = 0
        skipped = 0
        errors = []
        
        for i, hadith_item in enumerate(data):
            try:
                # Extract fields with multiple possible names
                arabic = self.get_field_value(hadith_item, 
                    ['arabic', 'arabic_text', 'hadith_arabic', 'arab', 'ar', 'text_ar'])
                
                english = self.get_field_value(hadith_item,
                    ['english', 'english_text', 'hadith_english', 'translation', 'en', 'text_en'])
                
                narrator = self.get_field_value(hadith_item,
                    ['narrator', 'rawi', 'transmitter', 'chain', 'isnad', 'sanad'])
                
                collection = self.get_field_value(hadith_item,
                    ['collection', 'book_name', 'source']) or 'Unknown'
                
                book = self.get_field_value(hadith_item,
                    ['book', 'kitab', 'book_title', 'book_name'])
                
                book_number = self.get_field_value(hadith_item,
                    ['book_number', 'book_no', 'kitab_number'])
                
                chapter = self.get_field_value(hadith_item,
                    ['chapter', 'bab', 'chapter_title', 'chapter_name'])
                
                chapter_number = self.get_field_value(hadith_item,
                    ['chapter_number', 'chapter_no', 'bab_number'])
                
                hadith_number = self.get_field_value(hadith_item,
                    ['hadith_number', 'number', 'hadith_no', 'no', 'id', 'hadith_id']) or str(i + 1)
                
                volume = self.get_field_value(hadith_item,
                    ['volume', 'vol', 'volume_number'])
                
                grade = self.get_field_value(hadith_item,
                    ['grade', 'grading', 'status', 'authenticity'])
                
                reference = self.get_field_value(hadith_item,
                    ['reference', 'ref', 'citation'])
                
                # Skip if missing essential content
                if not arabic and not english:
                    skipped += 1
                    continue
                
                # Auto-assign theme
                theme = self.auto_assign_theme(arabic or '', english or '', book or '', chapter or '')
                
                # Generate explanation and application
                explanation = self.generate_contextual_explanation(theme, english or '')
                application = self.generate_practical_application(theme, english or '')
                
                # Convert numbers to integers
                book_num = self.safe_int(book_number)
                chapter_num = self.safe_int(chapter_number)
                volume_num = self.safe_int(volume)
                
                # Insert into database
                cursor.execute('''
                    INSERT OR REPLACE INTO hadiths 
                    (arabic_text, english_translation, narrator, collection, book, book_number,
                     chapter, chapter_number, hadith_number, volume_number, authenticity, 
                     theme, explanation, application, grade, reference)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    arabic or '', english or '', narrator or '', collection,
                    book or '', book_num, chapter or '', chapter_num,
                    hadith_number, volume_num, grade or 'Sahih', theme,
                    explanation, application, grade or '', reference or ''
                ))
                
                imported += 1
                
                # Progress updates
                if imported % 500 == 0:
                    print(f"✅ Imported {imported} hadiths...")
                    conn.commit()  # Periodic commits
                
            except Exception as e:
                error_msg = f"Row {i+1}: {str(e)}"
                errors.append(error_msg)
                skipped += 1
                
                if len(errors) <= 5:  # Show first 5 errors
                    print(f"⚠️  {error_msg}")
                
                continue
        
        # Final commit
        conn.commit()
        conn.close()
        
        print(f"\n🎉 IMPORT COMPLETED!")
        print(f"✅ Successfully imported: {imported}")
        print(f"⏭️  Skipped: {skipped}")
        if len(errors) > 5:
            print(f"⚠️  Total errors: {len(errors)}")
        
        # Show final statistics
        self.show_import_statistics()
    
    def get_field_value(self, data: dict, field_names: list) -> str:
        """Get field value from various possible field names"""
        for field in field_names:
            if field in data and data[field] is not None:
                return str(data[field]).strip()
        return ""
    
    def safe_int(self, value) -> int:
        """Safely convert to integer"""
        if value is None:
            return None
        try:
            return int(float(str(value)))  # Handle decimal strings
        except:
            return None
    
    def show_import_statistics(self):
        """Show comprehensive import statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM hadiths")
        total = cursor.fetchone()[0]
        
        # By collection
        cursor.execute("""
            SELECT collection, COUNT(*) 
            FROM hadiths 
            GROUP BY collection 
            ORDER BY COUNT(*) DESC
        """)
        collections = cursor.fetchall()
        
        # By theme
        cursor.execute("""
            SELECT theme, COUNT(*) 
            FROM hadiths 
            GROUP BY theme 
            ORDER BY COUNT(*) DESC
            LIMIT 15
        """)
        themes = cursor.fetchall()
        
        # Data completeness
        cursor.execute("SELECT COUNT(*) FROM hadiths WHERE arabic_text != ''")
        with_arabic = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hadiths WHERE english_translation != ''")
        with_english = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hadiths WHERE narrator != ''")
        with_narrator = cursor.fetchone()[0]
        
        print(f"\n📊 FINAL DATABASE STATISTICS")
        print("=" * 40)
        print(f"📚 Total Hadiths: {total:,}")
        
        print(f"\n📖 By Collection:")
        for collection, count in collections:
            print(f"   {collection}: {count:,}")
        
        print(f"\n🏷️  Top Themes:")
        for theme, count in themes[:10]:
            print(f"   {theme}: {count:,}")
        
        print(f"\n📊 Data Completeness:")
        print(f"   With Arabic: {with_arabic:,} ({with_arabic/total*100:.1f}%)")
        print(f"   With English: {with_english:,} ({with_english/total*100:.1f}%)")
        print(f"   With Narrator: {with_narrator:,} ({with_narrator/total*100:.1f}%)")
        
        conn.close()
        
        print(f"\n🎯 Your hadith verification app is now ready with {total:,} hadiths!")

def main():
    """Main function to run the complete import"""
    
    print("🚀 COMPLETE HADITH COLLECTION IMPORTER")
    print("=" * 45)
    
    # Find JSON files
    json_files = list(Path('.').glob('*.json'))
    
    if not json_files:
        print("❌ No JSON files found in current directory")
        return
    
    print("📂 Available JSON files:")
    for i, file in enumerate(json_files, 1):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"   {i}. {file.name} ({size_mb:.1f} MB)")
    
    # Let user select file
    try:
        choice = input(f"\nSelect file to import (1-{len(json_files)}) or press Enter for largest: ").strip()
        
        if not choice:
            # Select largest file by default
            selected_file = max(json_files, key=lambda f: f.stat().st_size)
        else:
            selected_file = json_files[int(choice) - 1]
            
        print(f"📖 Selected: {selected_file.name}")
        
        # Import
        importer = CompleteHadithImporter()
        importer.import_complete_collection(str(selected_file))
        
    except (ValueError, IndexError):
        print("❌ Invalid selection")
    except KeyboardInterrupt:
        print("\n👋 Import cancelled")

if __name__ == "__main__":
    main()