import streamlit as st
import datetime
import os
import json
from ui.common import (
    display_section_header, display_subsection_header, 
    display_warning_message, display_info_message, display_success_message
)
from utils.file_utils import save_enhanced_jd

# Company description to add to all job descriptions
COMPANY_DESCRIPTION = """**About Apexon:**
 
Apexon is a digital-first technology services firm specializing in accelerating business transformation and delivering human-centric digital experiences. We have been meeting customers wherever they are in the digital lifecycle and helping them outperform their competition through speed and innovation.
 
Apexon brings together distinct core competencies – in AI, analytics, app development, cloud, commerce, CX, data, DevOps, IoT, mobile, quality engineering and UX, and our deep expertise in BFSI, healthcare, and life sciences – to help businesses capitalize on the unlimited opportunities digital offers. Our reputation is built on a comprehensive suite of engineering services, a dedication to solving clients' toughest technology problems, and a commitment to continuous improvement. 
 
Backed by Goldman Sachs Asset Management and Everstone Capital, Apexon now has a global presence of 15 offices (and 10 delivery centers) across four continents. 

We enable #HumanFirstDIGITAL
"""

# Standard benefits to add to all job descriptions
STANDARD_BENEFITS = """**Our Perks and Benefits:** 
Our benefits and rewards program has been thoughtfully designed to recognize your skills and contributions, elevate your learning/upskilling experience and provide care and support for you and your loved ones. 
 
As an Apexer, you get continuous skill-based development, opportunities for career advancement, and access to comprehensive health and well-being benefits and assistance.
 
**We also offer:**
1. Health Insurance with Dental & Vision
2. 401K Plan
3. Life Insurance, STD & LTD
4. Paid Vacations & Holidays
5. Paid Parental Leave
6. FSA Dependent & Limited Purpose care
7. Learning & Development
"""

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
    creation_tabs = st.tabs(["Create New JD", "Use Template"])
    
    # Tab 1: Create New JD (Merged Manual + AI Creation)
    with creation_tabs[0]:
        display_subsection_header("Create a New Job Description")
        
        # Common fields for both manual and AI creation
        job_title = st.text_input("Job Title:", 
                placeholder="e.g., Senior Software Engineer",
                help="Enter the title for this position")
                
     

        # Creation method selection
        st.markdown("### Creation Method")
        creation_method = st.radio(
            "How would you like to create this job description?",
            options=["Create Manually", "Generate with AI"],
            horizontal=True
        )
        
        if creation_method == "Create Manually":
            # Manual creation fields
            st.markdown("### Job Description Details")
            
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
            
            # Combine all sections into a complete job description
            if st.button("Generate Job Description", type="primary"):
                if not job_title or not responsibilities or not requirements:
                    display_warning_message("Please fill in the required fields: Job Title, Responsibilities, and Requirements.")
                else:
                    complete_jd = f"""# {job_title}

{COMPANY_DESCRIPTION}

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
                    
                    # Add standard benefits section
                    complete_jd += f"\n{STANDARD_BENEFITS}\n"
                    
                    # Add generated timestamp
                    complete_jd += f"\n\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d')}"
                    
                    # Store in state manager
                    save_and_display_jd(complete_jd, job_title, state_manager, logger, "jd_creation")
                    
        else:  # AI Generation
            # Additional fields for AI generation
            st.markdown("### AI Generation Details")
            
            # Key skills and technologies
            key_skills = st.text_area("Key Skills & Technologies:",
                placeholder="List the key skills and technologies required for this role (comma-separated)",
                height=100,
                key="ai_skills",
                help="Enter skills like: Python, React, AWS, data analysis, etc.")
            
            # Primary responsibilities
            primary_responsibilities = st.text_area("Primary Responsibilities:",
                placeholder="Briefly describe the main responsibilities of this role",
                height=150,
                key="ai_responsibilities",
                help="What will this person be doing on a day-to-day basis?")
            
            # Generate the JD with AI
            if st.button("Generate with AI", type="primary"):
                if not job_title or not key_skills or not primary_responsibilities:
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
- Primary Responsibilities: {primary_responsibilities}
- Location: {job_location}
- Employment Type: {job_type}

Please format the job description with the following sections:
1. Overview
2. Responsibilities
3. Requirements
4. Preferred Qualifications

Make the job description engaging, detailed, and professional. Use bullet points for clarity.
DO NOT include company information or benefits, as these will be added separately.
"""
                            
                            # Call the agent to generate the JD
                            if agent and agent.client:
                                model_response = agent._invoke_bedrock_model(prompt)
                                if model_response and "content" in model_response and isinstance(model_response["content"], list):
                                    ai_content = model_response["content"][0]["text"].strip()
                                else:
                                    # Fallback if response format is unexpected
                                    raise Exception("Unexpected response format from AI service")
                            else:
                                # Simulate response if agent is not available
                                ai_content = f"""# {job_title}

## Overview
We are seeking an experienced {job_title} to join our {department} team. This role will be responsible for developing and maintaining our core products, working with cross-functional teams to deliver high-quality solutions.

## Responsibilities
- Design, develop, and maintain applications using {key_skills}
- Collaborate with product managers, designers, and other engineers
- Write clean, efficient, and maintainable code
- Participate in code reviews and technical discussions
- {primary_responsibilities}

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
"""
                            
                            # Add company description and benefits
                            complete_jd = f"# {job_title}\n\n{COMPANY_DESCRIPTION}\n\n{ai_content.split('# ')[1]}\n\n{STANDARD_BENEFITS}"
                            
                            # Add generated timestamp
                            complete_jd += f"\n\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d')}"
                            
                            # Store in state manager
                            save_and_display_jd(complete_jd, job_title, state_manager, logger, "jd_creation")
                                
                        except Exception as e:
                            display_warning_message(f"Error generating job description: {str(e)}")
                            st.error("Please try again or use manual creation.")
    
    # Tab 2: Use Template
    with creation_tabs[1]:
        display_subsection_header("Select a Template")
        
        # Load existing templates
        templates = load_templates()
        
        # Display template options
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
                customized_jd_with_company = ensure_company_info(customized_jd)
                
                job_title = extract_job_title(customized_jd) or selected_template
                save_and_display_jd(customized_jd_with_company, f"{job_title} - Customized", 
                                  state_manager, logger, "jd_creation")
                
        else:
            # Use the template as-is
            if st.button("Use This Template", type="primary"):
                template_content = ensure_company_info(templates[selected_template])
                
                save_and_display_jd(template_content, selected_template, 
                                  state_manager, logger, "jd_creation")
                
    # Get current JD content if available for download options
    show_download_options(state_manager, logger)

def save_and_display_jd(jd_content, title_prefix, state_manager, logger, source_tab):
    """Helper function to save and display a job description"""
    # Store in state manager
    state_manager.update_jd_repository('original', jd_content, source_tab=source_tab)
    state_manager.update_jd_repository('source_name', f"{title_prefix} - Created by {state_manager.get('role')}", source_tab=source_tab)
    state_manager.update_jd_repository('unique_id', f"created_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}", source_tab=source_tab)
    
    # Reset versions
    state_manager.update_jd_repository('enhanced_versions', [], source_tab=source_tab)
    state_manager.update_jd_repository('selected_version_idx', 0, source_tab=source_tab)
    state_manager.update_jd_repository('final_version', None, source_tab=source_tab)
    
    # Add to templates if not already there
    add_to_templates(jd_content, title_prefix)
    
    # Log if logger is available
    if logger:
        logger.log_file_selection(f"{title_prefix} - Created", jd_content)
    
    display_success_message("Job description created successfully!")
    
    # Show the created JD
    st.markdown("### Created Job Description")
    st.text_area("Preview", jd_content, height=400, disabled=True)
    
    # Offer to proceed to optimization
    if st.button("Continue to JD Optimization", key="proceed_to_optimization"):
        state_manager.set('active_tab', "JD Optimization")
        st.rerun()

def extract_job_title(jd_content):
    """Extract job title from JD content"""
    lines = jd_content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line.replace('# ', '').strip()
    return "Job Description"

def ensure_company_info(jd_content):
    """Ensure job description has company info and benefits"""
    # Check if company description is already included
    if "About Apexon" not in jd_content:
        # Find the first heading and insert company info after it
        lines = jd_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# '):
                lines.insert(i+1, "\n" + COMPANY_DESCRIPTION + "\n")
                break
        jd_content = '\n'.join(lines)
    
    # Check if benefits section is already included
    if "Our Perks and Benefits" not in jd_content:
        # Add benefits at the end
        jd_content += f"\n\n{STANDARD_BENEFITS}"
    
    return jd_content

def load_templates():
    """Load job description templates including user-created ones"""
    # Base templates
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
"""
    }
    
    # Try to load custom templates
    try:
        templates_dir = os.path.join(os.getcwd(), "jd_optim_OOP_implement(vasu)", "Data", "Templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        templates_file = os.path.join(templates_dir, "custom_templates.json")
        if os.path.exists(templates_file):
            with open(templates_file, 'r') as f:
                custom_templates = json.load(f)
                # Merge with base templates, custom templates take priority
                templates.update(custom_templates)
    except Exception as e:
        st.error(f"Error loading custom templates: {str(e)}")
    
    return templates

def add_to_templates(jd_content, template_name):
    """Add a new JD to the templates database"""
    try:
        templates_dir = os.path.join(os.getcwd(), "jd_optim_OOP_implement(vasu)", "Data", "Templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        templates_file = os.path.join(templates_dir, "custom_templates.json")
        
        # Load existing custom templates
        custom_templates = {}
        if os.path.exists(templates_file):
            with open(templates_file, 'r') as f:
                custom_templates = json.load(f)
        
        # Add new template if not already exists
        if template_name not in custom_templates:
            custom_templates[template_name] = jd_content
            
            # Save updated templates
            with open(templates_file, 'w') as f:
                json.dump(custom_templates, f, indent=2)
    except Exception as e:
        st.warning(f"Could not save template: {str(e)}")

def show_download_options(state_manager, logger):
    """Display download options for the current JD"""
    jd_content, jd_source_name, _ = state_manager.get_jd_content()
    
    if jd_content:
        st.markdown("---")
        display_subsection_header("Save Job Description")
        
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