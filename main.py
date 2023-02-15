import requests
import datetime
from random import randrange, choice
from config import vk_group_token, access_token, api_version
from database import *


def call_server(token: str = vk_group_token, version: str = api_version) -> tuple:
    """ Функция, получающая данные для подключения к серверу LongPoll. """

    url: str = 'https://api.vk.com/method/messages.getLongPollServer'
    params: dict = {'access_token': token, 'v': version}

    response: dict = requests.get(url, params=params).json()

    server: str = response['response']['server']  # 'im.vk.com/nim218675354'
    key: str = response['response']['key']  # 'e3204e3b853fcd801b167136feb1e7b846887b07',
    ts: int = response['response']['ts']  # 1724780811

    return server, key, ts


def send_message(user_id: int, message: str, token: str = vk_group_token, version: str = api_version) -> None:
    """ Функция, отправляющая написавшему юзеру ответные сообщения. """

    url: str = 'https://api.vk.com/method/messages.send'
    params: dict = {'access_token': token,
                    'v': version,
                    'random_id': randrange(10 ** 7),
                    'user_id': user_id,
                    'message': message}

    requests.post(url, params=params).json()


def send_photo(user_id: int, candidate_id: int, photo_id: int,
               token: str = vk_group_token, version: str = api_version) -> None:
    """ Функция, отправляющая написавшему юзеру фотки потенциальных кандидатов. """

    url: str = 'https://api.vk.com/method/messages.send'
    params: dict = {'access_token': token,
                    'v': version,
                    'random_id': randrange(10 ** 7),
                    'user_id': user_id,
                    'attachment': f'photo{candidate_id}_{photo_id}'}

    requests.post(url, params=params).json()


def get_person_info(person_id: int, token: str = vk_group_token, version: str = api_version) -> tuple:
    """
    Функция, которая по id пользователя получает его имя и фамилию.
    Возвращает кортеж из id, имени, фамилии и ссылки на данного пользователя.
    """

    url: str = 'https://api.vk.com/method/users.get'
    params: dict = {'access_token': token,
                    'v': version,
                    'user_ids': person_id}

    response: dict = requests.get(url, params=params).json()

    vk_id: int = response['response'][0]['id']
    first_name: str = response['response'][0]['first_name']
    last_name: str = response['response'][0]['last_name']
    vk_link: str = 'vk.com/id' + str(vk_id)
    return vk_id, first_name, last_name, vk_link


def ask_sex(user_id: int) -> int:
    """ Функция, которая спрашивает пол юзера и меняет его на противоположный. """

    server, key, ts = call_server()

    send_message(user_id=user_id, message=f"Укажите, пожалуйста, Ваш пол ('м' или 'ж') без кавычек.")

    while True:
        resp: dict = requests.get(f'https://{server}?act=a_check&key={key}&ts={ts}&wait=90&mode=2&version=2').json()

        try:
            updates: list = resp['updates']

        except KeyError:
            server, key, ts = call_server()
            continue

        if updates:

            for element in updates:
                action_code: int = element[0]

                if action_code == 4:
                    flags = []
                    flag: int = element[2]

                    for number in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 65536]:
                        if flag & number:
                            flags.append(number)

                    if 2 not in flags:
                        text: str = element[5]

                        if text.lower() == 'ж':
                            find_sex: int = 2
                            return find_sex
                        elif text.lower() == 'м':
                            find_sex: int = 1
                            return find_sex
                        else:
                            send_message(user_id=user_id,
                                         message=f"Пол указан неверно. Введите 'м' или 'ж' (без кавычек!).")

        ts: int = resp['ts']


def get_sex(user_id: int, token: str = vk_group_token, version: str = api_version) -> int:
    """
    Функция определяет пол юзера и меняет его на противоположный.
    Если пол не указан, то произойдет обращение к функции ask_sex() для получения необходимой информации.
    """

    url: str = 'https://api.vk.com/method/users.get'
    params: dict = {'access_token': token,
                    'v': version,
                    'user_ids': user_id,
                    'fields': 'sex'}

    response: dict = requests.get(url, params=params).json()

    if 'sex' in response['response'][0]:
        sex: int = response['response'][0]['sex']
        if sex == 1:  # 1 - женский пол
            find_sex: int = 2
        else:  # 2 - мужской пол
            find_sex: int = 1

    else:
        find_sex: int = ask_sex(user_id=user_id)

    return find_sex


def ask_age(user_id: int) -> int:
    """ Функция, которая спрашивает возраст юзера. """

    server, key, ts = call_server()

    send_message(user_id=user_id, message=f"Укажите, пожалуйста, Ваш возраст цифрами (от 18 до 65).")

    while True:
        resp: dict = requests.get(f'https://{server}?act=a_check&key={key}&ts={ts}&wait=90&mode=2&version=2').json()

        try:
            updates: list = resp['updates']

        except KeyError:
            server, key, ts = call_server()
            continue

        if updates:

            for element in updates:
                action_code: int = element[0]

                if action_code == 4:
                    flags = []
                    flag: int = element[2]

                    for number in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 65536]:
                        if flag & number:
                            flags.append(number)

                    if 2 not in flags:
                        text: str = element[5]

                        if text.isdigit():
                            if 18 <= int(text) <= 65:
                                age: int = int(text)
                                return age
                            elif int(text) < 18 or int(text) > 65:
                                send_message(user_id=user_id,
                                             message=f"Ваш возраст должен быть не меньше 18 лет и не более 65 лет, "
                                                     f"иначе я не смогу Вам помочь.\n"
                                                     f"Пожалуйста, повторите ввод, если Вы вдруг ошиблись.")

                        else:
                            send_message(user_id=user_id,
                                         message=f"Возраст необходимо указать цифрами. "
                                                 f"Пожалуйста, используйте числа от 18 до 65 включительно.")

        ts: int = resp['ts']


def get_age(user_id: int, token: str = vk_group_token, version: str = api_version) -> int:
    """
    Функция, которая определяет возраст юзера. Если дата рождения не указана или указана не полностью,
    то произойдет обращение к функции ask_age() для получения необходимой информации.
    """

    url: str = 'https://api.vk.com/method/users.get'
    params: dict = {'access_token': token,
                    'v': version,
                    'user_ids': user_id,
                    'fields': 'bdate'}

    response: dict = requests.get(url, params=params).json()

    if 'bdate' in response['response'][0]:
        birthday: str = response['response'][0]['bdate']

        if len(birthday) > 5:  # то есть, если указаны не только дата и месяц, но и год рождения
            birthday_day, birthday_month, birthday_year = map(int, birthday.split('.'))
            today = datetime.date.today()
            age: int = today.year - birthday_year
            if today.month < birthday_month:
                age -= 1
            elif today.month == birthday_month and today.day < birthday_day:
                age -= 1
            return age

    else:
        age: int = ask_age(user_id=user_id)
        return age


def ask_city(user_id: int, token: str = access_token, version: str = api_version) -> int:
    """ Функция, которая спрашивает город юзера и ищет его идентификатор в базе. """

    server, key, ts = call_server()

    send_message(user_id=user_id, message=f"Введите, пожалуйста, название Вашего города.\n"
                                          f"Внимание! Сервис работает только по России!")

    while True:
        resp: dict = requests.get(f'https://{server}?act=a_check&key={key}&ts={ts}&wait=90&mode=2&version=2').json()

        try:
            updates: list = resp['updates']

        except KeyError:
            server, key, ts = call_server()
            continue

        if updates:

            for element in updates:
                action_code: int = element[0]

                if action_code == 4:
                    flags = []
                    flag: int = element[2]

                    for number in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 65536]:
                        if flag & number:
                            flags.append(number)

                    if 2 not in flags:
                        city_input: str = element[5]

                        url: str = f'https://api.vk.com/method/database.getCities'
                        params: dict = {'access_token': token,
                                        'v': version,
                                        'country_id': 1,  # ищем только по России
                                        'q': city_input}

                        response: dict = requests.get(url, params=params).json()

                        list_cities: list = response['response']['items']

                        if not list_cities:  # []
                            send_message(user_id=user_id,
                                         message=f"К сожалению, я не смог отыскать город с таким именем.\n"
                                                 f"Возможно Вы ошиблись при вводе или ищете город не в России.\n"
                                                 f"Попробуйте снова.")

                        else:
                            for city_info in list_cities:
                                if city_info['title'].lower() == city_input.lower():
                                    city_id: int = city_info['id']
                                    return city_id

        ts: int = resp['ts']


def get_city(user_id: int, token: str = vk_group_token, version: str = api_version) -> int:
    """
    Функция, которая определяет город юзера.
    Если город не указан, то произойдет обращение к функции ask_city() для получения необходимой информации. """

    url: str = 'https://api.vk.com/method/users.get'
    params: dict = {'access_token': token,
                    'v': version,
                    'user_ids': user_id,
                    'fields': 'city'}

    response: dict = requests.get(url, params=params).json()

    if 'city' in response['response'][0]:
        city_info: dict = response['response'][0]['city']  # {'id': 1, 'title': 'Москва'}
        city_id: int = city_info['id']  # 1

    else:
        city_id: int = ask_city(user_id=user_id)

    return city_id


def search_candidates(user_id: int, token: str = access_token, version: str = api_version) -> list:
    """
    Функция, которая ищет подходящих по указанным критериям кандидатов.
    Возвращает список из id подходящих кандидатов, у которых профиль не закрыт.
    """

    url: str = 'https://api.vk.com/method/users.search'
    params: dict = {'access_token': token,
                    'v': version,
                    'count': 100,  # Количество возвращаемых кандидатов. По умолчанию - 20 человек! max - 1000
                    'offset': randrange(100),  # нужно ли здесь смещение - ?
                    'sex': get_sex(user_id),
                    'age_from': get_age(user_id) - 1,
                    'age_to': get_age(user_id) + 1,
                    'city_id': get_city(user_id),
                    'status': choice([1, 5, 6]),  # 1 - не женат / не замужем, 5 — всё сложно, 6 — в активном поиске
                    'has_photo': 1}  # только с фотографией профиля!

    response: dict = requests.get(url, params=params).json()

    candidates_id_list: list = []

    for candidate in response['response']['items']:
        if not candidate['is_closed'] or candidate['is_closed'] and candidate['can_access_closed']:
            candidates_id_list.append(candidate['id'])

    return candidates_id_list  # [155581803, 361521300, 21797088, 282718024, 261809217, 488565167, 537242478, ...]


def get_candidate_photo_id(candidate_id: int, token: str = access_token, version: str = api_version) -> list:
    """
    Функция, которая по id потенциального кандидата получает всю информацию по фоткам профиля данного кандидата,
    в том числе кол-во лайков, комментов, репостов...
    Обрабатывает полученную информацию и возвращает список из id наиболее популярных фоток конкретного кандидата.
    """

    url: str = 'https://api.vk.com/method/photos.get'
    params: dict = {'access_token': token,
                    'v': version,
                    'owner_id': candidate_id,
                    'album_id': 'profile',
                    'extended': 1}  # будут возвращены дополнительные поля: likes, comments, tags, can_comment, reposts

    response: dict = requests.get(url, params=params).json()

    all_photos: list = response['response']['items']  # список словарей (каждый словарь - информация об одной фотке)

    all_photos_id: list = [item['id'] for item in all_photos]  # список из id всех фоток кандидата
    # [274089554, 323489102, 338026977, 379483339, 381444604, 391632430, 410785974, 415743018, 456239023, 456239081]

    if 1 <= len(all_photos_id) <= 3:
        best_photos_id: list = all_photos_id  # отсылаем юзеру все фотки, что есть у потенциального кандидата

    else:  # т.к. мы изначально запрашиваем кандидатов только с фотографиями профиля, то значит их больше трёх !!!
        best_photo_dict = {}
        # {274089554: 49, 323489102: 15, 338026977: 29, 379483339: 16, 381444604: 17,
        #  391632430: 21, 410785974: 11, 415743018: 25, 456239023: 24, 456239081: 30}
        likes_comments_summand = []  # [49, 15, 29, 16, 17, 21, 11, 25, 24, 30]

        for item in all_photos:
            best_photo_dict.update({item['id']: item['comments']['count'] + item['likes']['count']})
            likes_comments_summand.append(item['comments']['count'] + item['likes']['count'])

        sorted_summand = sorted(likes_comments_summand, reverse=True)  # [49, 30, 29, 25, 24, 21, 17, 16, 15, 11]

        best_photos_id = []

        for summa in sorted_summand[:3]:  # 49, 30, 29
            for key, value in best_photo_dict.items():
                if summa == value:
                    if len(best_photos_id) < 3:  # на случай, если несколько фоток имеют одно и то же количество лайков
                        best_photos_id.append(key)
                    else:
                        break

    return best_photos_id  # [274089554, 456239081, 338026977]


def main() -> None:
    """
    Собственно бот.
    Отслеживает новые сообщения в чате сообщества 'VKinder'.
    При получении нового сообщения обрабатывает полученные данные, выдает и записывает результат в БД PostgreSQL.
    Ничего не возвращает.
    """
    server, key, ts = call_server()

    while True:
        resp: dict = requests.get(f'https://{server}?act=a_check&key={key}&ts={ts}&wait=90&mode=2&version=2').json()
        # {'ts': 1724780633, 'updates': [[4, 50, 1, 11933849, 1675533592, 'hello', {'title': ' ... '}]]}

        try:
            updates: list = resp['updates']

        except KeyError:  # если здесь возбуждается исключение KeyError, то параметр key устарел, и нужно получить новый
            server, key, ts = call_server()
            continue  # переходим на следующую итерацию цикла, чтобы сделать повторный запрос

        if updates:  # проверка, были ли обновления
            for element in updates:
                # [4, 50, 1, 11933849, 1675533592, 'hello', {'title': ' ... '}]
                action_code: int = element[0]

                if action_code == 4:  # цифра 4 - это новое сообщение

                    # научим программу отличать исходящие сообщения от входящих:
                    flags = []  # массив, где мы будем хранить слагаемые
                    flag = element[2]  # флаг сообщения
                    for number in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 65536]:  # идём циклом по возможным слагаемым
                        if flag & number:  # проверяем, является ли число слагаемым с помощью побитового И
                            flags.append(number)  # если является, добавляем его в массив
                    if 2 not in flags:  # если это не исходящее сообщение, то:

                        # NB! Если юзер не в сети, то его id начинается с минуса - берём модуль на всякий случай!
                        user_id = abs(element[3])  # получаем id написавшего юзера
                        text = element[5]  # получаем текст сообщения юзера

                        if text.lower() == 'начать':
                            send_message(user_id=user_id,
                                         message=f"Рад Вас приветствовать, {get_person_info(person_id=user_id)[1]}!\n\n"
                                                 f"Я чат-бот VKinder и сейчас я постараюсь подобрать Вам пару.")

                            send_message(user_id=user_id,
                                         message=f"К сожалению, я только учусь, поэтому мне очень важно, "
                                                 f"чтобы ты правильно отвечал на мои вопросы.\n\n"
                                                 f"Также мне понадобится время. Просто немножечко терпения.. ")

                            create_table()  # создаем таблицу для потенциальных кандидатов

                            # делаем подбор подходящих кандидатов и вносим информацию о них в БД (таблица 'Candidates')
                            for candidate in search_candidates(user_id=user_id):
                                insert_candidates_info(info=get_person_info(person_id=candidate))

                            send_message(user_id=user_id,
                                         message=f"Я подобрал Вам самых лучших кандидатов.\n\n"
                                                 f"Пожалуйста, введите 'да', чтобы насладиться первым!")

                        elif text.lower() == 'да':

                            if get_user_from_db():

                                vk_id, vk_name, vk_surname, vk_link = get_user_from_db()
                                # 490728474 Миша Сафаров vk.com/id490728474
                                send_message(user_id=user_id, message=f"{vk_name} {vk_surname}\n{vk_link}")

                                for index, value in enumerate(get_candidate_photo_id(vk_id)):
                                    send_photo(user_id=user_id, candidate_id=vk_id,
                                               photo_id=get_candidate_photo_id(vk_id)[index])

                                delete_candidate(vk_id)

                                send_message(user_id=user_id,
                                             message=f"Желаете продолжить? Тогда смело вводите 'да'.\n"
                                                     f"Если Вы уже подобрали себе пару - введите 'нет'.")
                            else:
                                send_message(user_id=user_id,
                                             message=f"Кажется, кандидаты закончились. "
                                                     f"Введите 'начать', чтобы найти новых.")

                        elif text.lower() == 'нет':
                            send_message(user_id=user_id, message=f"Рад был Вам помочь! Надеюсь, я был полезен! :)\n"
                                                                  f"Если захотите повторить - введите 'начать'!")

                        else:
                            # работа с БД, чтобы бот не реагировал на сообщения, запрашивающие у юзера доп. инфу:
                            if get_select_users(user_id=user_id):  # если юзер не понял с 1 раза - это его проблемы!
                                pass
                            else:  # отправляем подсказку для нового юзера в самом начале беседы с ботом
                                create_table_user()
                                insert_users(user_id=user_id)
                                send_message(user_id=user_id,
                                             message=f"Введите \'начать\', чтобы я смог начать поиск партнера.")

        ts: int = resp['ts']  # обновление номера ts последнего обновления


if __name__ == '__main__':
    main()
