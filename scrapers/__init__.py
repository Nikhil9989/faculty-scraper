"""
Faculty scrapers package.
"""

from .stanford_scraper import StanfordScraper
from .mit_scraper import MITScraper
from .berkeley_scraper import BerkeleyScraper

# Export scrapers
__all__ = [
    'StanfordScraper',
    'MITScraper',
    'BerkeleyScraper'
]
