import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
import os

# Define the base URL and page range for web scraping
BRAND = "trend___"

# Dict of category and URLs for erkek with www and {BRAND} placeholder
category_urls = {
    "erkek-tshirt-m": "https://www.{BRAND}.com/erkek-t-shirt-x-g2-c73",
    "erkek-sort-m": "https://www.{BRAND}.com/erkek-sort-x-g2-c119",
    "erkek-gomlek-m": "https://www.{BRAND}.com/erkek-gomlek-x-g2-c75",
    "erkek-esofman-m": "https://www.{BRAND}.com/erkek-esofman-x-g2-c1049",
    "erkek-pantolon-m": "https://www.{BRAND}.com/erkek-pantolon-x-g2-c70",
    "erkek-ceket-m": "https://www.{BRAND}.com/erkek-ceket-x-g2-c1030",
    "erkek-jean-m": "https://www.{BRAND}.com/erkek-jean-x-g2-c120",
    "erkek-kazak-m": "https://www.{BRAND}.com/erkek-kazak-x-g2-c1092",
    "erkek-mont-m": "https://www.{BRAND}.com/erkek-mont-x-g2-c118",
    "erkek-sweatshirt-m": "https://www.{BRAND}.com/erkek-sweatshirt-x-g2-c1179",
    "erkek-kaban-m": "https://www.{BRAND}.com/erkek-kaban-x-g2-c1075",
    "erkek-hirka-m": "https://www.{BRAND}.com/erkek-hirka-x-g2-c1066",
    "erkek-trenckot-m": "https://www.{BRAND}.com/erkek-trenckot-x-g2-c79",
    "erkek-palto-m": "https://www.{BRAND}.com/erkek-palto-x-g2-c1130",
    "erkek-polar-m": "https://www.{BRAND}.com/erkek-polar-x-g2-c1149",
    "erkek-spor-ayakkabi-m": "https://www.{BRAND}.com/erkek-spor-ayakkabi-x-g2-c109",
    "erkek-gunluk-ayakkabi-m": "https://www.{BRAND}.com/erkek-gunluk-ayakkabi-x-g2-c1352",
    "erkek-sneaker-m": "https://www.{BRAND}.com/erkek-sneaker-x-g2-c1172",
    "erkek-bot-m": "https://www.{BRAND}.com/erkek-bot-x-g2-c1025",
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
