"""
PDF Resume parsing functionality.

This module extracts relevant information from PDF resumes using PyMuPDF,
including name, education, and research interests.
"""

import re
import fitz  # PyMuPDF
import spacy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Loaded spaCy NLP model")
except Exception as e:
    logger.warning(f"Could not load spaCy model: {e}")
    logger.warning("Using spaCy's default English model")
    nlp = spacy.blank("en")

class ResumeParser:
    """
    A class to handle parsing PDF resumes and extracting structured information.
    """
    
    def __init__(self, file_path):
        """
        Initialize the ResumeParser with a PDF file path.
        
        Args:
            file_path (str): Path to the PDF resume file
        """
        self.file_path = file_path
        self.text = self._extract_text()
        self.sections = self._split_into_sections()
        
    def _extract_text(self):
        """
        Extract all text from the PDF file.
        
        Returns:
            str: The entire text content of the PDF
        """
        try:
            doc = fitz.open(self.file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def _split_into_sections(self):
        """
        Split the resume text into sections based on common section headers.
        
        Returns:
            dict: A dictionary of section names and their content
        """
        # Define common section headers in resumes
        section_headers = [
            "EDUCATION", "ACADEMIC BACKGROUND", "QUALIFICATIONS",
            "EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT", "PROFESSIONAL EXPERIENCE",
            "SKILLS", "TECHNICAL SKILLS", "TECHNOLOGIES", "CORE COMPETENCIES",
            "RESEARCH", "RESEARCH INTERESTS", "RESEARCH EXPERIENCE",
            "PROJECTS", "PROJECT EXPERIENCE", 
            "PUBLICATIONS", "PAPERS", "ARTICLES",
            "CERTIFICATIONS", "CERTIFICATES",
            "AWARDS", "HONORS", "ACHIEVEMENTS",
            "LANGUAGES", "LANGUAGE SKILLS",
            "REFERENCES", "PROFESSIONAL REFERENCES"
        ]
        
        # Create a regex pattern for finding section headers
        pattern = r"(?i)(?:^|\n)(?:(?:I\.?|II\.?|III\.?|IV\.?)\s+)?({})[:\s]*(?:\n|$)".format("|".join(section_headers))
        
        # Split text by section headers
        matches = list(re.finditer(pattern, self.text))
        sections = {}
        
        for i, match in enumerate(matches):
            section_name = match.group(1).upper()
            start_pos = match.end()
            
            # If this is the last section, take text until the end
            if i == len(matches) - 1:
                section_content = self.text[start_pos:].strip()
            else:
                # Otherwise, take text until the start of the next section
                next_match = matches[i + 1]
                section_content = self.text[start_pos:next_match.start()].strip()
            
            sections[section_name] = section_content
        
        # If no sections found, try to infer them
        if not sections:
            # Special case: very simple resume might just have the whole content
            sections["FULL_TEXT"] = self.text
        
        return sections
    
    def extract_name(self):
        """
        Extract the candidate's name from the resume.
        
        Returns:
            str: The extracted name or empty string if not found
        """
        # Try to find the name at the beginning of the resume
        # Typically, names are at the very top, often in a larger font
        first_few_lines = self.text.split('\n')[:5]  # Check first 5 lines
        first_block = ' '.join(first_few_lines)
        
        # Use spaCy to extract named entities (PERSON)
        doc = nlp(first_block)
        
        # Look for PERSON entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        
        # If spaCy doesn't find a name, try a simple approach to get the first line
        # if it looks like a name (no common resume words, appropriate length)
        first_line = first_few_lines[0].strip()
        
        # Check if first line seems like a name
        if (len(first_line.split()) <= 4 and 
            not any(word in first_line.lower() for word in ["resume", "cv", "curriculum", "vitae"])):
            return first_line
        
        return ""
    
    def extract_education(self):
        """
        Extract education information from the resume.
        
        Returns:
            list: A list of dictionaries with education details
        """
        education_info = []
        
        # Find the education section
        education_section = None
        for section_name, content in self.sections.items():
            if "EDUCATION" in section_name or "ACADEMIC" in section_name or "QUALIFICATIONS" in section_name:
                education_section = content
                break
        
        if not education_section and "FULL_TEXT" in self.sections:
            # Try to find education-related info in the full text
            education_section = self.sections["FULL_TEXT"]
        
        if not education_section:
            return education_info
        
        # Look for common degree keywords
        degree_keywords = [
            "PhD", "Ph.D", "Doctor of Philosophy",
            "MS", "M.S.", "Master of Science", "Master's", "Masters", "MA", "M.A.",
            "BS", "B.S.", "Bachelor of Science", "Bachelor's", "Bachelors", "BA", "B.A.",
            "MBA", "M.B.A.", "Master of Business Administration"
        ]
        
        # Split education section into paragraphs (probably each institution)
        paragraphs = education_section.split('\n\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Try to extract degree information
            degree = None
            field = None
            institution = None
            year = None
            
            # Look for degree
            for keyword in degree_keywords:
                pattern = r"\b" + re.escape(keyword) + r"\b"
                if re.search(pattern, paragraph, re.IGNORECASE):
                    degree = keyword
                    
                    # Try to find the field of study (often follows the degree)
                    match = re.search(r"\b" + re.escape(keyword) + r"\b[,\s]+(?:in|of)?\s+([^,\n]+)", paragraph, re.IGNORECASE)
                    if match:
                        field = match.group(1).strip()
                    break
            
            # Look for institution name (common university terms)
            university_patterns = [
                r"(?:^|\n|\s)([A-Z][a-zA-Z\s]+(?:University|College|Institute|School))",
                r"(?:^|\n|\s)(University of [A-Z][a-zA-Z\s]+)"
            ]
            
            for pattern in university_patterns:
                match = re.search(pattern, paragraph)
                if match:
                    institution = match.group(1).strip()
                    break
            
            # Look for year (typically 4 digits between 1900 and current year)
            year_matches = re.findall(r"\b(19\d{2}|20\d{2})\b", paragraph)
            if year_matches:
                # Use the most recent year as the graduation year
                year = max(int(y) for y in year_matches)
            
            # If we have at least a degree or institution, add to our list
            if degree or institution:
                education_info.append({
                    "degree": degree,
                    "field": field,
                    "institution": institution,
                    "year": year
                })
        
        return education_info
    
    def extract_research_interests(self):
        """
        Extract research interests from the resume.
        
        Returns:
            list: A list of extracted research interests
        """
        interests = []
        
        # Find sections that might contain research interests
        research_section = None
        for section_name, content in self.sections.items():
            if "RESEARCH" in section_name or "INTERESTS" in section_name:
                research_section = content
                break
        
        if not research_section:
            # Try to find research interests in skills section
            for section_name, content in self.sections.items():
                if "SKILLS" in section_name:
                    research_section = content
                    break
        
        if not research_section and "FULL_TEXT" in self.sections:
            # If we still don't have a section, use the full text
            research_section = self.sections["FULL_TEXT"]
        
        if not research_section:
            return interests
        
        # Look for common patterns indicating research interests
        # Bullet points or comma-separated lists are common
        
        # Try to find bulleted or numbered lists
        bullet_pattern = r"(?:^|\n)[\s]*(?:[\*\-•◦‣⁃⁌⁍⦾⦿⧈⧇⧄⧅]|\d+\.)[\s]+([^\n]+)"
        bullet_matches = re.findall(bullet_pattern, research_section)
        
        if bullet_matches:
            # Process each bullet point
            for match in bullet_matches:
                # If bullet point is very long, it might be a project description, not an interest
                if len(match) < 100:  # Arbitrary threshold
                    match = re.sub(r"^[^a-zA-Z0-9]+", "", match).strip()  # Remove non-alphanumeric prefixes
                    interests.append(match)
        else:
            # Try to find interests in the text
            # First, look for keywords that signal research interests
            interest_markers = [
                "research interests include", "interested in", "focusing on",
                "specializing in", "research areas", "areas of interest"
            ]
            
            for marker in interest_markers:
                pattern = r"(?:" + re.escape(marker) + r")\s*:?\s*([^.]+)"
                match = re.search(pattern, research_section, re.IGNORECASE)
                if match:
                    interest_text = match.group(1).strip()
                    # Split by common delimiters
                    for interest in re.split(r"[,;]", interest_text):
                        clean_interest = interest.strip()
                        if clean_interest and clean_interest.lower() not in ["and", "or"]:
                            interests.append(clean_interest)
                    break
            
            # If still no interests found, try to extract technical skills and research topics
            if not interests:
                # Extract phrases that look like technical topics
                topic_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[a-z]+)*)\b"
                topic_matches = re.findall(topic_pattern, research_section)
                
                for topic in topic_matches:
                    # Filter to reasonable length phrases
                    if 5 <= len(topic) <= 50 and len(topic.split()) <= 5:
                        # Check if it contains tech/research words
                        tech_words = [
                            "learning", "intelligence", "mining", "vision", "language",
                            "processing", "recognition", "network", "computing", "systems",
                            "design", "engineering", "analysis", "theory", "optimization"
                        ]
                        if any(word.lower() in topic.lower() for word in tech_words):
                            interests.append(topic)
                
                # Limit to a reasonable number of interests if we have too many
                interests = interests[:10]  # Arbitrary limit
        
        return interests
    
    def parse(self):
        """
        Parse the resume and extract all available information.
        
        Returns:
            dict: A dictionary of all extracted information
        """
        return {
            "name": self.extract_name(),
            "education": self.extract_education(),
            "research_interests": self.extract_research_interests()
        }


# Example usage
if __name__ == "__main__":
    parser = ResumeParser("test_resume.pdf")
    parsed_data = parser.parse()
    print(parsed_data)
