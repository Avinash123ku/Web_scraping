# Capterra Review Scraper

A robust Python script that scrapes company reviews from Capterra, a popular software review website. The script uses the Firecrawl API for web scraping and BeautifulSoup for HTML parsing, saving all scraped data into a structured JSON file.

## 🌟 Features

- **Dynamic Scraping**: Scrapes multiple pages of reviews for any specified company
- **Detailed Data Extraction**: Extracts reviewer name, review title, date, rating, main content, pros, and cons
- **Date Filtering**: Filter reviews by specific date ranges
- **Robust Parsing**: Multiple CSS selectors and fallback mechanisms handle variations in Capterra's page structure
- **Command-Line Interface**: Easy-to-use CLI with customizable parameters
- **JSON Output**: Clean, human-readable JSON file output
- **Firecrawl Integration**: Bypasses scraping challenges and handles JavaScript-rendered pages effectively

## 📋 Prerequisites

- Python 3.x
- Firecrawl API key (free account available)

## 🚀 Installation

1. **Clone or download the script**
   ```bash
   git clone <your-repo-url>
   cd capterra-review-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Firecrawl API Key**
   - Sign up at [Firecrawl website](https://firecrawl.dev) to get your free API key

4. **Create environment file**
   
   Create a `.env` file in the script directory:
   ```env
   FIRECRAWL_API_KEY="YOUR_FIRECRAWL_API_KEY_HERE"
   ```
   Replace `YOUR_FIRECRAWL_API_KEY_HERE` with your actual API key.


## 🔍 Finding Company ID

To scrape reviews for any company, you need to find their Capterra company ID:

1. Go to [Capterra website](https://www.capterra.in)
2. Search for your target company
3. Navigate to their reviews page
4. Check the URL format: `https://www.capterra.in/reviews/COMPANY_ID/company-name`

**Examples:**
- FloBooks: `https://www.capterra.in/reviews/202732/flobooks` → Company ID: `202732`
- TyaSuite: `https://www.capterra.in/reviews/190444/tyasuite` → Company ID: `190444`

## 📝 Usage

### Command-Line Arguments

| Argument | Description | Default | Required |
|----------|-------------|---------|----------|
| `--company` | Company name | FloBooks | No |
| `--company_id` | Capterra company ID | 202732 | Yes (for non-default) |
| `--start_date` | Start date for filtering (DD/MM/YYYY) | None | No |
| `--end_date` | End date for filtering (DD/MM/YYYY) | None | No |

### Example Commands

1. **Scrape FloBooks reviews (default)**
   ```bash
   python scrapper.py --company "flobooks" --company_id "202732" --start_date "01/01/2018" --end_date "31/12/2025"
   ```

2. **Scrape TyaSuite reviews with date filtering**
   ```bash
   python scrapper.py --company "tyasuite" --company_id "190444" --start_date "01/01/2018" --end_date "31/12/2025"
   ```

3. **Scrape any company reviews**
   ```bash
   python scrapper.py --company "COMPANY_NAME" --company_id "COMPANY_ID" --start_date "DD/MM/YYYY" --end_date "DD/MM/YYYY"
   ```

## 📄 Output

The script generates a JSON file containing all scraped reviews with the following structure:

```json
{
  "company": "Company Name",
  "total_reviews": 50,
  "scraped_at": "2025-09-08T10:30:00",
  "reviews": [
    {
      "reviewer_name": "John Doe",
      "review_title": "Great software!",
      "review_date": "15/08/2024",
      "rating": 4.5,
      "review_content": "Main review content...",
      "pros": "Easy to use, great features",
      "cons": "Could be faster"
    }
  ]
}
```

## 🛠️ Requirements

Create a `requirements.txt` file with the following dependencies:

```txt
requests
beautifulsoup4
firecrawl-py
python-dotenv
argparse
json
datetime
```



**Happy Scraping! 🎉**
