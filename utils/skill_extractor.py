import re
from typing import List, Dict

class SkillExtractor:
    # Predefined skill categories and keywords
    SKILL_CATEGORIES = {
        'programming': [
            'javascript', 'python', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 
            'rust', 'kotlin', 'swift', 'scala', 'r', 'matlab', 'typescript'
        ],
        'frameworks': [
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
            'spring', 'laravel', 'rails', 'next.js', 'nuxt.js', 'svelte'
        ],
        'databases': [
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'sqlite', 'cassandra', 'dynamodb'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'jenkins', 'ci/cd', 'devops', 'microservices'
        ],
        'data': [
            'machine learning', 'data science', 'analytics', 'tableau', 'powerbi',
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'
        ],
        'soft': [
            'leadership', 'communication', 'project management', 'agile', 'scrum',
            'teamwork', 'problem solving', 'critical thinking'
        ]
    }

    @classmethod
    def extract_skills_from_jd(cls, job_description: str) -> List[str]:
        """Extract skills from job description text"""
        text = job_description.lower()
        extracted_skills = []
        
        # Extract skills from all categories
        for category, skills in cls.SKILL_CATEGORIES.items():
            for skill in skills:
                if skill.lower() in text:
                    extracted_skills.append(skill)
        
        # Extract years of experience requirements
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(of\s*)?experience',
            r'(\d+)\+?\s*year\s*experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                years = match[0] if isinstance(match, tuple) else match
                extracted_skills.append(f"{years}+ years experience")
                break  # Only add one experience requirement
        
        # Extract education requirements
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'certification', 'diploma']
        for keyword in education_keywords:
            if keyword in text:
                extracted_skills.append(keyword)
        
        # Extract specific technologies mentioned
        tech_patterns = [
            r'\b(react\.js|reactjs)\b',
            r'\b(node\.js|nodejs)\b',
            r'\b(vue\.js|vuejs)\b',
            r'\b(next\.js|nextjs)\b',
            r'\b(express\.js|expressjs)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                extracted_skills.append(match)
        
        return list(set(extracted_skills))  # Remove duplicates
    
    @classmethod
    def categorize_skills(cls, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different categories"""
        categorized = {
            'programming': [],
            'frameworks': [],
            'databases': [],
            'cloud': [],
            'data': [],
            'soft': [],
            'other': []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized_flag = False
            
            for category, category_skills in cls.SKILL_CATEGORIES.items():
                if any(cat_skill.lower() in skill_lower or skill_lower in cat_skill.lower() 
                       for cat_skill in category_skills):
                    categorized[category].append(skill)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['other'].append(skill)
        
        return categorized
    
    @classmethod
    def get_skill_importance_score(cls, skill: str, job_description: str) -> float:
        """Calculate importance score of a skill based on frequency in JD"""
        text = job_description.lower()
        skill_lower = skill.lower()
        
        # Count occurrences
        count = text.count(skill_lower)
        
        # Check if skill appears in important sections
        important_sections = ['requirements', 'qualifications', 'must have', 'essential']
        importance_bonus = 0
        
        for section in important_sections:
            if section in text:
                section_start = text.find(section)
                section_text = text[section_start:section_start + 500]  # Next 500 chars
                if skill_lower in section_text:
                    importance_bonus += 2
        
        return min(count + importance_bonus, 10)  # Cap at 10