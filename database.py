import psycopg2
from config import host, port, database, user, password


def create_table() -> None:
    """ Функция, которая сначала удаляет таблицу 'Seen_candidates', если она уже есть, а затем создает новую. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:

                # 1-ый этап: удаление таблицы, если она есть (чтобы для разных юзеров данные не перемешивались)
                cursor.execute("""DROP TABLE IF EXISTS Seen_candidates;""")
                conn.commit()

                # 2-ой этап: создание таблицы
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Seen_candidates (vk_id INTEGER PRIMARY KEY);
                """)
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def insert_candidate_id(candidate_id) -> None:
    """ Функция, добавляющая в таблицу 'Seen_candidates' id уже просмотренных кандидатов. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Seen_candidates(vk_id)
                    VALUES(%s);
                """, (candidate_id, ))
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def get_seen_users(candidate_id) -> bool:
    """ Функция, проверяющая, выдавался ли по запросу уже данный кандидат. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT vk_id FROM Seen_candidates
                    WHERE vk_id = %s;                
                """, (candidate_id, ))
                if cursor.fetchone():
                    return True
                else:
                    return False

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def create_table_user() -> None:
    """
    Функция, которая создает таблицу 'Users', если её нет.
    Таблица одна для всех пользователей. Будет хранить id всех юзеров, которые воспользовались услугами бота. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY);
                """)
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def insert_users(user_id) -> None:
    """ Функция, добавляющая в таблицу 'Users' id воспользовавшихся ботом юзеров. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Users(id)
                    VALUES(%s);
                """, (user_id, ))
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def get_select_users(user_id) -> bool:
    """
    Функция, проверяющая, пользовался ли данный юзер услугами бота прежде.
    Если да, то ему больше не будет отправляться подсказка 'начать'.
    """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM Users
                    WHERE id = %s;                
                """, (user_id, ))
                if cursor.fetchone():
                    return True
                else:
                    return False

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()
