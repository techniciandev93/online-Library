import cgi
from pathlib import Path
import requests

requests.packages.urllib3.disable_warnings()


def download_book(path):
    tululu_url = 'https://tululu.org/txt.php?id={}'
    for book_id in range(1, 10):
        response = requests.get(tululu_url.format(book_id), verify=False)
        response.raise_for_status()
        Path(path).mkdir(parents=True, exist_ok=True)
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            _, params = cgi.parse_header(content_disposition)
            file_name = params['filename']
            with open(f'{path}{file_name}', 'wb') as file:
                file.write(response.content)


if __name__ == '__main__':
    folder_path = 'book/'
    download_book(folder_path)


