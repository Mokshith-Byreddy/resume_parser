from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import json
from typing import List, Dict, Any, Tuple

class BERTSkillAnalyzer:
    """
    Advanced skill analysis using BERT embeddings for semantic understanding
    """
    
    def __init__(self):
        # Load pre-trained BERT model for sentence embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Predefined skill categories with semantic keywords
        self.skill_categories = {
            'Programming Languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 
                'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab'
            ],
            'Web Development': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 
                'flask', 'spring', 'laravel', 'bootstrap', 'tailwind', 'sass', 'webpack'
            ],
            'Data Science & AI': [
                'machine learning', 'deep learning', 'artificial intelligence', 'data science',
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
                'statistics', 'data analysis', 'data visualization', 'nlp', 'computer vision'
            ],
            'Cloud & DevOps': [
                'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'ci/cd',
                'terraform', 'ansible', 'linux', 'bash', 'git', 'github', 'gitlab'
            ],
            'Databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'oracle', 'sqlite', 'cassandra', 'neo4j', 'database design'
            ],
            'Mobile Development': [
                'android', 'ios', 'react native', 'flutter', 'xamarin', 'swift',
                'kotlin', 'mobile app development', 'app store', 'play store'
            ],
            'Soft Skills': [
                'leadership', 'communication', 'teamwork', 'project management',
                'problem solving', 'critical thinking', 'time management', 'agile', 'scrum'
            ]
        }
    
    def get_skill_embeddings(self, skills: List[str]) -> np.ndarray:
        """Generate BERT embeddings for a list of skills"""
        if not skills:
            return np.array([])
        
        # Clean and normalize skills
        cleaned_skills = [skill.lower().strip() for skill in skills if skill.strip()]
        
        if not cleaned_skills:
            return np.array([])
        
        # Generate embeddings
        embeddings = self.model.encode(cleaned_skills)
        return embeddings
    
    def categorize_skills_semantic(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills using semantic similarity with BERT"""
        if not skills:
            return {}
        
        skill_embeddings = self.get_skill_embeddings(skills)
        if skill_embeddings.size == 0:
            return {}
        
        categorized = {category: [] for category in self.skill_categories.keys()}
        
        # Get embeddings for category keywords
        category_embeddings = {}
        for category, keywords in self.skill_categories.items():
            category_embeddings[category] = self.model.encode(keywords)
        
        # Categorize each skill
        for i, skill in enumerate(skills):
            if not skill.strip():
                continue
                
            skill_embedding = skill_embeddings[i].reshape(1, -1)
            best_category = None
            best_similarity = 0
            
            for category, cat_embeddings in category_embeddings.items():
                # Calculate similarity with all keywords in category
                similarities = cosine_similarity(skill_embedding, cat_embeddings)
                max_similarity = np.max(similarities)
                
                if max_similarity > best_similarity and max_similarity > 0.3:  # Threshold
                    best_similarity = max_similarity
                    best_category = category
            
            if best_category:
                categorized[best_category].append(skill)
            else:
                # If no good match, put in a general category
                if 'Other' not in categorized:
                    categorized['Other'] = []
                categorized['Other'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def find_skill_gaps_semantic(self, candidate_skills: List[str], 
                                job_requirements: List[str]) -> Dict[str, Any]:
        """Find skill gaps using semantic similarity"""
        if not candidate_skills or not job_requirements:
            return {'matched': [], 'missing': job_requirements, 'similarity_scores': {}}
        
        candidate_embeddings = self.get_skill_embeddings(candidate_skills)
        job_embeddings = self.get_skill_embeddings(job_requirements)
        
        if candidate_embeddings.size == 0 or job_embeddings.size == 0:
            return {'matched': [], 'missing': job_requirements, 'similarity_scores': {}}
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(job_embeddings, candidate_embeddings)
        
        matched_skills = []
        missing_skills = []
        similarity_scores = {}
        
        threshold = 0.5  # Semantic similarity threshold
        
        for i, job_skill in enumerate(job_requirements):
            max_similarity = np.max(similarity_matrix[i])
            best_match_idx = np.argmax(similarity_matrix[i])
            
            similarity_scores[job_skill] = {
                'max_similarity': float(max_similarity),
                'best_match': candidate_skills[best_match_idx] if max_similarity > threshold else None
            }
            
            if max_similarity > threshold:
                matched_skills.append({
                    'job_skill': job_skill,
                    'candidate_skill': candidate_skills[best_match_idx],
                    'similarity': float(max_similarity)
                })
            else:
                missing_skills.append(job_skill)
        
        return {
            'matched': matched_skills,
            'missing': missing_skills,
            'similarity_scores': similarity_scores
        }
    
    def cluster_skills(self, skills: List[str], n_clusters: int = 5) -> Dict[str, Any]:
        """Cluster skills using BERT embeddings and K-means"""
        if not skills or len(skills) < 2:
            return {'clusters': [], 'labels': []}
        
        embeddings = self.get_skill_embeddings(skills)
        if embeddings.size == 0:
            return {'clusters': [], 'labels': []}
        
        # Adjust number of clusters if we have fewer skills
        n_clusters = min(n_clusters, len(skills))
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        # Group skills by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(skills[i])
        
        # Convert to list format
        cluster_list = []
        for cluster_id, cluster_skills in clusters.items():
            cluster_list.append({
                'id': int(cluster_id),
                'skills': cluster_skills,
                'size': len(cluster_skills)
            })
        
        return {
            'clusters': cluster_list,
            'labels': cluster_labels.tolist()
        }
    
    def get_skill_recommendations(self, current_skills: List[str], 
                                 target_role: str = None) -> List[Dict[str, Any]]:
        """Get skill recommendations based on current skills and target role"""
        if not current_skills:
            return []
        
        # Categorize current skills
        categorized = self.categorize_skills_semantic(current_skills)
        
        recommendations = []
        
        # Role-specific recommendations
        role_skills = {
            'software developer': [
                'git version control', 'unit testing', 'code review', 'debugging',
                'software architecture', 'design patterns', 'api development'
            ],
            'data scientist': [
                'statistical analysis', 'data visualization', 'feature engineering',
                'model evaluation', 'big data', 'sql optimization', 'a/b testing'
            ],
            'devops engineer': [
                'infrastructure as code', 'monitoring', 'logging', 'security',
                'automation', 'container orchestration', 'cloud architecture'
            ],
            'frontend developer': [
                'responsive design', 'cross-browser compatibility', 'performance optimization',
                'accessibility', 'state management', 'testing frameworks'
            ]
        }
        
        if target_role and target_role.lower() in role_skills:
            role_specific = role_skills[target_role.lower()]
            current_embeddings = self.get_skill_embeddings(current_skills)
            role_embeddings = self.get_skill_embeddings(role_specific)
            
            if current_embeddings.size > 0 and role_embeddings.size > 0:
                # Find skills not already possessed
                similarity_matrix = cosine_similarity(role_embeddings, current_embeddings)
                
                for i, skill in enumerate(role_specific):
                    max_similarity = np.max(similarity_matrix[i])
                    if max_similarity < 0.5:  # Not already possessed
                        recommendations.append({
                            'skill': skill,
                            'category': 'Role-specific',
                            'priority': 'high',
                            'reason': f'Essential for {target_role} role'
                        })
        
        # General recommendations based on current skill gaps
        for category, skills in categorized.items():
            if len(skills) < 3:  # If weak in this category
                category_skills = self.skill_categories.get(category, [])
                for skill in category_skills[:2]:  # Top 2 recommendations
                    if skill not in [s.lower() for s in current_skills]:
                        recommendations.append({
                            'skill': skill,
                            'category': category,
                            'priority': 'medium',
                            'reason': f'Strengthen {category} skills'
                        })
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def calculate_skill_strength_score(self, skills: List[str]) -> Dict[str, float]:
        """Calculate strength scores for different skill categories"""
        if not skills:
            return {}
        
        categorized = self.categorize_skills_semantic(skills)
        scores = {}
        
        # Calculate scores based on number of skills and their semantic diversity
        for category, category_skills in categorized.items():
            if not category_skills:
                scores[category] = 0.0
                continue
            
            # Base score from number of skills
            base_score = min(len(category_skills) / 5.0, 1.0) * 70  # Max 70 from quantity
            
            # Diversity bonus - check semantic diversity within category
            if len(category_skills) > 1:
                embeddings = self.get_skill_embeddings(category_skills)
                if embeddings.size > 0:
                    # Calculate average pairwise distance
                    similarity_matrix = cosine_similarity(embeddings)
                    # Get upper triangle (excluding diagonal)
                    upper_triangle = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]
                    avg_similarity = np.mean(upper_triangle) if len(upper_triangle) > 0 else 0
                    diversity_score = (1 - avg_similarity) * 30  # Max 30 from diversity
                    base_score += diversity_score
            
            scores[category] = min(base_score, 100.0)  # Cap at 100
        
        return scores