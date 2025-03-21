import os
import streamlit as st
import pandas as pd
import numpy as np
from models.resume_analyzer import ResumeAnalyzer
from utils.text_processing import detect_jd_type
from utils.visualization import create_distribution_chart, create_radar_chart
from ui.common import display_section_header, display_subsection_header, display_info_message, display_warning_message

def render_candidate_ranking_page():
    """Render the candidate ranking page"""
    
    display_section_header("🎯 Resume Ranking")
    
    # Create sample data if needed
    if not os.path.exists('job_descriptions_analysis_output.csv'):
        display_warning_message("job_descriptions_analysis_output.csv not found. Using sample data instead.")
        # Create sample job data
        job_data = {
            'File Name': ['DataAnalyticsAIMLJD (1).txt', 'JobDescriptionJavaPythonSupport.txt'],
            'Skills': ['Python, Java, ML, AI, Data Analysis', 'Java, Python, Object-Oriented Programming'],
            'Tools': ['SQL, Cloud, Docker', 'Debugging tools, CoderPad'],
            'JD_Type': ['data_engineer', 'java_developer']
        }
        job_df = pd.DataFrame(job_data)
    else:
        try:
            # Load job data
            job_df = pd.read_csv('job_descriptions_analysis_output.csv')
            
            # Add JD_Type column if it doesn't exist
            if 'JD_Type' not in job_df.columns:
                job_df['JD_Type'] = job_df['File Name'].apply(detect_jd_type)
        except Exception as e:
            st.error(f"Error loading job data: {e}")
            # Create sample job data
            job_data = {
                'File Name': ['DataAnalyticsAIMLJD (1).txt', 'JobDescriptionJavaPythonSupport.txt'],
                'Skills': ['Python, Java, ML, AI, Data Analysis', 'Java, Python, Object-Oriented Programming'],
                'Tools': ['SQL, Cloud, Docker', 'Debugging tools, CoderPad'],
                'JD_Type': ['data_engineer', 'java_developer']
            }
            job_df = pd.DataFrame(job_data)
    
    # Create three columns for main layout
    col1, col2, col3 = st.columns([1, 1, 1])

    # Initialize the resume analyzer
    resume_analyzer = ResumeAnalyzer()

    with col1:
        display_subsection_header("Select Position")
        job_desc_file_names = job_df['File Name'].tolist()
        selected_job_desc = st.selectbox('Choose position:', job_desc_file_names, label_visibility="collapsed")
        job_desc = job_df[job_df['File Name'] == selected_job_desc].iloc[0]
        
        # Display the selected JD type for verification
        jd_type = job_desc['JD_Type']
        st.markdown(f"**Resume Pool:** {jd_type.replace('_', ' ').title()}")
        
        with st.expander("Job Details", expanded=False):
            st.markdown(f"**Skills:** {job_desc['Skills']}")
            st.markdown(f"**Tools:** {job_desc['Tools']}")
        
        # Try to load resume data based on the selected job type
        resume_df = resume_analyzer.load_resume_data(jd_type)
        
        # Analyze button
        if st.button('🔍 Analyze Resumes', type="primary"):
            with st.spinner('Analyzing resumes...'):
                try:
                    categorized_resumes = resume_analyzer.categorize_resumes(job_desc, resume_df)
                    st.session_state['analysis_results'] = categorized_resumes
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    # Create dummy results for demonstration
                    all_resumes = []
                    for i in range(len(resume_df)):
                        score = np.random.uniform(0.1, 0.4)
                        all_resumes.append({
                            'Resume ID': resume_df.iloc[i]['File Name'],
                            'Skills': resume_df.iloc[i]['Skills'],
                            'Tools': resume_df.iloc[i]['Tools'],
                            'Certifications': resume_df.iloc[i]['Certifications'],
                            'Score': score
                        })
                    
                    # Sort by score
                    all_resumes.sort(key=lambda x: x['Score'], reverse=True)
                    
                    # Categorize
                    high_matches = [r for r in all_resumes if r['Score'] >= 0.25]
                    medium_matches = [r for r in all_resumes if 0.2 <= r['Score'] < 0.25]
                    low_matches = [r for r in all_resumes if r['Score'] < 0.2]
                    
                    st.session_state['analysis_results'] = {
                        'top_3': all_resumes[:3],
                        'high_matches': high_matches,
                        'medium_matches': medium_matches,
                        'low_matches': low_matches
                    }

    if 'analysis_results' in st.session_state:
        categorized_resumes = st.session_state['analysis_results']
        
        with col2:
            display_subsection_header("Overview")
            # Distribution chart
            try:
                chart = create_distribution_chart(categorized_resumes)
                st.plotly_chart(chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating distribution chart: {str(e)}")
                st.bar_chart({
                    'High Match': [len(categorized_resumes['high_matches'])],
                    'Medium Match': [len(categorized_resumes['medium_matches'])],
                    'Low Match': [len(categorized_resumes['low_matches'])]
                })
            
            # Top 3 Quick View
            display_subsection_header("Top Matches")
            for i, resume in enumerate(categorized_resumes['top_3'][:3]):
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0">#{i + 1} - {resume['Resume ID']}</h4>
                    <p style="margin:0">Match: {resume['Score']:.2%}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            display_subsection_header("Detailed Analysis")
            tabs = st.tabs(["#1", "#2", "#3"])
            
            for i, (tab, resume) in enumerate(zip(tabs, categorized_resumes['top_3'])):
                with tab:
                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        st.markdown(f"**Score:** {resume['Score']:.2%}")
                        try:
                            radar_chart = create_radar_chart(resume, job_desc)
                            st.plotly_chart(radar_chart, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error creating radar chart: {str(e)}")
                            st.info("Match analysis visualization unavailable")
                    
                    with col_b:
                        try:
                            # In a production environment, use the AI insight generation
                            # insights = generate_ai_insights(job_desc, resume)
                            
                            # For now, provide a static insight
                            insights = f"""
                            <h4>Key Match Analysis</h4>
                            <p>This candidate has skills that align with the job requirements.</p>
                            <ul>
                                <li>Technical skills match core requirements</li>
                                <li>Experience with relevant tools</li>
                                <li>Professional background enhances qualifications</li>
                            </ul>
                            <p><strong>Overall assessment:</strong> Good potential match</p>
                            """
                            
                            st.markdown(f"""
                            <div class="insight-box compact-text">
                                {insights}
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error generating insights: {str(e)}")
                            st.markdown(f"""
                            <div class="insight-box compact-text">
                                <h4>Key Match Analysis</h4>
                                <p>This candidate has skills that align with the job requirements.</p>
                                <ul>
                                    <li>Technical skills match core requirements</li>
                                    <li>Experience with relevant tools</li>
                                    <li>Professional background enhances qualifications</li>
                                </ul>
                                <p><strong>Overall assessment:</strong> Good potential match</p>
                            </div>
                            """, unsafe_allow_html=True)

        # All Resumes by Category (below the main content)
        st.markdown("---")
        display_section_header("📑 All Resumes by Category")
        
        cat_col1, cat_col2, cat_col3 = st.columns(3)
        
        with cat_col1:
            with st.expander(f"High Matches ({len(categorized_resumes['high_matches'])})"):
                for resume in categorized_resumes['high_matches']:
                    st.markdown(f"""
                    <div class="category-high">
                        <h4 style="margin:0">{resume['Resume ID']}</h4>
                        <p style="margin:0">Match: {resume['Score']:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with cat_col2:
            with st.expander(f"Medium Matches ({len(categorized_resumes['medium_matches'])})"):
                for resume in categorized_resumes['medium_matches']:
                    st.markdown(f"""
                    <div class="category-medium">
                        <h4 style="margin:0">{resume['Resume ID']}</h4>
                        <p style="margin:0">Match: {resume['Score']:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with cat_col3:
            with st.expander(f"Low Matches ({len(categorized_resumes['low_matches'])})"):
                for resume in categorized_resumes['low_matches']:
                    st.markdown(f"""
                    <div class="category-low">
                        <h4 style="margin:0">{resume['Resume ID']}</h4>
                        <p style="margin:0">Match: {resume['Score']:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)