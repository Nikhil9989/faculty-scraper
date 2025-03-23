"""
Base classes for university scrapers.
"""

import requests
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod

class UniversityScraper(ABC):
    """
    Abstract base class for university faculty scrapers.
    All university-specific scrapers should inherit from this class.
    """
    
    def __init__(self, delay=1):
        """
        Initialize the scraper.
        
        Args:
            delay (int): Time delay in seconds between requests to be respectful
        """
        self.delay = delay
        self.university_name = "Unknown University"
        self.department_name = "Unknown Department"
    
    @abstractmethod
    def scrape_faculty_list(self):
        """
        Scrape the list of faculty members from the university website.
        
        Returns:
            list: A list of dictionaries containing faculty information
        """
        pass
    
    @abstractmethod
    def scrape_faculty_profile(self, profile_url):
        """
        Scrape detailed information from a faculty profile page.
        
        Args:
            profile_url (str): URL to the faculty profile page
        
        Returns:
            dict: Dictionary containing detailed faculty information
        """
        pass
    
    def make_request(self, url, headers=None):
        """
        Make an HTTP request to the specified URL.
        
        Args:
            url (str): The URL to request
            headers (dict, optional): HTTP headers to include
            
        Returns:
            BeautifulSoup: Parsed HTML content or None if the request fails
        """
        try:
            print(f"Fetching: {url}")
            
            # Default headers to mimic a browser
            if headers is None:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5'
                }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Add delay to be respectful to the server
            time.sleep(self.delay)
            
            return BeautifulSoup(response.text, 'html.parser')
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
