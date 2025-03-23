# Faculty Scraper

A web scraping tool to extract faculty data from top AI/ML university websites.

## Overview

This project aims to collect information about faculty members from top AI/ML universities, specifically focusing on:
- Faculty names
- Research interests
- University affiliation
- Contact information (email)
- Publications

The collected data will be stored in structured formats (JSON/CSV) and can be used for matching with student resumes to find potential research advisors based on shared interests.

## Current Features

- Basic scraping of Stanford CS faculty information
- Data extraction and JSON storage

## Installation

```bash
# Clone the repository
git clone https://github.com/Nikhil9989/faculty-scraper.git
cd faculty-scraper

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python scraper.py
```

This will scrape faculty data and save it as `faculty_data.json` in the current directory.

## Future Enhancements

- Support for additional universities
- More comprehensive data extraction
- Database integration
- Resume matching algorithm

## License

MIT
