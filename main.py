import re
import csv
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com"
HEADERS_CSV = [
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


def get_all_books_data_in_categorie(book_links_categorie):
    books_data = []
    for book_link in book_links_categorie:
        books_data.append(extract_book_infos(book_link))
    return books_data


def extract_book_infos(url_book):
    try:
        response = requests.get(url_book)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, features="html.parser")
        
        title = soup.find("h1").text.strip()
        description = soup.find("div", id="product_description").find_next_sibling("p").text.strip()
        category = soup.find("ul", "breadcrumb").find_all("a")[2].text.strip()
        stars = get_stars(soup)
        
        relative_image_url = soup.find("img")["src"]
        url_image = urljoin(BASE_URL, relative_image_url)
        
        product_infos = extract_product_infos(soup)
            
        data = [
                url_book,
                title,
                description,
                category,
                product_infos.get("upc", ""),
                product_infos.get("price_exclude_tax", ""),
                product_infos.get("price_include_tax", ""),
                product_infos.get("availability", ""),
                stars,
                url_image
            ]
        
        return data
    
    except Exception as e:
        print("Error has occured : ", e)
        
       
def extract_product_infos(soup):
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
        
    return product_infos


def get_all_books_urls_categorie(url_categorie):
    books_urls = []
    
    while True:
        try:
            response = requests.get(url_categorie)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, features="html.parser")
            
            book_links = extract_book_urls(soup)
            books_urls.extend(book_links)
            
            next_url = get_next_url(soup)
            if next_url:
                url_categorie = urljoin(url_categorie, next_url)
            else:
                break

        except Exception as e:
            print("Error has occured : ", e)
        
    return books_urls
        

def extract_book_urls(soup):
    book_links = soup.select("h3 a")
    links_book = []
    for link in book_links:
        relative_url = link["href"]
        cleaned_url = "/catalogue/" + re.sub(r'\.\./', '', relative_url)
        complete_url = urljoin(BASE_URL, cleaned_url)
        links_book.append(complete_url)
        
    return links_book


def get_next_url(soup):
    btn_next = soup.find("li", class_="next")
    if btn_next:
        relative_next_link = btn_next.find("a")["href"]
        return relative_next_link
    return None


def get_stars(soup):
        bloc_stars = soup.find(class_="col-sm-6 product_main")
        stars = bloc_stars.find_next("p").find_next("p").find_next("p")["class"][1]
        
        match stars:
            case "Five": 
                stars = 5
            case "Four": 
                stars = 4
            case "Three": 
                stars = 3
            case "Two": 
                stars = 2
            case "One": 
                stars = 1
            case "Zero":
                stars = 0
            case _:
                pass
        
        return stars


def get_urls_categorie(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, features="html.parser")
    
    side_nav_categorie = soup.find(class_="side_categories").find("ul").find("ul")
    list_categorie = side_nav_categorie.find_all("li")
    urls_categorie = []
    for link in list_categorie:
        relative_link = link.find("a")["href"]
        complete_link = urljoin(BASE_URL, relative_link)
        urls_categorie.append(complete_link)
    
    return urls_categorie


def main():
    url_category = "http://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
    
    book_links_categorie = get_all_books_urls_categorie(url_category)
    books_data = get_all_books_data_in_categorie(book_links_categorie)
    
    with open("book.csv", "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(HEADERS_CSV)
        for data in books_data:
            writer.writerow(data)
            

if __name__ == "__main__":
    main()