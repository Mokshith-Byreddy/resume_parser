import PyPDF2
import re
import io
from typing import Dict, List, Any

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    @staticmethod
    def parse_resume(text: str, filename: str) -> Dict[str, Any]:
        """Parse resume text and extract structured information"""
        lines = text.lower().split('\n')
        
        # Extract email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text)
        email = email_match.group(0) if email_match else ''
        
        # Extract phone
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        phone = phone_match.group(0) if phone_match else ''
        
        # Extract name (heuristic approach)
        name_candidates = []
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if (len(line.split()) <= 4 and len(line) > 2 and 
                not '@' in line and not any(char.isdigit() for char in line) and
                not any(keyword in line for keyword in ['experience', 'education', 'skills', 'objective'])):
                name_candidates.append(line.title())
        
        name = name_candidates[0] if name_candidates else filename.replace('.pdf', '').replace('_', ' ').title()
        
        # Extract skills
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'html', 'css', 'typescript', 'sql', 'mongodb', 'postgresql', 'mysql',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'agile', 'scrum',
            'machine learning', 'ai', 'data science', 'analytics', 'tableau',
            'powerbi', 'excel', 'project management', 'leadership', 'communication',
            'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift',
            'django', 'flask', 'spring', 'laravel', 'express', 'next.js',
            'redis', 'elasticsearch', 'jenkins', 'terraform', 'pandas', 'numpy'
        ]
        
        skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill in text_lower:
                skills.append(skill)
        
        # Extract experience (simplified)
        experience = []
        experience_keywords = ['experience', 'work', 'employment', 'career', 'position']
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in experience_keywords):
                # Get next few lines as experience
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip() and len(lines[j].strip()) > 10:
                        experience.append(lines[j].strip().title())
                break
        
        # Extract education
        education = []
        education_keywords = ['education', 'university', 'college', 'degree', 'bachelor', 'master', 'phd']
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in education_keywords):
                # Get next few lines as education
                for j in range(i+1, min(i+3, len(lines))):
                    if lines[j].strip() and len(lines[j].strip()) > 5:
                        education.append(lines[j].strip().title())
                break
        
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'experience': experience[:3],  # Limit to 3 entries
            'education': education[:2]     # Limit to 2 entries
        }
    
    @staticmethod
    def calculate_match_score(resume_data: Dict[str, Any], job_skills: List[str]) -> float:
        """Calculate match score between resume and job requirements"""
        if not resume_data.get('skills') or not job_skills:
            return 0.0
        
        resume_skills = [skill.lower() for skill in resume_data['skills']]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matched_skills = []
        for resume_skill in resume_skills:
            for job_skill in job_skills_lower:
                if (resume_skill in job_skill or job_skill in resume_skill or
                    resume_skill == job_skill):
                    matched_skills.append(resume_skill)
                    break
        
        if len(job_skills_lower) == 0:
            return 0.0
        
        return (len(matched_skills) / len(job_skills_lower)) * 100
    
    @staticmethod
    def analyze_skill_gap(resume_data: Dict[str, Any], job_skills: List[str]) -> Dict[str, List[str]]:
        """Analyze skill gaps between resume and job requirements"""
        if not resume_data.get('skills'):
            return {'matched': [], 'missing': job_skills, 'match_percentage': 0}
        
        resume_skills = [skill.lower() for skill in resume_data['skills']]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matched = []
        missing = []
        
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            is_matched = False
            
            for resume_skill in resume_skills:
                if (resume_skill in job_skill_lower or job_skill_lower in resume_skill or
                    resume_skill == job_skill_lower):
                    matched.append(job_skill)
                    is_matched = True
                    break
            
            if not is_matched:
                missing.append(job_skill)
        
        match_percentage = (len(matched) / len(job_skills)) * 100 if job_skills else 0
        
        return {
            'matched': matched,
            'missing': missing,
            'match_percentage': match_percentage
        }