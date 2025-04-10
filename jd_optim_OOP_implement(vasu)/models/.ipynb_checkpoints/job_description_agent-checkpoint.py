import json
import re
import boto3
import streamlit as st

class JobDescriptionAgent:
    """Agent for enhancing job descriptions using AWS Bedrock Claude"""
    def __init__(self, model_id, max_tokens=10000, temperature=0.7):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize AWS client for Bedrock
        try:
            # Use Streamlit secrets for credentials in production
            self.client = boto3.client(
                service_name='bedrock-runtime',
                aws_access_key_id=st.secrets["aws"]["access_key"],
                aws_secret_access_key=st.secrets["aws"]["secret_key"],
                region_name=st.secrets["aws"]["region"],
            )
        except Exception as e:
            print(f"Error initializing AWS Bedrock client: {e}")
            self.client = None

    def _invoke_bedrock_model(self, prompt):
        """Private method to invoke the Bedrock model with a prompt"""
        if not self.client:
            return None
            
        try:
            native_request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(native_request),
                contentType="application/json",
            )
            
            response_body = response['body'].read().decode("utf-8")
            return json.loads(response_body)
        except Exception as e:
            print(f"Error invoking Bedrock model: {e}")
            return None
            
    def generate_initial_descriptions(self, job_description):
        """Generate three distinct enhanced versions of a job description with change summaries."""
        # If client is not initialized properly, return dummy versions
        if not self.client:
            return [
                f"Enhanced Version 1 (Example):\n\nOverview: This role is responsible for...\n\nKey Responsibilities:\n- Responsibility 1\n- Responsibility 2\n\nRequired Skills:\n- Skill 1\n- Skill 2",
                f"Enhanced Version 2 (Example):\n\nOverview: This position focuses on...\n\nKey Responsibilities:\n- Responsibility A\n- Responsibility B\n\nRequired Skills:\n- Skill A\n- Skill B",
                f"Enhanced Version 3 (Example):\n\nOverview: A key position that...\n\nKey Responsibilities:\n- Primary task 1\n- Primary task 2\n\nRequired Skills:\n- Critical skill 1\n- Critical skill 2"
            ]
        
        prompt = (
            "You are a job description specialist with expertise in creating compelling, differentiated job descriptions. "
            "Your task is to transform the provided job description into THREE distinctly different enhanced versions, "
            "each with a unique focus and approach while maintaining accuracy and core requirements.\n\n"
            
            "### Each version must have a DIFFERENT FOCUS:\n"
            "- VERSION 1: Focus on TECHNICAL EXCELLENCE and DOMAIN EXPERTISE. Emphasize technical skills, tools, "
            "methodologies, and domain knowledge. Use precise technical language and highlight opportunities for technical growth.\n\n"
            
            "- VERSION 2: Focus on LEADERSHIP & IMPACT. Emphasize business impact, strategic thinking, collaboration, "
            "and leadership qualities. Highlight how this role influences outcomes and drives organizational success.\n\n"
            
            "- VERSION 3: Focus on INNOVATION & GROWTH. Emphasize creativity, problem-solving, continuous learning, "
            "and professional development. Highlight how this role contributes to innovation and transformation.\n\n"
            
            "### Guidelines for all versions:\n"
            "- Do NOT make assumptions or introduce inaccuracies about the role or requirements.\n"
            "- Avoid using specific job titles; refer to the position as **'this role'** throughout.\n"
            "- Ensure clarity, conciseness, and engagement in the descriptions.\n"
            "- Each version should be SUBSTANTIALLY different in tone, emphasis, and presentation.\n"
            "- Maintain the same core requirements and essential functions across all versions.\n\n"
            
            "### Structure for Each Job Description:\n"
            "**1. Role Overview:** A compelling and detailed explanation of this role's significance.\n"
            "**2. Key Responsibilities:** Bullet points outlining core duties, including specifics where applicable.\n"
            "**3. Required Skills:** Essential technical and soft skills, with explanations of their importance.\n"
            "**4. Preferred Skills:** Additional skills that would be advantageous, with context on their relevance.\n"
            "**5. Required Experience:** The necessary experience levels, with examples of relevant past roles.\n"
            "**6. Tools & Technologies:** Key tools, software, and technologies required for this role.\n"
            "**7. Work Environment & Expectations:** Details on work conditions, methodologies, or collaboration requirements.\n\n"
            
            "### Required Format:\n"
            "For each version, include:\n"
            "1. The complete enhanced job description with all sections\n"
            "2. A brief 'CHANGE SUMMARY' section at the end that explains the key enhancements and focus of this version\n\n"
            
            "Present your response exactly as follows:\n\n"
            
            "VERSION 1: TECHNICAL EXCELLENCE FOCUS\n"
            "[Complete first job description with all sections]\n\n"
            "CHANGE SUMMARY 1:\n"
            "[Brief summary of key changes and enhancements in this version]\n\n"
            
            "VERSION 2: LEADERSHIP & IMPACT FOCUS\n"
            "[Complete second job description with all sections]\n\n"
            "CHANGE SUMMARY 2:\n"
            "[Brief summary of key changes and enhancements in this version]\n\n"
            
            "VERSION 3: INNOVATION & GROWTH FOCUS\n"
            "[Complete third job description with all sections]\n\n"
            "CHANGE SUMMARY 3:\n"
            "[Brief summary of key changes and enhancements in this version]\n\n"
            
            f"### Original Job Description:\n{job_description}\n"
        )
        
        try:
            model_response = self._invoke_bedrock_model(prompt)
            
            if model_response and "content" in model_response and isinstance(model_response["content"], list):
                full_text = model_response["content"][0]["text"].strip()
                
                # Parse versions using regex
                import re
                descriptions = []
                version_pattern = re.compile(r'VERSION [1-3][^\n]*:(.*?)(?=VERSION [1-3]|CHANGE SUMMARY [1-3]:|$)', re.DOTALL)
                summary_pattern = re.compile(r'CHANGE SUMMARY [1-3]:(.*?)(?=VERSION [1-3]|CHANGE SUMMARY [1-3]:|$)', re.DOTALL)
                
                version_matches = version_pattern.findall(full_text)
                summary_matches = summary_pattern.findall(full_text)
                
                # Combine version content with its summary
                for i, content in enumerate(version_matches[:3]):
                    version_content = content.strip()
                    summary = summary_matches[i].strip() if i < len(summary_matches) else "No summary provided."
                    formatted_version = f"{version_content}\n\nCHANGE SUMMARY:\n{summary}"
                    descriptions.append(formatted_version)
                
                if len(descriptions) == 3:
                    return descriptions
                
                # Ensure we return exactly 3 versions
                while len(descriptions) < 3:
                    default_content = f"Enhanced Version {len(descriptions)+1}:\n\n{job_description}\n\nCHANGE SUMMARY:\nBasic enhancement of original content."
                    descriptions.append(default_content)
                
                return descriptions[:3]
            else:
                print(f"Unexpected model response format: {model_response}")
                return [job_description] * 3  # Return original as fallback
                
        except Exception as e:
            print(f"Error generating descriptions: {str(e)}")
            return [job_description] * 3  # Return original as fallback

    def generate_final_description_structured(self, selected_description, feedback_history, jd_sections=None):
        """
        Generate enhanced description incorporating feedback history, respecting JD structure
        
        Args:
            selected_description (str): The base description to enhance
            feedback_history (list): List of previous feedback items
            jd_sections (dict, optional): Dictionary of job description sections
            
        Returns:
            str: Enhanced job description
        """
        # If client is not initialized properly, return the selected description
        if not self.client:
            return selected_description + "\n\n[Note: This would normally be enhanced based on your feedback, but the AI service connection is currently unavailable.]"
                
        # Compile feedback into a structured, categorized format
        categorized_feedback = {
            "Content": [],
            "Structure": [],
            "Clarity": [],
            "Language": [],
            "Technical": [],
            "General": []
        }
        
        # Process all feedback and categorize
        for i, feedback_item in enumerate(feedback_history):
            if isinstance(feedback_item, dict):
                feedback_type = feedback_item.get("type", "General Feedback")
                feedback_text = feedback_item.get("feedback", "")
                
                # Categorize feedback based on content
                feedback_lower = feedback_text.lower()
                
                if any(term in feedback_lower for term in ["add", "include", "missing", "needs more", "require"]):
                    categorized_feedback["Content"].append(f"({feedback_type}): {feedback_text}")
                elif any(term in feedback_lower for term in ["organize", "format", "section", "layout", "bullet"]):
                    categorized_feedback["Structure"].append(f"({feedback_type}): {feedback_text}")
                elif any(term in feedback_lower for term in ["clear", "specific", "vague", "explain", "detail"]):
                    categorized_feedback["Clarity"].append(f"({feedback_type}): {feedback_text}")
                elif any(term in feedback_lower for term in ["tone", "wording", "phrase", "language"]):
                    categorized_feedback["Language"].append(f"({feedback_type}): {feedback_text}")
                elif any(term in feedback_lower for term in ["technical", "skill", "technology", "tool", "framework"]):
                    categorized_feedback["Technical"].append(f"({feedback_type}): {feedback_text}")
                else:
                    categorized_feedback["General"].append(f"({feedback_type}): {feedback_text}")
            else:
                # If feedback isn't a dict, place in general category
                categorized_feedback["General"].append(f"Feedback {i+1}: {feedback_item}")
        
        # Create consolidated feedback sections
        feedback_sections = []
        for category, items in categorized_feedback.items():
            if items:
                section = f"### {category} Feedback:\n"
                for item in items:
                    section += f"- {item}\n"
                feedback_sections.append(section)
        
        # Combine all feedback sections
        all_feedback = "\n".join(feedback_sections)
        
        # Create enhanced prompt for generating the final version
        prompt = f"""
    You are a senior talent acquisition specialist with expertise in crafting compelling, effective job descriptions
    that attract high-quality candidates. Your task is to enhance the provided job description by applying all feedback
    while maintaining accuracy and professional quality.
    
    ### JOB DESCRIPTION TO ENHANCE:
    ```
    {selected_description}
    ```
    
    ### FEEDBACK TO IMPLEMENT:
    {all_feedback}
    
    ### ENHANCEMENT APPROACH:
    When enhancing this job description, follow this strategic approach:
    
    1. STRUCTURE & ORGANIZATION:
       - Maintain clear section headings with logical flow
       - Use bullet points for responsibilities and requirements
       - Ensure consistent formatting throughout
       - Create visual separation between sections for readability
    
    2. CONTENT ENHANCEMENT:
       - Add specificity and detail to vague statements
       - Incorporate all missing elements identified in feedback
       - Ensure technical requirements are accurate and current
       - Balance must-have vs. nice-to-have qualifications
    
    3. LANGUAGE OPTIMIZATION:
       - Use active, engaging language throughout
       - Replace generic terms with specific, measurable criteria
       - Maintain a consistent, professional tone
       - Use inclusive language that appeals to diverse candidates
       - Keep the position referenced as "this role" throughout
    
    4. SECTION-SPECIFIC GUIDELINES:
    """
    
        # Add section-specific guidelines if provided
        if jd_sections and all(key in jd_sections for key in ['company_role', 'foundations', 'specific_requirements', 'preferences']):
            prompt += """
       - Company & Role Overview: Make minimal changes (10% modification) - focus on clarity improvements only
       - Foundation Requirements: Make minimal changes (10% modification) - focus on clarity and relevance
       - Specific Role Requirements: This is where most changes should occur (up to 90% modification) - focus on specificity and engagement
       - Preferred Qualifications: Make minimal changes (10% modification) - focus on alignment with core requirements
    """
        else:
            prompt += """
       - Overview/Introduction: Focus on compelling value proposition and role context
       - Responsibilities: Enhance with specific details and impact metrics
       - Requirements: Clarify with precise technical and professional expectations
       - Qualifications: Balance required vs. preferred for inclusivity
    """
    
        prompt += """
    5. QUALITY STANDARDS:
       - Eliminate any jargon or unnecessary complexity
       - Ensure all statements are accurate and verifiable
       - Maintain authenticity while improving appeal
       - Preserve all essential requirements from the original
    
    ### OUTPUT REQUIREMENTS:
    1. Provide the complete enhanced job description incorporating ALL feedback points
    2. Maintain the same overall structure as the original
    3. Ensure the final description is polished, professional, and ready for immediate publication
    4. Do not include explanations or commentary - only provide the finished job description
    """
    
        try:
            # Call the model with enhanced prompt
            model_response = self._invoke_bedrock_model(prompt)
            
            if model_response and "content" in model_response and isinstance(model_response["content"], list):
                enhanced_jd = model_response["content"][0]["text"].strip()
                
                # Check if the response starts with any common headers or markdown and remove them
                common_headers = ["ENHANCED JOB DESCRIPTION:", "FINAL JOB DESCRIPTION:", "# ", "## "]
                for header in common_headers:
                    if enhanced_jd.startswith(header):
                        enhanced_jd = enhanced_jd[len(header):].strip()
                
                # Remove any markdown code blocks if present
                if enhanced_jd.startswith("```") and "```" in enhanced_jd[3:]:
                    first_block_end = enhanced_jd[3:].find("```") + 6  # 3 + 3
                    enhanced_jd = enhanced_jd[first_block_end:].strip()
                
                return enhanced_jd
                
        except Exception as e:
            print(f"Error generating final description: {e}")
            
        return selected_description + f"\n\n[Error generating final version: Unable to process feedback]"anced_jd[first_block_end:].st    rip()
                
            return enhanced_jd
            
    except Exception as e:
        print(f"Error generating final description: {e}")
        
    return selected_description + f"\n\n[Error generating final version: Unable to process feedback]"