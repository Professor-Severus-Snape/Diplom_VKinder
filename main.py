from vk import *


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

        try:
            updates: list = resp['updates']

        except KeyError:  # если здесь возбуждается исключение KeyError, то параметр key устарел, и нужно получить новый
            server, key, ts = call_server()
            continue  # переходим на следующую итерацию цикла, чтобы сделать повторный запрос

        if updates:  # проверка, были ли обновления
            for element in updates:
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
                            create_table()  # создаем таблицу куда будем кидать уже просмотренных кандидатов

                            send_message(user_id=user_id,
                                         message=f"Рад Вас приветствовать, {get_person_info(person_id=user_id)[0]}!\n\n"
                                                 f"Я чат-бот VKinder и сейчас я постараюсь подобрать Вам пару.\n\n"
                                                 f"К сожалению, я только учусь, поэтому мне очень важно, "
                                                 f"чтобы Вы правильно отвечали на мои вопросы.\n\n"
                                                 f"Введите 'да', если Вы готовы насладиться первым кандидатом.")

                        elif text.lower() == 'да':

                            vk_id = search_candidates(user_id=user_id)

                            vk_name, vk_surname, vk_link = get_person_info(person_id=vk_id)

                            send_message(user_id=user_id, message=f"{vk_name} {vk_surname}\n{vk_link}")

                            for index, value in enumerate(get_candidate_photo_id(vk_id)):
                                send_photo(user_id=user_id, candidate_id=vk_id,
                                           photo_id=get_candidate_photo_id(vk_id)[index])

                            insert_candidate_id(candidate_id=vk_id)

                            send_message(user_id=user_id,
                                         message=f"Желаете продолжить? Тогда смело вводите 'да'.\n\n"
                                                 f"Если Вы уже подобрали себе пару - введите 'нет'.")

                        elif text.lower() == 'нет':
                            send_message(user_id=user_id, message=f"Рад был Вам помочь! Надеюсь, я был полезен! :)\n\n"
                                                                  f"Если захотите повторить - введите 'начать'!")

                        else:
                            # работа с БД, чтобы бот не реагировал на сообщения, запрашивающие у юзера доп. инфу:
                            create_table_user()  # таблица создастся только в случае если её не было - общая для всех!!!
                            if get_select_users(user_id=user_id):  # если юзер не понял с 1 раза - это его проблемы!
                                pass
                            else:  # отправляем подсказку для нового юзера в самом начале беседы с ботом
                                insert_users(user_id=user_id)
                                send_message(user_id=user_id,
                                             message=f"Введите \'начать\', чтобы я смог начать поиск партнера.")

        ts: int = resp['ts']  # обновление номера ts последнего обновления


if __name__ == '__main__':
    main()
