import re

class JobDescriptionAnalyzer:
    """Analyzes job descriptions for skill coverage and other metrics"""
    def __init__(self):
        self.categories = {
            'Technical Skills': ['python', 'java', 'javascript', 'c#', 'ruby', 'sql', 'aws', 'azure', 'cloud', 
                               'docker', 'kubernetes', 'api', 'database', 'git', 'linux', 'agile', 'devops', 
                               'ml', 'ai', 'analytics', 'full-stack', 'frontend', 'backend'],
            'Soft Skills': ['communication', 'leadership', 'teamwork', 'collaboration', 'problem-solving', 
                           'analytical', 'initiative', 'organizational', 'time management', 'interpersonal'],
            'Experience Level': ['year', 'years', 'senior', 'junior', 'mid-level', 'lead', 'manager', 'experience'],
            'Education': ['degree', 'bachelor', 'master', 'phd', 'certification', 'education'],
            'Tools & Technologies': ['jira', 'confluence', 'slack', 'github', 'gitlab', 'azure', 'jenkins', 
                                   'terraform', 'react', 'angular', 'vue', 'node'],
            'Domain Knowledge': ['finance', 'healthcare', 'retail', 'banking', 'insurance', 'technology', 
                               'manufacturing', 'telecom', 'e-commerce']
        }

    def analyze_text(self, text):
        """Analyze text for keyword coverage in each category"""
        if not text:
            return {category: 0.0 for category in self.categories}
            
        text = text.lower()
        scores = {}
        
        for category, keywords in self.categories.items():
            category_score = 0
            for keyword in keywords:
                count = len(re.findall(r'\b' + keyword + r'\b', text))
                category_score += count
            max_possible = len(keywords)
            scores[category] = min(category_score / max_possible, 1.0)
            
        return scores
    
    def compare_jd_versions(self, original_jd, enhanced_versions):
        """Compare the original JD with enhanced versions"""
        # Get scores for original
        original_scores = self.analyze_text(original_jd)
        
        # Get scores for each enhanced version
        enhanced_scores = {
            f'Version {i+1}': self.analyze_text(version)
            for i, version in enumerate(enhanced_versions)
        }
        
        # Combine all for comparison
        all_scores = {'Original': original_scores, **enhanced_scores}
        
        return all_scores
    
    def identify_skill_gaps(self, jd_text):
        """Identify potential skill gaps in a job description"""
        scores = self.analyze_text(jd_text)
        gaps = []
        
        # Look for categories with low coverage
        for category, score in scores.items():
            if score < 0.2:
                gaps.append({
                    'category': category,
                    'score': score,
                    'suggestion': f"Consider adding more {category.lower()} requirements"
                })
        
        return gaps
    
    def extract_key_requirements(self, jd_text):
        """Extract key requirements from job description text"""
        # Simple extraction based on common patterns
        requirements = []
        
        # Look for bullet points
        bullet_pattern = r'[•\-\*]\s*(.*?)(?=\n[•\-\*]|\n\n|$)'
        bullets = re.findall(bullet_pattern, jd_text, re.DOTALL)
        for bullet in bullets:
            requirement = bullet.strip()
            if len(requirement) > 10:  # Only include substantive items
                requirements.append(requirement)
        
        # Look for lines with "required" or "must have"
        required_pattern = r'(?:required|must have|essential)[^\n]*'
        required_lines = re.findall(required_pattern, jd_text.lower())
        for line in required_lines:
            requirements.append(line.strip())
        
        return list(set(requirements))  # Remove duplicates

    def identify_jd_sections(self, jd_text):
        """
        Identify and segment the job description into its key sections
        
        Args:
            jd_text (str): The job description text
            
        Returns:
            dict: Dictionary containing the segmented sections of the JD
        """
        import re
        
        # Initialize the sections dictionary
        sections = {
            'company_role': '',
            'foundations': '',
            'specific_requirements': '',
            'preferences': ''
        }
        
        # If JD is empty, return empty sections
        if not jd_text or jd_text.strip() == '':
            return sections
        
        # Split the JD into paragraphs for analysis
        paragraphs = [p.strip() for p in jd_text.split('\n\n') if p.strip()]
        
        # Function to check paragraph content type
        def get_paragraph_type(paragraph):
            paragraph = paragraph.lower()
            
            # Check for company/role introduction indicators
            company_indicators = ['about', 'company', 'organization', 'who we are', 'our client']
            role_indicators = ['role overview', 'position summary', 'job summary', 'summary', 'title']
            
            # Check for foundation/basic requirements
            foundation_indicators = ['foundation', 'basic', 'core competencies', 'essential', 'key skills']
            
            # Check for specific requirements
            requirement_indicators = ['responsibilities', 'duties', 'functions', 'requirements', 
                                    'required', 'qualifications', 'skills', 'experience']
            
            # Check for preferences
            preference_indicators = ['preferred', 'desirable', 'bonus', 'nice to have', 'plus', 'additionally']
            
            # Determine paragraph type based on content
            if any(indicator in paragraph for indicator in company_indicators + role_indicators):
                return 'company_role'
            elif any(indicator in paragraph for indicator in foundation_indicators):
                return 'foundations'
            elif any(indicator in paragraph for indicator in requirement_indicators) and \
                 not any(indicator in paragraph for indicator in preference_indicators):
                return 'specific_requirements'
            elif any(indicator in paragraph for indicator in preference_indicators):
                return 'preferences'
            else:
                # Default section determination based on position in document
                return None
        
        # Initial section assignment based on content indicators
        assigned_paragraphs = {}
        unassigned_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            paragraph_type = get_paragraph_type(paragraph)
            if paragraph_type:
                if paragraph_type not in assigned_paragraphs:
                    assigned_paragraphs[paragraph_type] = []
                assigned_paragraphs[paragraph_type].append(i)
            else:
                unassigned_paragraphs.append(i)
        
        # For unassigned paragraphs, determine section based on position
        if unassigned_paragraphs:
            total_paragraphs = len(paragraphs)
            
            for i in unassigned_paragraphs:
                # Position-based heuristic
                relative_position = i / total_paragraphs
                
                if relative_position < 0.25:
                    if 'company_role' not in assigned_paragraphs:
                        assigned_paragraphs['company_role'] = []
                    assigned_paragraphs['company_role'].append(i)
                elif relative_position < 0.4:
                    if 'foundations' not in assigned_paragraphs:
                        assigned_paragraphs['foundations'] = []
                    assigned_paragraphs['foundations'].append(i)
                elif relative_position < 0.75:
                    if 'specific_requirements' not in assigned_paragraphs:
                        assigned_paragraphs['specific_requirements'] = []
                    assigned_paragraphs['specific_requirements'].append(i)
                else:
                    if 'preferences' not in assigned_paragraphs:
                        assigned_paragraphs['preferences'] = []
                    assigned_paragraphs['preferences'].append(i)
        
        # If any section is completely empty, assign paragraphs based on document structure
        if 'company_role' not in assigned_paragraphs or not assigned_paragraphs['company_role']:
            if paragraphs:
                assigned_paragraphs['company_role'] = [0]  # First paragraph
        
        if 'foundations' not in assigned_paragraphs or not assigned_paragraphs['foundations']:
            if len(paragraphs) > 1:
                assigned_paragraphs['foundations'] = [1]  # Second paragraph
        
        if 'specific_requirements' not in assigned_paragraphs or not assigned_paragraphs['specific_requirements']:
            if len(paragraphs) > 2:
                middle_indexes = list(range(2, len(paragraphs) - 1 if len(paragraphs) > 3 else len(paragraphs)))
                assigned_paragraphs['specific_requirements'] = middle_indexes
        
        if 'preferences' not in assigned_paragraphs or not assigned_paragraphs['preferences']:
            if len(paragraphs) > 3:
                assigned_paragraphs['preferences'] = [len(paragraphs) - 1]  # Last paragraph
        
        # Construct the sections from the assigned paragraphs
        for section_type, paragraph_indices in assigned_paragraphs.items():
            paragraph_indices.sort()  # Ensure paragraphs are in original order
            sections[section_type] = '\n\n'.join([paragraphs[i] for i in paragraph_indices])
        
        return sections

    def recommend_section_modifications(self, jd_sections):
        """
        Recommend which portions of each section should be modified during optimization
        
        Args:
            jd_sections (dict): Dictionary of JD sections from identify_jd_sections
            
        Returns:
            dict: Recommendations for modification percentages and focus
        """
        recommendations = {
            'company_role': {
                'modify_percentage': 10,  # Keep ~90% unchanged
                'focus': 'Maintain company identity and role title with minimal adjustments for clarity.'
            },
            'foundations': {
                'modify_percentage': 10,  # Keep ~90% unchanged
                'focus': 'Preserve core requirements with minor enhancements to clarity and relevance.'
            },
            'specific_requirements': {
                'modify_percentage': 90,  # 85-90% changes
                'focus': 'This is the core differentiator - focus optimization efforts here to enhance specificity, relevance, and appeal.'
            },
            'preferences': {
                'modify_percentage': 10,  # ~10% changes
                'focus': 'Maintain preferences with slight refinements to ensure alignment with core requirements.'
            }
        }
        
        return recommendations

    def generate_version_summary(self, original_text, enhanced_text):
        """
        Generate a summary of key changes between the original and enhanced version
        
        Args:
            original_text (str): Original job description text
            enhanced_text (str): Enhanced job description text
            
        Returns:
            dict: Summary of changes including key skills added and modified sections
        """
        import re
        
        # Helper function to extract skills from text
        def extract_skills(text):
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
            
            for skill in common_skills:
                if f" {skill} " in f" {text_lower} " or f" {skill}," in f" {text_lower} " or f" {skill}." in f" {text_lower} ":
                    found_skills.append(skill)
            
            return found_skills
        
        # Extract skills from both texts
        original_skills = extract_skills(original_text)
        enhanced_skills = extract_skills(enhanced_text)
        
        # Find new skills added
        new_skills = [skill for skill in enhanced_skills if skill not in original_skills]
        
        # Analyze sections that were modified
        # Look for common section headers in job descriptions
        section_headers = [
            'overview', 'responsibilities', 'requirements', 'qualifications', 
            'experience', 'skills', 'preferred', 'about', 'benefits'
        ]
        
        # Find sentences that appear to be different
        original_sentences = re.split(r'[.!?]', original_text)
        enhanced_sentences = re.split(r'[.!?]', enhanced_text)
        
        # Clean sentences (remove extra whitespace, make lowercase for comparison)
        original_sentences = [s.strip().lower() for s in original_sentences if s.strip()]
        enhanced_sentences = [s.strip().lower() for s in enhanced_sentences if s.strip()]
        
        # Find new sentences in enhanced version
        new_sentences = [s for s in enhanced_sentences if s not in original_sentences]
        
        # Determine which sections were modified
        modified_sections = []
        for header in section_headers:
            # Check if any new sentence contains this section header
            for sentence in new_sentences:
                if header in sentence:
                    modified_sections.append(header.title())
                    break
        
        # Determine the overall focus of the changes
        focus_areas = []
        technical_terms = ['technical', 'skills', 'programming', 'tools', 'technologies']
        experience_terms = ['experience', 'background', 'history', 'worked']
        responsibility_terms = ['responsibilities', 'duties', 'tasks', 'role', 'function']
        
        # Count occurrences of terms in new sentences
        term_counts = {
            'Technical Skills': sum(1 for s in new_sentences if any(term in s for term in technical_terms)),
            'Experience': sum(1 for s in new_sentences if any(term in s for term in experience_terms)),
            'Responsibilities': sum(1 for s in new_sentences if any(term in s for term in responsibility_terms))
        }
        
        # Get the top focus areas
        focus_areas = [area for area, count in sorted(term_counts.items(), key=lambda x: x[1], reverse=True) if count > 0][:2]
        
        # Create summary
        summary = {
            'new_skills': new_skills[:5],  # Limit to top 5 new skills
            'modified_sections': modified_sections,
            'focus_areas': focus_areas,
            'clarity_improved': len(enhanced_sentences) != len(original_sentences)
        }
        
        return summary

    def generate_detailed_version_summary(self, original_text, enhanced_text):
        """
        Generate a comprehensive summary of key changes between original and enhanced versions
        with more detailed and differentiating information
        
        Args:
            original_text (str): Original job description text
            enhanced_text (str): Enhanced job description text
            
        Returns:
            dict: Detailed summary of changes with enhanced differentiation metrics
        """
        import re
        
        # Helper function to extract skills from text with importance ranking
        def extract_skills(text):
            common_skills = {
                'python': 'programming',
                'java': 'programming',
                'javascript': 'programming',
                'react': 'frontend',
                'angular': 'frontend',
                'node': 'backend',
                'aws': 'cloud',
                'azure': 'cloud',
                'docker': 'devops',
                'kubernetes': 'devops',
                'sql': 'database',
                'nosql': 'database',
                'mongodb': 'database',
                'machine learning': 'ai',
                'ai': 'ai',
                'data analysis': 'analytics',
                'cloud': 'infrastructure',
                'devops': 'infrastructure',
                'ci/cd': 'infrastructure',
                'agile': 'methodology',
                'scrum': 'methodology',
                'rest api': 'integration',
                'spring': 'framework',
                'hibernate': 'framework',
                'microservices': 'architecture',
                'django': 'framework',
                'flask': 'framework',
                'vue': 'frontend',
                'typescript': 'programming',
                'html': 'frontend',
                'css': 'frontend',
                'php': 'programming',
                'ruby': 'programming',
                'c#': 'programming',
                'c++': 'programming',
                'golang': 'programming',
                'scala': 'programming',
                'rust': 'programming',
                'git': 'tools',
                'jenkins': 'tools',
                'terraform': 'infrastructure',
                'ansible': 'infrastructure',
                'prometheus': 'monitoring',
                'grafana': 'monitoring'
            }
            
            found_skills = {}
            text_lower = text.lower()
            
            for skill, category in common_skills.items():
                if f" {skill} " in f" {text_lower} " or f" {skill}," in f" {text_lower} " or f" {skill}." in f" {text_lower} ":
                    # Count occurrences to determine emphasis
                    count = text_lower.count(skill)
                    if category not in found_skills:
                        found_skills[category] = []
                    found_skills[category].append((skill, count))
            
            # Extract skills as flat list
            flat_skills = [item[0] for sublist in found_skills.values() for item in sublist]
            
            # Get the most emphasized categories
            category_emphasis = {}
            for category, skills in found_skills.items():
                category_emphasis[category] = sum(count for _, count in skills)
            
            top_categories = sorted(category_emphasis.items(), key=lambda x: x[1], reverse=True)[:3]
            top_categories = [cat for cat, _ in top_categories]
            
            return flat_skills, top_categories
        
        # Extract skills and top categories from both texts
        original_skills, original_categories = extract_skills(original_text)
        enhanced_skills, enhanced_categories = extract_skills(enhanced_text)
        
        # Find new skills added
        new_skills = [skill for skill in enhanced_skills if skill not in original_skills]
        
        # Find category shifts
        category_shifts = [cat for cat in enhanced_categories if cat not in original_categories]
        
        # Analyze clarity improvements
        def analyze_clarity(text):
            sentences = re.split(r'[.!?]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            bullet_points = len(re.findall(r'[•\-\*]\s+', text))
            structure_elements = len(re.findall(r'(?i)(responsibilities|requirements|qualifications|about|overview|skills required)', text))
            return {
                'avg_sentence_length': avg_length,
                'bullet_points': bullet_points,
                'structure_elements': structure_elements
            }
        
        original_clarity = analyze_clarity(original_text)
        enhanced_clarity = analyze_clarity(enhanced_text)
        
        clarity_improvements = {}
        if enhanced_clarity['avg_sentence_length'] < original_clarity['avg_sentence_length']:
            clarity_improvements['conciseness'] = "Improved sentence conciseness"
        
        if enhanced_clarity['bullet_points'] > original_clarity['bullet_points']:
            clarity_improvements['formatting'] = "Enhanced bullet point structure"
            
        if enhanced_clarity['structure_elements'] > original_clarity['structure_elements']:
            clarity_improvements['organization'] = "Better section organization"
        
        # Analyze sections that were modified
        # Look for common section headers in job descriptions
        section_headers = {
            'overview': 'role context',
            'responsibilities': 'daily activities', 
            'requirements': 'technical needs',
            'qualifications': 'candidate profile',
            'experience': 'background needed',
            'skills': 'technical abilities',
            'preferred': 'ideal attributes',
            'about': 'company culture',
            'benefits': 'compensation package'
        }
        
        # Find sentences that appear to be different
        original_sentences = re.split(r'[.!?]', original_text)
        enhanced_sentences = re.split(r'[.!?]', enhanced_text)
        
        # Clean sentences (remove extra whitespace, make lowercase for comparison)
        original_sentences = [s.strip().lower() for s in original_sentences if s.strip()]
        enhanced_sentences = [s.strip().lower() for s in enhanced_sentences if s.strip()]
        
        # Find new sentences in enhanced version
        new_sentences = [s for s in enhanced_sentences if s not in original_sentences]
        
        # Determine which sections were modified and to what extent
        modified_sections = {}
        for header, description in section_headers.items():
            # Check for header mentions
            original_mentions = len([s for s in original_sentences if header in s.lower()])
            enhanced_mentions = len([s for s in enhanced_sentences if header in s.lower()])
            
            if enhanced_mentions > original_mentions:
                modified_sections[header.title()] = description
        
        # Determine the overall focus of the changes
        focus_areas = []
        technical_terms = ['technical', 'skills', 'programming', 'tools', 'technologies']
        experience_terms = ['experience', 'background', 'history', 'worked', 'career']
        responsibility_terms = ['responsibilities', 'duties', 'tasks', 'role', 'function', 'day-to-day']
        culture_terms = ['environment', 'culture', 'team', 'collaborate', 'grow', 'impact']
        
        # Count occurrences of terms in new sentences
        term_counts = {
            'Technical Skills': sum(1 for s in new_sentences if any(term in s for term in technical_terms)),
            'Experience': sum(1 for s in new_sentences if any(term in s for term in experience_terms)),
            'Responsibilities': sum(1 for s in new_sentences if any(term in s for term in responsibility_terms)),
            'Culture & Environment': sum(1 for s in new_sentences if any(term in s for term in culture_terms))
        }
        
        # Get the top focus areas
        focus_areas = [area for area, count in sorted(term_counts.items(), key=lambda x: x[1], reverse=True) if count > 0][:2]
        
        # Analyze tone shifts
        original_words = ' '.join(original_sentences).split()
        enhanced_words = ' '.join(enhanced_sentences).split()
        
        # Create tone indicators
        tone_indicators = {
            'action_verbs': ['create', 'develop', 'lead', 'manage', 'analyze', 'design', 'implement', 'drive', 'collaborate'],
            'inclusive_terms': ['diverse', 'inclusive', 'teamwork', 'together', 'partnership', 'collaborate'],
            'growth_focus': ['learn', 'grow', 'develop', 'advance', 'opportunity', 'challenge']
        }
        
        tone_improvements = {}
        for tone, words in tone_indicators.items():
            original_count = sum(1 for word in original_words if word.lower() in words)
            enhanced_count = sum(1 for word in enhanced_words if word.lower() in words)
            
            if enhanced_count > original_count:
                if tone == 'action_verbs':
                    tone_improvements['dynamic'] = 'More dynamic language'
                elif tone == 'inclusive_terms':
                    tone_improvements['inclusive'] = 'More inclusive language'
                elif tone == 'growth_focus':
                    tone_improvements['growth'] = 'Greater emphasis on growth opportunities'
        
        # Create comprehensive summary
        summary = {
            'new_skills': new_skills[:5],  # Limit to top 5 new skills
            'category_shifts': category_shifts,
            'modified_sections': [f"{section}" for section in modified_sections.keys()],
            'section_improvements': [f"{description}" for description in modified_sections.values()],
            'focus_areas': focus_areas,
            'clarity_improved': len(clarity_improvements) > 0,
            'clarity_details': list(clarity_improvements.values()),
            'tone_improvements': list(tone_improvements.values())
        }
        
        return summary