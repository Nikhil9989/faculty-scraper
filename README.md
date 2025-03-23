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

## Features

- Modular architecture with university-specific scrapers
- Support for multiple universities:
  - Stanford University CS
  - MIT CSAIL
  - UC Berkeley EECS
- Configurable scraping settings
- Export to JSON or CSV formats
- Command-line arguments for customization

## Installation

```bash
# Clone the repository
git clone https://github.com/Nikhil9989/faculty-scraper.git
cd faculty-scraper

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python scraper.py
```

This will scrape faculty data from all enabled universities and save it as `faculty_data.json` in the current directory.

### Advanced Usage

```bash
# Specify output format (json or csv)
python scraper.py --format csv

# Specify custom output filename
python scraper.py --output my_faculty_data

# Create separate files for each university
python scraper.py --separate
```

### Configuration

Edit the `config.py` file to customize:
- Which universities to scrape
- Request delay times
- Output format and filenames
- Maximum faculty members per university

## Project Structure

```
faculty-scraper/
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── stanford_scraper.py
│   ├── mit_scraper.py
│   └── berkeley_scraper.py
├── scraper.py
├── config.py
├── requirements.txt
└── README.md
```

## Adding a New University

To add support for a new university:

1. Create a new scraper class in the `scrapers` directory, inheriting from `UniversityScraper`
2. Implement the required methods: `scrape_faculty_list` and `scrape_faculty_profile`
3. Add your scraper to `__init__.py`
4. Update the `config.py` file to include your new university
5. Add an instance of your scraper to the `get_scrapers()` function in `scraper.py`

## License

MIT
