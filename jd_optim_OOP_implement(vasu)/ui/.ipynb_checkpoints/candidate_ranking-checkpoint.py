import os
import streamlit as st
import pandas as pd
import numpy as np
import tempfile
from docx import Document
from ui.common import display_section_header, display_subsection_header, display_info_message, display_warning_message, display_success_message
from utils.visualization import create_distribution_chart, create_radar_chart
from models.resume_analyzer import ResumeAnalyzer
from utils.text_processing import extract_skills, preprocess_text

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
        
    # Place this in candidate_ranking.py, replacing the existing analyze button section
    
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
                
                # Manually create analysis results instead of using the analyzer
                # This ensures we have data to display and can debug
                
                all_resumes = []
                for i, row in resume_df.iterrows():
                    # Simple scoring algorithm
                    resume_skills = row.get('Skills', '')
                    resume_tools = row.get('Tools', '')
                    
                    # Direct matching for demonstration
                    skill_matches = sum(1 for skill in skills.split(', ') if skill.lower() in resume_skills.lower())
                    tool_matches = sum(1 for tool in tools.split(', ') if tool.lower() in resume_tools.lower())
                    
                    # Calculate score (simple version)
                    max_skills = max(1, len(skills.split(', ')))
                    max_tools = max(1, len(tools.split(', ')))
                    
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
        # Display top matches preview
        analysis_results = resume_repository.get('analysis_results')
        if analysis_results:
            display_top_matches(analysis_results)
    
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

# The rest of the code remains the same, so I've omitted it for brevity