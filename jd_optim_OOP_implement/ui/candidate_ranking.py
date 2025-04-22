import os
import streamlit as st
import pandas as pd
import numpy as np
import tempfile
import re
from docx import Document
from ui.common import display_section_header, display_subsection_header, display_info_message, display_warning_message, display_success_message
from utils.visualization import create_distribution_chart, create_radar_chart
from models.resume_analyzer import ResumeAnalyzer

def render_candidate_ranking_page(services):
    """
    Render the candidate ranking page with enhanced resume pool management
    
    Args:
        services (dict): Dictionary of shared services
    """
    # Unpack services
    logger = services.get('logger')
    analyzer = services.get('analyzer')
    agent = services.get('agent')
    state_manager = services.get('state_manager')
    
    display_section_header("🎯 Resume Ranking")
    
    # Check if we have a specifically selected JD for candidate ranking
    jd_repository = state_manager.get('jd_repository', {})
    candidate_ranking_jd = jd_repository.get('for_candidate_ranking')
    
    # Initialize variables to prevent UnboundLocalError
    jd_content = None
    jd_source_name = None
    jd_unique_id = None
    jd_version_type = 'unknown'  # Default value
    
    # If we have a specific JD selection for candidate ranking, use it
    if candidate_ranking_jd and candidate_ranking_jd.get('content'):
        jd_content = candidate_ranking_jd.get('content')
        jd_source_name = candidate_ranking_jd.get('source')
        jd_version_type = candidate_ranking_jd.get('version_type', 'unknown')
        jd_unique_id = jd_repository.get('unique_id')
    else:
        # Fall back to the default JD content from repository
        jd_content, jd_source_name, jd_unique_id = state_manager.get_jd_content()
        
        # Determine version type based on repository state
        if jd_repository.get('final_version') == jd_content:
            jd_version_type = 'final'
        elif jd_repository.get('original') == jd_content:
            jd_version_type = 'original'
        elif state_manager.get('client_enhanced_jd') == jd_content:
            jd_version_type = 'client_enhanced'
        else:
            jd_version_type = 'enhanced'
    
    # Create resume analyzer
    resume_analyzer = ResumeAnalyzer()
    
    # --- Create Layout Columns ---
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        display_subsection_header("Select Position")
        
        if not jd_content:
            # No active JD, need to select one first
            st.warning("No active job description found.")
            st.info("Please select a job description in the JD Optimization tab first.")
            
            # Show button to navigate to JD Optimization
            if st.button("Go to JD Optimization", key="goto_jd_opt"):
                state_manager.set('active_tab', "JD Optimization")
                st.rerun()
            
            return
        
        # Show active job description info - enhance display with version type info
        version_badges = {
            'final': "🏆 Final Enhanced",
            'enhanced': "⭐ Enhanced",
            'original': "📄 Original",
            'client_enhanced': "👥 Client Enhanced",
            'unknown': "📄"
        }
        
        badge = version_badges.get(jd_version_type, "📄")
        
        st.success(f"Using job description: {badge} {jd_source_name}")
        
        # Show JD preview button
        with st.expander("Show Job Description Content", expanded=False):
            st.text_area(
                "JD Content",
                jd_content,
                height=250,
                disabled=True,
                key="ranking_jd_content"
            )
        
        # Detect job type from repository or use default
        jd_type = jd_repository.get('JD_Type', "general")
        if not jd_type:
            jd_type = detect_jd_type(jd_source_name) if jd_source_name else "general"
        
        st.markdown(f"**Resume Pool:** {jd_type.replace('_', ' ').title()}")
        
        # --- Resume Pool Selection ---
        display_subsection_header("Resume Pools")
        
        # Get resume repository
        resume_repository = state_manager.get('resume_repository', {})
        
        # Initialize resume_pools if empty
        if not resume_repository.get('pools'):
            resume_repository['pools'] = []
            state_manager.set('resume_repository', resume_repository)
        
        # Add generic options along with any user-uploaded pools
        generic_options = ["General", "Data Engineer", "Java Developer"]
        user_pools = [pool["pool_name"] for pool in resume_repository.get('pools', [])]
        
        pool_options = ["(Auto Selection)"] + user_pools + generic_options + ["Upload New Resume Pool"]
        selected_pool_option = st.selectbox(
            "Select Resume Pool Manually (Optional)", 
            pool_options,
            key="resume_pool_selector"
        )
        
        # Handle resume pool selection
        resume_df = handle_resume_pool_selection(selected_pool_option, resume_analyzer, jd_type, state_manager)
        if resume_df is None:
            st.warning("No resume data available. Please select or upload a valid resume pool.")
            return
    
    # Analyze button
    if st.button('🔍 Analyze Resumes', type="primary", key="analyze_resume_btn"):
        with st.spinner('Analyzing resumes...'):
            try:
                # Get job description as dict/Series for analysis
                skills = extract_skills_from_text(jd_content)
                tools = extract_tools_from_text(jd_content)
                
                st.info(f"Analyzing job description: {jd_source_name}")
                st.info(f"Found skills: {skills}")
                st.info(f"Found tools: {tools}")
                
                job_desc = pd.Series({
                    'File Name': jd_source_name,
                    'JD_Type': jd_type,
                    'Skills': skills,
                    'Tools': tools
                })
                
                # Check resume data
                if resume_df is None or len(resume_df) == 0:
                    st.error("No resume data available to analyze")
                    return
                    
                st.info(f"Processing {len(resume_df)} resumes")
                
                # Create placeholder for results
                placeholder = st.empty()
                placeholder.info("Starting analysis...")
                
                # Manually create analysis results
                all_resumes = []
                for i, row in resume_df.iterrows():
                    # Simple scoring algorithm
                    resume_skills = str(row.get('Skills', ''))
                    resume_tools = str(row.get('Tools', ''))
                    
                    # Direct matching for demonstration
                    skill_matches = 0
                    if skills and resume_skills:
                        for skill in skills.split(', '):
                            if skill.lower() in resume_skills.lower():
                                skill_matches += 1
                    
                    tool_matches = 0
                    if tools and resume_tools:
                        for tool in tools.split(', '):
                            if tool.lower() in resume_tools.lower():
                                tool_matches += 1
                    
                    # Calculate score (simple version)
                    skill_count = len(skills.split(', ')) if skills else 1
                    tool_count = len(tools.split(', ')) if tools else 1
                    
                    max_skills = max(1, skill_count)
                    max_tools = max(1, tool_count)
                    
                    skill_score = skill_matches / max_skills
                    tool_score = tool_matches / max_tools
                    
                    # Combined score
                    score = 0.7 * skill_score + 0.3 * tool_score
                    
                    # Add to results
                    all_resumes.append({
                        'Resume ID': row.get('File Name', f"Resume_{i+1}"),
                        'Skills': row.get('Skills', ''),
                        'Tools': row.get('Tools', ''),
                        'Certifications': row.get('Certifications', ''),
                        'Score': float(score)
                    })
                    
                    # Update progress
                    if i % 10 == 0 or i == len(resume_df) - 1:
                        placeholder.info(f"Processed {i+1}/{len(resume_df)} resumes...")
                
                # Sort by score
                all_resumes.sort(key=lambda x: x['Score'], reverse=True)
                
                # Categorize
                high_threshold = 0.25
                medium_threshold = 0.15
                
                high_matches = [r for r in all_resumes if r['Score'] >= high_threshold]
                medium_matches = [r for r in all_resumes if medium_threshold <= r['Score'] < high_threshold]
                low_matches = [r for r in all_resumes if r['Score'] < medium_threshold]
                
                # Create results dictionary
                results = {
                    'top_3': all_resumes[:3] if len(all_resumes) >= 3 else all_resumes,
                    'high_matches': high_matches,
                    'medium_matches': medium_matches,
                    'low_matches': low_matches
                }
                
                # Store results in state manager
                resume_repository['analysis_results'] = results
                state_manager.set('resume_repository', resume_repository)
                
                placeholder.success(f"Analysis complete! Found {len(high_matches)} high matches, {len(medium_matches)} medium matches, and {len(low_matches)} low matches")
                st.success(f"Resume analysis completed with {len(all_resumes)} resumes processed")
                
                # Force a rerun to update the UI
                st.rerun()
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.exception(e)  # This will show the full traceback
    
    # --- Results Display ---
    analysis_results = resume_repository.get('analysis_results')
    if analysis_results:
        # Analysis overview in second column
        with col2:
            display_subsection_header("Overview")
            try:
                chart = create_distribution_chart(analysis_results)
                st.plotly_chart(chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating distribution chart: {str(e)}")
                display_info_message("Chart visualization failed. Please check your data.")
        
        # Detailed analysis in third column
        with col3:
            display_subsection_header("Detailed Analysis")
            if 'top_3' in analysis_results and len(analysis_results['top_3']) > 0:
                # Get JD as a Series for radar chart
                job_desc = pd.Series({
                    'File Name': jd_source_name,
                    'JD_Type': jd_type,
                    'Skills': extract_skills_from_text(jd_content),
                    'Tools': extract_tools_from_text(jd_content)
                })
                
                display_detailed_resume_analysis(analysis_results, job_desc)
            else:
                st.info("No detailed analysis available.")
        
        # All Resumes by Category section
        st.markdown("---")
        display_section_header("📑 All Resumes by Category")
        display_categorized_resumes(analysis_results)

def detect_jd_type(file_name):
    """Detect the job description type based on the file name"""
    if file_name is None:
        return "general"
        
    file_name = str(file_name).lower()
    
    # Define keyword patterns for each type
    java_python_keywords = ['java', 'python', 'support']
    data_engineer_keywords = ['data', 'analytics', 'aiml']
    
    # Check for Java/Python developer
    if any(keyword in file_name for keyword in java_python_keywords):
        return 'java_developer'
    
    # Check for Data Engineer
    elif any(keyword in file_name for keyword in data_engineer_keywords):
        return 'data_engineer'
    
    # Default type
    return 'general'

def extract_skills_from_text(text):
    """
    Extract skills from text (simplified version)
    
    Args:
        text (str): The text to extract skills from
        
    Returns:
        str: Comma-separated list of found skills
    """
    if not text:
        return ""
        
    # Real implementation would use NLP or pattern matching
    common_skills = [
        'python', 'java', 'javascript', 'react', 'angular', 'node', 'aws', 'azure',
        'docker', 'kubernetes', 'sql', 'nosql', 'mongodb', 'machine learning', 'ai',
        'data analysis', 'cloud', 'devops', 'ci/cd', 'agile', 'scrum', 'rest api',
        'spring', 'hibernate', 'microservices', 'django', 'flask', 'vue', 'typescript',
        'html', 'css', 'php', 'ruby', 'c#', 'c++', 'golang', 'scala', 'rust',
        'git', 'jenkins', 'terraform', 'ansible', 'prometheus', 'grafana'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    # Use simpler string matching instead of regex
    for skill in common_skills:
        # Ensure case-insensitive string matching
        if f" {skill} " in f" {text_lower} " or f" {skill}," in f" {text_lower} " or f" {skill}." in f" {text_lower} ":
            found_skills.append(skill)
    
    return ", ".join(found_skills)

def extract_tools_from_text(text):
    """
    Extract tools from text (simplified version)
    
    Args:
        text (str): The text to extract tools from
        
    Returns:
        str: Comma-separated list of found tools
    """
    if not text:
        return ""
        
    # Real implementation would use NLP or pattern matching
    common_tools = [
        'git', 'jenkins', 'travis', 'circle ci', 'jira', 'confluence', 'slack',
        'vscode', 'intellij', 'eclipse', 'visual studio', 'docker', 'terraform',
        'ansible', 'chef', 'puppet', 'kubernetes', 'aws cli', 'azure cli',
        'maven', 'gradle', 'npm', 'yarn', 'webpack', 'babel', 'gulp', 'grunt',
        'jupyter', 'numpy', 'pandas', 'scikit-learn', 'tensorflow', 'pytorch',
        'tableau', 'power bi', 'excel', 'postman', 'soapui', 'github', 'gitlab'
    ]
    
    found_tools = []
    text_lower = text.lower()
    
    # Use simpler string matching instead of regex
    for tool in common_tools:
        # Ensure case-insensitive string matching
        if f" {tool} " in f" {text_lower} " or f" {tool}," in f" {text_lower} " or f" {tool}." in f" {text_lower} ":
            found_tools.append(tool)
    
    return ", ".join(found_tools)

def create_fallback_analysis(resume_df):
    """
    Create a basic analysis result structure with no dummy data
    
    Args:
        resume_df (DataFrame): Resume DataFrame to generate analysis for
        
    Returns:
        dict: Dictionary with categorized results structure
    """
    # Return an empty analysis structure
    return {
        'top_3': [],
        'high_matches': [],
        'medium_matches': [],
        'low_matches': []
    }

def handle_resume_pool_selection(selection, resume_analyzer, jd_type, state_manager):
    """
    Handle different resume pool selection options
    
    Args:
        selection (str): Selected pool option
        resume_analyzer: Resume analyzer instance
        jd_type (str): Job description type
        state_manager: State manager instance
        
    Returns:
        DataFrame or None: Resume DataFrame or None if still in selection process
    """
    resume_repository = state_manager.get('resume_repository', {})
    
    if selection == "(Auto Selection)":
        # Auto-select resume pool based on JD type
        st.info(f"Attempting to auto-select resume pool for job type: {jd_type}")
        
        # Use the helper method from the ResumeAnalyzer to find the appropriate file
        resume_file_path = resume_analyzer.find_default_resume_file(jd_type)
        
        if resume_file_path and os.path.exists(resume_file_path):
            try:
                # Load the resume file
                resume_df = pd.read_csv(resume_file_path)
                st.success(f"Loaded resume pool from {os.path.basename(resume_file_path)}")
                
                # Ensure required columns exist
                for col in ['File Name', 'Skills', 'Tools', 'Certifications']:
                    if col not in resume_df.columns:
                        resume_df[col] = ""
                
                return resume_df
            except Exception as e:
                st.error(f"Error loading resume file: {e}")
                st.error("Please check the file format and try again.")
                return None
        
        # If we reach here, file wasn't found or couldn't be loaded
        st.error("Default resume pool file not found in expected locations.")
        st.info("Try using 'Upload New Resume Pool' option to upload resume files manually.")
        return None
    
    elif selection == "Upload New Resume Pool":
        # Create UI for uploading new resumes
        new_pool_name = st.text_input("Enter new pool name:", key="new_pool_name")
        new_pool_files = st.file_uploader(
            "Upload resumes for the new pool", 
            type=['docx', 'csv'], 
            accept_multiple_files=True, 
            key="new_pool_files"
        )
        
        if st.button("Add Resume Pool", key="add_pool"):
            if new_pool_name and new_pool_files:
                with st.spinner("Processing resume files..."):
                    # Process all uploaded resumes
                    pool_df = resume_analyzer.process_resume_pool(new_pool_files)
                    
                    if pool_df is not None and not pool_df.empty:
                        # Display preview of the processed data
                        st.success(f"Successfully processed {len(pool_df)} resumes")
                        
                        with st.expander("Preview Processed Resumes"):
                            st.dataframe(pool_df[['File Name', 'Skills', 'Tools']].head(5))
                        
                        # Update resume repository
                        pools = resume_repository.get('pools', [])
                        pools.append({
                            "pool_name": new_pool_name, 
                            "data": pool_df.to_dict('records')  # Convert to dict for storage
                        })
                        resume_repository['pools'] = pools
                        state_manager.set('resume_repository', resume_repository)
                        
                        st.success(f"Resume pool '{new_pool_name}' added with {len(pool_df)} resumes!")
                        st.rerun()
                    else:
                        st.warning("No valid resumes were processed. Please check your files.")
                
                # Display helpful tips for file formats
                with st.expander("File Format Tips"):
                    st.markdown("""
                    ### DOCX Files
                    - Each DOCX file is treated as a single resume
                    - Make sure your DOCX files contain clear sections for skills, experience, etc.
                    
                    ### CSV Files
                    - CSV files can contain either a single resume or multiple resumes
                    - For multiple resumes, the CSV should have columns: `File Name`, `Skills`, `Tools`, and optionally `Certifications`
                    - Column names are case-sensitive, but the system will try to match lowercase alternatives
                    """)
            else:
                st.warning("Please provide both a pool name and upload at least one resume file.")
        return None
        
    elif selection in ["General", "Data Engineer", "Java Developer"]:
        # Map selection to job type for finding the right resume file
        jd_type_map = {
            "General": "general",
            "Data Engineer": "data_engineer",
            "Java Developer": "java_developer"
        }
        mapped_type = jd_type_map.get(selection, "general")
        
        # Use the helper method to find the file
        resume_file_path = resume_analyzer.find_default_resume_file(mapped_type)
        
        if resume_file_path and os.path.exists(resume_file_path):
            try:
                resume_df = pd.read_csv(resume_file_path)
                st.success(f"Loaded {selection} resume pool from {os.path.basename(resume_file_path)}")
                
                # Ensure required columns exist
                for col in ['File Name', 'Skills', 'Tools', 'Certifications']:
                    if col not in resume_df.columns:
                        resume_df[col] = ""
                
                return resume_df
            except Exception as e:
                st.error(f"Error loading resume file: {e}")
                st.error("Please check the file format and try again.")
                return None
        
        # If no file found, return none
        st.error(f"Resume pool file for {selection} not found.")
        st.info("Try using 'Upload New Resume Pool' option to upload resume files manually.")
        return None
    
    else:
        # Check if a user-uploaded pool was selected
        pools = resume_repository.get('pools', [])
        for pool in pools:
            if pool["pool_name"] == selection:
                try:
                    # Convert stored dict back to DataFrame
                    pool_df = pd.DataFrame(pool["data"])
                    st.success(f"Loaded custom resume pool '{selection}' with {len(pool_df)} resumes")
                    return pool_df
                except Exception as e:
                    st.error(f"Error loading custom resume pool: {e}")
                    return None
    
    # Default fallback - return None
    st.error("No valid resume pool selected.")
    st.info("Please select a resume pool or upload new resume files.")
    return None

def display_top_matches(analysis_results):
    """Display top match previews"""
    if not analysis_results:
        st.info("No analysis results available.")
        return
        
    display_subsection_header("Top Matches")
    
    if isinstance(analysis_results, dict) and 'top_3' in analysis_results and analysis_results['top_3']:
        st.success(f"Found {len(analysis_results['top_3'])} top matches")
        
        for i, resume in enumerate(analysis_results['top_3'][:3]):
            try:
                # Ensure score is a float and format it
                score = resume.get('Score', 0)
                if not isinstance(score, (int, float)):
                    score = 0
                
                resume_id = resume.get('Resume ID', f"Resume #{i+1}")
                skills = resume.get('Skills', '')
                
                # Safely truncate skills to avoid errors with very long strings
                skills_preview = skills[:100] + "..." if skills and len(skills) > 100 else skills
                
                # Display in a more reliable way
                st.markdown(f"**#{i + 1} - {resume_id}**")
                st.markdown(f"Match: {score:.2%}")
                st.markdown(f"Skills: {skills_preview}")
                st.markdown("---")
            except Exception as e:
                st.error(f"Error displaying match #{i+1}: {str(e)}")
    else:
        if not isinstance(analysis_results, dict):
            st.error(f"Invalid analysis results type: {type(analysis_results)}")
        elif 'top_3' not in analysis_results:
            st.error("Analysis results missing 'top_3' key")
        elif not analysis_results['top_3']:
            st.info("No top matches available yet. Click 'Analyze Resumes' to see results.")
        else:
            st.error("Unknown error displaying top matches")

def display_detailed_resume_analysis(categorized_resumes, job_desc):
    """Display detailed analysis of top resumes"""
    if not categorized_resumes or not categorized_resumes.get('top_3'):
        st.info("No resume analysis data available")
        return
        
    # Create tabs dynamically based on the number of top matches
    top_matches = categorized_resumes['top_3'][:3]
    tab_labels = [f"#{i+1}" for i in range(len(top_matches))]
    
    if not tab_labels:
        st.info("No top matches to display")
        return
        
    tabs = st.tabs(tab_labels)
    
    for i, (tab, resume) in enumerate(zip(tabs, top_matches)):
        with tab:
            col_a, col_b = st.columns([1, 1])
            with col_a:
                try:
                    score = resume.get('Score', 0)
                    if not isinstance(score, (int, float)):
                        score = 0
                    st.markdown(f"**Score:** {score:.2%}")
                    
                    radar_chart = create_radar_chart(resume, job_desc)
                    st.plotly_chart(radar_chart, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating radar chart: {str(e)}")
                    st.info("Match analysis visualization unavailable")
            
            with col_b:
                # Get certifications with safe fallback
                certs = resume.get('Certifications', 'Experience')
                if not certs or certs.strip() == '':
                    certs = 'Experience'
                
                st.markdown(f"""
                <div class="insight-box compact-text">
                    <h4>Key Match Analysis</h4>
                    <p>This candidate shows alignment with the job requirements based on their skills and experience:</p>
                    <ul>
                        <li>Technical skills match core requirements</li>
                        <li>Experience with relevant tools and technologies</li>
                        <li>{certs} enhances qualifications</li>
                    </ul>
                    <p><strong>Overall assessment:</strong> Good potential match based on technical qualifications.</p>
                </div>
                """, unsafe_allow_html=True)

def display_categorized_resumes(analysis_results):
    """Display all resumes categorized by match level"""
    if not analysis_results:
        st.info("No analysis results available")
        return
        
    cat_col1, cat_col2, cat_col3 = st.columns(3)
    
    with cat_col1:
        high_matches = analysis_results.get('high_matches', [])
        with st.expander(f"High Matches ({len(high_matches)})"):
            if high_matches:
                for resume in high_matches:
                    try:
                        resume_id = resume.get('Resume ID', "Unknown")
                        score = resume.get('Score', 0)
                        if not isinstance(score, (int, float)):
                            score = 0
                            
                        st.markdown(f"""
                        <div class="category-high">
                            <h4 style="margin:0">{resume_id}</h4>
                            <p style="margin:0">Match: {score:.2%}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error displaying high match: {str(e)}")
            else:
                st.info("No high matches found")
    
    with cat_col2:
        medium_matches = analysis_results.get('medium_matches', [])
        with st.expander(f"Medium Matches ({len(medium_matches)})"):
            if medium_matches:
                for resume in medium_matches:
                    try:
                        resume_id = resume.get('Resume ID', "Unknown")
                        score = resume.get('Score', 0)
                        if not isinstance(score, (int, float)):
                            score = 0
                            
                        st.markdown(f"""
                        <div class="category-medium">
                            <h4 style="margin:0">{resume_id}</h4>
                            <p style="margin:0">Match: {score:.2%}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error displaying medium match: {str(e)}")
            else:
                st.info("No medium matches found")
    
    with cat_col3:
        low_matches = analysis_results.get('low_matches', [])
        with st.expander(f"Low Matches ({len(low_matches)})"):
            if low_matches:
                for resume in low_matches:
                    try:
                        resume_id = resume.get('Resume ID', "Unknown")
                        score = resume.get('Score', 0)
                        if not isinstance(score, (int, float)):
                            score = 0
                            
                        st.markdown(f"""
                        <div class="category-low">
                            <h4 style="margin:0">{resume_id}</h4>
                            <p style="margin:0">Match: {score:.2%}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error displaying low match: {str(e)}")
            else:
                st.info("No low matches found")

def analyze_uploaded_resume(uploaded_file):
    """
    Analyze a user-uploaded resume (.docx) and extract the information
    
    Args:
        uploaded_file: The uploaded file object
        
    Returns:
        dict: Dictionary with extracted resume details
    """
    if not uploaded_file or not hasattr(uploaded_file, 'name'):
        return None
        
    # Only process .docx files
    if not uploaded_file.name.endswith(".docx"):
        raise ValueError(f"Unsupported file format for {uploaded_file.name}. Only .docx files are supported.")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.getvalue())
        temp_path = tmp.name
    
    try:
        # Extract text from the document
        doc = Document(temp_path)
        resume_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        
        if not resume_text:
            st.warning(f"No text content found in {uploaded_file.name}")
            return None
        
        # Extract skills (simplified)
        skills = extract_skills_from_text(resume_text)
        tools = extract_tools_from_text(resume_text)
        
        # Detect certifications (very simplified)
        cert_keywords = ['certified', 'certification', 'certificate', 'aws', 'azure', 
                       'google', 'professional', 'associate', 'expert']
        has_cert = any(kw in resume_text.lower() for kw in cert_keywords)
        certification = "Certification detected" if has_cert else "None specified"
        
        return {
            'File Name': uploaded_file.name,
            'Skills': skills,
            'Tools': tools,
            'Certifications': certification
        }
    except Exception as e:
        st.error(f"Error analyzing resume {uploaded_file.name}: {e}")
        return None
    finally:
        # Always remove the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            st.warning(f"No text content foun")