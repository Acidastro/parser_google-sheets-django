from config import host, user, password, db_name, NAME_TABLE
import psycopg2
from main import sheet, sheet_id


def create_table(name_table=NAME_TABLE):
    """
    Создает пустую таблицу, с первичным ключом.
    Добавляет заголовки колонок из гугл таблицы в БД.
    :param name_table: Имя создаваемой таблицы
    :return:
    """
    header_list = sheet.values().get(spreadsheetId=sheet_id, range="Лист1").execute()['values'][0]
    try:
        # Подключиться к базе
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        with connection:
            with connection.cursor() as cursor:
                # Создание таблицы
                sql = f"CREATE TABLE {name_table} (" \
                      f"id SERIAL PRIMARY KEY);"
                cursor.execute(sql)
                print(f'Создана таблица {name_table}')
                # Добавление заголовков
                header_list.append("стоимость в руб.")  # # Дополнительная колонка которой нет в таблице
                for name_column in header_list:  # добавляем каждую колонку
                    sql = f'ALTER TABLE IF EXISTS {name_table}' \
                          f' ADD COLUMN "{name_column}" character varying;'
                    cursor.execute(sql)
                print(f'Добавлены имена колонок {header_list}')
    except (Exception, psycopg2.Error) as _ex:
        print('[INFO] Ошибка при работе с PostgreSQL', _ex)


if __name__ == '__main__':
    create_table()
