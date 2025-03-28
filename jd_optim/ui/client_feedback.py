import streamlit as st
import os
import datetime
from docx import Document
from ui.common import (
    display_section_header, display_subsection_header,
    display_warning_message, display_info_message, display_success_message
)
from utils.file_utils import read_job_description, read_feedback_file, save_enhanced_jd

def render_client_feedback_page(logger, analyzer, agent):
    """Render the Client Feedback tab with JD + Feedback drop zones"""
    display_section_header("💬 Client Feedback Enhancement")
    
    # Create two columns for file upload
    jd_col, feedback_col = st.columns(2)
    
    with jd_col:
        display_subsection_header("Upload Job Description")
        jd_file = st.file_uploader(
            "📄 Drop or upload a Job Description",
            type=["txt", "docx"],
            key="client_jd_upload",
            help="Upload the job description you want to enhance"
        )
        
        # Optional: Display JD preview if uploaded
        if jd_file:
            try:
                if jd_file.name.endswith(".txt"):
                    job_description = jd_file.getvalue().decode("utf-8")
                else:  # .docx
                    # Save to temporary file to use python-docx
                    temp_path = f"temp_{jd_file.name}"
                    with open(temp_path, 'wb') as f:
                        f.write(jd_file.getvalue())
                    
                    doc = Document(temp_path)
                    job_description = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
                # Store in session state for later use
                st.session_state.client_jd = job_description
                
                # Preview
                with st.expander("Preview Job Description", expanded=False):
                    st.text_area("Job Description Content", job_description, height=200, disabled=True)
            except Exception as e:
                st.error(f"Error reading job description file: {str(e)}")
    
    with feedback_col:
        display_subsection_header("Upload Client Feedback")
        feedback_file = st.file_uploader(
            "📝 Drop or upload Client Feedback",
            type=["txt", "docx"],
            key="client_feedback_upload",
            help="Upload the feedback received from your client"
        )
        
        # Feedback type selection
        feedback_types = [
            "Client Feedback", 
            "Rejected Candidate Feedback", 
            "Hiring Manager Feedback", 
            "Selected Candidate Feedback", 
            "Interview Feedback"
        ]
        
        selected_feedback_type = st.selectbox(
            "Feedback Type:",
            options=feedback_types,
            index=0,
            key="client_feedback_type"
        )
        
        # Optional: Display feedback preview if uploaded
        if feedback_file:
            try:
                if feedback_file.name.endswith(".txt"):
                    client_feedback = feedback_file.getvalue().decode("utf-8")
                else:  # .docx
                    # Save to temporary file to use python-docx
                    temp_path = f"temp_{feedback_file.name}"
                    with open(temp_path, 'wb') as f:
                        f.write(feedback_file.getvalue())
                    
                    doc = Document(temp_path)
                    client_feedback = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
                # Store in session state for later use
                st.session_state.client_feedback = client_feedback
                st.session_state.client_feedback_type = selected_feedback_type
                
                # Preview
                with st.expander("Preview Client Feedback", expanded=False):
                    st.text_area("Feedback Content", client_feedback, height=200, disabled=True)
            except Exception as e:
                st.error(f"Error reading feedback file: {str(e)}")

    # Allow manual feedback input as an alternative to file upload
    with st.expander("Or Enter Feedback Manually", expanded=False):
        manual_feedback = st.text_area(
            "Enter client feedback:",
            height=150,
            placeholder="Enter the feedback from your client here...",
            key="manual_client_feedback"
        )
        
        if st.button("Use This Feedback", key="use_manual_feedback"):
            if manual_feedback.strip():
                st.session_state.client_feedback = manual_feedback
                st.session_state.client_feedback_type = selected_feedback_type
                st.success("Manual feedback saved!")
            else:
                st.warning("Please enter some feedback first.")

    # Generate enhanced JD button
    st.markdown(f"<div class='subsection-header'>Generate Enhanced Job Description</div>", unsafe_allow_html=True)
    
    generate_col1, generate_col2 = st.columns([3, 1])
    
    with generate_col1:
        generate_btn = st.button(
            "🚀 Generate Enhanced Job Description", 
            type="primary", 
            key="generate_client_enhanced_jd",
            help="Generate an enhanced version of the job description based on client feedback"
        )
        
    with generate_col2:
        st.caption("AI will enhance the job description based on the provided client feedback.")
    
    # Handle generation process
    if generate_btn:
        if not hasattr(st.session_state, 'client_jd') or not hasattr(st.session_state, 'client_feedback'):
            st.warning("Please upload both a job description and client feedback before generating.")
            return
        
        job_description = st.session_state.client_jd
        client_feedback = st.session_state.client_feedback
        feedback_type = st.session_state.client_feedback_type
        
        with st.spinner("Enhancing job description with client feedback..."):
            try:
                # Create feedback object with type
                feedback_obj = {
                    "feedback": client_feedback,
                    "type": feedback_type,
                    "role": st.session_state.role
                }
                
                # Add to the logger's feedback history
                logger.current_state["feedback_history"].append(feedback_obj)
                logger._save_state()
                
                # Log the action
                logger.current_state["actions"].append({
                    "action": "client_feedback",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "feedback_type": feedback_type
                })
                logger._save_state()
                
                # Generate enhanced JD using the agent
                enhanced_jd = agent.generate_final_description(
                    job_description,
                    [feedback_obj]
                )
                
                # Store the enhanced JD
                st.session_state.client_enhanced_jd = enhanced_jd
                
                # Log the enhanced version
                logger.log_enhanced_version(enhanced_jd, is_final=True)
                
                # Display success message
                display_success_message("Job description enhanced successfully based on client feedback!")
                
                # Force page refresh to show results
                st.rerun()
            except Exception as e:
                st.error(f"Error enhancing job description: {str(e)}")
                st.error("Please try again or contact support if the problem persists.")
    
    # Display results if generation was successful
    if hasattr(st.session_state, 'client_enhanced_jd'):
        # Display results in an organized layout
        st.markdown("---")
        display_section_header("Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            display_subsection_header("Original Job Description")
            st.text_area(
                "Original Content",
                st.session_state.client_jd,
                height=300,
                disabled=True,
                key="client_original_jd_display"
            )
        
        with col2:
            display_subsection_header("Enhanced Job Description")
            st.text_area(
                "Enhanced Content",
                st.session_state.client_enhanced_jd,
                height=300,
                key="client_enhanced_jd_display"
            )
        
        # Compare original vs enhanced with skill analysis
        if hasattr(st.session_state, 'client_jd') and hasattr(st.session_state, 'client_enhanced_jd'):
            display_section_header("Comparison Analysis")
            
            # Analyze both versions
            original_scores = analyzer.analyze_text(st.session_state.client_jd)
            enhanced_scores = analyzer.analyze_text(st.session_state.client_enhanced_jd)
            
            from utils.visualization import create_multi_radar_chart, create_comparison_dataframe
            
            comp_col1, comp_col2 = st.columns([1, 1])
            
            with comp_col1:
                display_subsection_header("Skill Coverage Comparison")
                radar_chart = create_multi_radar_chart({'Original': original_scores, 'Enhanced': enhanced_scores})
                st.plotly_chart(radar_chart, use_container_width=True, key="client_radar")
            
            with comp_col2:
                display_subsection_header("Detailed Analysis")
                comparison_df = create_comparison_dataframe({'Original': original_scores, 'Enhanced': enhanced_scores})
                st.dataframe(
                    comparison_df,
                    height=400,
                    use_container_width=True,
                    hide_index=True,
                    key="client_comparison"
                )
                st.caption("Percentages indicate keyword coverage in each category")
        
        # Download options
        display_section_header("Download Options")
        
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            st.download_button(
                label="Download as TXT",
                data=st.session_state.client_enhanced_jd,
                file_name=f"client_enhanced_jd_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="client_download_txt"
            )
            logger.log_download("txt", f"client_enhanced_jd_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with download_col2:
            if st.button("Download as DOCX", key="client_download_docx"):
                docx_filename = f"client_enhanced_jd_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                save_enhanced_jd(st.session_state.client_enhanced_jd, docx_filename, 'docx')
                display_success_message(f"Saved as {docx_filename}")
                logger.log_download("docx", docx_filename)