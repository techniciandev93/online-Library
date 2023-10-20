# Парсинг книг с сайта [tululu.org](https://tululu.org/)

## Как установить

Python 3.8 должен быть уже установлен.
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

## download_tululu_books.py
Этот скрипт предназначен для скачивания книг и обложек
в заданном диапазоне с сайта [tululu.org](https://tululu.org/). Книги будут скачиваться в
каталог books/, обложки в images/.

### Как запустить
Запустите скрипт, указав диапазон ID
```
python download_tululu_books.py -s 5 -e 10
```
По умолчанию без аргументов будет поиск в диапазоне от 1 до 10
```
python download_tululu_books.py
```
## parse_tululu_category.py
Этот скрипт предназначен для скачивания книг и обложек в жанре фантастика
с tululu.org, указывая начальную и конечную страницы. 

### Как запустить
Запустите скрипт, указав начальную и конечную страницы.
```
python parse_tululu_category.py --start_page 1 --end_page 4
```
По умолчанию без аргументов будет поиск от 1 до последней страницы
```
python parse_tululu_category.py
```
Для просмотра дополнительных параметров используйте 
```
python parse_tululu_category.py --help
```

## render_website.py
Этот скрипт запускает веб приложение онлайн библиотеки. 
### Как запустить
Чтобы сформировать json  с книгами запустите скрипт
```
python parse_tululu_category.py --start_page 1 --end_page 4 
```
Запустите
```
python render_website.py
```
и перейдите по ссылке http://127.0.0.1:5500.\
Для просмотра параметров используйте
```
python render_website.py --help
```
Пример библиотеки можно посмотреть по ссылке https://techniciandev93.github.io/online-Library/pages/ 

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).