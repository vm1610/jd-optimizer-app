import streamlit as st
from ui.common import display_section_header

def render_interview_prep_page():
    """Render the interview preparation page"""
    display_section_header("Interview Preparation")
    
    # Display "Coming Soon" message with a professional look and improved text visibility
    st.markdown("""
    <div style="text-align: center; padding: 40px; background-color: #2D3748; border-radius: 10px; margin: 20px 0; border: 1px solid #4299E1;">
        <img src="https://img.icons8.com/cotton/100/000000/time-machine--v1.png" alt="Coming Soon" width="64" height="64">
        <h2 style="margin-top: 20px; color: #FFFFFF;">Coming Soon</h2>
        <p style="color: #FFFFFF; max-width: 600px; margin: 0 auto; padding: 10px 0;">
            We're working on an advanced interview preparation module to help you create structured interview 
            questions, evaluation criteria, and candidate scoring templates based on your job descriptions.
        </p>
        <p style="color: #FFFFFF; max-width: 600px; margin: 10px auto;">
            Stay tuned for updates! This feature will be available in the next release.
        </p>
    </div>
    """, unsafe_allow_html=True)