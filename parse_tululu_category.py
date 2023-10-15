import json
import re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

from main import check_for_redirect, parse_book_page, download_txt, download_image

requests.packages.urllib3.disable_warnings()


def parse_category(start_page, end_page):
    info_books = []
    category_url = 'https://tululu.org/l55/'
    for page in range(start_page, end_page+1):
        page_url = urljoin(category_url, f'{page}')
        response = requests.get(page_url, verify=False)
        response.raise_for_status()
        check_for_redirect(response)

        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.find_all('table', class_='d_book')
        book_urls = [urljoin(response.url, book.a['href']) for book in books]

        for book_url in book_urls:
            try:
                download_book(book_url, info_books)
            except requests.HTTPError:
                continue


def download_book(url, info_books):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    txt_url = f'https://tululu.org/txt.php'
    book_page = parse_book_page(response.text, response.url)

    parse_book_id = urlparse(response.url).path
    book_id = re.search(r'\d+', parse_book_id).group()
    params = {'id': book_id}

    book_path = download_txt(txt_url, f'{book_page["title"]}.txt', params)
    image_path = download_image(book_page['full_img_url'])

    info_books.append({
        'title': book_page['title'],
        'author': book_page['author'],
        'img_src': image_path,
        'book_path': book_path,
        'comments': book_page['comments'],
        'genres': book_page['genres']
    })

    info_books_json = json.dumps(info_books, ensure_ascii=False)

    with open('books.json', "w") as file:
        file.write(info_books_json)


if __name__ == "__main__":
    parse_category(1, 4)
