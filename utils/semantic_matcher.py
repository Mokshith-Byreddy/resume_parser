import re
from typing import List, Dict, Tuple
from collections import Counter
import math

class SemanticMatcher:
    """
    Simulated BERT-based semantic matching
    In production, this would integrate with actual BERT models or APIs
    """
    
    COMMON_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Synonym mapping for better semantic understanding
    SYNONYMS = {
        'javascript': ['js', 'ecmascript', 'node'],
        'python': ['py', 'python3'],
        'machine learning': ['ml', 'artificial intelligence', 'ai'],
        'database': ['db', 'data storage', 'sql'],
        'frontend': ['front-end', 'client-side', 'ui'],
        'backend': ['back-end', 'server-side', 'api'],
        'experience': ['years', 'background', 'expertise'],
        'development': ['dev', 'programming', 'coding'],
        'management': ['mgmt', 'leadership', 'supervision']
    }

    @classmethod
    def preprocess_text(cls, text: str) -> List[str]:
        """Preprocess text by cleaning and tokenizing"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = text.split()
        
        # Remove common words and short words
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in cls.COMMON_WORDS
        ]
        
        return filtered_words

    @classmethod
    def expand_with_synonyms(cls, words: List[str]) -> List[str]:
        """Expand word list with synonyms"""
        expanded = words.copy()
        
        for word in words:
            for key, synonyms in cls.SYNONYMS.items():
                if word in synonyms or word == key:
                    expanded.extend([key] + synonyms)
        
        return list(set(expanded))  # Remove duplicates

    @classmethod
    def calculate_cosine_similarity(cls, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        words1 = cls.preprocess_text(text1)
        words2 = cls.preprocess_text(text2)
        
        # Expand with synonyms for better matching
        words1 = cls.expand_with_synonyms(words1)
        words2 = cls.expand_with_synonyms(words2)
        
        # Create word frequency vectors
        all_words = list(set(words1 + words2))
        
        if not all_words:
            return 0.0
        
        vector1 = [words1.count(word) for word in all_words]
        vector2 = [words2.count(word) for word in all_words]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(a * a for a in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        similarity = dot_product / (magnitude1 * magnitude2)
        return round(similarity * 100, 2)

    @classmethod
    def find_key_matches(cls, text1: str, text2: str) -> List[str]:
        """Find key matching terms between two texts"""
        words1 = set(cls.preprocess_text(text1))
        words2 = set(cls.preprocess_text(text2))
        
        # Direct matches
        matches = words1.intersection(words2)
        
        # Synonym matches
        synonym_matches = set()
        for word1 in words1:
            for word2 in words2:
                for key, synonyms in cls.SYNONYMS.items():
                    if ((word1 in synonyms or word1 == key) and 
                        (word2 in synonyms or word2 == key)):
                        synonym_matches.add(key)
        
        all_matches = matches.union(synonym_matches)
        
        # Filter out very common terms and sort by length (longer terms first)
        filtered_matches = [
            match for match in all_matches 
            if len(match) > 3 and match not in cls.COMMON_WORDS
        ]
        
        return sorted(filtered_matches, key=len, reverse=True)[:10]

    @classmethod
    def generate_semantic_insights(cls, similarity_score: float, key_matches: List[str]) -> List[str]:
        """Generate insights based on semantic analysis"""
        insights = []
        
        if similarity_score > 80:
            insights.append("Excellent semantic match - strong alignment with job requirements")
            insights.append("Candidate demonstrates comprehensive understanding of the role")
        elif similarity_score > 60:
            insights.append("Good semantic match - candidate shows relevant experience")
            insights.append("Strong potential for success in this position")
        elif similarity_score > 40:
            insights.append("Moderate match - some relevant experience but gaps exist")
            insights.append("May require additional training or development")
        else:
            insights.append("Limited match - significant skill gaps identified")
            insights.append("Consider for entry-level positions or with extensive training")
        
        if len(key_matches) > 5:
            insights.append(f"Strong keyword alignment with {len(key_matches)} matching terms")
        elif len(key_matches) > 2:
            insights.append(f"Moderate keyword alignment with {len(key_matches)} matching terms")
        else:
            insights.append("Limited keyword alignment - consider resume optimization")
        
        return insights

    @classmethod
    def semantic_match(cls, resume_text: str, job_description: str) -> Dict[str, any]:
        """
        Perform semantic matching between resume and job description
        Returns similarity score, key matches, and insights
        """
        similarity_score = cls.calculate_cosine_similarity(resume_text, job_description)
        key_matches = cls.find_key_matches(resume_text, job_description)
        insights = cls.generate_semantic_insights(similarity_score, key_matches)
        
        return {
            'similarity_score': similarity_score,
            'key_matches': key_matches,
            'semantic_insights': insights,
            'match_quality': cls._get_match_quality(similarity_score)
        }
    
    @classmethod
    def _get_match_quality(cls, score: float) -> str:
        """Get qualitative assessment of match quality"""
        if score > 80:
            return "Excellent"
        elif score > 60:
            return "Good"
        elif score > 40:
            return "Fair"
        else:
            return "Poor"

    @classmethod
    def batch_semantic_analysis(cls, resumes: List[str], job_description: str) -> List[Dict[str, any]]:
        """Perform semantic analysis on multiple resumes"""
        results = []
        
        for i, resume_text in enumerate(resumes):
            result = cls.semantic_match(resume_text, job_description)
            result['resume_index'] = i
            results.append(result)
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results