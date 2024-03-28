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


