import argparse
import json
import os.path
from functools import partial
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def read_json_books(path):
    with open(path, "r") as file:
        books_json = file.read()
    books = json.loads(books_json)
    return books


def on_reload(json_path, template_path, pages_path, default_html, books_per_page):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_path)
    books = list(chunked(read_json_books(json_path), books_per_page))
    count_pages = len(books)
    Path(pages_path).mkdir(parents=True, exist_ok=True)
    paginator = {page: os.path.join(pages_path, f'index{page}.html') for page in range(1, count_pages+1)}

    for page, book in enumerate(books, 1):
        previous_url = ''
        next_url = ''
        if page <= 1:
            previous = False
            next_page = True
            next_url = os.path.join(pages_path, f'index{page+1}.html')
        elif page >= count_pages:
            previous = True
            previous_url = os.path.join(pages_path, f'index{page-1}.html')
            next_page = False
        else:
            previous = True
            previous_url = os.path.join(pages_path, f'index{page - 1}.html')
            next_page = True
            next_url = os.path.join(pages_path, f'index{page + 1}.html')

        file_path = os.path.join(pages_path, f'index{page}.html')
        rendered_page = template.render(
            books=book,
            count_pages=count_pages,
            current_page=page,
            paginator=paginator,
            previous=previous,
            previous_url=previous_url,
            next_page=next_page,
            next_url=next_url
        )
        with open(file_path, 'w', encoding='utf8') as file:
            file.write(rendered_page)
        if page == 1:
            with open(default_html, 'w', encoding='utf8') as file:
                file.write(rendered_page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Этот скрипт запускает веб приложение онлайн библиотеки. Запустите "
                                                 "python render_website.py и перейдите по ссылке "
                                                 "http://127.0.0.1:5500. Чтобы сформировать json  с книгами запустите "
                                                 "скрипт python parse_tululu_category.py --start_page 1 --end_page 4 "
                                                 "Для просмотра параметров используйте python render_website.py --help")

    parser.add_argument('--json_path', type=str, help="Укажите путь к json файлу с книгами", default='books.json')
    parser.add_argument('--pages_path', type=str, help="Укажите путь к папке где будут лежать html страницы",
                        default='pages')
    parser.add_argument('--template_path', type=str, help="Укажите путь к html шаблону",
                        default='template.html')
    parser.add_argument('--books_per_page', type=int, help="Укажи какое количество книг выводить на страницу",
                        default=4)
    args = parser.parse_args()
    default_html = os.path.join(args.pages_path, 'index.html')
    on_reload_with_args = partial(on_reload,
                                  args.json_path,
                                  args.template_path,
                                  args.pages_path,
                                  default_html,
                                  args.books_per_page)
    on_reload_with_args()
    server = Server()
    server.watch(args.template_path, on_reload_with_args)
    server.serve(root='.', default_filename=default_html)
