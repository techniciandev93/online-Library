import argparse
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse

requests.packages.urllib3.disable_warnings()


def check_for_redirect(response):
    status_codes = [response.status_code for response in response.history]
    if 302 in status_codes or 301 in status_codes:
        raise requests.HTTPError()


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
        Args:
            url (str): Cсылка на текст, который хочется скачать.
            filename (str): Имя файла, с которым сохранять.
            folder (str): Папка, куда сохранять.
        Returns:
            str: Путь до файла, куда сохранён текст.
    """
    file_name = sanitize_filename(filename)
    full_path = download_file(url, folder, file_name)
    return full_path


def download_image(url, folder='images/'):
    file_name = os.path.basename(urlparse(url).path)
    full_path = download_file(url, folder, file_name)
    return full_path


def download_file(url, folder, file_name):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    Path(folder).mkdir(parents=True, exist_ok=True)
    full_path = os.path.join(folder, file_name)
    with open(full_path, 'wb') as file:
        file.write(response.content)
    return full_path


def parse_book_page(html):
    soup = BeautifulSoup(html, 'lxml')
    img_url = soup.find('div', class_='bookimage').a.img['src']
    full_img_url = urljoin('https://tululu.org', img_url)

    h1 = soup.find('div', id='content').find('h1')
    title = h1.text.split('::')[0].strip()
    author = h1.a.text
    find_comments = soup.find_all('div', class_='texts')
    comments = '\n'.join([comment.span.text for comment in find_comments])
    genres = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]
    content = soup.find_all('table', class_='d_book')[-1].text

    book_page = {'content': content,
                 'full_img_url': full_img_url,
                 'genres': genres,
                 'comments': comments,
                 'author': author,
                 'title': title}
    return book_page


def download_book(start_id, end_id):
    tululu_url = 'https://tululu.org/b{}/'
    for book_id in range(start_id, end_id+1):
        try:
            response = requests.get(tululu_url.format(book_id), verify=False)
            response.raise_for_status()
            check_for_redirect(response)
            txt_url = f'https://tululu.org/txt.php?id={book_id}'
            book_page = parse_book_page(response.text)

            download_txt(txt_url, f"{book_id}. {book_page['title']}")
            download_image(book_page['full_img_url'])
        except requests.HTTPError:
            continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Этот скрипт предназначен для скачивания книг и обложек "
                                                 "в заданном диапазоне с сайта tululu.org. Книги будут скачиваться в "
                                                 "каталог books/, обложки в images/. Запустите скрипт, "
                                                 "указав диапазон ID. python main.py -s 1 -e 10."
                                                 "По умолчанию без аргументов будет поиск в диапазоне от 1 до 10 "
                                                 "python main.py")
    parser.add_argument('-s', '--start_id', type=str, help="Введите ID книги для начала диапазона",
                        nargs='*', default=1)
    parser.add_argument('-e', '--end_id', type=str, help="Введите ID книги для конца диапазона",
                        nargs='*', default=10)
    args = parser.parse_args()
    download_book(args.start_id, args.end_id)
