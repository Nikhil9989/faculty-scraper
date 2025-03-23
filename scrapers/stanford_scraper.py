"""
Stanford University scraper for CS faculty.
"""

import re
from .base_scraper import UniversityScraper

class StanfordScraper(UniversityScraper):
    """
    Scraper for Stanford University's Computer Science faculty.
    """
    
    def __init__(self, delay=1):
        """Initialize the Stanford scraper"""
        super().__init__(delay)
        self.university_name = "Stanford University"
        self.department_name = "Computer Science"
        self.base_url = "https://cs.stanford.edu"
        self.faculty_list_url = f"{self.base_url}/people/faculty"
    
    def scrape_faculty_list(self):
        """
        Scrape the list of faculty members from Stanford CS department.
        
        Returns:
            list: A list of dictionaries containing faculty information
        """
        print(f"Scraping {self.university_name} {self.department_name} faculty data...")
        
        # Get the faculty listing page
        faculty_soup = self.make_request(self.faculty_list_url)
        if not faculty_soup:
            return []
        
        # Extract faculty information
        faculty_list = []
        
        # Find all faculty members
        faculty_elements = faculty_soup.select('.views-row')
        
        for faculty_elem in faculty_elements:
            try:
                # Extract basic information
                name_elem = faculty_elem.select_one('.field-content h3')
                name = name_elem.text.strip() if name_elem else "Unknown"
                
                # Extract title
                title_elem = faculty_elem.select_one('.field-content .people-title')
                title = title_elem.text.strip() if title_elem else ""
                
                # Extract faculty profile URL
                profile_elem = name_elem.find('a') if name_elem else None
                profile_url = profile_elem['href'] if profile_elem and 'href' in profile_elem.attrs else None
                
                # Get more detailed information from profile page if available
                detailed_info = {}
                if profile_url:
                    detailed_info = self.scrape_faculty_profile(profile_url)
                
                # Construct faculty data
                faculty_data = {
                    "name": name,
                    "title": title,
                    "university": self.university_name,
                    "department": self.department_name,
                    "email": detailed_info.get('email', ''),
                    "research_interests": detailed_info.get('research_interests', []),
                    "publications": detailed_info.get('publications', []),
                    "profile_url": profile_url
                }
                
                faculty_list.append(faculty_data)
                
            except Exception as e:
                print(f"Error processing Stanford faculty member {name if 'name' in locals() else 'unknown'}: {e}")
                continue
        
        print(f"Successfully scraped {len(faculty_list)} faculty members from {self.university_name}")
        return faculty_list
    
    def scrape_faculty_profile(self, profile_url):
        """
        Scrape detailed information from a Stanford faculty profile page.
        
        Args:
            profile_url (str): URL to faculty profile page
            
        Returns:
            dict: Dictionary containing detailed faculty information
        """
        detailed_info = {
            'research_interests': [],
            'email': '',
            'publications': []
        }
        
        # Handle relative URLs
        if profile_url and not profile_url.startswith('http'):
            profile_url = f"{self.base_url}{profile_url}"
        
        # Get the profile page
        profile_soup = self.make_request(profile_url)
        if not profile_soup:
            return detailed_info
        
        try:
            # Extract research interests
            research_section = profile_soup.find('h2', string=re.compile('Research', re.IGNORECASE))
            if research_section:
                # Get the container that follows the research header
                research_container = research_section.find_next('div')
                if research_container:
                    # Extract text content and split into interests
                    research_text = research_container.get_text(strip=True)
                    interests = [interest.strip() for interest in re.split(r'[,;•]', research_text) if interest.strip()]
                    detailed_info['research_interests'] = interests
            
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_matches = re.findall(email_pattern, profile_soup.get_text())
            if email_matches:
                detailed_info['email'] = email_matches[0]
            
            # Extract publications
            pubs_section = profile_soup.find(['h2', 'h3'], string=re.compile('Publications|Selected Publications', re.IGNORECASE))
            if pubs_section:
                # Get the container that follows the publications header
                pubs_container = pubs_section.find_next(['div', 'ul'])
                if pubs_container:
                    # If the container is a list, extract list items
                    if pubs_container.name == 'ul':
                        for li in pubs_container.find_all('li'):
                            pub_text = li.get_text(strip=True)
                            if pub_text:
                                detailed_info['publications'].append(pub_text)
                    # Otherwise, look for paragraph elements or other text
                    else:
                        for p in pubs_container.find_all('p'):
                            pub_text = p.get_text(strip=True)
                            if pub_text:
                                detailed_info['publications'].append(pub_text)
                
                # Limit to 5 publications to keep data manageable
                detailed_info['publications'] = detailed_info['publications'][:5]
                
        except Exception as e:
            print(f"Error fetching Stanford faculty profile {profile_url}: {e}")
        
        return detailed_info
