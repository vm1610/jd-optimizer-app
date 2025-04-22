"""
JD Summary utility module for generating summaries of changes between JD versions.
This module should be placed in the utils directory.
"""

import re
import difflib
from nltk.tokenize import sent_tokenize

class JDSummaryGenerator:
    """
    Utility class to generate summaries of changes between job description versions
    """
    
    def __init__(self):
        """Initialize the summary generator"""
        # Keywords that indicate important changes
        self.key_phrases = [
            "experience", "responsibilities", "skills", "qualifications", 
            "requirements", "education", "technologies", "tools", "frameworks",
            "competencies", "knowledge", "abilities", "certification", "degree"
        ]
    
    def generate_summary(self, original_text, enhanced_text):
        """
        Generate a human-readable summary of changes between original and enhanced text
        
        Args:
            original_text (str): Original job description text
            enhanced_text (str): Enhanced job description text
            
        Returns:
            str: Summary of significant changes
        """
        # Handle empty inputs
        if not original_text or not enhanced_text:
            return "No changes to summarize - one or both texts are empty."
        
        # Normalize texts - split into paragraphs, sections, and sentences
        original_sections = self._extract_sections(original_text)
        enhanced_sections = self._extract_sections(enhanced_text)
        
        # Identify section-level additions, removals, modifications
        summary_lines = []
        
        # Compare overall text length
        orig_words = len(original_text.split())
        enhanced_words = len(enhanced_text.split())
        word_diff = enhanced_words - orig_words
        
        if word_diff > 0:
            summary_lines.append(f"• Added approximately {word_diff} words to the description (+{(word_diff/max(1, orig_words))*100:.1f}%).")
        elif word_diff < 0:
            summary_lines.append(f"• Removed approximately {abs(word_diff)} words from the description (-{(abs(word_diff)/max(1, orig_words))*100:.1f}%).")
        
        # Find new sections
        new_section_names = set(enhanced_sections.keys()) - set(original_sections.keys())
        if new_section_names:
            new_sections = ", ".join([name for name in new_section_names])
            summary_lines.append(f"• Added new section(s): {new_sections}.")
        
        # Find removed sections
        removed_section_names = set(original_sections.keys()) - set(enhanced_sections.keys())
        if removed_section_names:
            removed_sections = ", ".join([name for name in removed_section_names])
            summary_lines.append(f"• Removed section(s): {removed_sections}.")
        
        # Check for changes in existing sections
        common_sections = set(original_sections.keys()) & set(enhanced_sections.keys())
        for section in common_sections:
            # Compare section content
            original_content = original_sections[section]
            enhanced_content = enhanced_sections[section]
            
            # Skip if contents are identical
            if original_content == enhanced_content:
                continue
            
            # Calculate section-level changes
            section_changes = self._analyze_section_changes(original_content, enhanced_content)
            if section_changes:
                summary_lines.append(f"• In '{section}' section: {section_changes}")
        
        # Check for key phrases to identify specific changes
        for phrase in self.key_phrases:
            orig_count = len(re.findall(r'\b' + re.escape(phrase) + r'\b', original_text.lower()))
            enhanced_count = len(re.findall(r'\b' + re.escape(phrase) + r'\b', enhanced_text.lower()))
            
            if enhanced_count > orig_count + 2:  # Significant increase
                summary_lines.append(f"• Enhanced emphasis on '{phrase}' requirements.")
            elif orig_count > enhanced_count + 2:  # Significant decrease
                summary_lines.append(f"• Reduced emphasis on '{phrase}' requirements.")
        
        # Check for bullet points to identify list changes
        orig_bullets = len(re.findall(r'[\n\r][ \t]*[•\-\*][ \t]', original_text))
        enhanced_bullets = len(re.findall(r'[\n\r][ \t]*[•\-\*][ \t]', enhanced_text))
        
        bullet_diff = enhanced_bullets - orig_bullets
        if bullet_diff > 3:
            summary_lines.append(f"• Added {bullet_diff} bullet points for improved readability.")
        
        # Look for key sentence additions using sentence tokenization
        try:
            orig_sentences = set(sent_tokenize(original_text))
            enhanced_sentences = set(sent_tokenize(enhanced_text))
            
            new_sentences = enhanced_sentences - orig_sentences
            key_new_sentences = []
            
            for sentence in new_sentences:
                if any(phrase in sentence.lower() for phrase in self.key_phrases) and len(sentence.split()) > 5:
                    # Truncate very long sentences
                    if len(sentence) > 100:
                        sentence = sentence[:97] + "..."
                    key_new_sentences.append(sentence)
            
            # Add up to 3 important new sentences to the summary
            for sentence in key_new_sentences[:3]:
                summary_lines.append(f"• Added: \"{sentence}\"")
        except:
            # If NLTK tokenization fails (e.g., if NLTK not installed), skip this part
            pass
        
        # Fallback if no specific changes were detected
        if not summary_lines:
            # Try using difflib to get a simple difference summary
            diff = difflib.unified_diff(
                original_text.splitlines(),
                enhanced_text.splitlines(),
                lineterm=''
            )
            
            # Count additions and removals from diff
            additions = 0
            removals = 0
            
            for line in diff:
                if line.startswith('+') and not line.startswith('+++'):
                    additions += 1
                elif line.startswith('-') and not line.startswith('---'):
                    removals += 1
            
            if additions or removals:
                summary_lines.append(f"• Made {additions} additions and {removals} removals to the text.")
            else:
                summary_lines.append("• Refined the language and structure while maintaining the same content.")
        
        return "\n".join(summary_lines)
    
    def _extract_sections(self, text):
        """
        Extract sections from job description text
        
        Args:
            text (str): Job description text
            
        Returns:
            dict: Dictionary of section_name: section_content
        """
        # Common section header patterns
        section_patterns = [
            # Headers with numbers like "1. Section Name"
            r'\n\s*\d+\.\s*([A-Z][A-Za-z\s]+)[\:\n]',
            # Headers with ## markdown format
            r'\n\s*##\s*([A-Z][A-Za-z\s]+)[\:\n]',
            # Headers with capitalized words followed by colon
            r'\n\s*([A-Z][A-Z\s]+)[\:\n]',
            # Headers with strong formatting or bold text
            r'\n\s*\*\*([A-Z][A-Za-z\s]+)\*\*[\:\n]',
            # Uppercase headers
            r'\n\s*([A-Z][A-Z\s]+[A-Z])[\:\n]',
            # Headers with title case words
            r'\n\s*([A-Z][a-z]+\s+(?:[A-Z][a-z]+\s*)+)[\:\n]'
        ]
        
        # Find all potential section headers
        sections = {}
        rest_of_text = text
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, '\n' + text)
            
            for match in matches:
                section_name = match.group(1).strip()
                # Skip very short section names or generic words
                if len(section_name) < 3 or section_name.lower() in ['the', 'and', 'for', 'a', 'an', 'note']:
                    continue
                    
                start_pos = match.end()
                
                # Find the next section header
                next_match = None
                for p in section_patterns:
                    next_matches = list(re.finditer(p, '\n' + text[start_pos:]))
                    if next_matches:
                        potential_next = next_matches[0]
                        potential_pos = start_pos + potential_next.start()
                        if next_match is None or potential_pos < next_match[0]:
                            next_match = (potential_pos, potential_next.start())
                
                # Extract section content
                if next_match:
                    end_pos = next_match[0]
                    section_content = text[start_pos:end_pos].strip()
                else:
                    section_content = text[start_pos:].strip()
                
                # Store the section
                sections[section_name] = section_content
        
        # If no sections were found, try to identify them based on common job description sections
        if not sections:
            common_sections = [
                "Overview", "About", "Summary", "Introduction",
                "Responsibilities", "Duties", "Key Responsibilities",
                "Requirements", "Qualifications", "Skills",
                "Experience", "Education", "Background",
                "Benefits", "Perks", "Compensation"
            ]
            
            for section in common_sections:
                pattern = r'(?i)(?:\n|^)\s*' + re.escape(section) + r'\s*(?:\:|\n)'
                match = re.search(pattern, text)
                if match:
                    start_pos = match.end()
                    
                    # Find the next potential section
                    next_pos = float('inf')
                    for next_section in common_sections:
                        if next_section != section:
                            next_pattern = r'(?i)(?:\n|^)\s*' + re.escape(next_section) + r'\s*(?:\:|\n)'
                            next_match = re.search(next_pattern, text[start_pos:])
                            if next_match:
                                if start_pos + next_match.start() < next_pos:
                                    next_pos = start_pos + next_match.start()
                    
                    # Extract section content
                    if next_pos != float('inf'):
                        section_content = text[start_pos:next_pos].strip()
                    else:
                        section_content = text[start_pos:].strip()
                    
                    sections[section] = section_content
        
        # If still no sections found, treat the whole text as one section
        if not sections:
            sections["Job Description"] = text
            
        return sections
    
    def _analyze_section_changes(self, original_content, enhanced_content):
        """
        Analyze changes within a section
        
        Args:
            original_content (str): Original section content
            enhanced_content (str): Enhanced section content
            
        Returns:
            str: Description of the changes
        """
        changes = []
        
        # Compare bullet points
        orig_bullets = re.findall(r'[\n\r][ \t]*[•\-\*][ \t](.*?)(?=[\n\r][ \t]*[•\-\*][ \t]|$)', original_content, re.DOTALL)
        enhanced_bullets = re.findall(r'[\n\r][ \t]*[•\-\*][ \t](.*?)(?=[\n\r][ \t]*[•\-\*][ \t]|$)', enhanced_content, re.DOTALL)
        
        orig_bullet_set = {b.strip() for b in orig_bullets}
        enhanced_bullet_set = {b.strip() for b in enhanced_bullets}
        
        new_bullets = enhanced_bullet_set - orig_bullet_set
        removed_bullets = orig_bullet_set - enhanced_bullet_set
        
        if len(new_bullets) > len(removed_bullets) + 2:
            changes.append(f"added {len(new_bullets) - len(removed_bullets)} new points")
        elif len(removed_bullets) > len(new_bullets) + 2:
            changes.append(f"removed {len(removed_bullets) - len(new_bullets)} points")
        elif len(new_bullets) > 0 and len(removed_bullets) > 0:
            changes.append(f"replaced {len(removed_bullets)} points with {len(new_bullets)} new ones")
        
        # Check section length change
        orig_words = len(original_content.split())
        enhanced_words = len(enhanced_content.split())
        word_diff = enhanced_words - orig_words
        
        if word_diff > 10 and word_diff > 0.3 * orig_words:
            changes.append(f"expanded content significantly (+{word_diff} words)")
        elif word_diff < -10 and abs(word_diff) > 0.3 * orig_words:
            changes.append(f"streamlined content (-{abs(word_diff)} words)")
        
        # Look for formatting improvements
        if enhanced_content.count('\n') > original_content.count('\n') + 5:
            changes.append("improved formatting and readability")
        
        # Look for important key phrases
        for phrase in self.key_phrases:
            if phrase.lower() in enhanced_content.lower() and phrase.lower() not in original_content.lower():
                changes.append(f"added '{phrase}' requirements")
        
        return ", ".join(changes) if changes else "refined content"


def generate_version_summary(original_jd, enhanced_jd):
    """
    Wrapper function to generate a summary of changes
    
    Args:
        original_jd (str): Original job description
        enhanced_jd (str): Enhanced job description
        
    Returns:
        str: Summary of changes
    """
    generator = JDSummaryGenerator()
    return generator.generate_summary(original_jd, enhanced_jd)