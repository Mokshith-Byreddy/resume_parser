from typing import List, Dict, Any
from collections import defaultdict

class JobRecommendationEngine:
    """
    AI-powered job recommendation system
    Analyzes resume skills and suggests matching job roles
    """
    
    JOB_CATEGORIES = {
        'Software Developer': {
            'required_skills': ['javascript', 'python', 'java', 'react', 'node.js', 'sql'],
            'weight': {'programming': 0.4, 'frameworks': 0.3, 'databases': 0.2, 'soft': 0.1},
            'salary_range': '$70,000 - $120,000',
            'growth_rate': 'High'
        },
        'Data Scientist': {
            'required_skills': ['python', 'machine learning', 'sql', 'pandas', 'numpy', 'analytics'],
            'weight': {'data': 0.5, 'programming': 0.3, 'databases': 0.1, 'soft': 0.1},
            'salary_range': '$80,000 - $140,000',
            'growth_rate': 'Very High'
        },
        'DevOps Engineer': {
            'required_skills': ['aws', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'terraform'],
            'weight': {'cloud': 0.5, 'programming': 0.2, 'frameworks': 0.2, 'soft': 0.1},
            'salary_range': '$85,000 - $130,000',
            'growth_rate': 'High'
        },
        'Frontend Developer': {
            'required_skills': ['react', 'javascript', 'html', 'css', 'typescript', 'vue'],
            'weight': {'frameworks': 0.4, 'programming': 0.4, 'soft': 0.2},
            'salary_range': '$65,000 - $110,000',
            'growth_rate': 'High'
        },
        'Backend Developer': {
            'required_skills': ['node.js', 'python', 'java', 'sql', 'mongodb', 'express'],
            'weight': {'programming': 0.4, 'frameworks': 0.3, 'databases': 0.2, 'soft': 0.1},
            'salary_range': '$70,000 - $115,000',
            'growth_rate': 'High'
        },
        'Product Manager': {
            'required_skills': ['project management', 'agile', 'scrum', 'leadership', 'analytics'],
            'weight': {'soft': 0.6, 'data': 0.2, 'frameworks': 0.1, 'programming': 0.1},
            'salary_range': '$90,000 - $150,000',
            'growth_rate': 'High'
        },
        'UI/UX Designer': {
            'required_skills': ['design', 'figma', 'adobe', 'user experience', 'prototyping'],
            'weight': {'soft': 0.5, 'frameworks': 0.3, 'programming': 0.2},
            'salary_range': '$60,000 - $100,000',
            'growth_rate': 'Medium'
        },
        'Machine Learning Engineer': {
            'required_skills': ['python', 'tensorflow', 'pytorch', 'machine learning', 'ai', 'data science'],
            'weight': {'data': 0.6, 'programming': 0.3, 'cloud': 0.1},
            'salary_range': '$95,000 - $160,000',
            'growth_rate': 'Very High'
        },
        'Full Stack Developer': {
            'required_skills': ['javascript', 'react', 'node.js', 'sql', 'python', 'html', 'css'],
            'weight': {'programming': 0.3, 'frameworks': 0.3, 'databases': 0.2, 'soft': 0.2},
            'salary_range': '$75,000 - $125,000',
            'growth_rate': 'High'
        },
        'Cloud Architect': {
            'required_skills': ['aws', 'azure', 'kubernetes', 'terraform', 'microservices', 'devops'],
            'weight': {'cloud': 0.6, 'programming': 0.2, 'soft': 0.2},
            'salary_range': '$110,000 - $180,000',
            'growth_rate': 'Very High'
        }
    }

    @classmethod
    def generate_recommendations(cls, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate job recommendations based on resume skills"""
        recommendations = []
        resume_skills = resume_data.get('skills', [])
        
        if not resume_skills:
            return recommendations

        for job_title, job_data in cls.JOB_CATEGORIES.items():
            # Calculate skill match
            matched_skills = [
                skill for skill in resume_skills
                if any(req_skill.lower() in skill.lower() or skill.lower() in req_skill.lower()
                       for req_skill in job_data['required_skills'])
            ]
            
            match_score = round((len(matched_skills) / len(job_data['required_skills'])) * 100)
            
            if match_score > 20:  # Only recommend if match score > 20%
                reasons = [
                    f"{len(matched_skills)} matching skills found",
                    f"{match_score}% skill compatibility",
                    f"Salary range: {job_data['salary_range']}",
                    f"Growth rate: {job_data['growth_rate']}"
                ]
                
                # Add specific skill matches
                if matched_skills:
                    reasons.append(f"Strong in: {', '.join(matched_skills[:3])}")

                recommendations.append({
                    'job_title': job_title,
                    'match_score': match_score,
                    'reasons': reasons,
                    'salary_range': job_data['salary_range'],
                    'growth_rate': job_data['growth_rate'],
                    'matched_skills': matched_skills
                })

        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:6]  # Return top 6 recommendations

    @classmethod
    def generate_feedback(cls, resume_data: Dict[str, Any], target_job_skills: List[str]) -> Dict[str, List[str]]:
        """Generate detailed feedback for resume improvement"""
        resume_skills = resume_data.get('skills', [])
        resume_experience = resume_data.get('experience', [])
        resume_education = resume_data.get('education', [])
        
        # Find matched and missing skills
        matched_skills = [
            skill for skill in resume_skills
            if any(job_skill.lower() in skill.lower() or skill.lower() in job_skill.lower()
                   for job_skill in target_job_skills)
        ]
        
        missing_skills = [
            job_skill for job_skill in target_job_skills
            if not any(skill.lower() in job_skill.lower() or job_skill.lower() in skill.lower()
                      for skill in resume_skills)
        ]

        # Generate strengths
        strengths = []
        if matched_skills:
            strengths.append(f"Strong technical skills in: {', '.join(matched_skills[:4])}")
        if len(resume_experience) > 0:
            strengths.append(f"{len(resume_experience)} relevant experience entries documented")
        if len(resume_education) > 0:
            strengths.append(f"{len(resume_education)} education qualifications listed")
        if len(resume_skills) > 10:
            strengths.append("Diverse skill set with broad technical knowledge")
        
        # Generate improvement areas
        improvements = [
            "Consider adding more quantified achievements and metrics",
            "Include specific project examples with technologies used",
            "Highlight leadership and collaboration experiences",
            "Add certifications relevant to your target role"
        ]
        
        if len(resume_experience) < 2:
            improvements.append("Expand experience section with more detailed descriptions")
        
        if not any('project' in exp.lower() for exp in resume_experience):
            improvements.append("Include personal or professional projects in your experience")

        # Generate recommendations
        recommendations = []
        if missing_skills:
            recommendations.append(f"Focus on developing skills in: {', '.join(missing_skills[:4])}")
        
        recommendations.extend([
            "Consider obtaining relevant industry certifications",
            "Build a portfolio showcasing your technical abilities",
            "Tailor resume keywords to match specific job descriptions",
            "Network with professionals in your target industry"
        ])
        
        # Add skill-specific recommendations
        skill_categories = cls._categorize_skills(resume_skills)
        if len(skill_categories.get('programming', [])) < 2:
            recommendations.append("Learn additional programming languages to increase versatility")
        if len(skill_categories.get('cloud', [])) == 0:
            recommendations.append("Consider learning cloud technologies (AWS, Azure, or GCP)")

        return {
            'strengths': strengths[:4],
            'improvements': improvements[:4],
            'missing_skills': missing_skills[:6],
            'recommendations': recommendations[:5]
        }

    @classmethod
    def _categorize_skills(cls, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different categories"""
        categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask'],
            'databases': ['sql', 'mongodb', 'postgresql', 'mysql'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'data': ['machine learning', 'data science', 'analytics'],
            'soft': ['leadership', 'communication', 'project management']
        }
        
        categorized = defaultdict(list)
        
        for skill in skills:
            skill_lower = skill.lower()
            for category, category_skills in categories.items():
                if any(cat_skill in skill_lower for cat_skill in category_skills):
                    categorized[category].append(skill)
                    break
        
        return dict(categorized)

    @classmethod
    def get_career_path_suggestions(cls, current_skills: List[str]) -> List[Dict[str, Any]]:
        """Suggest career progression paths based on current skills"""
        paths = []
        
        # Analyze current skill level
        skill_categories = cls._categorize_skills(current_skills)
        
        # Junior to Mid-level paths
        if len(current_skills) < 8:
            paths.append({
                'path': 'Junior to Mid-level Developer',
                'timeline': '1-2 years',
                'required_skills': ['Add 3-5 more technical skills', 'Gain project experience'],
                'salary_increase': '20-40%'
            })
        
        # Specialization paths
        if skill_categories.get('data'):
            paths.append({
                'path': 'Data Science Specialization',
                'timeline': '6-12 months',
                'required_skills': ['Advanced ML', 'Statistics', 'Domain expertise'],
                'salary_increase': '25-50%'
            })
        
        if skill_categories.get('cloud'):
            paths.append({
                'path': 'Cloud Architecture',
                'timeline': '1-2 years',
                'required_skills': ['Multi-cloud expertise', 'Security', 'Leadership'],
                'salary_increase': '30-60%'
            })
        
        return paths[:3]