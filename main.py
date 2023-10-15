import argparse
import os
import time
import traceback
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse

requests.packages.urllib3.disable_warnings()


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def download_txt(url, filename, params, folder='books/'):
    """Функция для скачивания текстовых файлов.
        Args:
            url (str): Cсылка на текст, который хочется скачать.
            filename (str): Имя файла, с которым сохранять.
            params (dict): параметры для запроса.
            folder (str): Папка, куда сохранять.
        Returns:
            str: Путь до файла, куда сохранён текст.
    """
    file_name = sanitize_filename(filename)
    full_path = download_file(url, folder, file_name, params)
    return full_path


def download_image(url, folder='images/'):
    file_name = os.path.basename(urlparse(url).path)
    full_path = download_file(url, folder, file_name)
    return full_path


def download_file(url, folder, file_name, params=None):
    response = requests.get(url, verify=False, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    Path(folder).mkdir(parents=True, exist_ok=True)
    full_path = os.path.join(folder, file_name)
    with open(full_path, 'wb') as file:
        file.write(response.content)
    return full_path


def parse_book_page(html, url):
    soup = BeautifulSoup(html, 'lxml')
    img_url = soup.find('div', class_='bookimage').a.img['src']
    full_img_url = urljoin(url, img_url)

    h1 = soup.find('div', id='content').find('h1')
    title = h1.text.split('::')[0].strip()
    author = h1.a.text
    soup_comments = soup.find_all('div', class_='texts')
    comments = [comment.span.text for comment in soup_comments]
    genres = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]
    book_description = soup.find_all('table', class_='d_book')[-1].text

    book_page = {'book_description': book_description,
                 'full_img_url': full_img_url,
                 'genres': genres,
                 'comments': comments,
                 'author': author,
                 'title': title}
    return book_page


def download_books(start_id, end_id):
    tululu_url = 'https://tululu.org/b{}/'
    for book_id in range(start_id, end_id+1):
        while True:
            try:
                response = requests.get(tululu_url.format(book_id), verify=False)
                response.raise_for_status()
                check_for_redirect(response)
                params = {'id': book_id}
                txt_url = f'https://tululu.org/txt.php'
                book_page = parse_book_page(response.text, response.url)

                download_txt(txt_url, f"{book_id}. {book_page['title']}", params)
                download_image(book_page['full_img_url'])
                break
            except requests.HTTPError:
                traceback.print_exc()
                break
            except requests.ConnectionError:
                traceback.print_exc()
                time.sleep(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Этот скрипт предназначен для скачивания книг и обложек "
                                                 "в заданном диапазоне с сайта tululu.org. Книги будут скачиваться в "
                                                 "каталог books/, обложки в images/. Запустите скрипт, "
                                                 "указав диапазон ID. python main.py -s 1 -e 10."
                                                 "По умолчанию без аргументов будет поиск в диапазоне от 1 до 10 "
                                                 "python main.py")
    parser.add_argument('-s', '--start_id', type=int, help="Введите ID книги для начала диапазона", default=1)
    parser.add_argument('-e', '--end_id', type=int, help="Введите ID книги для конца диапазона", default=10)
    args = parser.parse_args()
    download_books(args.start_id, args.end_id)
