import os
import re
import csv
import requests
from datetime import date
from urllib.parse import urljoin
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


def get_all_books_data_in_categorie(book_links_categorie, session_request):
    """Extracts data for all books in a category from their URLs.

    Args:
        book_links_categorie (list): A list containing the URLs of books in the category.
        session_request (requests.Session): A session object for making HTTP requests.

    Returns:
        list: A list containing data for all books found in the category.
    """
    
    books_data_categorie = []
    for book_link in book_links_categorie:
        response = session_request.get(book_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, features="html.parser")
        books_data_categorie.append(extract_book_infos(soup, book_link))
    return books_data_categorie


def get_all_books_urls_categorie(url_categorie, session_request):
    """Extracts the URLs of all books from a category.

    This function iterates through multiple pages of the category if Next button pagination is present.

    Args:
        url_categorie (str): The URL of the category page.
        session_request (requests.Session): A session object for making HTTP requests.

    Returns:
        list: A list containing the URLs of all books found in the category.
    """
    
    books_urls = []
    
    while True:
        try:
            response = session_request.get(url_categorie)
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
    """Extracts the complete URLs of books from a BeautifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the HTML of the page.

    Returns:
        list: A list containing the complete URLs of books found on the page.
    """
    
    book_links = soup.select("h3 a")
    links_book = []
    for link in book_links:
        relative_url = link["href"]
        cleaned_url = "/catalogue/" + re.sub(r'\.\./', '', relative_url)
        complete_url = urljoin(BASE_URL, cleaned_url)
        links_book.append(complete_url)
        
    return links_book


def get_next_url(soup):
    """Extracts the relative URL of the next page if the 'Next' button is present from a BeautifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the HTML of the current page.

    Returns:
        str or None: The relative URL of the next page if the 'Next' button is present, otherwise None.
    """
    
    btn_next = soup.find("li", class_="next")
    if btn_next:
        relative_next_link = btn_next.find("a")["href"]
        return relative_next_link
    return None


def get_urls_categories(base_url, session_request):
    """Extracts the URLs of all categories from a base URL.

    Args:
        base_url (str): The base URL of the website to extract category URLs from.
        session_request (requests.Session): A session object for making HTTP requests.

    Returns:
        list: A list containing the URLs of all categories found on the website.
    """
    
    response = session_request.get(base_url)
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
    """Extracts necessary information about a book from a BeautifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the book page HTML.
        url_book (str): The URL of the book's page.

    Returns:
        list: A list containing the extracted information about the book.
              The list has the following elements in order:
                1. URL of the book
                2. Title of the book
                3. Description of the book
                4. Category of the book
                5. UPC (Universal Product Code) of the book
                6. Price of the book excluding tax
                7. Price of the book including tax
                8. Availability status of the book
                9. Star rating of the book
                10. URL of the book image
    """
    
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
    """Extracts the title of a product from a BeautifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the HTML of the product page.

    Returns:
        str: The title of the product.
    """
    
    return soup.find("h1").text.strip()


def extract_description(soup):
    """Extracts the description of a product from a BeautifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the HTML of the product page.

    Returns:
        str: The description of the product, or 'Aucune description trouvée' if no description is found.
    """
    
    description = soup.find("div", id="product_description")
    return description.find_next_sibling("p").text.strip() if description else "Aucune description trouvée"


def extract_categorie(soup):
    """Extracts the category of a product from a BeautifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the HTML of the product page.

    Returns:
        str: The category of the product.
    """
    
    category = soup.find("ul", "breadcrumb").find_all("a")[2].text.strip()
    return category


def extract_image_url(soup):
    """Extracts the URL of an image from a <img> HTML tag within a BeatifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the product page HTML.

    Returns:
        str: The full image URL if found, otherwise returns "No image link found".
    """
    
    relative_image_url = soup.find("img")["src"]
    url_image = urljoin(BASE_URL, relative_image_url)
    return url_image if relative_image_url else "Aucun lien d'image trouvé"


def extract_stars_rating(soup):
    """Extracts the star rating of a product from a BeautifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the HTML of the product page.

    Returns:
        int: The star rating of the product (0-5).
    """
    
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
    """Extract product information from a <table> HTML tag within a BeautifulSoup object.

    Args:
        soup: A BeautifulSoup object representing the product page HTML.

    Returns:
        dict: A dictionary containing the extracted product information.
              Keys:
                - "upc": The UPC (Universal Product Code) of the product.
                - "product_type": The type or category of the product.
                - "price_exclude_tax": The price of the product excluding tax.
                - "price_include_tax": The price of the product including tax.
                - "tax": The tax applied to the product.
                - "availability": The availability status of the product.
                - "number_of_reviews": The number of reviews for the product.
    """
    
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


def download_image(url, file_path):
    """Download an image from a URL and save it to a file

    Args:
        url (str): The URL of the image to download
        file_path (str): The path where the image will be saved
    """
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Image download in folder : '{file_path}'")
    else:
        print(f"Image download fails URL : {url}")


def clean_special_characters(title):
    """Clean special characters from a title and format it for use as a file name

    Args:
        title (str): The original title string

    Returns:
        str: The cleaned and formatted title string suitable for use as a file name
    """
    
    if ":" in title:
        title_cleaned = title.split(":")[0]
    else:
        title_cleaned = title

    title_cleaned = re.sub(r'[^\w\s]', '', title_cleaned)
    title_cleaned = title_cleaned.strip().replace(" ", "-").lower()
    return title_cleaned


def main():
    folder = "bookscrap_files"
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    # Create a session to speed up request times
    session = requests.Session()
    
    # Get URLs of all categories    
    urls_category = get_urls_categories(BASE_URL, session)
    
    for url_category in urls_category:
        # Extract URLs of all books in the category
        book_links_category = get_all_books_urls_categorie(url_category, session)
        
        # Extract data for all books in the category
        books_data = get_all_books_data_in_categorie(book_links_category, session)
        
        # Retrieve and format category name, replacing spaces with underscores 
        category = books_data[0][3].replace(" ", "_")
        
        # Create a folder for the category if it doesn't already exist
        category_folder = os.path.join(folder, category)
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)
        
        # Get and format today date to include in the filename csv
        today = date.today().strftime("%d-%m-%Y")
        filename = os.path.join(category_folder, f"{category}_{today}.csv")

        with open(filename, "w", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(HEADERS_CSV)
            
            # Write book data to CSV file
            for data in books_data:
                writer.writerow(data)
                
                # Download image
                url_image = data[-1]  # Last column CSV (URL of the image)
                book_title_cleaned = clean_special_characters(data[1])
                file_path = os.path.join(category_folder, f"{book_title_cleaned}.jpg")
                download_image(url_image, file_path)
                            

if __name__ == "__main__":
    main()