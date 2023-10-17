import argparse
import json
import os
import re
import time
import traceback
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from main import check_for_redirect, parse_book_page, download_txt, download_image

requests.packages.urllib3.disable_warnings()


def parse_category(start_page, end_page, skip_imgs, skip_txt, dest_folder):
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
                        download_book(book_url, info_books, skip_imgs, skip_txt, dest_folder)
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

    file_path = os.path.join(dest_folder, 'books.json')
    Path(dest_folder).mkdir(parents=True, exist_ok=True)
    info_books_json = json.dumps(info_books, ensure_ascii=False)
    with open(file_path, 'w') as file:
        file.write(info_books_json)


def download_book(url, books, skip_imgs, skip_txt, dest_folder):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    print(response.url)

    txt_url = f'https://tululu.org/txt.php'
    book_page = parse_book_page(response.text, response.url)

    parse_book_id = urlparse(response.url).path
    book_id = re.search(r'\d+', parse_book_id).group()
    params = {'id': book_id}

    image_path = ''
    book_path = ''
    if skip_txt:
        book_path = download_txt(txt_url, f'{book_page["title"]}.txt', params, dest_folder=dest_folder)
    if skip_imgs:
        image_path = download_image(book_page['full_img_url'], dest_folder=dest_folder)

    books.append({
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
                                                 "parse_tululu_category.py --start_page 1 --end_page 4 "
                                                 "По умолчанию без аргументов будет поиск от 1 до последней страницы"
                                                 "python parse_tululu_category.py. Для просмотра дополнительных "
                                                 "параметров  используйте python parse_tululu_category.py --help")
    parser.add_argument('--start_page', type=int, help="Введите номер страницы для начала диапазона", default=1)
    parser.add_argument('--end_page', type=int, help="Введите номер страницы для конца диапазона", default=0)
    parser.add_argument('--dest_folder', type=str, help="Путь к каталогу с результатами парсинга: картинкам, книгам, "
                                                        "JSON.", default='')
    parser.add_argument('--skip_imgs', action='store_false', help="Не скачивать картинки")
    parser.add_argument('--skip_txt', action='store_false', help="Не скачивать книги")
    args = parser.parse_args()
    parse_category(args.start_page, args.end_page, args.skip_imgs, args.skip_txt, args.dest_folder)
