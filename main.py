import os
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
    # Create a session to speed up request times
    session = requests.Session()
    
    books_data = []
    for book_link in book_links_categorie:
        response = session.get(book_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, features="html.parser")
        books_data.append(extract_book_infos(soup, book_link))
    return books_data


def get_all_books_urls_categorie(url_categorie):
    books_urls = []
    # Create a session to speed up request times
    session = requests.Session()
    
    while True:
        try:
            response = session.get(url_categorie)
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


def get_urls_categorie(base_url):
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, features="html.parser")
    
    side_nav_categorie = soup.find(class_="side_categories").find("ul").find("ul")
    list_categorie = side_nav_categorie.find_all("li")
    urls_categorie = []
    for link in list_categorie:
        relative_link = link.find("a")["href"]
        complete_link = urljoin(base_url, relative_link)
        urls_categorie.append(complete_link)
    
    return urls_categorie


def extract_book_infos(soup, url_book):
        title = extract_title(soup)
        description = extract_description(soup)
        category = extract_categorie(soup)
        stars = extract_stars_rating(soup)
        url_image = extract_image_url(soup)
        
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


def extract_title(soup):
    return soup.find("h1").text.strip()


def extract_description(soup):
    description = soup.find("div", id="product_description")
    return description.find_next_sibling("p").text.strip() if description else "Aucune description trouvée"


def extract_categorie(soup):
    category = soup.find("ul", "breadcrumb").find_all("a")[2].text.strip()
    return category


def extract_image_url(soup):
    relative_image_url = soup.find("img")["src"]
    url_image = urljoin(BASE_URL, relative_image_url)
    return url_image if relative_image_url else "Aucun lien d'image trouvé"


def extract_stars_rating(soup):
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


def download_image(url, file):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file, 'wb') as f:
            f.write(response.content)
        print(f"Image download in folder : '{file}'")
    else:
        print(f"Image download fails URL : {url}")


def clean_special_characters(title):
    if ":" in title:
        splited_title = title.split(":")
        title_cleaned = splited_title[0]
    else:
        title_cleaned = title

    title_cleaned = re.sub(r'[^\w\s]', '', title_cleaned)
    title_cleaned = title_cleaned.strip().replace(" ", "-").lower()
    return title_cleaned


def main():
    folder = "bookscrap_files"
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    urls_category = get_urls_categorie(BASE_URL)
    
    for url_category in urls_category:
        book_links_category = get_all_books_urls_categorie(url_category)
        books_data = get_all_books_data_in_categorie(book_links_category)
        category = books_data[0][3]
        
        # Create a folder for the category if it doesn't already exist
        category_folder = os.path.join(folder, category)
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)
        
        filename = os.path.join(category_folder, f"{category}.csv")

        with open(filename, "w", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(HEADERS_CSV)
            for data in books_data:
                writer.writerow(data)
                
                # Download image
                url_image = data[-1]  # Last col CSV (URL image)
                book_title = clean_special_characters(data[1])
                name_image = os.path.join(category_folder, f"{book_title}.jpg") 
                download_image(url_image, name_image)
                            

if __name__ == "__main__":
    main()