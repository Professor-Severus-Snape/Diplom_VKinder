import psycopg2
from config import host, port, database, user, password


def create_tables() -> None:
    """ Функция, которая создает 2 таблицы: 'Users' и 'Users_seen_candidates', если их ещё нет.
    Таблица 'Users' хранит id воспользовавшихся услугами бота юзеров.
    Таблица 'Users_seen_candidates' хранит связь: id юзера - id кандидата.
    Т.е. организована связь 'один ко многим'.
    """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY);
                """)
                conn.commit()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Users_seen_candidates (
                        id INTEGER NOT NULL REFERENCES Users(id),
                        vk_id INTEGER
                        );
                """)
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def select_users_seen_candidates(user_id, candidate_id) -> bool:
    """ Функция, проверяющая, выдавался ли по запросу уже данный кандидат для данного конкретного юзера. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, vk_id FROM Users_seen_candidates
                    WHERE (id, vk_id) = (%s, %s);                  
                """, (user_id, candidate_id))
                if cursor.fetchone():
                    return True
                else:
                    return False

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()


def select_users(user_id) -> bool:
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


def insert_users_seen_candidates(user_id, candidate_id) -> None:
    """ Функция, добавляющая в таблицу 'Users_seen_candidates' данные айдишников. """

    try:
        with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    INSERT INTO Users_seen_candidates(id, vk_id)
                    VALUES(%s, %s);
                """, (user_id, candidate_id))
                conn.commit()

    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if conn:
            conn.close()
