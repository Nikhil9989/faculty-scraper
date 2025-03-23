#!/usr/bin/env python3
"""
Enhanced web scraper for faculty data from Stanford University's CS department.
Extracts more detailed information including research interests, email, and publications.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

def scrape_stanford_cs_faculty():
    """
    Scrape detailed faculty data from Stanford University's Computer Science department.
    
    Returns:
        list: A list of dictionaries containing faculty information
    """
    print("Scraping Stanford CS faculty data...")
    
    # URL for Stanford CS faculty
    url = "https://cs.stanford.edu/people/faculty"
    
    # Send HTTP request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []
    
    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract faculty information
    faculty_list = []
    
    # Find all faculty members (this selector will need to be adjusted based on the actual webpage structure)
    faculty_elements = soup.select('.views-row')
    
    for faculty_elem in faculty_elements:
        try:
            # Extract basic information (selectors will need adjustment)
            name_elem = faculty_elem.select_one('.field-content h3')
            name = name_elem.text.strip() if name_elem else "Unknown"
            
            # Extract title
            title_elem = faculty_elem.select_one('.field-content .people-title')
            title = title_elem.text.strip() if title_elem else ""
            
            # Extract faculty profile URL
            profile_elem = name_elem.find('a') if name_elem else None
            profile_url = profile_elem['href'] if profile_elem and 'href' in profile_elem.attrs else None
            
            # Get more detailed information from profile page if available
            research_interests = []
            email = ""
            publications = []
            
            if profile_url:
                detailed_info = scrape_faculty_profile(profile_url)
                research_interests = detailed_info.get('research_interests', [])
                email = detailed_info.get('email', '')
                publications = detailed_info.get('publications', [])
            
            # Construct faculty data
            faculty_data = {
                "name": name,
                "title": title,
                "university": "Stanford University",
                "department": "Computer Science",
                "email": email,
                "research_interests": research_interests,
                "publications": publications,
                "profile_url": profile_url
            }
            
            faculty_list.append(faculty_data)
            
            # Be a good citizen - add delay to not overload the server
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing faculty member {name if 'name' in locals() else 'unknown'}: {e}")
            continue
    
    print(f"Successfully scraped {len(faculty_list)} faculty members from Stanford CS")
    return faculty_list

def scrape_faculty_profile(profile_url):
    """
    Scrape detailed information from faculty profile page
    
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
        profile_url = f"https://cs.stanford.edu{profile_url}"
    
    try:
        # Make request to profile page
        print(f"Fetching profile: {profile_url}")
        response = requests.get(profile_url)
        response.raise_for_status()
        
        # Parse HTML content
        profile_soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract research interests (selector needs to be adjusted based on actual page structure)
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
        print(f"Error fetching faculty profile {profile_url}: {e}")
    
    return detailed_info

def save_to_json(data, filename="faculty_data.json"):
    """
    Save faculty data to a JSON file
    
    Args:
        data (list): List of faculty data dictionaries
        filename (str): Output filename
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to file: {e}")

def main():
    # Scrape faculty data
    faculty_data = scrape_stanford_cs_faculty()
    
    # Save to JSON file
    if faculty_data:
        save_to_json(faculty_data)

if __name__ == "__main__":
    main()
