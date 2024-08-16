import random
from excel import init_table, url_to_ticket, check_ticket_cost
from admin_database import get_rowid, get_all_event_name_with_review
from globals import events_data


from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardButton,InlineKeyboardMarkup)

main = ReplyKeyboardMarkup(keyboard=
                            [[KeyboardButton(text='MuseumGPT֎')],
                            [KeyboardButton(text='Календарь мероприятий📅'),KeyboardButton(text='Напомнить о мероприятии🔔')],
                            [KeyboardButton(text='Перейти на сайт музея🌐'),KeyboardButton(text='Купить билеты💸')],
                            [KeyboardButton(text='Ближайший маршрут до музея🛣️')],
						    [KeyboardButton(text='Написать сообщение сотрудникам музея✉️')]
                             ],
                            resize_keyboard=True,
                            input_field_placeholder='Чем могу быть полезен ?'
                           )

gptboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Вернуться в меню')]],
        input_field_placeholder='Ваш запрос...', resize_keyboard=True)



def create_keyboard(start=0, num_options=3):
    #init_slovar()
    df_orders = init_table()
    keys = list(events_data.keys())
    keyboard = []
    if start != 0:
        keyboard.append([InlineKeyboardButton(text="⬆ Показать предыдущие", callback_data=f"previous:{start}")])
        
    for i in range(start, min(start + num_options, len(keys))):
        keyboard.append([InlineKeyboardButton(text=keys[i], callback_data=f"event:{i}")])
    
    if start + num_options < len(keys):
        keyboard.append([InlineKeyboardButton(text="⬇ Показать следующие", callback_data=f"show_more:{start + num_options}")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def create_info_event_keyboard (curr_index):
    event_name = list(events_data.keys())[curr_index]
    event_free = check_ticket_cost(event_name)
    #start = (curr_index // 3) * 3
    if not(event_free):
        return InlineKeyboardMarkup(inline_keyboard=
                                     [[InlineKeyboardButton(text='Купить билет на мероприятие💸', url=f"{url_to_ticket(event_name)}")],
                                      [InlineKeyboardButton(text='Хотите установить напоминание?🔔', callback_data=f"how_notify_event:{curr_index}")],
                                      [InlineKeyboardButton(text='Отзывы о мероприятии📝', callback_data=f"review:{curr_index}")],
                                      [InlineKeyboardButton(text='⬅ Назад',callback_data=f"back:{curr_index}")]
                                        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=
                                    [[InlineKeyboardButton(text='Хотите установить напоминание?🔔',
                                                           callback_data=f"how_notify_event:{curr_index}")],
                                     [InlineKeyboardButton(text='Отзывы о мероприятии📝',
                                                           callback_data=f"review:{curr_index}")],
                                     [InlineKeyboardButton(text='⬅ Назад', callback_data=f"back:{curr_index}")]
                                     ])
def create_review_keyboard(index, is_event_now = True):
    if is_event_now:
        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Посмотреть все отзывы📋',callback_data=f"check_review:{index}"),
                                                                InlineKeyboardButton(text='Написать отзыв✍️',callback_data=f"write_review:{index}")],
                                                                [InlineKeyboardButton(text='⬅ Назад',callback_data=f"back_to_event_info:{index}")]])
    else:
        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='⬅ Назад', callback_data=f"back_to_event_info:{index}")]])
    return inline_keyboard

marks_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='1'),KeyboardButton(text='2'),KeyboardButton(text='3'),KeyboardButton(text='4'),KeyboardButton(text='5')]], resize_keyboard=True)
to_site = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Нажмите, чтобы перейти сейчас', url='https://каменский-музей.рф' )]])
to_afisha_site = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Перейти на widget.afisha.yandex.ru', url='https://widget.afisha.yandex.ru/w/venues/10315?clientKey=e6ca775a-c361-4b04-8cac-f3ae19bbd850&widgetName=w2' )]])

location = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Предоставить геолокацию📍',request_location=True)],
        [KeyboardButton(text='Выход в меню⬅️')]],
        resize_keyboard=True)

send_mail = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Вернуться в меню')]],
        resize_keyboard=True)

def capch_kbr(emj):
    button_list = [[],[],[]]
    random.shuffle(emj)
    counter = 0
    for item in emj:
        if counter < 3:
            button_list[0].append(InlineKeyboardButton(text=item, callback_data=item))
        elif counter < 6:
            button_list[1].append(InlineKeyboardButton(text=item, callback_data=item))
        else:
            button_list[2].append(InlineKeyboardButton(text=item, callback_data=item))
        counter += 1
    keyboard = InlineKeyboardMarkup(inline_keyboard=button_list)
    return keyboard


submit_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отправить'), KeyboardButton(text='Отменить отправку')]
    ],
    resize_keyboard=True
)


admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Создать рассылку📣')],
        [KeyboardButton(text='Настроить список мероприятий📅')],
        [KeyboardButton(text='Удалить отзывы💬')],
        [KeyboardButton(text='Выйти из режима администратора⚙️')]
    ],
    resize_keyboard=True
)

event_editor_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Добавить мероприятие📝',callback_data='add_event'),
                                                         InlineKeyboardButton(text='Удалить мероприятие🗑️',callback_data='delete_event')],
                                                        [InlineKeyboardButton(text='Редактировать список через Excel𝄜', callback_data='edit_excel')]])

def create_add_event_kb(event_name='Установите название', event_describe='Установите описание',
                        event_start_time='Установите время начала', event_end_time='Установите время завершения',
                        event_cost='Установите стоимость', event_url='Установите ссылку на покупку билета'):
    event_name = 'Название: ' + event_name
    event_describe = 'Описание: ' + event_describe
    event_start_time='Время начала: ' + event_start_time
    event_end_time='Время конца: ' + event_end_time
    event_cost = 'Стоимость: ' + event_cost
    event_url = 'Ссылка: ' + event_url
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=event_name, callback_data='name'),InlineKeyboardButton(text=event_describe, callback_data='describe')],
                                                      [InlineKeyboardButton(text=event_start_time,callback_data='start_time'),InlineKeyboardButton(text=event_end_time,callback_data='end_time')],
                                                      [InlineKeyboardButton(text=event_cost, callback_data='cost'),InlineKeyboardButton(text=event_url, callback_data='ticket_url')]])

    return inline_kb

add_event_param = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Добавить/изменить название мероприятия',callback_data='add_event'),
                                                         InlineKeyboardButton(text='Отменить изменения',callback_data='last_event')]])

def create_add_kb(is_can_add):
    keybd = []
    if is_can_add:
        keybd.append([KeyboardButton(text='Добавить мероприятие'), KeyboardButton(text='Отменить добавление')])
    else:
        keybd.append([KeyboardButton(text='Отменить добавление')])
    kb = ReplyKeyboardMarkup(keyboard=keybd, resize_keyboard=True)
    return kb

go_meling = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Сделать рассылку✔'),
                                                  KeyboardButton(text='Не делать рассылку')]], resize_keyboard=True)

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_admin_event_list():
    inline_kb = []
    df = init_table()
    keys = list(events_data.keys())
    for i in range(len(keys)):
        inline_kb.append([InlineKeyboardButton(text=keys[i], callback_data=f'to_delete:{i}')])
    inline_kb.append([InlineKeyboardButton(text='⬅ Вернуться в панель администратора', callback_data='to_admin')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    return keyboard

def create_del_or_no_kb(index):
    return (InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Удалить мероприятие🗑️',callback_data=f'go_del:{index}'),
                                                      InlineKeyboardButton(text='⬅ Вернуться к списку',callback_data='to_list')]]))


def create_admin_event_with_review():
    inline_kb = []
    collection_review = get_all_event_name_with_review()
    events_names = [i[0] for i in collection_review]
    events_index = [i[1] for i in collection_review]
    for i in range(len(events_names)):
        inline_kb.append([InlineKeyboardButton(text=events_names[i], callback_data=f'look_rev:{events_index[i]}')])
    inline_kb.append([InlineKeyboardButton(text='⬅ Вернуться в панель администратора', callback_data='to_admin')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    return keyboard

def create_admin_reviews_by_event(event_index, reviews_list, marks_list):
    inline_kb = []
    for i in range(len(reviews_list)):
        rowid = get_rowid(event_index,
                           reviews_list[i], marks_list[i])
        inline_kb.append([InlineKeyboardButton(text=f'Отзыв: {reviews_list[i]} Оценка: {marks_list[i]}', callback_data=f'rowid_del:{rowid}')])
    inline_kb.append([InlineKeyboardButton(text='⬅ Вернуться к списку мероприятий с отзывами', callback_data='to_events')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    return keyboard



def create_del_or_no_rev_kb(rowid):
    return (InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Удалить отзыв🗑️',callback_data=f'go_kill:{rowid}'),
                                                      InlineKeyboardButton(text='⬅ Вернуться к списку',callback_data=f'to_review:{rowid}')]]))
def create_notification_keyboard(curr_index):
    return InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(
                text='Напомнить за 3 дня',
                callback_data= f"notify_event:{curr_index}:3days")],
            [InlineKeyboardButton(
                text='Напомнить за 1 день',
                callback_data= f"notify_event:{curr_index}:1day"
            )],
            [InlineKeyboardButton(
                text='Ввести свое время',
                callback_data= f"notify_event:{curr_index}:custom"
            )]
        ]
    )
def back_to_and_tickets(index):
     return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Перейти на widget.afisha.yandex.ru', url='https://widget.afisha.yandex.ru/w/venues/10315?clientKey=e6ca775a-c361-4b04-8cac-f3ae19bbd850&widgetName=w2' )],
                                                  [InlineKeyboardButton(text='⬅ Назад к мероприятиям',callback_data=f"back:{index}")]])


def back_to_events (index):
     return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⬅ Назад к мероприятиям',callback_data=f"back:{index}")]])


def future_create_keyboard(start=0, num_options=3):
    from handlers import event_isnt_going_now
    df_orders = init_table()
    keys = list(events_data.keys())
    keyboard = []
    counter_future_event = 0
    for i in range(len(keys)):
        if event_isnt_going_now(i):
            keyboard.append([InlineKeyboardButton(text=keys[i], callback_data=f"future_event:{i}")])
            counter_future_event += 1


    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def counter_future_event():
    from handlers import event_isnt_going_now
    keys = list(events_data.keys())
    counter = 0
    for i in range(len(keys)):
        if event_isnt_going_now(i):
            counter += 1
            break;
    return counter

def future_create_info_event_keyboard (curr_index):
    #start = (curr_index // 3) * 3
    return InlineKeyboardMarkup(inline_keyboard=
                                 [[InlineKeyboardButton(text='Хотите установить напоминание?🔔', callback_data=f"future_how_notify_event:{curr_index}")],
                                  [InlineKeyboardButton(text='⬅ Назад',callback_data=f"future_back:{curr_index}")]
                                   ])
def future_create_notification_keyboard(curr_index):
    return InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(
                text='Напомнить за 3 дня',
                callback_data= f"fnotify_event:{curr_index}:3days")],
            [InlineKeyboardButton(
                text='Напомнить за 1 день',
                callback_data= f"fnotify_event:{curr_index}:1day"
            )],
            [InlineKeyboardButton(
                text='Ввести свое время',
                callback_data= f"fnotify_event:{curr_index}:custom"
            )]
        ]
    )

excel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Не менять список мероприятий')]
    ], resize_keyboard=True
)