import psycopg2
from config import host, port, database, user, password


def create_table() -> None:
    """ Функция, которая сначала удаляет таблицу 'Candidates', если она уже есть, а затем создает новую. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:

                # 1-ый этап: удаление таблицы, если она есть (чтобы для разных юзеров данные не перемешивались)
                cursor.execute("""DROP TABLE IF EXISTS Candidates;""")
                conn.commit()

                # 2-ой этап: создание таблицы
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Candidates (
                        vk_id INTEGER PRIMARY KEY,
                        first_name VARCHAR(40) NOT NULL,
                        last_name VARCHAR(40) NOT NULL,
                        vk_link VARCHAR(60) NOT NULL UNIQUE
                    );
                """)
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def insert_candidates_info(info) -> None:
    """ Функция, добавляющая в таблицу 'Candidates' всех(!!!) подошедших по заданным критериям кандидатов. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Candidates(vk_id, first_name, last_name, vk_link)
                    VALUES(%s, %s, %s, %s);
                """, (info[0], info[1], info[2], info[3]))
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def get_user_from_db() -> tuple:
    """ Функция, выдающая по запросу пользователя данные об одном случайном кандидате из таблицы 'Candidates'. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT * FROM Candidates""")
                return cursor.fetchone()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def delete_candidate(vk_id) -> None:
    """ Функция, которая удаляет просмотренных кандидатов из таблицы, чтобы они больше не выпадали при запросе. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Candidates
                    WHERE vk_id = %s;
                """, (vk_id, ))
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def create_table_user() -> None:
    """ Функция, которая создает таблицу 'Users', если её нет. """

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
