import re
import requests
from bs4 import BeautifulSoup

url = "http://books.toscrape.com/"
url_business_book = url + "catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html"

response = requests.get(url_business_book)

if response.ok:
    soup = BeautifulSoup(response.content, features="html.parser")

    title = soup.find("h1").text.strip()
    
    description = soup.find("div", id="product_description").find_next_sibling("p").text.strip()
    
    category = soup.find("ul", "breadcrumb").find_all("a")[2].text.strip()



    tds_informations_book = soup.find_all("td")
    
    text_informations_book = []
    regex_pattern = r'In stock \((\d+) available\)'
    
    for info in tds_informations_book:
        clean_info = re.sub(regex_pattern, r"\1", info.text.replace("£", ""))
        text_informations_book.append(clean_info)
    
    