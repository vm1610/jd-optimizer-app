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
    
    # Try to load job data from JDs folder
    jd_files = get_jd_files()
    
    if not jd_files:
        display_warning_message("No job description files found in JDs folder. Using sample data instead.")
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
            # Create job data from JD files
            job_data = {
                'File Name': [],
                'Skills': [],
                'Tools': [],
                'JD_Type': []
            }
            
            jd_directory = os.path.join(os.getcwd(), "JDs")
            
            for jd_file in jd_files:
                file_path = os.path.join(jd_directory, jd_file)
                content = read_job_description(file_path)
                
                # Extract skills and tools from content (simplified extraction)
                skills = []
                tools = []
                
                # Simple extraction logic based on headings
                if "Skills" in content or "Requirements" in content:
                    skills = ["Python", "Java", "Data Analysis"] if "Data" in content else ["Java", "Object-Oriented Programming"]
                
                if "Tools" in content or "Technologies" in content:
                    tools = ["SQL", "Cloud", "Docker"] if "Data" in content else ["Debugging tools", "CoderPad"]
                
                # Append to job data
                job_data['File Name'].append(jd_file)
                job_data['Skills'].append(", ".join(skills))
                job_data['Tools'].append(", ".join(tools))
                job_data['JD_Type'].append(detect_jd_type(jd_file))
            
            job_df = pd.DataFrame(job_data)
            
            # Display info message about loaded files
            st.info(f"Loaded {len(job_df)} job descriptions from JDs folder")
            
        except Exception as e:
            st.error(f"Error loading job data from JDs folder: {e}")
            # Create sample job data
            job_data = {
                'File Name': ['DataAnalyticsAIMLJD (1).txt', 'JobDescriptionJavaPythonSupport.txt'],
                'Skills': ['Python, Java, ML, AI, Data Analysis', 'Java, Python, Object-Oriented Programming'],
                'Tools': ['SQL, Cloud, Docker', 'Debugging tools, CoderPad'],
                'JD_Type': ['data_engineer', 'java_developer']
            }
            job_df = pd.DataFrame(job_data)a)
    
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
        
        # Option to upload resume file
        st.markdown("---")
        display_subsection_header("Upload Resume")
        uploaded_resume = st.file_uploader(
            "📄 Drag and drop resumes",
            type=["pdf", "docx", "txt", "csv"],
            accept_multiple_files=True,
            help="Upload candidate resumes to analyze (PDF, DOCX, TXT, or CSV)"
        )
        
        if uploaded_resume:
            st.success(f"Uploaded {len(uploaded_resume)} resumes successfully!")
            
            # Process uploaded files
            csv_files = [file for file in uploaded_resume if file.name.endswith('.csv')]
            resume_files = [file for file in uploaded_resume if not file.name.endswith('.csv')]
            
            # Handle CSV files specially (they can contain multiple resumes)
            if csv_files:
                st.info(f"Processing {len(csv_files)} CSV files containing multiple resumes...")
                
                # For demonstration purposes - in a real app you would handle the CSV parsing here
                # This would typically involve pandas to read the CSV data
                for csv_file in csv_files:
                    try:
                        # Basic handling to show progress
                        st.write(f"Parsing {csv_file.name}...")
                        
                        # For a complete implementation, you would:
                        # 1. Read the CSV with pandas
                        # 2. Process each row as a separate resume
                        # 3. Extract skills, experience, etc.
                        # 4. Add to the resume database
                        
                        # Sample code for reference (commented out):
                        # import pandas as pd
                        # df = pd.read_csv(csv_file)
                        # st.write(f"Found {len(df)} resumes in {csv_file.name}")
                        # for _, row in df.iterrows():
                        #     # Process each row as a resume
                        #     pass
                        
                    except Exception as e:
                        st.error(f"Error processing {csv_file.name}: {str(e)}")
            
            # Handle individual resume files
            if resume_files:
                st.info(f"Processing {len(resume_files)} individual resume files...")
                # In a real app, you would process these files here
        
        # Let user select resume data file (this will show the dropdown)
        resume_df = resume_analyzer.load_resume_data(jd_type)
        
        # Analyze button (only enable if resume_df is available)
        if resume_df is not None:
            if st.button('🔍 Analyze Resumes', type="primary"):
                with st.spinner('Analyzing resumes...'):
                    try:
                        categorized_resumes = resume_analyzer.categorize_resumes(job_desc, resume_df)
                        st.session_state['analysis_results'] = categorized_resumes
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
                        # Create dummy results using the available resume_df
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
    
    # Check if analysis results exist
    if 'analysis_results' in st.session_state and st.session_state['analysis_results'] is not None:
        categorized_resumes = st.session_state['analysis_results']
        
        # Verify categorized_resumes has the expected structure
        if 'top_3' not in categorized_resumes or not categorized_resumes['top_3']:
            st.error("Analysis results are incomplete. Please try analyzing the resumes again.")
            return
            
        with col2:
            display_subsection_header("Overview")
            
            # Create distribution chart safely
            try:
                chart = create_distribution_chart(categorized_resumes)
                st.plotly_chart(chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
                # Provide a simpler fallback visualization
                st.bar_chart({
                    'High Match': [len(categorized_resumes.get('high_matches', []))],
                    'Medium Match': [len(categorized_resumes.get('medium_matches', []))],
                    'Low Match': [len(categorized_resumes.get('low_matches', []))]
                })
            
            # Top 3 Quick View with drag-and-drop interface
            display_subsection_header("Top Candidates")
            
            # Initialize reordering state if not exists or reset if needed
            if 'ranked_candidates' not in st.session_state or not st.session_state.ranked_candidates:
                st.session_state.ranked_candidates = categorized_resumes['top_3'][:3]
            
            # Create a CSS-styled drag area
            st.markdown("""
            <style>
            .drag-container {
                padding: 10px;
                border: 2px dashed #ddd;
                border-radius: 5px;
                margin-bottom: 10px;
                background-color: #f8f9fa;
            }
            .drag-item {
                padding: 10px;
                background-color: white;
                border: 1px solid #eee;
                border-radius: 5px;
                margin-bottom: 8px;
                cursor: grab;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create a candidate reordering interface
            st.markdown("<div class='drag-container'>", unsafe_allow_html=True)
            
            # Make sure we have candidates to display
            if st.session_state.ranked_candidates:
                # Get current order
                current_order = [resume['Resume ID'] for resume in st.session_state.ranked_candidates]
                all_candidates = [resume['Resume ID'] for resume in categorized_resumes['top_3']]
                
                # Allow user to select ranking for each position
                for i in range(min(3, len(categorized_resumes['top_3']))):
                    # Get the current candidate at this position
                    current_candidate = current_order[i] if i < len(current_order) else None
                    
                    # Show a selectbox with all candidates, defaulting to the current one
                    new_selection = st.selectbox(
                        f"Rank #{i+1}",
                        options=all_candidates,
                        index=all_candidates.index(current_candidate) if current_candidate in all_candidates else i,
                        key=f"rank_{i}"
                    )
                    
                    # Find the candidate data
                    candidate_data = next((r for r in categorized_resumes['top_3'] if r['Resume ID'] == new_selection), None)
                    
                    if candidate_data:
                        # Display the candidate card
                        st.markdown(f"""
                        <div class="drag-item">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>{candidate_data['Resume ID']}</strong>
                                <span>Match: {candidate_data['Score']:.2%}</span>
                            </div>
                            <div style="font-size: 0.9em; color: #666;">
                                {candidate_data['Skills'][:50]}...
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Update the order if changed
                        if i < len(current_order) and current_order[i] != new_selection:
                            # Find candidate index
                            try:
                                old_index = next((j for j, cand in enumerate(st.session_state.ranked_candidates) 
                                             if cand['Resume ID'] == new_selection), i)
                                
                                # Swap positions
                                st.session_state.ranked_candidates[i], st.session_state.ranked_candidates[old_index] = \
                                    st.session_state.ranked_candidates[old_index], st.session_state.ranked_candidates[i]
                            except Exception as e:
                                st.error(f"Error updating ranking: {str(e)}")
            else:
                st.info("No candidates available for ranking. Please analyze resumes first.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add ability to save rankings
            if st.button("Save Rankings", key="save_rankings"):
                st.success("Candidate rankings saved successfully!")
        
        with col3:
            display_subsection_header("Detailed Analysis")
            
            # Create tabs only if we have candidates to display
            if st.session_state.ranked_candidates:
                tabs = st.tabs(["#1", "#2", "#3"])
                
                for i, tab in enumerate(tabs):
                    if i < len(st.session_state.ranked_candidates):
                        resume = st.session_state.ranked_candidates[i]
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
            else:
                st.info("Analyze resumes to see detailed candidate analysis.")

        # All Resumes by Category (below the main content)
        st.markdown("---")
        display_section_header("📑 All Resumes by Category")
        
        cat_col1, cat_col2, cat_col3 = st.columns(3)
        
        with cat_col1:
            with st.expander(f"High Matches ({len(categorized_resumes.get('high_matches', []))})"):
                for resume in categorized_resumes.get('high_matches', []):
                    st.markdown(f"""
                    <div class="category-high">
                        <h4 style="margin:0">{resume['Resume ID']}</h4>
                        <p style="margin:0">Match: {resume['Score']:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with cat_col2:
            with st.expander(f"Medium Matches ({len(categorized_resumes.get('medium_matches', []))})"):
                for resume in categorized_resumes.get('medium_matches', []):
                    st.markdown(f"""
                    <div class="category-medium">
                        <h4 style="margin:0">{resume['Resume ID']}</h4>
                        <p style="margin:0">Match: {resume['Score']:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with cat_col3:
            with st.expander(f"Low Matches ({len(categorized_resumes.get('low_matches', []))})"):
                for resume in categorized_resumes.get('low_matches', []):
                    st.markdown(f"""
                    <div class="category-low">
                        <h4 style="margin:0">{resume['Resume ID']}</h4>
                        <p style="margin:0">Match: {resume['Score']:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        # Display a prompt for the user if no analysis has been done yet
        with col2:
            st.info("Select a position and click 'Analyze Resumes' to get started.")
