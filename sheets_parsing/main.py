import os
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import psycopg2
from config import user, host, password, db_name, NAME_TABLE
from read_xml import currency_parsing
from psycopg2.extensions import AsIs
import time
from datetime import datetime, date
import requests
from telegram_config import token, chat_id


# Идея скрипта:
# 1. Создать пустую таблицу
# 2. Добавить пустые колонки
# 3. Добавить содержимое в эти колонки
# 4. Поддерживать изменения

# Чтение из таблицы
def get_service_sacc():
    """
    Могу читать таблицу которой выдан доступ
    для сервисного аккаунта приложения

    kanal-service-test@kanalservistest-357710.iam.gserviceaccount.com
    """
    creds_json = os.path.dirname(__file__) + "/creds/sacc1.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


service = get_service_sacc()
sheet = service.spreadsheets()
sheet_id = "1IP2qVacjpvBrV80RA9nbiU41ylg3KfYLoS4jR5Y9mKw"  # https://docs.google.com/spreadsheets/d/xxx/edit#gid=0


# Добавление новых строк в БД
def adding_new_lines(resp):
    """
    Вычисляю разницу в количестве строк между sheets и SQL.
    Добавляются пустые строки.
    :type resp: Данные из sheets
    :return:
    """
    # Подключиться к базе
    connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {NAME_TABLE} ORDER BY id ASC")  # Парсим SQL
                column_names = resp[0]  # Имена колонок
                len_data_sheets = len(resp[1:])  # Количество строк в Sheets
                len_data_sql = len(cursor.fetchall())  # Количество строк в БД
                row_count_difference = len_data_sheets - len_data_sql  # Разница в количестве строк
                if row_count_difference > 0:  # Если в sheets строк больше чем в БД
                    for string in range(row_count_difference):  # Сколько строк добавить
                        cursor.execute(f'INSERT INTO {NAME_TABLE} ("{column_names[0]}") VALUES (NULL)')
                        print('Добавлена новая строка')
    except (Exception, psycopg2.Error) as _ex:
        print('[INFO] Ошибка при работе с PostgreSQL', _ex)


def change_line(data_sheets, sql_id, column_name_list):
    """
    Меняет старые значения базы данных на новые
    :param sql_id: Старые значения по которым будет найдена изменяемая строка
    :param data_sheets: Значения которые нужно внести
    :param column_name_list: Названия колонок
    :return:
    """
    connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
    try:
        with connection:
            with connection.cursor() as cursor:
                for num, column_name in enumerate(column_name_list):
                    # Случай для доп строки
                    if num == 4:
                        if data_sheets[2]:  # Если есть информация о цене в долларах
                            price_rubles = str(
                                round(int(data_sheets[2]) * currency_parsing()))  # Вычислить стоимость в рублях
                            data_sheets += (price_rubles,)
                        else:  # Иначе добавить пустую строку
                            data_sheets += ('',)
                    cursor.execute(f'UPDATE %s SET "{column_name}" = %s WHERE id = %s;',
                                   (AsIs(NAME_TABLE), data_sheets[num], AsIs(sql_id)))
                    print(f'{data_sheets[num]} добавлено в колонку "{column_name}"')
    except (Exception, psycopg2.Error) as _ex:
        print('[INFO] Ошибка при работе с PostgreSQL', _ex)
    else:
        print(f'Строка id={sql_id} изменена')


def past_date(the_date: str):
    """
    :param the_date: Дата из таблицы (пример: 24.05.2023)
    :return: True если дата в прошлом
    """
    date_list = [int(x) for x in the_date.split('.')]
    day, month, year = date_list[0], date_list[1], date_list[2]
    d = datetime(year=year, month=month, day=day)
    return d < datetime.today()


def use_send_notification(the_date: str, order_n: str):
    """
    Отправляет сообщение в ТГ, если срок прошел
    :param the_date: дата поставки
    :param order_n: номер заказа
    :return:
    """
    if past_date(the_date):
        message = f'Срок поставки {order_n} прошел'
        print(message)
        requests.get(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}')


# Проверяю на внесенные изменения
def check_for_changes():
    """
    Проверяю, появились ли изменения в таблице
    """
    try:
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {NAME_TABLE} ORDER BY id ASC")
                resp = sheet.values().get(spreadsheetId=sheet_id, range="Лист1").execute()['values']
                name_columns = resp[0]  # Название колонок
                data_sheets = resp[1:]  # Содержимое колонок
                data_sql = cursor.fetchall()  # Содержимое БД
                if len(data_sheets) > len(data_sql):  # Если найдена новая строка, добавить ее в БД
                    adding_new_lines(resp)
                # Проверка на изменения в существующих строках
                for line_sheets, line_sql in zip(data_sheets, data_sql):
                    # Уровнять строки по длине
                    while len(line_sheets) < len(line_sql) - 2:
                        line_sheets.append('')  # Добавление пустых строк в конец, если такие должны быть
                    line_sheets = tuple(line_sheets)
                    sql_id = line_sql[0]  # id строки в БД
                    line_sql = line_sql[1:-1]  # Отрезаем колонку с id и прайс в рублях
                    # Строка из бд должна быть без id и без последней колонки
                    # Если они равны, значит изменений не было
                    # Если не равны, значит строку в БД нужно изменить
                    if line_sheets != line_sql:
                        print('Найдены изменения в строке', line_sheets, 'sheets', line_sql, 'sql')
                        # Вызов функции, которая изменит старую строку на новую.
                        # Передаём id строки, которую нужно поменять.
                        change_line(line_sheets, sql_id, tuple(name_columns) + ("стоимость в руб.",))
                        use_send_notification(line_sheets[3], line_sheets[1])
    except (Exception, psycopg2.Error) as _ex:
        print('[INFO] Ошибка при работе с PostgreSQL', _ex)


if __name__ == '__main__':
    while True:
        check_for_changes()
        time.sleep(10)
