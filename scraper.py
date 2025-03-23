#!/usr/bin/env python3
"""
Enhanced faculty scraper that supports multiple university websites.
Collects and stores faculty information from top AI/ML universities.
"""

import json
import csv
import os
import time
import argparse
from datetime import datetime

# Import university-specific scrapers
from scrapers import StanfordScraper, MITScraper, BerkeleyScraper
import config

def get_scrapers():
    """
    Initialize enabled university scrapers based on configuration.
    
    Returns:
        list: List of initialized scraper instances
    """
    scrapers = []
    
    # Add Stanford scraper if enabled
    if config.UNIVERSITIES['stanford']['enabled']:
        scrapers.append(StanfordScraper(delay=config.UNIVERSITIES['stanford']['delay']))
    
    # Add MIT scraper if enabled
    if config.UNIVERSITIES['mit']['enabled']:
        scrapers.append(MITScraper(delay=config.UNIVERSITIES['mit']['delay']))
    
    # Add Berkeley scraper if enabled
    if config.UNIVERSITIES['berkeley']['enabled']:
        scrapers.append(BerkeleyScraper(delay=config.UNIVERSITIES['berkeley']['delay']))
    
    return scrapers

def save_to_json(data, filename="faculty_data.json"):
    """
    Save faculty data to a JSON file
    
    Args:
        data (list): List of faculty data dictionaries
        filename (str): Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to file: {e}")

def save_to_csv(data, filename="faculty_data.csv"):
    """
    Save faculty data to a CSV file
    
    Args:
        data (list): List of faculty data dictionaries
        filename (str): Output filename
    """
    try:
        if not data:
            print("No data to save to CSV")
            return
            
        # Get fieldnames from the first item (assumes all items have the same structure)
        fieldnames = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Handle list fields like research_interests and publications
            for row in data:
                # Convert list fields to string representation for CSV
                for key, value in row.items():
                    if isinstance(value, list):
                        row[key] = '; '.join(value)
                writer.writerow(row)
                
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to CSV file: {e}")

def main():
    """Main entry point for the scraper"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape faculty data from top AI/ML universities')
    parser.add_argument('--format', choices=['json', 'csv'], help='Output format (json or csv)')
    parser.add_argument('--output', help='Output filename (without extension)')
    parser.add_argument('--separate', action='store_true', help='Create separate files for each university')
    args = parser.parse_args()
    
    # Override config with command line arguments if provided
    output_format = args.format or config.OUTPUT['format']
    filename = args.output or config.OUTPUT['filename']
    separate_files = args.separate or config.OUTPUT['separate_files']
    
    # Initialize scrapers
    scrapers = get_scrapers()
    
    if not scrapers:
        print("No scrapers enabled in configuration. Please enable at least one university in config.py")
        return
    
    print(f"Starting faculty data scraping with {len(scrapers)} universities...")
    start_time = time.time()
    
    # Run scrapers and collect results
    all_faculty = []
    
    for scraper in scrapers:
        university_name = scraper.university_name
        print(f"\n{'='*50}")
        print(f"Scraping {university_name}...")
        print(f"{'='*50}")
        
        faculty_data = scraper.scrape_faculty_list()
        
        # Limit the number of faculty per university if configured
        max_faculty = config.SCRAPING['max_faculty_per_university']
        if max_faculty > 0 and len(faculty_data) > max_faculty:
            print(f"Limiting to {max_faculty} faculty members from {university_name}")
            faculty_data = faculty_data[:max_faculty]
        
        print(f"Found {len(faculty_data)} faculty members at {university_name}")
        
        # Add timestamp for data freshness tracking
        timestamp = datetime.now().isoformat()
        for faculty in faculty_data:
            faculty['scraped_at'] = timestamp
        
        # Save university data to separate file if configured
        if separate_files:
            university_filename = f"{filename}_{university_name.lower().replace(' ', '_')}"
            if output_format == 'json':
                save_to_json(faculty_data, f"{university_filename}.json")
            else:
                save_to_csv(faculty_data, f"{university_filename}.csv")
        
        # Add to combined results
        all_faculty.extend(faculty_data)
    
    # Save combined results
    if not separate_files or len(scrapers) > 1:
        if output_format == 'json':
            save_to_json(all_faculty, f"{filename}.json")
        else:
            save_to_csv(all_faculty, f"{filename}.csv")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nScraping completed in {duration:.2f} seconds")
    print(f"Total faculty members scraped: {len(all_faculty)}")

if __name__ == "__main__":
    main()
