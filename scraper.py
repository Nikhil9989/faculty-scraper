#!/usr/bin/env python3
"""
Basic web scraper for faculty data from Stanford University's CS department.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time

def scrape_stanford_cs_faculty():
    """
    Scrape faculty data from Stanford University's Computer Science department.
    
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
            
            # Some basic information extraction
            title_elem = faculty_elem.select_one('.field-content .people-title')
            title = title_elem.text.strip() if title_elem else ""
            
            # Construct faculty data
            faculty_data = {
                "name": name,
                "title": title,
                "university": "Stanford University",
                "department": "Computer Science"
            }
            
            faculty_list.append(faculty_data)
            
        except Exception as e:
            print(f"Error processing faculty member: {e}")
            continue
    
    print(f"Successfully scraped {len(faculty_list)} faculty members from Stanford CS")
    return faculty_list

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
