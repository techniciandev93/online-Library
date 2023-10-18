import json
from jinja2 import Environment, FileSystemLoader, select_autoescape


def read_books_file(path):
    with open(path, "r") as file:
        books_json = file.read()
    books = json.loads(books_json)
    return books


def render_html(template_path, json_path):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_path)
    books = read_books_file(json_path)
    rendered_page = template.render(
        books=books
    )
    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)


if __name__ == '__main__':
    json_path = 'books.json'
    template_path = 'template.html'
    render_html(template_path, json_path)
