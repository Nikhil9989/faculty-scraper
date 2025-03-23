"""
Resume parser factory module.

This module provides a factory pattern to create the appropriate parser
based on the resume file type.
"""

import os
import logging
from parser import ResumeParser
from docx_parser import DocxResumeParser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParserFactory:
    """
    Factory class for creating resume parsers based on file type.
    """
    
    @staticmethod
    def get_parser(file_path):
        """
        Get the appropriate parser for the given file.
        
        Args:
            file_path (str): Path to the resume file
            
        Returns:
            ResumeParser: The appropriate parser instance
            
        Raises:
            ValueError: If the file type is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        _, ext = os.path.splitext(file_path.lower())
        
        # Create appropriate parser based on file extension
        if ext == '.pdf':
            logger.info(f"Creating PDF parser for {file_path}")
            return ResumeParser(file_path)
        elif ext == '.docx':
            logger.info(f"Creating DOCX parser for {file_path}")
            return DocxResumeParser(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}. Supported types are: .pdf, .docx")

def parse_resume(file_path):
    """
    Parse a resume file using the appropriate parser.
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        dict: Parsed resume data
    """
    try:
        parser = ParserFactory.get_parser(file_path)
        return parser.parse()
    except Exception as e:
        logger.error(f"Error parsing resume {file_path}: {str(e)}")
        return {
            "error": str(e),
            "file_path": file_path
        }

def main():
    """Simple test for the parser factory"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python parser_factory.py [resume_file_path]")
        return
    
    try:
        result = parse_resume(sys.argv[1])
        print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
