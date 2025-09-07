import os
import json
import requests
from bs4 import BeautifulSoup
from firecrawl import Firecrawl
import time
import re
from datetime import datetime
import argparse
from dotenv import load_dotenv

load_dotenv()


class CapterraScraper:
    def __init__(self, company_name=None, company_id=None, start_date=None, end_date=None):
        self.company_name = company_name
        self.company_id = company_id
        self.start_date = start_date
        self.end_date = end_date
        self.all_reviews = []

    @staticmethod
    def parse_date_argument(input_date: str) -> datetime:
        """
        Convert CLI date argument strings like '09/05/2023', '9/5/2023', '9//5/2023'
        into a datetime object.
        """
        # Remove any duplicate slashes and leading/trailing whitespace
        clean_date = input_date.replace("//", "/").strip()

        # List of possible formats to try
        date_formats = [
            "%d/%m/%Y",  # e.g., 09/05/2023
            "%d/%m/%y",  # e.g., 09/05/23
            "%m/%d/%Y",  # e.g., 05/09/2023 (US format)
            "%m/%d/%y",  # e.g., 05/09/23 (US format)
        ]

        for fmt in date_formats:
            try:
                # Return the datetime object on the first successful parse
                return datetime.strptime(clean_date, fmt)
            except ValueError:
                continue

        # If all formats fail, raise an error with guidance
        raise ValueError(
            f"Unsupported date format: '{input_date}'. Please use a format like DD/MM/YYYY.")

    @staticmethod
    def parse_review_date(review_date_str: str) -> datetime:
        """
        Parse review date strings in various formats to datetime objects
        Handles formats like:
        - "9 March 2023"
        - "March 9, 2023"
        - "09/03/2023"
        """
        # Remove any commas and extra spaces
        date_str = review_date_str.replace(',', '').strip()

        # Try different date formats
        date_formats = [
            "%d %B %Y",  # 9 March 2023
            "%B %d %Y",  # March 9 2023
            "%d/%m/%Y",  # 09/03/2023
            "%m/%d/%Y",  # 03/09/2023 (US format)
            "%Y-%m-%d",  # 2023-03-09
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # If none of the formats work, return None
        print(f"Warning: Could not parse review date: {review_date_str}")
        return None

    def extract_element_text(self, card, selectors, attribute=None):
        """
        Extract text from an HTML element using multiple selector options.
        """
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                if attribute and element.has_attr(attribute):
                    return element[attribute]
                return element.get_text(strip=True)
        return "Unknown" if attribute is None else ""

    def scrape_page(self, firecrawl, url, page_number):
        """
        Scrape a single page using Firecrawl and return parsed HTML.
        """
        print(f"Scraping page {page_number}...")
        print(f"URL: {url}")

        try:
            # Scrape the page with Firecrawl
            doc = firecrawl.scrape(url, formats=["html"])

            # Extract HTML content from response
            if hasattr(doc, 'html'):
                html_content = doc.html
            elif isinstance(doc, dict) and 'html' in doc:
                html_content = doc['html']
            else:
                print("Unexpected response format from Firecrawl")
                return None

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Save HTML for debugging
            with open(f"debug_page_{page_number}.html", "w", encoding="utf-8") as f:
                f.write(str(soup))

            return soup

        except Exception as e:
            print(f"Error scraping page {page_number}: {e}")
            return None

    def extract_review_data(self, card, current_page):
        """
        Extract review data from a single review card element.
        """
        try:
            # Define CSS selectors for various review elements
            NAME_SELECTORS = ['div.fw-600', '.reviewer-name',
                              '[data-testid*="reviewer"]', 'h4', 'strong']
            TITLE_SELECTORS = ['h3', 'h2',
                               '.review-title', '[data-testid*="title"]']
            DATE_SELECTORS = ['time', '.review-date',
                              '[datetime]', '.fs-5', '.text-muted']
            CONTENT_SELECTORS = ['p', '.review-content', '.fs-4.lh-2',
                                 '[data-testid*="content"]']

            # Extract reviewer name
            reviewer_name = self.extract_element_text(card, NAME_SELECTORS)

            # Extract review title
            review_title = self.extract_element_text(card, TITLE_SELECTORS)

            # Extract review date - try both text content and datetime attribute
            review_date_str = self.extract_element_text(
                card, DATE_SELECTORS, 'datetime')
            if review_date_str == "Unknown":
                review_date_str = self.extract_element_text(
                    card, DATE_SELECTORS)

            # Parse the date string to datetime object
            review_date = self.parse_review_date(review_date_str)

            # Extract rating - special handling for rating elements
            rating = 0.0
            rating_selectors = [
                '[aria-label*="star"]', '[class*="rating"]',
                '[class*="star"]', '.rating'
            ]

            for selector in rating_selectors:
                element = card.select_one(selector)
                if element:
                    rating_text = element.get_text(
                        strip=True) or element.get('aria-label', '')
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                    break

            # Extract review content
            content = self.extract_element_text(card, CONTENT_SELECTORS)

            # Extract pros and cons if available
            pros, cons = "", ""
            pros_cons_sections = card.find_all(
                ['div', 'p', 'ul'],
                string=re.compile(r'pros:|cons:', re.IGNORECASE)
            )

            for section in pros_cons_sections:
                text = section.get_text(strip=True).lower()
                if 'pros:' in text:
                    pros = section.get_text(strip=True)
                elif 'cons:' in text:
                    cons = section.get_text(strip=True)

            # Compile review data
            review_data = {
                'reviewer_name': reviewer_name,
                'review_title': review_title,
                'review_date': review_date_str,
                'parsed_date': review_date.isoformat() if review_date else None,
                'rating': rating,
                'content': content,
                'pros': pros,
                'cons': cons,
                'page': current_page,
                'source': 'Capterra'
            }

            return review_data

        except Exception as e:
            print(f"Error parsing a review card: {e}")
            return None

    def has_next_page(self, soup, current_page):
        """
        Check if there is a next page available.
        """
        # Look for pagination controls with multiple strategies
        pagination = soup.find('nav', {'aria-label': 'Pagination'})
        if pagination:
            next_button = pagination.find('a', {'aria-label': 'Next Page'})
            if next_button:
                # Check if next button is disabled
                if next_button.get('aria-disabled') == 'true':
                    return False
                return True

        # Alternative detection methods
        next_button = soup.find('a', string=re.compile(r'next', re.IGNORECASE))
        if next_button:
            return True

        # Look for page number links
        page_links = soup.find_all(
            'a', href=re.compile(r'page', re.IGNORECASE))
        for link in page_links:
            href = link.get('href', '')
            page_num_match = re.search(r'page=(\d+)', href, re.IGNORECASE)
            if page_num_match:
                page_num = int(page_num_match.group(1))
                if page_num == current_page + 1:
                    return True

        return False

    def run(self):
        """
        Main method to execute the scraping process.
        """
        api_key = os.getenv("FIRECRAWL_API_KEY")
        # Initialize Firecrawl
        firecrawl = Firecrawl(api_key)

        # Default to FloBooks if no company name is provided
        if self.company_name is None:
            self.company_name = "flobooks"

        company_name_lower = self.company_name.lower()

        # Set URL based on company name
        if company_name_lower == "flobooks":
            first_page_url = "https://www.capterra.in/reviews/202732/flobooks"
        elif self.company_id:
            first_page_url = f"https://www.capterra.in/reviews/{self.company_id}/{company_name_lower}"
        else:
            print(
                "Error: A --company_id must be provided for companies other than FloBooks.")
            return []

        print("--- Starting Capterra Review Scraper ---")
        print(f"Scraping reviews for: {self.company_name}")

        if self.start_date and self.end_date:
            print(
                f"Filtering reviews between {self.start_date.strftime('%Y-%m-%d')} and {self.end_date.strftime('%Y-%m-%d')}")

        self.all_reviews = []
        current_page = 1
        has_next_page = True

        while has_next_page:
            print(f"Scraping page {current_page}...")

            # Determine the URL for the current page
            if current_page == 1:
                page_url = first_page_url
            else:
                page_url = f"{first_page_url}?page={current_page}"

            print(f"URL: {page_url}")

            try:
                # Scrape the page
                soup = self.scrape_page(firecrawl, page_url, current_page)
                if not soup:
                    break

                # Find all review containers
                review_cards = soup.find_all('div', {'class': 'review-card'})

                if not review_cards:
                    print("No reviews found on this page. Stopping pagination.")
                    break

                print(f"Found {len(review_cards)} potential review elements")
                page_reviews = []

                for card in review_cards:
                    try:
                        review_data = self.extract_review_data(
                            card, current_page)
                        if review_data:
                            # Apply date filtering if specified
                            review_date = self.parse_review_date(
                                review_data['review_date'])
                            should_add_review = False

                            if self.start_date and self.end_date:
                                if review_date and (self.start_date <= review_date <= self.end_date):
                                    should_add_review = True
                            else:
                                should_add_review = True

                            if should_add_review:
                                page_reviews.append(review_data)
                                print(
                                    f"Added review from {review_data['reviewer_name']} on {review_data['review_date']}")

                    except Exception as e:
                        print(f"Error parsing a review card: {e}")
                        continue

                self.all_reviews.extend(page_reviews)
                print(
                    f"Successfully parsed {len(page_reviews)} reviews on page {current_page}")

                # Check for next page
                has_next_page = self.has_next_page(soup, current_page)
                current_page += 1

                time.sleep(2)  # Increased delay to be more respectful

            except Exception as e:
                print(f"Error scraping page {current_page}: {e}")
                # Try to continue to next page even if this one failed
                current_page += 1

        # Save results to JSON file
        filename = f"capterra_reviews_{company_name_lower}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_reviews, f, indent=2,
                      ensure_ascii=False, default=str)

        print(
            f"Successfully extracted {len(self.all_reviews)} reviews and saved to {filename}")

        # Print summary
        if self.start_date and self.end_date:
            date_filtered = [
                r for r in self.all_reviews
                if r['parsed_date'] and
                self.start_date <= datetime.fromisoformat(
                    r['parsed_date']) <= self.end_date
            ]
            print(f"Reviews within date range: {len(date_filtered)}")

        return self.all_reviews


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape Capterra reviews with date filtering")
    parser.add_argument("--company", default="FloBooks",
                        help="Company name to scrape reviews for")
    parser.add_argument("--company_id", type=int,
                        help="Company's unique ID on Capterra")
    parser.add_argument(
        "--start_date", help="Start date for filtering (e.g., 'DD/MM/YYYY')")
    parser.add_argument(
        "--end_date", help="End date for filtering (e.g., 'DD/MM/YYYY')")

    args = parser.parse_args()

    start_date, end_date = None, None
    try:
        if args.start_date:
            start_date = CapterraScraper.parse_date_argument(args.start_date)
        if args.end_date:
            end_date = CapterraScraper.parse_date_argument(args.end_date)
    except ValueError as e:
        print(f"Error: Invalid date format. {e}")
        exit(1)

    if (start_date and not end_date) or (end_date and not start_date):
        print("Error: Both --start_date and --end_date must be provided together.")
        exit(1)
    if start_date and end_date and start_date > end_date:
        print("Error: Start date cannot be after end date.")
        exit(1)

    # Initialize the scraper and run the process
    scraper = CapterraScraper(
        company_name=args.company,
        company_id=args.company_id,
        start_date=start_date,
        end_date=end_date
    )
    scraper.run()
