import os
import numpy as np
import pandas as pd
import tempfile
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from io import BytesIO, StringIO
from docx import Document
from utils.text_processing import extract_skills, preprocess_text

class ResumeAnalyzer:
    """Analyze and rank resumes based on job descriptions"""
    
    def __init__(self):
        """Initialize the ResumeAnalyzer"""
        self.vectorizer = TfidfVectorizer()
        # Get the base directory (where your app is running)
        self.base_dir = os.getcwd()
        
        # Define the specific path to the Extracted Resumes folder
        self.resume_dir = os.path.join(self.base_dir, "Data", "Extracted Resumes")
        
        # Fallback directories in case primary directory isn't found
        self.fallback_dirs = [
            os.path.join(self.base_dir, "Data", "Extracted Resumes"),
            os.path.join(self.base_dir, "Data", "Exctracted Resumes"),  # Include typo version
            os.path.join(self.base_dir, "jd_optim_OOP_implement(vasu)", "Data", "Extracted Resumes"),
            os.path.join(self.base_dir, "jd_optim_OOP_implement(vasu)", "Data", "Exctracted Resumes"),
            os.path.join(self.base_dir, "Data"),
            os.path.join(self.base_dir, "jd_optim_OOP_implement(vasu)", "Data"),
        ]
    
    def compute_similarity(self, job_desc, resume_df):
        """
        Compute enhanced similarity scores between job description and resumes
        
        Args:
            job_desc (dict): Job description with Skills and Tools fields
            resume_df (DataFrame): DataFrame containing resume data
            
        Returns:
            numpy.ndarray: Array of similarity scores
        """
        # Check if job_desc is valid
        if not isinstance(job_desc, (dict, pd.Series)) or 'Skills' not in job_desc:
            job_skills = {'programming_languages': [], 'frameworks': [], 'databases': [], 'cloud': [], 'tools': []}
        else:
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
            job_text = preprocess_text(str(job_desc.get('Skills', '')) + ' ' + str(job_desc.get('Tools', '')))
            resume_text = preprocess_text(
                str(resume['Skills']) + ' ' + 
                str(resume['Tools']) + ' ' + 
                str(resume.get('Certifications', ''))
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
        # Check if inputs are valid
        if resume_df is None or len(resume_df) == 0:
            empty_result = {
                'top_3': [],
                'high_matches': [],
                'medium_matches': [],
                'low_matches': []
            }
            return empty_result
            
        # Compute similarity scores
        try:
            similarity_scores = self.compute_similarity(job_desc, resume_df)
        except Exception as e:
            # Return empty results in case of error
            empty_result = {
                'top_3': [],
                'high_matches': [],
                'medium_matches': [],
                'low_matches': []
            }
            return empty_result
        
        all_resumes = []
        for i, score in enumerate(similarity_scores):
            # Make sure we don't go out of bounds
            if i < len(resume_df):
                resume_row = resume_df.iloc[i]
                all_resumes.append({
                    'Resume ID': resume_row.get('File Name', f"Resume_{i+1}"),
                    'Skills': resume_row.get('Skills', ''),
                    'Tools': resume_row.get('Tools', ''),
                    'Certifications': resume_row.get('Certifications', ''),
                    'Score': float(score)
                })
        
        # Sort all resumes by score
        all_resumes.sort(key=lambda x: x['Score'], reverse=True)
        
        # Categorize based on score thresholds
        high_matches = [r for r in all_resumes if r['Score'] >= 0.25]
        medium_matches = [r for r in all_resumes if 0.2 <= r['Score'] < 0.25]
        low_matches = [r for r in all_resumes if r['Score'] < 0.2]
        
        return {
            'top_3': all_resumes[:3] if len(all_resumes) >= 3 else all_resumes,
            'high_matches': high_matches,
            'medium_matches': medium_matches,
            'low_matches': low_matches
        }
    
    def _find_resume_file(self, file_name):
        """
        Helper method to find a resume file across multiple possible directories
        
        Args:
            file_name (str): Name of the file to find
            
        Returns:
            str or None: Full path to the file if found, None otherwise
        """
        # Try all potential directories
        for directory in self.fallback_dirs:
            if os.path.exists(directory):
                file_path = os.path.join(directory, file_name)
                if os.path.exists(file_path):
                    return file_path
                
        # If we reach here, file wasn't found
        return None
    
    def find_default_resume_file(self, jd_type):
        """
        Find the default resume file based on JD type
        
        Args:
            jd_type (str): Type of job description
            
        Returns:
            str or None: Path to the default resume file if found, None otherwise
        """
        # Map of JD types to potential file names (in order of preference)
        default_file_map = {
            "java_developer": [
                "resumes_analysis_outputJDJavaDeveloper.csv",
                "java_resumes.csv",
                "resumes_analysis_output.csv"
            ],
            "data_engineer": [
                "resumes_analysis_output_JDPrincipalSoftwareEngineer.csv", 
                "data_resumes.csv",
                "resumes_analysis_output.csv"
            ],
            "general": [
                "resumes_analysis_output.csv",
                "Resume_Dataset_Output.csv",
                "resumes_analysis_output2.csv"
            ]
        }
        
        # Get list of potential file names
        file_names = default_file_map.get(jd_type, ["resumes_analysis_output.csv"])
        
        # Try each file name in order
        for file_name in file_names:
            file_path = self._find_resume_file(file_name)
            if file_path:
                return file_path
                
        # If no specific file was found, try to find ANY resume CSV
        for directory in self.fallback_dirs:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if file.endswith('.csv') and ('resume' in file.lower() or 'analysis' in file.lower()):
                        return os.path.join(directory, file)
        
        # Perform broader search as a last resort
        for root, _, files in os.walk(os.getcwd()):
            csv_files = [f for f in files if f.endswith('.csv')]
            for file in csv_files:
                if 'resume' in file.lower() or 'analysis' in file.lower():
                    return os.path.join(root, file)
        
        return None
    
    def process_resume_pool(self, uploaded_files):
        """
        Process a batch of uploaded resume files and return a DataFrame
        
        Args:
            uploaded_files (list): List of uploaded resume files
            
        Returns:
            DataFrame: DataFrame containing processed resume data
        """
        processed_resumes = []
        csv_dataframes = []
        
        # First pass: Process each file
        for uploaded_file in uploaded_files:
            try:
                if uploaded_file.name.endswith(".docx"):
                    # Process DOCX as individual resume
                    resume_data = self.analyze_uploaded_resume(uploaded_file)
                    if resume_data is not None:
                        processed_resumes.append(resume_data)
                
                elif uploaded_file.name.endswith(".csv"):
                    # Check if CSV is a single resume or a dataset
                    resume_data = self._analyze_csv_resume(uploaded_file)
                    
                    if resume_data is not None:
                        # This is a single resume in CSV format
                        processed_resumes.append(resume_data)
                    else:
                        # This might be a multi-resume CSV dataset
                        try:
                            df = pd.read_csv(BytesIO(uploaded_file.getvalue()))
                            
                            # Check if it has the required columns
                            required_cols = ['File Name', 'Skills', 'Tools']
                            missing_cols = [col for col in required_cols if col not in df.columns]
                            
                            if missing_cols:
                                # Try lowercase column names
                                lowercase_cols = {col.lower(): col for col in df.columns}
                                renamed_cols = {}
                                
                                for required in required_cols:
                                    if required.lower() in lowercase_cols:
                                        renamed_cols[lowercase_cols[required.lower()]] = required
                                
                                if renamed_cols:
                                    df = df.rename(columns=renamed_cols)
                                    
                                    # Check again for missing columns
                                    missing_cols = [col for col in required_cols if col not in df.columns]
                            
                            if not missing_cols:
                                # This is a valid resume dataset
                                csv_dataframes.append(df)
                        except Exception:
                            pass
            except Exception:
                pass
        
        # Second pass: Combine results
        if csv_dataframes:
            # If we have CSV datasets, use those first
            combined_df = pd.concat(csv_dataframes, ignore_index=True)
            
            # Add any individually processed resumes
            if processed_resumes:
                individual_df = pd.DataFrame(processed_resumes)
                combined_df = pd.concat([combined_df, individual_df], ignore_index=True)
            
            # Ensure all required columns exist
            for col in ['File Name', 'Skills', 'Tools', 'Certifications']:
                if col not in combined_df.columns:
                    combined_df[col] = ""
            
            return combined_df
            
        elif processed_resumes:
            # If we only have individually processed resumes
            return pd.DataFrame(processed_resumes)
        
        # No valid data
        return None
        
    def analyze_uploaded_resume(self, uploaded_file):
        """
        Analyze a user-uploaded resume (.docx) and extract the information
        
        Args:
            uploaded_file (UploadedFile): The uploaded resume file
            
        Returns:
            dict: Dictionary with extracted resume details
        """
        try:
            # Process based on file extension
            if uploaded_file.name.endswith('.docx'):
                return self._analyze_docx_resume(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                return self._analyze_csv_resume(uploaded_file)
            else:
                return None
        except Exception:
            return None
    
    def _analyze_docx_resume(self, uploaded_file):
        """
        Analyze a DOCX resume file
        
        Args:
            uploaded_file (UploadedFile): The uploaded DOCX file
            
        Returns:
            dict: Dictionary with extracted resume details
        """
        try:
            # Get file content
            docx_bytes = uploaded_file.getvalue()
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(docx_bytes)
                temp_path = tmp.name
            
            try:
                # Load the document
                doc = Document(temp_path)
                
                # Extract text from paragraphs
                paragraphs = []
                for para in doc.paragraphs:
                    if para.text.strip():  # Only include non-empty paragraphs
                        paragraphs.append(para.text)
                
                resume_text = "\n".join(paragraphs)
                
                # Extract information
                skills_map = extract_skills(resume_text)
                skills_str = ", ".join([item for sublist in skills_map.values() for item in sublist])
                
                # Detect tools
                tools_keywords = [
                    'git', 'docker', 'kubernetes', 'jenkins', 'jira', 
                    'confluence', 'aws', 'azure', 'vs code', 'intellij',
                    'eclipse', 'idea', 'visual studio', 'vscode', 'maven',
                    'gradle', 'npm', 'yarn', 'webpack', 'jupyter'
                ]
                
                detected_tools = []
                for tool in tools_keywords:
                    if tool.lower() in resume_text.lower():
                        detected_tools.append(tool)
                
                # Detect certifications
                cert_keywords = [
                    'certified', 'certification', 'certificate', 'aws', 'azure', 
                    'google', 'professional', 'associate', 'expert', 'oracle',
                    'microsoft', 'java', 'python', 'scrum', 'pmp'
                ]
                
                certification_text = ""
                for line in paragraphs:
                    if any(kw.lower() in line.lower() for kw in cert_keywords):
                        certification_text += line + "\n"
                
                if not certification_text:
                    certification_text = "None specified"
                
                return {
                    'File Name': uploaded_file.name,
                    'Skills': skills_str or "General technical skills",
                    'Tools': ", ".join(detected_tools) or "Standard development tools",
                    'Certifications': certification_text
                }
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception:
            return None
    
    def _analyze_csv_resume(self, uploaded_file):
        """
        Process a CSV resume file
        
        Args:
            uploaded_file (UploadedFile): The uploaded CSV file
            
        Returns:
            dict: Dictionary with extracted resume details or None if CSV has multiple rows
        """
        try:
            # Read CSV content
            csv_content = uploaded_file.getvalue().decode('utf-8')
            
            # Parse CSV
            import csv
            
            # First check if this is a multi-row CSV (resume dataset) or single resume
            csv_rows = list(csv.reader(StringIO(csv_content)))
            
            if len(csv_rows) <= 2:  # Header + single data row
                # This is likely a single resume in CSV format
                if len(csv_rows) == 2:
                    # Has header and one data row
                    header = csv_rows[0]
                    data = csv_rows[1]
                    
                    # Create a dictionary of header->value
                    resume_data = {header[i]: data[i] for i in range(min(len(header), len(data)))}
                    
                    # Extract required fields or use defaults
                    return {
                        'File Name': uploaded_file.name,
                        'Skills': resume_data.get('Skills', resume_data.get('skills', '')),
                        'Tools': resume_data.get('Tools', resume_data.get('tools', '')),
                        'Certifications': resume_data.get('Certifications', resume_data.get('certifications', ''))
                    }
                else:
                    # No data rows, just header
                    return None
            else:
                # This is a multi-row CSV, likely a resume dataset
                # Return None to indicate this should be treated as a full dataset not a single resume
                return None
        except Exception:
            return None