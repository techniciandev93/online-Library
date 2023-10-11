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


def download_book(path):
    tululu_url = 'https://tululu.org/b{}/'
    for book_id in range(1, 11):
        try:
            response = requests.get(tululu_url.format(book_id), verify=False)
            response.raise_for_status()
            check_for_redirect(response)
            txt_url = f'https://tululu.org/txt.php?id={book_id}'

            soup = BeautifulSoup(response.text, 'lxml')
            img_url = soup.find('div', class_='bookimage').a.img['src']
            full_img_url = urljoin('https://tululu.org', img_url)

            h1 = soup.find('div', id='content').find('h1')
            title = h1.text.split('::')[0].strip()
            author = h1.a.text
            find_comments = soup.find_all('div', class_='texts')
            comments = '\n'.join([comment.span.text for comment in find_comments])

            download_txt(txt_url, f'{book_id}. {title}', path)
            download_image(full_img_url, folder='images/')
        except requests.HTTPError:
            continue


if __name__ == '__main__':
    download_book('books/')
