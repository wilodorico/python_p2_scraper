import re
import csv
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com"
url_business_book = urljoin(BASE_URL , "catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html")

print(url_business_book)

response = requests.get(url_business_book)

if response.ok:
    soup = BeautifulSoup(response.content, features="html.parser")

    title = soup.find("h1").text.strip()
    description = soup.find("div", id="product_description").find_next_sibling("p").text.strip()
    category = soup.find("ul", "breadcrumb").find_all("a")[2].text.strip()
    
    relative_url_image = soup.find("img")["src"]
    url_image = urljoin(BASE_URL, relative_url_image)

    tds_informations_book = soup.find_all("td")
    
    text_informations_book = []
    regex_pattern = r'In stock \((\d+) available\)'
    
    for info in tds_informations_book:
        clean_info = re.sub(regex_pattern, r"\1", info.text.replace("£", ""))
        text_informations_book.append(clean_info)
        
    
    th_informations_list = [
        "upc", 
        "product_type", 
        "price_exclude_tax", 
        "price_include_tax", 
        "tax", 
        "availability", 
        "number_of_reviews"
    ]
    product_infos = {}
    
    for key, text in zip(th_informations_list, text_informations_book):
        product_infos[key] = text
        

    data = [
        url_business_book,
        title,
        description,
        category,
        product_infos.get("upc", ""),
        product_infos.get("price_exclude_tax", ""),
        product_infos.get("price_include_tax", ""),
        product_infos.get("availability", ""),
        product_infos.get("number_of_reviews", ""),
        url_image
    ]
    
    headers = [
        "product_page_url",
        "title",
        "product_description",
        "category",
        "universal_product_code",
        "price_excluding_tax",
        "price_include_tax",
        "number_available",
        "review_rating",
        "image_url"
    ]
    
    
    with open("book.csv", "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerow(data)
        
    
    
    