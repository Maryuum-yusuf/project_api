import re
import langdetect
from langdetect import detect, DetectorFactory
from googletrans import Translator
import numpy as np
from collections import Counter

# Set seed for consistent language detection
DetectorFactory.seed = 0

class SomaliLanguageDetector:
    def __init__(self):
        self.translator = Translator()
        
        # Somali language patterns and characteristics
        self.somali_patterns = {
            'common_words': [
                'waa', 'waxaa', 'waxay', 'waxuu', 'waxaad', 'waxaas',
                'ku', 'ka', 'la', 'si', 'oo', 'iyo', 'ama', 'hadday', 'haddii',
                'ma', 'miyaa', 'balse', 'laakiin', 'sidoo', 'sidoo kale',
                'dhammaan', 'qof', 'qofka', 'qofkaas', 'wax', 'waxa',
                'halkan', 'halkaas', 'halkii', 'halka', 'maanta', 'shalay', 
                'berri', 'maalin', 'habeen', 'subax', 'galab', 'caawa',
                'salaan', 'mahadsanid', 'fadlan', 'iga', 'sidee', 'tahay',
                'waan', 'waxaan', 'waxay', 'waxuu', 'waxaad', 'waxaas',
                'halkan', 'halkaas', 'halkii', 'halka', 'maanta', 'shalay',
                'berri', 'maalin', 'habeen', 'subax', 'galab', 'caawa',
                'salaan', 'mahadsanid', 'fadlan', 'iga', 'sidee', 'tahay',
                'waan', 'waxaan', 'waxay', 'waxuu', 'waxaad', 'waxaas',
                'halkan', 'halkaas', 'halkii', 'halka', 'maanta', 'shalay',
                'berri', 'maalin', 'habeen', 'subax', 'galab', 'caawa',
                'salaan', 'mahadsanid', 'fadlan', 'iga', 'sidee', 'tahay'
            ],
            'common_prefixes': ['waa', 'wax', 'qof', 'halk', 'maal', 'habe', 'sub', 'gal', 'caa', 'sal', 'maha', 'fad', 'iga'],
            'common_suffixes': ['aa', 'ay', 'uu', 'ad', 'as', 'ku', 'ka', 'la', 'si', 'oo', 'iyo', 'ama'],
            'somali_letters': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            'somali_diacritics': set('áéíóúñü')
        }
        
        # Common Somali phrases and greetings
        self.somali_phrases = [
            'salaan', 'salaan alaikum', 'wa alaikum salaam',
            'mahadsanid', 'mahadsanid', 'fadlan',
            'waa', 'waxaa', 'waxay', 'waxuu',
            'halkan', 'halkaas', 'maanta', 'shalay',
            'qof', 'qofka', 'qofkaas',
            'wax', 'waxa', 'waxay', 'waxuu'
        ]
    
    def detect_text_language(self, text):
        """
        Detect if the given text is Somali or not
        Returns: {'language': 'so' or 'other', 'confidence': float, 'method': str}
        """
        if not text or not text.strip():
            return {'language': 'unknown', 'confidence': 0.0, 'method': 'empty_text'}
        
        text = text.strip().lower()
        
        # Method 1: Use langdetect library
        try:
            detected_lang = detect(text)
            if detected_lang == 'so':
                return {'language': 'so', 'confidence': 0.9, 'method': 'langdetect'}
        except:
            pass
        
        # Method 2: Pattern matching for Somali words
        somali_word_count = 0
        total_words = len(text.split())
        
        if total_words > 0:
            words = text.split()
            for word in words:
                # Clean word (remove punctuation)
                clean_word = re.sub(r'[^\w\s]', '', word)
                if clean_word in self.somali_patterns['common_words']:
                    somali_word_count += 1
                elif any(clean_word.startswith(prefix) for prefix in self.somali_patterns['common_prefixes']):
                    somali_word_count += 0.5
                elif any(clean_word.endswith(suffix) for suffix in self.somali_patterns['common_suffixes']):
                    somali_word_count += 0.3
            
            somali_ratio = somali_word_count / total_words
            if somali_ratio > 0.2:  # Lowered threshold for better detection
                return {'language': 'so', 'confidence': min(somali_ratio, 0.8), 'method': 'pattern_matching'}
        
        # Method 3: Character frequency analysis
        somali_char_ratio = self._analyze_somali_characteristics(text)
        if somali_char_ratio > 0.6:
            return {'language': 'so', 'confidence': somali_char_ratio * 0.7, 'method': 'character_analysis'}
        
        # Method 4: Google Translate API (fallback)
        try:
            detected = self.translator.detect(text)
            if detected.lang == 'so':
                return {'language': 'so', 'confidence': detected.confidence, 'method': 'google_translate'}
        except:
            pass
        
        # If none of the methods detect Somali, it's likely not Somali
        return {'language': 'other', 'confidence': 0.8, 'method': 'combined_analysis'}
    
    def _analyze_somali_characteristics(self, text):
        """
        Analyze text for Somali language characteristics
        """
        if not text:
            return 0.0
        
        # Count Somali-specific patterns
        somali_indicators = 0
        total_indicators = 0
        
        # Check for common Somali word patterns
        for phrase in self.somali_phrases:
            if phrase in text.lower():
                somali_indicators += 1
            total_indicators += 1
        
        # Check for Somali grammar patterns
        somali_patterns = [
            r'\bwaa\b', r'\bwaxaa\b', r'\bwaxay\b', r'\bwaxuu\b',
            r'\bku\b', r'\bka\b', r'\bla\b', r'\bsi\b', r'\boo\b',
            r'\biyo\b', r'\bama\b', r'\bhadday\b', r'\bhaddii\b'
        ]
        
        for pattern in somali_patterns:
            if re.search(pattern, text.lower()):
                somali_indicators += 1
            total_indicators += 1
        
        # Check for Somali sentence structure
        if 'waa' in text.lower() and ('ku' in text.lower() or 'ka' in text.lower()):
            somali_indicators += 2
            total_indicators += 2
        
        if total_indicators == 0:
            return 0.0
        
        return somali_indicators / total_indicators
    
    def is_somali_text(self, text, confidence_threshold=0.5):
        """
        Simple method to check if text is Somali
        Returns: bool
        """
        result = self.detect_text_language(text)
        return result['language'] == 'so' and result['confidence'] >= confidence_threshold

# Create a global instance
somali_detector = SomaliLanguageDetector()
