import streamlit as st
import datetime
import os
from ui.common import (
    display_section_header, display_subsection_header, 
    display_warning_message, display_info_message, display_success_message
)
from utils.file_utils import save_enhanced_jd

def render_jd_creation_page(services):
    """
    Render the JD Creation page for Hiring Managers
    
    Args:
        services (dict): Dictionary of shared services
    """
    # Unpack services
    logger = services.get('logger')
    analyzer = services.get('analyzer')
    agent = services.get('agent')
    state_manager = services.get('state_manager')
    
    display_section_header("✍️ Job Description Creation")
    
    st.markdown("""
    <div class="highlight-box">
        As a Hiring Manager, you can create a new job description from scratch or use a template. 
        This job description will be used for candidate sourcing, screening, and hiring.
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different creation methods
    creation_tabs = st.tabs(["Create from Scratch", "Use Template", "AI Assistant"])
    
    # Tab 1: Create from Scratch
    with creation_tabs[0]:
        display_subsection_header("Create a New Job Description")
        

        job_title = st.text_input("Job Title:", 
                placeholder="e.g., Senior Software Engineer",
                help="Enter the title for this position")

        
        # Job description sections
        st.markdown("### Job Description Content")
        
        # Overview
        overview = st.text_area("Overview:",
            placeholder="Provide a brief overview of the role and its importance to the organization.",
            height=100)
        
        # Responsibilities
        responsibilities = st.text_area("Responsibilities:",
            placeholder="List the key responsibilities and duties for this role. Use bullet points (- item) for clarity.",
            height=150)
        
        # Requirements
        requirements = st.text_area("Requirements:",
            placeholder="List the required skills, qualifications, and experience. Use bullet points (- item) for clarity.",
            height=150)
        
        # Preferred skills (optional)
        preferred = st.text_area("Preferred Skills (Optional):",
            placeholder="List any preferred or nice-to-have skills. Use bullet points (- item) for clarity.",
            height=100)
        
        # Benefits (optional)
        benefits = st.text_area("Benefits & Perks (Optional):",
            placeholder="List company benefits and perks. Use bullet points (- item) for clarity.",
            height=100)
        
        # Combine all sections into a complete job description
        if st.button("Generate Job Description", type="primary"):
            if not job_title or not responsibilities or not requirements:
                display_warning_message("Please fill in the required fields: Job Title, Responsibilities, and Requirements.")
            else:
                complete_jd = f"""# {job_title}
                
## Overview
{overview}

## Department
{department}

## Location
{job_location}

## Employment Type
{job_type}

## Experience Level
{experience_level}

## Responsibilities
{responsibilities}

## Requirements
{requirements}
"""
                
                # Add optional sections if provided
                if preferred:
                    complete_jd += f"\n## Preferred Skills\n{preferred}\n"
                
                if benefits:
                    complete_jd += f"\n## Benefits & Perks\n{benefits}\n"
                
                # Add generated timestamp
                complete_jd += f"\n\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d')}"
                
                # Store in state manager
                state_manager.update_jd_repository('original', complete_jd, source_tab="jd_creation")
                state_manager.update_jd_repository('source_name', f"{job_title} - Created by {state_manager.get('role')}", source_tab="jd_creation")
                state_manager.update_jd_repository('unique_id', f"created_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}", source_tab="jd_creation")
                
                # Reset versions
                state_manager.update_jd_repository('enhanced_versions', [], source_tab="jd_creation")
                state_manager.update_jd_repository('selected_version_idx', 0, source_tab="jd_creation")
                state_manager.update_jd_repository('final_version', None, source_tab="jd_creation")
                
                # Log if logger is available
                if logger:
                    logger.log_file_selection(f"{job_title} - Created", complete_jd)
                
                display_success_message("Job description created successfully!")
                
                # Show the created JD
                st.markdown("### Created Job Description")
                st.text_area("Preview", complete_jd, height=400, disabled=True)
                
                # Offer to proceed to optimization
                if st.button("Continue to JD Optimization", key="proceed_to_optimization"):
                    state_manager.set('active_tab', "JD Optimization")
                    st.rerun()
    
    # Tab 2: Use Template
    with creation_tabs[1]:
        display_subsection_header("Select a Template")
        
        # Display template options
        templates = {
            "Software Engineer": """# Software Engineer

## Overview
We are seeking a talented Software Engineer to join our team, responsible for designing, developing, and maintaining our software applications. This role will collaborate with cross-functional teams to deliver high-quality software solutions.

## Responsibilities
- Design, develop, and maintain software applications
- Write clean, scalable, and efficient code
- Collaborate with cross-functional teams to define, design, and ship new features
- Identify and fix bugs and performance issues
- Participate in code reviews and technical discussions

## Requirements
- Bachelor's degree in Computer Science, Engineering, or related field
- 2+ years of professional software development experience
- Proficiency in one or more programming languages (Java, Python, JavaScript, etc.)
- Experience with software development methodologies
- Strong problem-solving skills and attention to detail

## Preferred Skills
- Experience with cloud platforms (AWS, Azure, GCP)
- Knowledge of CI/CD pipelines
- Experience with containerization technologies
- Familiarity with Agile development practices
""",
            "Data Scientist": """# Data Scientist

## Overview
We are looking for a Data Scientist to help us discover insights from data and build machine learning models. You will work with stakeholders to understand business needs and develop data-driven solutions.

## Responsibilities
- Collect, process, and analyze large datasets
- Build predictive models and machine learning algorithms
- Collaborate with product and engineering teams to implement data solutions
- Communicate results and insights to stakeholders
- Stay up-to-date with the latest industry trends and technologies

## Requirements
- Master's or PhD in Computer Science, Statistics, Mathematics, or related field
- 3+ years of experience in data science or related field
- Strong programming skills in Python, R, or similar languages
- Experience with machine learning frameworks and libraries
- Excellent communication and presentation skills

## Preferred Skills
- Experience with big data technologies (Hadoop, Spark)
- Knowledge of deep learning frameworks
- Experience with data visualization tools
- Background in natural language processing or computer vision
""",
            "Product Manager": """# Product Manager

## Overview
We are seeking a Product Manager to lead the development and launch of our products. This role will drive product strategy, gather requirements, and work with cross-functional teams to deliver exceptional products.

## Responsibilities
- Define product vision, strategy, and roadmap
- Gather and prioritize product requirements from stakeholders
- Work closely with engineering, design, and marketing teams
- Analyze market trends and competitive landscape
- Monitor product performance and user feedback

## Requirements
- Bachelor's degree in Business, Computer Science, or related field
- 3+ years of experience in product management
- Strong analytical and problem-solving skills
- Excellent communication and presentation abilities
- Experience with product development methodologies

## Preferred Skills
- MBA or other advanced degree
- Technical background or experience
- Experience with Agile development methodologies
- Knowledge of user research and testing techniques
""",
        }
        
        # Template selection
        selected_template = st.selectbox(
            "Choose a Template:",
            options=list(templates.keys()),
            help="Select a job description template as a starting point"
        )
        
        # Display selected template
        st.markdown("### Template Preview")
        st.text_area("Template Content", templates[selected_template], height=300, disabled=True)
        
        # Allow customization
        customize = st.checkbox("Customize this template")
        
        if customize:
            # Pre-fill with selected template
            customized_jd = st.text_area(
                "Customized Job Description:",
                value=templates[selected_template],
                height=400,
                help="Modify the template to fit your needs"
            )
            
            # Use the customized version
            if st.button("Use Customized Template", type="primary"):
                # Store in state manager
                state_manager.update_jd_repository('original', customized_jd, source_tab="jd_creation")
                state_manager.update_jd_repository('source_name', f"{selected_template} - Customized by {state_manager.get('role')}", source_tab="jd_creation")
                state_manager.update_jd_repository('unique_id', f"template_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}", source_tab="jd_creation")
                
                # Reset versions
                state_manager.update_jd_repository('enhanced_versions', [], source_tab="jd_creation")
                state_manager.update_jd_repository('selected_version_idx', 0, source_tab="jd_creation")
                state_manager.update_jd_repository('final_version', None, source_tab="jd_creation")
                
                # Log if logger is available
                if logger:
                    logger.log_file_selection(f"{selected_template} - Customized", customized_jd)
                
                display_success_message("Customized template applied successfully!")
                
                # Offer to proceed to optimization
                if st.button("Continue to JD Optimization", key="template_to_optimization"):
                    state_manager.set('active_tab', "JD Optimization")
                    st.rerun()
        else:
            # Use the template as-is
            if st.button("Use This Template", type="primary"):
                template_content = templates[selected_template]
                
                # Store in state manager
                state_manager.update_jd_repository('original', template_content, source_tab="jd_creation")
                state_manager.update_jd_repository('source_name', f"{selected_template} Template", source_tab="jd_creation")
                state_manager.update_jd_repository('unique_id', f"template_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}", source_tab="jd_creation")
                
                # Reset versions
                state_manager.update_jd_repository('enhanced_versions', [], source_tab="jd_creation")
                state_manager.update_jd_repository('selected_version_idx', 0, source_tab="jd_creation")
                state_manager.update_jd_repository('final_version', None, source_tab="jd_creation")
                
                # Log if logger is available
                if logger:
                    logger.log_file_selection(f"{selected_template} Template", template_content)
                
                display_success_message(f"{selected_template} template applied successfully!")
                
                # Offer to proceed to optimization
                if st.button("Continue to JD Optimization", key="template_direct_to_optimization"):
                    state_manager.set('active_tab', "JD Optimization")
                    st.rerun()
    
    # Tab 3: AI Assistant
    with creation_tabs[2]:
        display_subsection_header("AI-Assisted Job Description Creation")
        
        st.markdown("""
        <div class="highlight-box">
            Let our AI assistant help you create a job description by answering a few questions about the role.
            The AI will generate a comprehensive job description that you can review and edit.
        </div>
        """, unsafe_allow_html=True)
        
        # Gather information for the AI
        job_title = st.text_input("Job Title:", 
            placeholder="e.g., Full Stack Developer",
            key="ai_job_title",
            help="Enter the title for this position")
        
        department = st.text_input("Department:",
            placeholder="e.g., Engineering",
            key="ai_department",
            help="Enter the department for this position")
        
        experience_level = st.selectbox("Experience Level:",
            options=["Entry Level", "Mid-Level", "Senior", "Lead", "Principal", "Director"],
            key="ai_experience",
            help="Select the experience level required for this position")
        
        # Key skills and technologies
        key_skills = st.text_area("Key Skills & Technologies:",
            placeholder="List the key skills and technologies required for this role (comma-separated)",
            height=100,
            key="ai_skills",
            help="Enter skills like: Python, React, AWS, data analysis, etc.")
        
        # Primary responsibilities
        responsibilities = st.text_area("Primary Responsibilities:",
            placeholder="Briefly describe the main responsibilities of this role",
            height=150,
            key="ai_responsibilities",
            help="What will this person be doing on a day-to-day basis?")
        
        # Company info
        company_info = st.text_area("About Your Company (Optional):",
            placeholder="Brief description of your company, industry, and culture",
            height=100,
            key="ai_company",
            help="This helps contextualize the job description")
        
        # Generate the JD with AI
        if st.button("Generate with AI", type="primary"):
            if not job_title or not key_skills or not responsibilities:
                display_warning_message("Please provide at least: Job Title, Key Skills, and Primary Responsibilities.")
            else:
                with st.spinner("Creating your job description with AI..."):
                    try:
                        # Construct prompt for the AI
                        prompt = f"""Create a comprehensive job description for a {job_title} position.

Information:
- Department: {department}
- Experience Level: {experience_level}
- Key Skills & Technologies: {key_skills}
- Primary Responsibilities: {responsibilities}
- Company Info: {company_info if company_info else "A growing company in the technology sector"}

Please format the job description with the following sections:
1. Overview
2. Responsibilities
3. Requirements
4. Preferred Qualifications
5. Benefits/Perks (generic if not specified)

Make the job description engaging, detailed, and professional. Use bullet points for clarity.
"""
                        
                        # Call the agent to generate the JD
                        if agent and agent.client:
                            model_response = agent._invoke_bedrock_model(prompt)
                            if model_response and "content" in model_response and isinstance(model_response["content"], list):
                                ai_generated_jd = model_response["content"][0]["text"].strip()
                            else:
                                # Fallback if response format is unexpected
                                raise Exception("Unexpected response format from AI service")
                        else:
                            # Simulate response if agent is not available
                            ai_generated_jd = f"""# {job_title}

## Overview
We are seeking an experienced {job_title} to join our {department} team. This role will be responsible for developing and maintaining our core products, working with cross-functional teams to deliver high-quality solutions.

## Responsibilities
- Design, develop, and maintain applications using {key_skills}
- Collaborate with product managers, designers, and other engineers
- Write clean, efficient, and maintainable code
- Participate in code reviews and technical discussions
- {responsibilities}

## Requirements
- {experience_level} experience in software development
- Proficiency in {key_skills}
- Strong problem-solving skills and attention to detail
- Excellent communication and teamwork abilities
- Bachelor's degree in Computer Science or related field (or equivalent experience)

## Preferred Qualifications
- Experience with additional technologies in our stack
- Contributions to open-source projects
- Experience in Agile development methodologies
- Understanding of software development best practices

## Benefits/Perks
- Competitive salary and benefits package
- Flexible work arrangements
- Professional development opportunities
- Collaborative and innovative work environment
- Regular team building activities and events

{company_info if company_info else ""}
"""
                        
                        # Store in state manager
                        state_manager.update_jd_repository('original', ai_generated_jd, source_tab="jd_creation")
                        state_manager.update_jd_repository('source_name', f"{job_title} - AI Generated", source_tab="jd_creation")
                        state_manager.update_jd_repository('unique_id', f"ai_generated_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}", source_tab="jd_creation")
                        
                        # Reset versions
                        state_manager.update_jd_repository('enhanced_versions', [], source_tab="jd_creation")
                        state_manager.update_jd_repository('selected_version_idx', 0, source_tab="jd_creation")
                        state_manager.update_jd_repository('final_version', None, source_tab="jd_creation")
                        
                        # Log if logger is available
                        if logger:
                            logger.log_file_selection(f"{job_title} - AI Generated", ai_generated_jd)
                        
                        display_success_message("AI-generated job description created successfully!")
                        
                        # Show the created JD
                        st.markdown("### AI-Generated Job Description")
                        
                        # Allow editing of the AI-generated content
                        edited_ai_jd = st.text_area("Edit if needed:", 
                            value=ai_generated_jd, 
                            height=400,
                            key="edit_ai_jd")
                        
                        if edited_ai_jd != ai_generated_jd:
                            if st.button("Save Edited Version", key="save_edited_ai"):
                                # Update with edited version
                                state_manager.update_jd_repository('original', edited_ai_jd, source_tab="jd_creation")
                                display_success_message("Edited version saved!")
                        
                        # Offer to proceed to optimization
                        if st.button("Continue to JD Optimization", key="ai_to_optimization"):
                            state_manager.set('active_tab', "JD Optimization")
                            st.rerun()
                            
                    except Exception as e:
                        display_warning_message(f"Error generating job description: {str(e)}")
                        st.error("Please try again or use one of the other creation methods.")
        
    # Save JD to file option
    st.markdown("---")
    display_subsection_header("Save Job Description")
    
    # Get current JD content if available
    jd_content, jd_source_name, _ = state_manager.get_jd_content()
    
    if jd_content:
        # Save options
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="Download as TXT",
                data=jd_content,
                file_name=f"job_description_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
        with col2:
            if st.button("Save as DOCX"):
                docx_filename = f"job_description_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                save_enhanced_jd(jd_content, docx_filename, 'docx')
                display_success_message(f"Saved as {docx_filename}")
                
                # Log if logger is available
                if logger:
                    logger.log_download("docx", docx_filename)
    else:
        st.info("Create a job description first to enable save options.")