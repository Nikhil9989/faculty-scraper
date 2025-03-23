"""
Configuration settings for the faculty scraper.
"""

# Universities to scrape
UNIVERSITIES = {
    'stanford': {
        'enabled': True,
        'delay': 1,  # Time delay between requests in seconds
    },
    'mit': {
        'enabled': True,
        'delay': 1,
    },
    'berkeley': {
        'enabled': True,
        'delay': 1,
    }
}

# Output settings
OUTPUT = {
    'format': 'json',  # 'json' or 'csv'
    'filename': 'faculty_data',  # Will be appended with appropriate extension
    'separate_files': False,  # If True, create separate files for each university
}

# Scraping settings
SCRAPING = {
    'max_faculty_per_university': 50,  # Maximum number of faculty to scrape per university (0 for no limit)
    'timeout': 30,  # HTTP request timeout in seconds
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}
