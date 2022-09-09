
Скрипт выполняет следующие функции:

1. Получение данных из документа при помощи Google API, сделанного в [Google Sheets](https://docs.google.com/spreadsheets/d/1IP2qVacjpvBrV80RA9nbiU41ylg3KfYLoS4jR5Y9mKw/edit#gid=0) (Необходимо иметь права просмотра и редактирования).
2. Данные добавляются в БД, в том же виде, что и в файле –источнике, с добавлением колонки «стоимость в руб.»
    
    a. Самостоятельно создает таблицу, СУБД на основе PostgreSQL.
    
    b. Данные для перевода $ в рубли получает по курсу [ЦБ РФ](https://www.cbr.ru/development/SXML/).
    
3. Скрипт работает постоянно для обеспечения обновления данных в онлайн режиме (учтено, что строки в Google Sheets таблицу могут удаляться, добавляться и изменяться).

Запуск программы:
1. Создать БД 'channel_service' на основе PostgreSQL, данные конфигурации хранятся в файле config.py
2. Выполнить установки зависимостей:

pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client creds psycopg2 bs4 lxml notifiers

3. Выполнить команду, которая создаст нужную таблицу

python create.py

4. Создать файл 'telegram_config.py', 
он содержит token бота и chat_id
в который бот отправляет уведомления,
в него заранее добавляем нашего бота как администратора.
Узнать id поможет бот @getmyid_bot

6. Выполнение основного скрипта:

python main.py

Ссылка на таблицу:
[Google Sheets](https://docs.google.com/spreadsheets/d/1IP2qVacjpvBrV80RA9nbiU41ylg3KfYLoS4jR5Y9mKw/edit#gid=0)
