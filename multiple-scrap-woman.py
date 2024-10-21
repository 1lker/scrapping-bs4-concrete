import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
import openpyxl
import os
import re

# Define the base URL and page range for web scraping
BRAND = "trend__"

# Dict of category and URLs
category_urls = {
    "kadin-jean": "https://www.{BRAND}.com/kadin-jean-x-g1-c120",
    "kadin-tshirt": "https://www.{BRAND}.com/kadin-t-shirt-x-g1-c73",
    "kadin-gomlek": "https://www.{BRAND}.com/kadin-gomlek-x-g1-c75",
    "kadin-t-shirt": "https://www.{BRAND}.com/kadin-t-shirt-x-g1-c73",
    "kadin-cizme": "https://www.{BRAND}.com/kadin-cizme-x-g1-c1037",
    "kadin-bot": "https://www.{BRAND}.com/kadin-bot-x-g1-c1025",
    "kadin-gunluk-ayakkabi": "https://www.{BRAND}.com/kadin-gunluk-ayakkabi-x-g1-c1352",
    "kadin-sneaker": "https://www.{BRAND}.com/kadin-sneaker-x-g1-c1172",
    "kadin-topuklu-ayakkabi": "https://www.{BRAND}.com/kadin-topuklu-ayakkabi-x-g1-c107",
    "kadin-palto": "https://www.{BRAND}.com/kadin-palto-x-g1-c1130",
    "kadin-hirka": "https://www.{BRAND}.com/kadin-hirka-x-g1-c1066",
    "kadin-kaban": "https://www.{BRAND}.com/kadin-kaban-x-g1-c1075",
    "kadin-sweatshirt": "https://www.{BRAND}.com/kadin-sweatshirt-x-g1-c1179",
    "kadin-trenckot": "https://www.{BRAND}.com/kadin-trenckot-x-g1-c79",
    "kadin-buyuk-beden": "https://www.{BRAND}.com/kadin-buyuk-beden-x-g1-c80",
    "kadin-tesettur-giyim": "https://www.{BRAND}.com/kadin-tesettur-giyim-x-g1-c81",
    "kadin-kazak": "https://www.{BRAND}.com/kadin-kazak-x-g1-c1092",
    "etek": "https://www.{BRAND}.com/etek-x-c69",
    "kadin-bluz": "https://www.{BRAND}.com/kadin-bluz-x-g1-c1019",
    "kadin-elbise": "https://www.{BRAND}.com/kadin-elbise-x-g1-c1020",
    "kadin-etek": "https://www.{BRAND}.com/etek-x-c69"
}




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
            "PropertyValues": json.dumps(property_values, ensure_ascii=False),
        }
        print(f"Scraped data for: {product_data['Name']}")
        return product_data
    return None

# Loop through each category URL
for category_name, category_url in category_urls.items():
    data = []  # Reset data for each category

    # Create a directory for the category
    os.makedirs("drive/MyDrive/" + category_name, exist_ok=True)

    # Loop through the pages and scrape the data for the current category
    for page_number in range(1, 26):  # 25 pages
        url = f"{category_url}?pi={page_number}"
        r = requests.get(url)
        r.encoding = 'utf-8'  # Ensure the response is interpreted as UTF-8
        soup = BeautifulSoup(r.text, "html.parser")
        products = soup.find_all("div", attrs={"class": "p-card-wrppr with-campaign-view"})

        product_links = []
        for product in products:
            product_links.extend([f"https://www.{BRAND}.com{link.find('a').get('href')}" for link in product.find_all("div", attrs={"class": "card-border"}) if link.find("a")])

        # Use ThreadPoolExecutor to fetch product details concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(scrape_product, product_links))

        # Filter out None results and extend the data list
        data.extend(filter(None, results))

    # Convert dataset to a DataFrame
    df = pd.DataFrame(data)
    print(f"Data for {category_name} scraped. Total products: {len(df)}")

    # Save as CSV and Excel files named after the category, in the respective folder
    df.to_csv(f'drive/MyDrive/{category_name}/{BRAND}_{category_name}.csv', encoding="utf-8", index=False)
