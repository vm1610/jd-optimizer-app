import streamlit as st
import datetime
import os
from utils.file_utils import save_enhanced_jd
from utils.job_search import render_job_search_section, find_data_files
from utils.visualization import create_multi_radar_chart, create_comparison_dataframe
from ui.common import (
    display_section_header, display_subsection_header, 
    display_warning_message, display_info_message, display_success_message,
    render_jd_selector, render_feedback_component, display_jd_comparison
)
from utils.file_utils import read_job_description

def render_enhanced_versions_with_summaries(enhanced_versions, jd_content, agent):
    """
    Render enhanced versions with summaries displayed before the content
    
    Args:
        enhanced_versions (list): List of enhanced versions
        jd_content (str): Original JD content
        agent: AI agent for generating summaries
    """
    # Create tabs for content and analysis
    enhanced_tabs = st.tabs(["Enhanced Versions", "Analysis & Comparison"])
    
    # Show enhanced versions tab content
    with enhanced_tabs[0]:
        version_tabs = st.tabs(["Version 1", "Version 2", "Version 3"])
        for idx, (tab, version) in enumerate(zip(version_tabs, enhanced_versions)):
            with tab:
                # Generate and display summary first
                st.markdown("### Version Summary")
                
                with st.spinner("Generating summary..."):
                    # Generate summary using the agent
                    summary_text = agent.generate_version_summary(jd_content, version)
                    
                    # Process summary into bullet points if it's not already in that format
                    if not summary_text.strip().startswith("•"):
                        # Split into sentences and convert to bullet points
                        sentences = [s.strip() for s in summary_text.split('.') if s.strip()]
                        bullet_summary = "\n".join([f"• {sentence}." for sentence in sentences if sentence])
                    else:
                        bullet_summary = summary_text
                    
                    st.markdown(
                        f"""
                        <div style="background-color: #2D3748; padding: 12px; border-radius: 5px; border-left: 4px solid #4299E1; margin-bottom: 15px;">
                            <div style="color: #FFFFFF; font-size: 0.9em;">
                                {bullet_summary}
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                # Display version content AFTER the summary
                st.text_area(
                    f"Enhanced Version {idx + 1}",
                    version,
                    height=300,
                    disabled=True,
                    key=f"enhanced_version_{idx}"
                )
                
                # Download button - ONLY ONE per version
                st.download_button(
                    label=f"Download Version {idx + 1}",
                    data=version,
                    file_name=f"enhanced_jd_version_{idx+1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key=f"download_version_{idx}"
                )


def render_jd_optimization_page(services):
    """
    Render the unified JD Optimization page with optimized performance by using cached results
    
    Args:
        services (dict): Dictionary of shared services 
    """
    # Unpack services
    logger = services.get('logger')
    analyzer = services.get('analyzer')
    agent = services.get('agent')
    state_manager = services.get('state_manager')
    
    display_section_header("📝 JD Optimization")
    
    # Create tabs for the main content and feedback history
    main_tabs = st.tabs(["JD Optimization", "Feedback History"])
    
    with main_tabs[0]:
        ##########################
        # Part 1: Unified Job Description Selection
        ##########################
        display_subsection_header("1. Select Job Description")
        
        # Create a selection for the source type (merged File Selection and Upload into one option)
        source_options = ["📁 Files", "🔍 Search Database"]
        selected_source = st.radio(
            "Choose job description source:",
            options=source_options,
            horizontal=True,
            key="jd_source_selector"
        )
        
        # Variables to track job description source
        jd_content = None
        jd_source_name = None
        jd_unique_id = None
        jd_selection_confirmed = False
        
        # Handle each source option
        if selected_source == "🔍 Search Database":
            # Initialize job search utility if needed
            job_search_initialized = render_job_search_section(state_manager)
            
            # Add status color coding info box
            status_info_expander = st.expander("📊 Job Status Information", expanded=False)
            with status_info_expander:
                st.markdown("""
                <div style="background-color: #2D3748; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <h4 style="margin-top: 0;">Available Jobs</h4>
                    <p>Only jobs with available job descriptions are shown in the dropdown.</p>
                    <p>If you don't see a specific job, it may not have an associated job description in the system.</p>
                </div>
                """, unsafe_allow_html=True)
            
            if not job_search_initialized:
                st.warning("Please initialize the job search database first using the options above.")
                return
                
            job_search = state_manager.get('job_search_utility')
            
            # Check if the job search has been initialized
            if not job_search.is_initialized:
                # Display warning message about not being initialized
                st.warning("Job search database not properly initialized. Please try reloading the page.")
                return
            else:
                # Get dropdown options
                options = job_search.get_dropdown_options()
                
                # Remove sample JDs from options
                options = [opt for opt in options if not opt.startswith("⚪ Sample_")]
                
                if not options:
                    st.warning("No job listings found in the data.")
                else:
                    # Add a search box for filtering the dropdown
                    st.markdown("**💼 Search for a job description:**")
                    search_col1, search_col2 = st.columns([3, 1])
                    
                    with search_col1:
                        search_term = st.text_input("Search for job by ID, name, or client:", key="job_search_term")
                    
                    with search_col2:
                        st.markdown("""
                        <span title="Search Help">ℹ️ Search by ID, name, or client</span>
                        """, unsafe_allow_html=True)
                    
                    # Filter options based on search term
                    if search_term:
                        filtered_options = [opt for opt in options if search_term.lower() in opt.lower()]
                    else:
                        filtered_options = options
                    
                    # Show the dropdown with filtered options
                    if filtered_options:
                        selected_option = st.selectbox(
                            "Select Job:",
                            options=filtered_options,
                            key="job_search_dropdown"
                        )
                        
                        # Find and display the job description
                        if selected_option:
                            job_description, job_details = job_search.find_job_description(selected_option)
                            
                            # Check if job details were returned even if description wasn't found
                            if job_details:
                                # Display job details
                                st.subheader("Job Details")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Job ID:** {job_details.get('Job Id', 'N/A')}")
                                    st.markdown(f"**Reference ID:** {job_details.get('Reference Id', 'N/A')}")
                                    st.markdown(f"**Job Name:** {job_details.get('Job Name', 'N/A')}")
                                with col2:
                                    st.markdown(f"**Client:** {job_details.get('Client', 'N/A')}")
                                    st.markdown(f"**Status:** {job_details.get('Status', 'N/A')}")
                                    st.markdown(f"**Parent ID:** {job_details.get('Parent Id', 'N/A')}")
                            
                            # If we have an actual job description, show it and allow selection
                            if job_description:
                                # Preview the job description
                                st.subheader("Job Description Preview")
                                with st.expander("View Job Description", expanded=True):
                                    st.text_area(
                                        "Preview Content", 
                                        job_description, 
                                        height=250, 
                                        disabled=True,
                                        key="job_preview"
                                    )
                                
                                # Confirm selection with a button
                                if st.button("🔒 Select This Job Description", type="primary", key="confirm_job_selection"):
                                    jd_content = job_description
                                    jd_source_name = selected_option
                                    jd_unique_id = f"db_{job_details.get('Job Id', '')}"
                                    
                                    # Store in session state for persistent access
                                    st.session_state.jd_content = jd_content
                                    st.session_state.jd_source_name = jd_source_name
                                    st.session_state.jd_unique_id = jd_unique_id
                                    st.session_state.jd_selection_confirmed = True
                                    
                                    jd_selection_confirmed = True
                                    display_success_message(f"Job description '{selected_option}' selected!")
                            else:
                                # No job description was found
                                st.error("No job description content found for this job. Please select another job with available content.")
                    else:
                        st.warning("No jobs match your search criteria.")
        
        elif selected_source == "📁 Files":
            # Create tabs for existing files and uploading new files
            file_col1, file_col2 = st.columns([1, 1])
            
            with file_col1:
                st.markdown("### Existing Files")
                jd_directory = os.path.join(os.getcwd(), "jd_optim_OOP_implement(vasu)/Data/JDs")
                try:
                    # Create directory if it doesn't exist
                    os.makedirs(jd_directory, exist_ok=True)
                    
                    # Get list of existing files
                    files = [f for f in os.listdir(jd_directory) if f.endswith(('.txt', '.docx'))]
                    
                    if files:
                        selected_file = st.selectbox(
                            "Select Existing Job Description File", 
                            files, 
                            key="file_selector"
                        )
                        
                        if selected_file:
                            # Load selected file
                            file_path = os.path.join(jd_directory, selected_file)
                            
                            try:
                                file_content = read_job_description(file_path)
                                
                                # Preview the job description
                                with st.expander("Preview Content", expanded=True):
                                    st.text_area(
                                        "File Content", 
                                        file_content, 
                                        height=250, 
                                        disabled=True,
                                        key="file_preview"
                                    )
                                
                                # Confirm selection with a button
                                if st.button("Select This File", type="primary", key="confirm_file_selection"):
                                    jd_content = file_content
                                    jd_source_name = selected_file
                                    jd_unique_id = f"file_{selected_file}"
                                    
                                    # Store in session state
                                    st.session_state.jd_content = jd_content
                                    st.session_state.jd_source_name = jd_source_name
                                    st.session_state.jd_unique_id = jd_unique_id
                                    st.session_state.jd_selection_confirmed = True
                                    
                                    jd_selection_confirmed = True
                                    display_success_message(f"Job description '{selected_file}' selected!")
                            except Exception as e:
                                st.error(f"Error reading file: {str(e)}")
                    else:
                        st.info("No job description files found. Please upload a new file.")
                except Exception as e:
                    st.error(f"Error accessing JDs directory: {str(e)}")
            
            with file_col2:
                st.markdown("### Upload New File")
                uploaded_file = st.file_uploader(
                    "Upload Job Description File", 
                    type=['txt', 'docx'],
                    key="file_uploader"
                )
                
                if uploaded_file:
                    # Process uploaded file
                    try:
                        if uploaded_file.name.endswith('.txt'):
                            file_content = uploaded_file.getvalue().decode('utf-8')
                        else:  # .docx
                            try:
                                from docx import Document
                                # Save temporarily
                                temp_path = f"temp_{uploaded_file.name}"
                                with open(temp_path, 'wb') as f:
                                    f.write(uploaded_file.getvalue())
                                
                                # Read with python-docx
                                doc = Document(temp_path)
                                file_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                                
                                # Clean up
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                            except ImportError:
                                st.error("python-docx package not found. Please install it to process DOCX files.")
                                file_content = f"[Could not process DOCX file: {uploaded_file.name}]"
                        
                        # Preview the job description first
                        with st.expander("Preview Content", expanded=True):
                            st.text_area(
                                "Uploaded Content", 
                                file_content, 
                                height=250, 
                                disabled=True,
                                key="upload_preview"
                            )
                        
                        # Confirm selection with a button
                        if st.button("Select This Upload", type="primary", key="confirm_upload_selection"):
                            jd_content = file_content
                            jd_source_name = uploaded_file.name
                            jd_unique_id = f"upload_{uploaded_file.name}"
                            
                            # Store in session state
                            st.session_state.jd_content = jd_content
                            st.session_state.jd_source_name = jd_source_name
                            st.session_state.jd_unique_id = jd_unique_id
                            st.session_state.jd_selection_confirmed = True
                            
                            jd_selection_confirmed = True
                            
                            # Save to JDs directory for future use
                            jd_dir = os.path.join(os.getcwd(), "jd_optim_OOP_implement(vasu)/Data/JDs")
                            os.makedirs(jd_dir, exist_ok=True)
                            save_path = os.path.join(jd_dir, uploaded_file.name)
                            
                            with open(save_path, 'wb') as f:
                                f.write(uploaded_file.getvalue())
                            
                            display_success_message(f"Job description '{uploaded_file.name}' selected and saved for future use!")
                    except Exception as e:
                        st.error(f"Error processing uploaded file: {str(e)}")
        
        # Alternative: Check if we have a confirmed JD selection in session state
        if (not jd_selection_confirmed and not jd_content and 
            'jd_selection_confirmed' in st.session_state and 
            st.session_state.jd_selection_confirmed and
            'jd_content' in st.session_state):
            jd_content = st.session_state.jd_content
            jd_source_name = st.session_state.jd_source_name
            jd_unique_id = st.session_state.jd_unique_id
            jd_selection_confirmed = True
        
        # Use the job description content if selection is confirmed
        if jd_content and jd_selection_confirmed:
            # Update state manager
            state_manager.update_jd_repository('original', jd_content, source_tab="jd_optimization")
            state_manager.update_jd_repository('source_name', jd_source_name, source_tab="jd_optimization")
            state_manager.update_jd_repository('unique_id', jd_unique_id, source_tab="jd_optimization")
            
            # Add notification for JD selection
            state_manager.add_notification({
                'type': 'jd_selected',
                'source_name': jd_source_name,
                'origin': "jd_optimization",
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            # Log file selection if logger exists
            if logger:
                logger.log_file_selection(jd_source_name, jd_content)
            
            # Display the job description preview with selection indicator
            display_subsection_header("Selected Job Description")
            
            st.success(f"✅ Currently working with: {jd_source_name}")
            
            # Show the JD preview in a collapsible section
            with st.expander("View Selected Job Description", expanded=True):
                st.text_area(
                    "Content", 
                    jd_content, 
                    height=250, 
                    disabled=True,
                    key="jd_preview"
                )
            
            ##########################
            # Part 2: Generate Enhanced Versions (with caching)
            ##########################
            display_subsection_header("2. Generate Enhanced Versions")
            
            # Get repository from state manager
            jd_repository = state_manager.get('jd_repository', {})
            
            # Check if we already have enhanced versions
            enhanced_versions = jd_repository.get('enhanced_versions', [])
            
            # Check if we need to generate versions
            if not enhanced_versions:
                # Check if we have cached versions from logger
                cached_versions = None
                if logger:
                    cached_versions = logger.get_cached_versions(jd_unique_id)
                
                # Display cache status
                if cached_versions:
                    st.success("📋 Found cached enhanced versions for this job description!")
                    
                    # Add option to regenerate if needed
                    regenerate = st.checkbox("Regenerate versions (not recommended unless necessary)", value=False)
                    
                    if regenerate:
                        generate_btn = st.button(
                            "Generate New Versions", 
                            type="primary", 
                            key="generate_btn",
                            help="Generate three new AI-enhanced versions (ignores cache)"
                        )
                    else:
                        # Load cached versions
                        enhanced_versions = cached_versions
                        state_manager.update_jd_repository('enhanced_versions', cached_versions, source_tab="jd_optimization")
                        
                        # Also store in session state
                        st.session_state.enhanced_versions = enhanced_versions
                        
                        # Show a fake button that's disabled
                        st.button(
                            "✅ Enhanced Versions Loaded", 
                            type="secondary", 
                            disabled=True,
                            key="loaded_btn"
                        )
                        
                        # Set generate_btn to False
                        generate_btn = False
                else:
                    # No cached versions, show normal generate button
                    generate_btn = st.button(
                        "Generate Enhanced Versions", 
                        type="primary", 
                        key="generate_btn",
                        help="Generate three AI-enhanced versions of your job description"
                    )
                
                # Handle generating enhanced versions
                if generate_btn:
                    with st.spinner("Generating enhanced versions... This may take a moment"):
                        # Call the agent to generate versions
                        try:
                            versions = agent.generate_initial_descriptions(jd_content)
                            
                            # Ensure we have 3 versions
                            while len(versions) < 3:
                                versions.append(f"Enhanced Version {len(versions)+1}:\n{jd_content}")
                            
                            # Update state
                            state_manager.update_jd_repository('enhanced_versions', versions, source_tab="jd_optimization")
                            
                            # Store in session state
                            st.session_state.enhanced_versions = versions
                            enhanced_versions = versions
                            
                            # Log generated versions
                            if logger:
                                logger.log_versions_generated(versions)
                            
                            st.success("Successfully generated enhanced versions!")
                        except Exception as e:
                            st.error(f"Error generating versions: {str(e)}")
                            return
            
            # Alternative: Check for enhanced versions in session state
            if not enhanced_versions and 'enhanced_versions' in st.session_state:
                enhanced_versions = st.session_state.enhanced_versions
                state_manager.update_jd_repository('enhanced_versions', enhanced_versions, source_tab="jd_optimization")
            
            # Display enhanced versions if available
            if enhanced_versions:
                # Use our custom function to render enhanced versions with summaries
                render_enhanced_versions_with_summaries(enhanced_versions, jd_content, agent)
                
                # Show analysis & comparison tab content
                enhanced_tabs = st.tabs(["Enhanced Versions", "Analysis & Comparison"])
                with enhanced_tabs[1]:
                    # Analyze all versions
                    original_scores = analyzer.analyze_text(jd_content)
                    intermediate_scores = {
                        f'Version {i+1}': analyzer.analyze_text(version)
                        for i, version in enumerate(enhanced_versions)
                    }
                    
                    # Combine all scores for comparison
                    all_scores = {'Original': original_scores, **intermediate_scores}
                    
                    # Update analytics repository
                    analytics_repository = state_manager.get('analytics_repository', {})
                    analytics_repository['original_scores'] = original_scores
                    analytics_repository['version_scores'] = intermediate_scores
                    state_manager.set('analytics_repository', analytics_repository)
                    
                    analysis_col1, analysis_col2 = st.columns([1, 1])
                        
                    with analysis_col1:
                        st.subheader("Skill Coverage Comparison")
                        radar_chart = create_multi_radar_chart(all_scores)
                        st.plotly_chart(radar_chart, use_container_width=True, key="intermediate_radar")
                        
                    with analysis_col2:
                        st.subheader("Detailed Analysis")
                        comparison_df = create_comparison_dataframe(all_scores)
                        st.dataframe(
                            comparison_df,
                            height=400,
                            use_container_width=True,
                            hide_index=True,
                            key="intermediate_comparison"
                        )
                        st.caption("Percentages indicate keyword coverage in each category")
                
                ##########################
                # Part 3: Provide Feedback & Generate Final Version
                ##########################
                display_subsection_header("3. Provide Feedback & Generate Final Version")
                
                left_col, right_col = st.columns([1, 1])
                
                with left_col:
                    # Version selection
                    selected_version = st.radio(
                        "Choose the version you'd like to use as a base:",
                        ["Version 1", "Version 2", "Version 3"],
                        help="Select the version that best matches your needs for further enhancement",
                        key="version_selector"
                    )
                    
                    selected_index = int(selected_version[-1]) - 1  # Get version index
                    
                    # Update selected version in repository
                    state_manager.update_jd_repository('selected_version_idx', selected_index, source_tab="jd_optimization")
                    
                    # Store in session state
                    st.session_state.selected_version_idx = selected_index
                    
                    # Display previous feedback if available
                    feedback_history = state_manager.get('feedback_repository', {}).get('history', [])
                    if feedback_history:
                        st.markdown("**Previous Feedback:**")
                        with st.expander("View Feedback History", expanded=False):
                            for i, feedback in enumerate(feedback_history, 1):
                                feedback_text = feedback.get("feedback", "") if isinstance(feedback, dict) else feedback
                                feedback_type = feedback.get("type", "General Feedback") if isinstance(feedback, dict) else "General Feedback"
                                st.markdown(f"**#{i} - {feedback_type}:**")
                                st.markdown(f"> {feedback_text}")
                                st.markdown("---")
                
                with right_col:
                    # Feedback input
                    # Define feedback types
                    feedback_types = [
                        "General Feedback", 
                        "Rejected Candidate", 
                        "Hiring Manager Feedback", 
                        "Client Feedback", 
                        "Selected Candidate", 
                        "Interview Feedback"
                    ]
                    
                    # Get current feedback type
                    feedback_repository = state_manager.get('feedback_repository', {})
                    current_type = feedback_repository.get('current_type', "General Feedback")
                    
                    selected_feedback_type = st.selectbox(
                        "Feedback Type:",
                        options=feedback_types,
                        index=feedback_types.index(current_type) if current_type in feedback_types else 0,
                        key="feedback_type_selector"
                    )
                    
                    # Update type in state if changed
                    if selected_feedback_type != current_type:
                        state_manager.update_feedback_repository('current_type', selected_feedback_type, source_tab="jd_optimization")
                    
                    # Feedback input
                    user_feedback = st.text_area(
                        "Enter your suggestions for improving the selected version:",
                        height=150,
                        value=feedback_repository.get('current_feedback', ''),
                        placeholder="E.g., 'Add more emphasis on leadership skills', 'Include cloud technologies', etc.",
                        key="user_feedback",
                        help="Be specific about what you'd like to change or improve"
                    )
                    
                    # Update current feedback in state
                    if user_feedback != feedback_repository.get('current_feedback', ''):
                        state_manager.update_feedback_repository('current_feedback', user_feedback, source_tab="jd_optimization")
                    
                    # Add feedback button
                    if st.button("➕ Add Feedback", type="secondary", key="add_feedback"):
                        if user_feedback.strip():
                            # Create feedback object
                            feedback_obj = {
                                "feedback": user_feedback,
                                "type": selected_feedback_type,
                                "role": state_manager.get('role', "Unknown"),
                                "timestamp": datetime.datetime.now().isoformat()
                            }
                            
                            # Add to feedback history
                            history = feedback_repository.get('history', [])
                            history.append(feedback_obj)
                            state_manager.update_feedback_repository('history', history, source_tab="jd_optimization")
                            
                            # Clear current feedback
                            state_manager.update_feedback_repository('current_feedback', '', source_tab="jd_optimization")
                            
                            # Log to logger
                            if logger:
                                logger.log_feedback(user_feedback, selected_feedback_type)
                            
                            # Display success message
                            display_success_message("Feedback added successfully!")
                            
                            # Force refresh
                            st.rerun()
                        else:
                            display_warning_message("Please enter some feedback first.")
                
                # Get final version from repository
                final_version = jd_repository.get('final_version')
                
                # Alternative: Check for final version in session state
                if final_version is None and 'final_enhanced_version' in st.session_state:
                    final_version = st.session_state.final_enhanced_version
                    # Update repository for consistency
                    state_manager.update_jd_repository('final_version', final_version, source_tab="jd_optimization")
                
                # Generate Final JD Button
                if st.button("🚀 Generate Final Enhanced Version", type="primary", key="generate_final_jd"):
                    try:
                        with st.spinner("Enhancing job description with feedback..."):
                            # Log version selection if using logger
                            if logger:
                                logger.log_version_selection(selected_index)
                            
                            # Get base version
                            base_description = enhanced_versions[selected_index]
                            
                            # Get feedback history
                            feedback_history = state_manager.get('feedback_repository', {}).get('history', [])
                            
                            # Generate final JD using AI agent
                            final_description = agent.generate_final_description(
                                base_description, feedback_history
                            )
                            
                            # Store in session state
                            st.session_state.final_enhanced_version = final_description
                            
                            # Update state
                            state_manager.update_jd_repository('final_version', final_description, source_tab="jd_optimization")
                            final_version = final_description
                            
                            # Log to logger
                            if logger:
                                logger.log_enhanced_version(final_description, is_final=True)
                            
                            display_success_message("Final version generated successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        return
                
                # Display Final Version if available
                if final_version:
                    st.markdown("---")
                    display_subsection_header("✅ Final Enhanced Job Description")
                    
                    # Display the final enhanced version
                    st.text_area(
                        "Final Content", 
                        final_version, 
                        height=400, 
                        key="final_description"
                    )
                    
                    # Create two columns for the summaries
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Changes from Original")
                        
                        with st.spinner("Generating summary..."):
                            # Generate summary compared to original
                            summary_vs_original = agent.generate_version_summary(jd_content, final_version)
                            
                            # Process summary into bullet points if it's not already in that format
                            if not summary_vs_original.strip().startswith("•"):
                                # Split into sentences and convert to bullet points
                                sentences = [s.strip() for s in summary_vs_original.split('.') if s.strip()]
                                bullet_summary = "\n".join([f"• {sentence}." for sentence in sentences if sentence])
                            else:
                                bullet_summary = summary_vs_original
                            
                            st.markdown(
                                f"""
                                <div style="background-color: #2D3748; padding: 12px; border-radius: 5px; border-left: 4px solid #4299E1;">
                                    <div style="color: #FFFFFF; font-size: 0.9em;">
                                        {bullet_summary}
                                    </div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                    
                    with col2:
                        st.markdown(f"### Changes from Version {selected_index + 1}")
                        
                        with st.spinner("Generating summary..."):
                            # Generate summary compared to base version
                            base_version = enhanced_versions[selected_index]
                            summary_vs_base = agent.generate_version_summary(base_version, final_version)
                            
                            # Process summary into bullet points if it's not already in that format
                            if not summary_vs_base.strip().startswith("•"):
                                # Split into sentences and convert to bullet points
                                sentences = [s.strip() for s in summary_vs_base.split('.') if s.strip()]
                                bullet_summary = "\n".join([f"• {sentence}." for sentence in sentences if sentence])
                            else:
                                bullet_summary = summary_vs_base
                            
                            st.markdown(
                                f"""
                                <div style="background-color: #2D3748; padding: 12px; border-radius: 5px; border-left: 4px solid #38A169;">
                                    <div style="color: #FFFFFF; font-size: 0.9em;">
                                        {bullet_summary}
                                    </div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                    
                    # Compare original vs final JD with skill analysis
                    display_subsection_header("📊 Final Analysis")
                    
                    # Calculate scores
                    original_scores = analyzer.analyze_text(jd_content)
                    final_scores = analyzer.analyze_text(final_version)
                    
                    # Update analytics repository
                    analytics_repository = state_manager.get('analytics_repository', {})
                    analytics_repository['final_scores'] = final_scores
                    state_manager.set('analytics_repository', analytics_repository)
                    
                    # Create comparison charts
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        final_radar = create_multi_radar_chart({'Original': original_scores, 'Final': final_scores})
                        st.plotly_chart(final_radar, use_container_width=True, key="final_radar")
                    
                    with col2:
                        final_comparison_df = create_comparison_dataframe({'Original': original_scores, 'Final': final_scores})
                        st.dataframe(
                            final_comparison_df,
                            height=400,
                            use_container_width=True,
                            hide_index=True,
                            key="final_comparison"
                        )
                    
                    # Download Final JD
                    display_subsection_header("📥 Download Options")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="Download as TXT", 
                            data=final_version, 
                            file_name=f"enhanced_jd_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
                            mime="text/plain", 
                            key="download_txt"
                        )
                        if logger:
                            logger.log_download("txt", f"enhanced_jd_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                    
                    with col2:
                        if st.button("Download as DOCX", key="download_docx"):
                            docx_filename = f"enhanced_jd_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                            save_enhanced_jd(final_version, docx_filename, 'docx')
                            display_success_message(f"Saved as {docx_filename}")
                            if logger:
                                logger.log_download("docx", docx_filename)
                    
                    # Select JD for Candidate Ranking
                    st.markdown("---")
                    display_subsection_header("🎯 Use for Candidate Ranking")
                    
                    # Create options for different JD versions
                    jd_options = [
                        {"label": "Final Enhanced Version", "value": "final", "description": "The final enhanced version with all feedback incorporated"},
                        {"label": f"Enhanced Version {selected_index + 1}", "value": f"enhanced_{selected_index}", "description": f"Enhanced version {selected_index + 1} without final feedback"},
                        {"label": "Original Version", "value": "original", "description": "The original unenhanced job description"}
                    ]
                    
                    st.markdown("""
                    <div style="background-color: #2D3748; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <h4 style="margin-top: 0; color: #90CDF4;">Select which version to use for candidate ranking</h4>
                        <p>Choose which job description version you want to use when ranking candidates.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display radio buttons for JD selection
                    selected_jd_version = st.radio(
                        "Job Description Version for Candidate Ranking:",
                        options=[option["label"] for option in jd_options],
                        index=0,  # Default to final version
                        key="jd_version_for_ranking",
                        help="This version will be used when you proceed to candidate ranking"
                    )
                    
                    # Find the selected option
                    selected_option = next((option for option in jd_options if option["label"] == selected_jd_version), jd_options[0])
                    
                    # When the user clicks the button to proceed to candidate ranking
                    if st.button("🎯 Continue to Candidate Ranking", type="primary", key="goto_ranking_btn"):
                        # Set the selected JD version based on user choice
                        if selected_option["value"] == "final":
                            state_manager.update_jd_repository('for_candidate_ranking', {
                                'content': final_version,
                                'source': f"Final Enhanced Version of {jd_source_name}",
                                'version_type': 'final'
                            }, source_tab="jd_optimization")
                        elif selected_option["value"].startswith("enhanced_"):
                            version_idx = int(selected_option["value"].split("_")[1])
                            state_manager.update_jd_repository('for_candidate_ranking', {
                                'content': enhanced_versions[version_idx],
                                'source': f"Enhanced Version {version_idx + 1} of {jd_source_name}",
                                'version_type': 'enhanced'
                            }, source_tab="jd_optimization")
                        else:  # original
                            state_manager.update_jd_repository('for_candidate_ranking', {
                                'content': jd_content,
                                'source': f"Original Version of {jd_source_name}",
                                'version_type': 'original'
                            }, source_tab="jd_optimization")
                        
                        # Switch to Candidate Ranking tab
                        state_manager.set('active_tab', "Candidate Ranking")
                        st.rerun()
        else:
            # Show message if no JD is selected yet or selection not confirmed
            if selected_source:
                st.info("Please select a job description and click the select button to continue.")
    
    # Feedback History Tab Content
    with main_tabs[1]:
        display_feedback_history_tab(state_manager, services)

def display_feedback_history_tab(state_manager, services):
    """
    Display the feedback history tab
    
    Args:
        state_manager: The global state manager
        services (dict): Dictionary of services
    """
    display_section_header("📝 Feedback History")
    
    # Get feedback repository
    feedback_repository = state_manager.get('feedback_repository', {})
    feedback_history = feedback_repository.get('history', [])
    
    if not feedback_history:
        st.info("No feedback history available yet.")
        return
    
    # Process feedback history
    import pandas as pd
    feedback_data = []
    
    for i, feedback in enumerate(feedback_history):
        # Extract feedback details
        feedback_text = feedback.get("feedback", "") if isinstance(feedback, dict) else feedback
        feedback_type = feedback.get("type", "General Feedback") if isinstance(feedback, dict) else "General Feedback"
        feedback_role = feedback.get("role", "Unknown") if isinstance(feedback, dict) else "Unknown"
        timestamp = feedback.get("timestamp", "")
        
        # Format timestamp
        formatted_time = "Unknown"
        if timestamp:
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = str(timestamp)
        
        # Add to feedback data
        feedback_data.append({
            "ID": i + 1,
            "Time": formatted_time,
            "Type": feedback_type,
            "Role": feedback_role,
            "Job Description": state_manager.get('jd_repository', {}).get('source_name', 'Unknown'),
            "Feedback": feedback_text
        })
    
    # Create filtering options
    st.subheader("Filter Feedback")
    
    # Create filter columns
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        # Get unique feedback types
        feedback_types = sorted(list(set(item["Type"] for item in feedback_data)))
        selected_types = st.multiselect("Filter by Type:", feedback_types, default=[], key="filter_types")
    
    with filter_col2:
        # Get unique roles
        roles = sorted(list(set(item["Role"] for item in feedback_data)))
        selected_roles = st.multiselect("Filter by Role:", roles, default=[], key="filter_roles")
    
    # Text search
    search_term = st.text_input("Search in feedback:", "", key="feedback_search")
    
    # Apply filters
    filtered_data = feedback_data
    
    if selected_types:
        filtered_data = [item for item in filtered_data if item["Type"] in selected_types]
    
    if selected_roles:
        filtered_data = [item for item in filtered_data if item["Role"] in selected_roles]
    
    if search_term:
        filtered_data = [item for item in filtered_data if search_term.lower() in item["Feedback"].lower()]
    
    # Convert to DataFrame for display
    df = pd.DataFrame(filtered_data)
    
    # Display filter summary
    st.write(f"Showing {len(filtered_data)} of {len(feedback_data)} feedback items")
    
    # Display the table
    if not df.empty:
        # Configure columns for display
        column_config = {
            "ID": st.column_config.NumberColumn("ID", help="Feedback ID"),
            "Time": st.column_config.TextColumn("Time", help="When feedback was provided"),
            "Type": st.column_config.TextColumn("Type", help="Type of feedback"),
            "Role": st.column_config.TextColumn("Role", help="Role of the person who provided feedback"),
            "Job Description": st.column_config.TextColumn("JD", help="Job description the feedback was for"),
            "Feedback": st.column_config.TextColumn("Feedback Content", width="large")
        }
        
        st.dataframe(
            df,
            use_container_width=True,
            column_config=column_config,
            hide_index=True
        )
        
        # Export option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export Filtered Feedback",
            data=csv,
            file_name=f"feedback_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No feedback matches the selected filters.")