import argparse
import json
import re
import time
import traceback
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from main import check_for_redirect, parse_book_page, download_txt, download_image

requests.packages.urllib3.disable_warnings()


def parse_category(start_page, end_page):
    info_books = []
    category_url = 'https://tululu.org/l55/'
    while start_page != end_page:
        try:
            page_url = urljoin(category_url, f'{start_page}')
            response = requests.get(page_url, verify=False)
            response.raise_for_status()
            check_for_redirect(response)

            soup = BeautifulSoup(response.text, 'lxml')
            books = soup.select('#content .d_book')
            book_urls = [urljoin(response.url, book.a['href']) for book in books]

            for book_url in book_urls:
                while True:
                    try:
                        download_book(book_url, info_books)
                        break
                    except requests.HTTPError:
                        traceback.print_exc()
                        break
                    except requests.ConnectionError:
                        traceback.print_exc()
                        time.sleep(10)
            start_page += 1

        except requests.ConnectionError:
            traceback.print_exc()
            time.sleep(10)
        except requests.HTTPError:
            break

    info_books_json = json.dumps(info_books, ensure_ascii=False)
    with open('books.json', "w") as file:
        file.write(info_books_json)


def download_book(url, info_books):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    print(response.url)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Этот скрипт предназначен для скачивания книг и обложек в жанре "
                                                 "фантастика "
                                                 "с tululu.org, указывая начальную и конечную страницы. Книги будут "
                                                 "скачиваться в "
                                                 "каталог books/, обложки в images/. Запустите скрипт, "
                                                 "указав начальную и конечную страницы. python "
                                                 "parse_tululu_category.py -s 1 -e 4 "
                                                 "По умолчанию без аргументов будет поиск от 1 до 4 страницы"
                                                 "python parse_tululu_category.py")
    parser.add_argument('-s', '--start_page', type=int, help="Введите номер страницы для начала диапазона", default=1)
    parser.add_argument('-e', '--end_page', type=int, help="Введите номер страницы для конца диапазона", default=0)
    args = parser.parse_args()
    if args.end_page == 0:
        args.end_page = 4
    parse_category(args.start_page, args.end_page)
