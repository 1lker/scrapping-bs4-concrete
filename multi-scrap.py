import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
import openpyxl

# Define the base URL and page range for web scraping
base_url = "here_is_the_url_you_want_to_scrape"
start_page = 1
end_page = 25

# Create an empty list to store the scraped data
data = []

# Function to extract JSON-LD data
def extract_json_ld(soup):
    json_ld = soup.find('script', type='application/ld+json')
    if json_ld:
        return json.loads(json_ld.string)
    return None

# Function to scrape product details
def scrape_product(link):
    detail = requests.get(link)
    detail.encoding = 'utf-8'  # Ensure the response is interpreted as UTF-8
    detail_soup = BeautifulSoup(detail.text, "html.parser")
    
    # Extract JSON-LD data
    json_ld_data = extract_json_ld(detail_soup)
    
    if json_ld_data:
        # Extract PropertyValue items
        property_values = {}
        for prop in json_ld_data.get("additionalProperty", []):
            if prop.get("@type") == "PropertyValue":
                property_values[prop["name"]] = prop["unitText"]
        
        product_data = {
            "Link": link,
            "Name": json_ld_data.get("name"),
            "Brand": json_ld_data.get("brand", {}).get("name"),
            "Description": json_ld_data.get("description"),
            "SKU": json_ld_data.get("sku"),
            "Color": json_ld_data.get("color"),
            "Pattern": json_ld_data.get("pattern"),
            "Price": json_ld_data.get("offers", {}).get("price"),
            "Currency": json_ld_data.get("offers", {}).get("priceCurrency"),
            "Availability": json_ld_data.get("offers", {}).get("availability"),
            "Images": json.dumps(json_ld_data.get("image", {}).get("contentUrl"), ensure_ascii=False),
            "AggregateRating": json.dumps(json_ld_data.get("aggregateRating"), ensure_ascii=False),
            "Reviews": json.dumps(json_ld_data.get("review"), ensure_ascii=False),
            "PropertyValues": json.dumps(property_values, ensure_ascii=False)
        }
        print(f"Scraped data for: {product_data['Name']}")
        return product_data
    return None

# Loop through the pages and scrape the data
for page_number in range(start_page, end_page + 1):
    url = base_url + str(page_number)
    r = requests.get(url)
    r.encoding = 'utf-8'  # Ensure the response is interpreted as UTF-8
    soup = BeautifulSoup(r.text, "html.parser")
    products = soup.find_all("div", attrs={"class": "p-card-wrppr with-campaign-view"})
    
    product_links = []
    for product in products:
        product_links.extend([f"https://www.___.com{link.find('a').get('href')}" for link in product.find_all("div", attrs={"class": "card-border"}) if link.find("a")])
    
    # Use ThreadPoolExecutor to fetch product details concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        print(f"Scraping product details for {len(product_links)} products...")
        results = list(executor.map(scrape_product, product_links))
    
    # Filter out None results and extend the data list
    data.extend(filter(None, results))

# Convert dataset to a DataFrame
df = pd.DataFrame(data)
print(df)

# Converting it to CSV so we can download
df.to_csv('csv_all_data.csv', encoding="utf-8", index=False)

# Optionally, you can also save as Excel file which handles UTF-8 well
df.to_excel('excel_all_data.xlsx', index=False, engine='openpyxl')


