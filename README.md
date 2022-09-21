# DataOx Junior Python Developer Test | Web Scraping www.kijiji.ca site #
Web Scraping www.kijiji.ca site with Selenium and save scraped information into PostgreSQL DB
***
### The project is built on libraries: ###
Selenium

BeautifulSoup

psycopg2


Для запуска программы:
1. В файле database.py в строках 102-106 указать параметры подключения к БД PostgreSQL для создания БД проекта, пользователя и таблицы.
2. После этого запустить файл database.py. Будет создана БД, пользователь БД и таблица для записи данных.
3. В файле scraper.py в строке 42 указать путь к установленному Chromedriver
4. Запустить файл main.py

Парсинг проходит в 3 потока. На моем компьютере это занимает 21 минуту на 3300 записей. Парсинг в 2 потока - 26 минут. 6 потоков мой компьютер не потянул.

В файле requirements.txt - список установленных в venv библиотек.
***
