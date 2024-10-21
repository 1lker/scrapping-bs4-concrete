# Web Scraping Project

## Overview

This project involves scraping product details from a specified website using Python. The scraped data is then stored in both CSV and Excel formats for further analysis.

## Libraries Used

- **requests**: To make HTTP requests to retrieve web pages.
- **BeautifulSoup**: For parsing HTML and extracting data.
- **pandas**: To organize the scraped data and save it in CSV and Excel formats.
- **json**: To handle JSON-LD data embedded in the HTML.
- **concurrent.futures**: To enable concurrent HTTP requests for improved performance.
- **openpyxl**: To save data in Excel format.

## Code Breakdown

### 1. Setup

- Defined the base URL and the range of pages to scrape.
- Created an empty list `data` to store the scraped product information.

### 2. Functions

- **extract_json_ld(soup)**:
  - Extracts JSON-LD data from the HTML content using BeautifulSoup.
  
- **scrape_product(link)**:
  - Takes a product link, retrieves the product detail page, and parses it to extract relevant product information.
  - Specifically looks for properties like name, brand, description, SKU, color, price, availability, and more.
  - Uses the `extract_json_ld` function to gather structured data in JSON format.
  
### 3. Main Scraping Loop

- Loops through the specified page range.
- For each page, retrieves the HTML content and parses it to find product links.
- Collects product links from the identified HTML elements.
- Utilizes `ThreadPoolExecutor` to concurrently scrape product details from the collected links, improving the efficiency of the scraping process.

### 4. Data Storage

- Filters out any `None` results and extends the `data` list with valid product data.
- Converts the collected data into a pandas DataFrame for easier manipulation and storage.
  
### 5. Output

- Saves the scraped data to a CSV file named `csv_all_data.csv` with UTF-8 encoding.
- Optionally saves the data to an Excel file named `excel_all_data.xlsx` using the `openpyxl` engine.

## Conclusion

This web scraping script efficiently gathers product details from multiple pages, processes the data, and stores it in both CSV and Excel formats for analysis or reporting purposes. Adjustments can be made to the base URL and product selection criteria as needed for different scraping tasks.
