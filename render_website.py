import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def read_json_books(path):
    with open(path, "r") as file:
        books_json = file.read()
    books = json.loads(books_json)
    return books


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_path)
    books = read_json_books(json_path)
    rendered_page = template.render(
        books=books
    )
    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)


if __name__ == '__main__':
    json_path = 'books.json'
    template_path = 'template.html'

    on_reload()
    server = Server()
    server.watch(template_path, on_reload)
    server.serve(root='.')
