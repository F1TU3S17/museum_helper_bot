import re
def validate_datetime_format(date_str):
    """
        Проверяет, соответствует ли введённая строка формату "ДД:ММ:ГГГГ ЧЧ:ММ:СС".

        Параметры:
        date_str (str): Введённая пользователем строка с датой и временем.

        Возвращаемое значение:
        bool: True, если строка соответствует формату, иначе False.
        """
    # Регулярное выражение для проверки формата
    pattern = re.compile(r"^\d{2}:\d{2}:\d{4} \d{2}:\d{2}:\d{2}$")

    if pattern.match(date_str):
        try:
            day, month, year, hour, minute, second = map(int, re.split('[: ]', date_str))
            if 1 <= day <= 31 and 1 <= month <= 12 and 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60:
                return True
        except ValueError:
            pass
    return False

def count_none_info(name, describe, start_time, end_time, cost, url):
    """
    Функция подсчитывает сколько еще данных остались незаполненными
    Параметры: название мероприятия, описание мероприятия, время его начала и время завершения
    Возвращаемое значение: Количество незаполненных данных
           """
    flag = True
    info_list = [name, describe, start_time, end_time, cost, url]
    counter = 0
    for i in info_list:
        if i == 'None':
            counter += 1
    return counter

