Capterra Review Scraper
This Python script scrapes company reviews from Capterra, a popular software review website. It uses the Firecrawl API to handle web scraping and BeautifulSoup for parsing HTML. The scraped data, including reviewer details, ratings, and review content, is saved into a structured JSON file.

The script is designed to be robust, with fallbacks for different HTML layouts, and includes features for filtering reviews by a specific date range.

Features
Dynamic Scraping: Scrapes multiple pages of reviews for a specified company.

Detailed Data Extraction: Extracts reviewer name, review title, date, rating, main content, pros, and cons.

Date Filtering: Allows you to scrape reviews only within a specified start and end date.

Robust Parsing: Uses multiple CSS selectors and fallback mechanisms to handle variations in Capterra's page structure.

Command-Line Interface: Easy to use with command-line arguments to specify the company, company ID, and date range.

JSON Output: Saves all scraped reviews in a clean, human-readable JSON file.

Firecrawl Integration: Leverages the Firecrawl service to bypass scraping challenges and handle JavaScript-rendered pages effectively.
