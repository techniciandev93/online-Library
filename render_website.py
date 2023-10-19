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


def on_reload(json_path, template_path, pages_path):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_path)
    books = list(chunked(read_json_books(json_path), 10))
    Path(pages_path).mkdir(parents=True, exist_ok=True)

    for page, book in enumerate(books, 1):
        rendered_page = template.render(
            books=book
        )
        file_path = os.path.join(pages_path, f'index{page}.html')
        with open(file_path, 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':
    json_path = 'books.json'
    template_path = 'template.html'
    pages_path = 'pages'
    default_html = os.path.join(pages_path, 'index1.html')

    on_reload_with_args = partial(on_reload, json_path, template_path, pages_path)

    on_reload_with_args()
    server = Server()
    server.watch(template_path, on_reload_with_args)
    server.serve(root='.', default_filename=default_html)
