import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_processing import extract_skills, preprocess_text

class ResumeAnalyzer:
    """Analyze and rank resumes based on job descriptions"""
    
    def __init__(self):
        """Initialize the ResumeAnalyzer"""
        self.vectorizer = TfidfVectorizer()
    
    def compute_similarity(self, job_desc, resume_df):
        """
        Compute enhanced similarity scores between job description and resumes
        
        Args:
            job_desc (dict): Job description with Skills and Tools fields
            resume_df (DataFrame): DataFrame containing resume data
            
        Returns:
            numpy.ndarray: Array of similarity scores
        """
        # Extract skills from job description
        job_skills = extract_skills(str(job_desc['Skills']) + ' ' + str(job_desc['Tools']))
        
        similarity_scores = []
        for _, resume in resume_df.iterrows():
            # Extract skills from resume
            resume_skills = extract_skills(str(resume['Skills']) + ' ' + str(resume['Tools']))
            
            # Calculate skill matches for each category
            category_scores = []
            for category in job_skills:
                job_set = set(job_skills[category])
                resume_set = set(resume_skills[category])
                if job_set:
                    match_ratio = len(resume_set.intersection(job_set)) / len(job_set)
                    category_scores.append(match_ratio)
                else:
                    category_scores.append(0)
            
            # Calculate weighted skill score
            skill_score = np.mean(category_scores) if category_scores else 0
            
            # Calculate text similarity
            job_text = preprocess_text(str(job_desc['Skills']) + ' ' + str(job_desc['Tools']))
            resume_text = preprocess_text(
                str(resume['Skills']) + ' ' + 
                str(resume['Tools']) + ' ' + 
                str(resume['Certifications'])
            )
            
            try:
                tfidf_matrix = self.vectorizer.fit_transform([job_text, resume_text])
                text_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            except:
                text_similarity = 0
            
            # Combine scores (70% skill match, 30% text similarity)
            final_score = (0.7 * skill_score) + (0.3 * text_similarity)
            similarity_scores.append(final_score)
        
        return np.array(similarity_scores)
    
    def categorize_resumes(self, job_desc, resume_df):
        """
        Categorize resumes into high, medium, and low matches
        
        Args:
            job_desc (dict): Job description with Skills and Tools fields
            resume_df (DataFrame): DataFrame containing resume data
            
        Returns:
            dict: Dictionary with categorized resumes
        """
        similarity_scores = self.compute_similarity(job_desc, resume_df)
        
        all_resumes = []
        for i, score in enumerate(similarity_scores):
            all_resumes.append({
                'Resume ID': resume_df.iloc[i]['File Name'],
                'Skills': resume_df.iloc[i]['Skills'],
                'Tools': resume_df.iloc[i]['Tools'],
                'Certifications': resume_df.iloc[i]['Certifications'],
                'Score': score
            })
        
        # Sort all resumes by score
        all_resumes.sort(key=lambda x: x['Score'], reverse=True)
        
        # Categorize based on score thresholds
        high_matches = [r for r in all_resumes if r['Score'] >= 0.25]
        medium_matches = [r for r in all_resumes if 0.2 <= r['Score'] < 0.25]
        low_matches = [r for r in all_resumes if r['Score'] < 0.2]
        
        return {
            'top_3': all_resumes[:3],
            'high_matches': high_matches,
            'medium_matches': medium_matches,
            'low_matches': low_matches
        }
    
    def load_resume_data(self, jd_type):
        """
        Load the appropriate resume data based on the JD type
        
        Args:
            jd_type (str): Type of job description
            
        Returns:
            DataFrame: DataFrame containing resume data
        """
        try:
            if jd_type == 'java_developer':
                resume_df = pd.read_csv('Exctracted Resumes/resumes_analysis_outputJDJavaDeveloper.csv')
            elif jd_type == 'data_engineer':
                resume_df = pd.read_csv('Exctracted Resumes/resumes_analysis_output_JDDataEngineer.csv')
            else:
                # Try to load a generic file
                resume_df = pd.read_csv('resumes_analysis_output.csv')
            
            return resume_df
        except Exception as e:
            print(f"Error loading resume data for {jd_type}: {e}")
            return None
    
    def get_resume_details(self, resume_id, resume_df):
        """
        Get detailed information about a specific resume
        
        Args:
            resume_id (str): ID of the resume to retrieve
            resume_df (DataFrame): DataFrame containing resume data
            
        Returns:
            dict: Dictionary with resume details
        """
        try:
            resume = resume_df[resume_df['File Name'] == resume_id].iloc[0]
            return {
                'Resume ID': resume_id,
                'Skills': resume['Skills'],
                'Tools': resume['Tools'],
                'Certifications': resume['Certifications'],
                'Additional Info': resume.get('Additional Expertise', '')
            }
        except:
            return None