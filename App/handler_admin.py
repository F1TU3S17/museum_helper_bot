import time

import pytz
from helpful_function import shorten_url
from database import *
from admin_database import *
from password import *
from excel import *
from admin_fucnction import *
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram import exceptions
from aiogram.utils.chat_action import ChatActionSender
from aiogram.exceptions import TelegramAPIError
from aiogram.utils import chat_action
import keyboards as kb

router_admin_panel = Router()
bot = Bot(token='6971765827:AAGGYCGi7ouJ_0A5ZKwFX-VPbm5Cl_sSI68')

class Admin(StatesGroup):
    login = State()
    password = State()
    logined = State()
    message = State()
    mailing = State()
    edit_event = State()

@router_admin_panel.message(Command('login'))
async def start_login(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if not(check_admin(tg_id)):
        await message.answer('***Введите логин***', parse_mode='Markdown')
        await state.set_state(Admin.login)
    else:
        await message.answer('Вы уже авторизованы!',reply_markup=kb.admin_kb)
        await state.set_state(Admin.logined)

@router_admin_panel.message(Admin.login)
async def set_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer('***Введите пароль***', parse_mode='Markdown')
    await state.set_state(Admin.password)

@router_admin_panel.message(Admin.password)
async def set_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    data_login = data.get('login')
    data_password = data.get('password')

    await message.answer('***Выполняем вход***⏳', parse_mode='Markdown')
    if authenticate_admin(data_login, data_password):
        await state.clear()
        tg_id = message.from_user.id
        moscow_tz = pytz.timezone('Europe/Moscow')
        date = message.date
        date_msk = date.astimezone(moscow_tz)
        await add_authorized_admin(tg_id, date_msk)
        await state.set_state(Admin.logined)
        await message.answer('Вы успешно,авторизировались!\nТеперь вам доступна панель администратора.\n Теперь вы можете пользоваться командой /admin, чтобы открыть панель администратора в любой момент',
                             reply_markup=kb.admin_kb)
    else:
        await message.answer('Неправильный логин или пароль!\nПовторите процедуру заного!\n', reply_markup=kb.main)

@router_admin_panel.message(Command('admin'))
async def start_admin(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if (check_admin(tg_id)):
        await message.answer('Вот ваша панель администратора', reply_markup=kb.admin_kb)
        await state.set_state(Admin.logined)


@router_admin_panel.message(F.text == 'Создать рассылку📣', Admin.logined)
async def start_mailing(message: Message, state: FSMContext):
    await message.answer('Хорошо, давайте создадим рассылку.\nДля этого отправьте сообщение, которое хотите разослать', reply_markup=kb.admin_kb)
    await state.set_state(Admin.message)
@router_admin_panel.message(Admin.message)
async def get_message_mailing(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await message.answer('Что дальше?', reply_markup=kb.submit_kb)
    await state.set_state(Admin.mailing)


async def send_message_to_malling(users, data_message):
    for i in users:
        try:
            await bot.send_message(i[0], data_message, parse_mode='Markdown')
        except exceptions.TelegramForbiddenError:
            print(i, 'ban')
        except Exception as e:
            print(f'warning for {i[0]}: {e}')


@router_admin_panel.message(Admin.mailing)
async def go_mailing(message: Message, state: FSMContext):
    await state.update_data(mailing=message.text)
    data = await state.get_data()
    mailing = data.get('mailing')
    if mailing == 'Отправить':
        data_message = str(data.get('message'))
        users = await users_list()
        await message.answer('***Выполняем рассылку***⏳', parse_mode='Markdown')
        try:
            await send_message_to_malling(users, data_message)
        except exceptions.TelegramForbiddenError:
            print('ban')
        except Exception as e:
            print(f'warning')
        await message.answer(f'***Сообщение доставлено всем*** ***пользователям***📧', parse_mode='Markdown', reply_markup=kb.admin_kb)
    else:
        await message.answer('Как вам угодно😊', reply_markup=kb.admin_kb)
    await state.clear()
    await state.set_state(Admin.logined)


class AddEvent(StatesGroup):
    name = State()
    describe = State()
    start_time = State()
    end_time = State()
    last_data = State()
    add_data = State()
    cost = State()
    url = State()


@router_admin_panel.message(F.text == ('Настроить список мероприятий📅'), Admin.logined)
async def start_edit_events(message: Message):
    #df = init_table()
    await message.answer('Выбирайте, что хотите сделать',reply_markup=kb.event_editor_kb)


@router_admin_panel.callback_query(lambda c: c.data.startswith("add_event"))
async def edit_event(cq: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data_name = str(data.get('name'))
    data_describe = str(data.get('describe'))
    data_start_time = str(data.get('start_time'))
    data_end_time = str(data.get('end_time'))
    data_cost = str(data.get('cost'))
    data_url = str(data.get('url'))
    count_none = count_none_info(data_name, data_describe, data_start_time, data_end_time, data_cost, data_url)
    is_can_add = not(bool(count_none))
    if count_none:
        await cq.message.answer(f'Еще не заполнено ***{count_none}/6*** ячеек с информацией, заполните',
                                reply_markup=kb.create_add_kb(is_can_add), parse_mode='Markdown')
    else:
        await cq.message.answer('Все ячейки заполнены, теперь вы можете отправить информцию',
                                reply_markup=kb.create_add_kb(is_can_add), parse_mode='Markdown')
    await cq.message.edit_text('Чтобы добавить мероприятие установите его параметры', reply_markup=kb.create_add_event_kb(data_name, data_describe, data_start_time, data_end_time, data_cost, data_url))

@router_admin_panel.callback_query(lambda c: c.data.startswith("name") or c.data.startswith('describe') or c.data.startswith('start_time') or c.data.startswith('end_time')
                                             or c.data.startswith('cost') or c.data.startswith('ticket_url'))
async def edit_event_param(cq: CallbackQuery, state: FSMContext):
    if cq.data.startswith("name"):
        await state.set_state(AddEvent.name)
        await cq.message.edit_text('Напишите название мероприятия')
    elif cq.data.startswith("describe"):
        await state.set_state(AddEvent.describe)
        await cq.message.edit_text('Напишите описание для мероприятия')
    elif cq.data.startswith("start_time"):
        await state.set_state(AddEvent.start_time)
        await cq.message.edit_text('Напишите дату начала мероприятия в формате ДД:ММ:ГГГГ ЧЧ:ММ:СС')
    elif cq.data.startswith("end_time"):
        await state.set_state(AddEvent.end_time)
        await cq.message.edit_text('Напишите дату завершения мероприятия в формате ДД:ММ:ГГГГ ЧЧ:ММ:СС')
    elif cq.data.startswith("cost"):
        await state.set_state(AddEvent.cost)
        await cq.message.edit_text('Напишите стоимость похода на мероприятие(если оно бесплатно, то напишите слово: \"Бесплатно\" ')
    elif cq.data.startswith("ticket_url"):
        await state.set_state(AddEvent.url)
        await cq.message.edit_text('Напишите ссылку на покупку билета на мероприятие(если мероприятие бесплатное, то напишите: \"-\" или \"Отсутсвует\" ')

@router_admin_panel.message(AddEvent.name)
async def add_event_name(message:Message, state: FSMContext):
    data = await state.get_data()
    data_type = ("name:" + str(data.get('name')))
    await state.update_data(name=message.text)
    await state.update_data(last_data=data_type)
    await message.answer('Что делаем?', reply_markup=kb.add_event_param)
    await state.set_state(Admin.logined)

@router_admin_panel.message(AddEvent.describe)
async def add_event_describe(message:Message, state: FSMContext):
    data = await state.get_data()
    data_type = ("describe:"+str(data.get('describe')))
    await state.update_data(describe=message.text)
    await state.update_data(last_data=data_type)
    await message.answer('Что делаем?', reply_markup=kb.add_event_param)
    await state.set_state(Admin.logined)

@router_admin_panel.message(AddEvent.start_time)
async def add_event_start_time(message:Message, state: FSMContext):
    data = await state.get_data()
    data_type = ("start_time:" + str(data.get('start_time')))
    await state.update_data(start_time=message.text)
    await state.update_data(last_data=data_type)
    if validate_datetime_format(str(message.text)):
        await message.answer('Что делаем?', reply_markup=kb.add_event_param)
        await state.set_state(Admin.logined)
    else:
        await message.answer('Введеная вами информация не соотвествует формату "ДД:ММ:ГГГГ ЧЧ:ММ:СС"\nПопробуйте снова!')


@router_admin_panel.message(AddEvent.end_time)
async def add_event_end_time(message:Message, state: FSMContext):
    data = await state.get_data()
    data_type = ("end_time:" + str(data.get('end_time')))
    await state.update_data(end_time=message.text)
    await state.update_data(last_data=data_type)
    if validate_datetime_format(str(message.text)):
        await message.answer('Что делаем?', reply_markup=kb.add_event_param)
        await state.set_state(Admin.logined)
    else:
        await message.answer('Введеная вами информация не соотвествует формату "ДД:ММ:ГГГГ ЧЧ:ММ:СС"\nПопробуйте снова!')


@router_admin_panel.message(AddEvent.cost)
async def add_event_name(message:Message, state: FSMContext):
    data = await state.get_data()
    data_type = ("cost:" + str(data.get('cost')))
    await state.update_data(cost=message.text)
    await state.update_data(last_data=data_type)
    await message.answer('Что делаем?', reply_markup=kb.add_event_param)
    await state.set_state(Admin.logined)

@router_admin_panel.message(AddEvent.url)
async def add_event_name(message:Message, state: FSMContext):
    data = await state.get_data()
    data_type = ("url:" + str(data.get('url')))
    user_url = message.text
    if str(message.text).startswith('https://'):
        user_url = shorten_url(message.text)
    await state.update_data(url=user_url)
    await state.update_data(last_data=data_type)
    await message.answer('Что делаем?', reply_markup=kb.add_event_param)
    await state.set_state(Admin.logined)

@router_admin_panel.callback_query(lambda c: c.data.startswith("last_event"))
async def last_param(cq: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data_last = str(data.get('last_data')).split(':')
    state_name = data_last[0]
    state_data = data_last[1]
    await state.update_data({str(state_name):state_data})
    new_data = await state.get_data()
    data_name = str(new_data.get('name'))
    data_describe = str(new_data.get('describe'))
    data_start_time = str(new_data.get('start_time'))
    data_end_time = str(new_data.get('end_time'))
    data_cost = str(data.get('cost'))
    data_url = str(data.get('url'))
    await cq.message.edit_text('Хорошо, изменения отменены', reply_markup=kb.create_add_event_kb(data_name, data_describe, data_start_time,
                                                                                                 data_end_time, data_cost, data_url))

@router_admin_panel.message(F.text == "Добавить мероприятие", Admin.logined)
async def add_event(message:Message, state: FSMContext):
    data = await state.get_data()
    data_name = str(data.get('name'))
    data_describe = str(data.get('describe'))
    data_start_time = str(data.get('start_time'))
    data_end_time = str(data.get('end_time'))
    data_cost = str(data.get('cost'))
    data_url = str(data.get('url'))
    await add_event_to_excel(data_name, data_describe, data_start_time, data_end_time, data_cost, data_url)
    #await state.clear()
    await state.set_state(Admin.logined)
    await message.answer('Мероприятие успешно добавлено!\nБудем оповещать пользователей об этом ?', reply_markup=kb.go_meling)

@router_admin_panel.message(F.text == "Отменить добавление", Admin.logined)
async def no_add_event(message:Message, state: FSMContext):
    await state.clear()
    await state.set_state(Admin.logined)
    await message.answer('Хорошо, в этот раз не будет ничего добавлять!', reply_markup=kb.admin_kb)

@router_admin_panel.message(F.text == "Сделать рассылку✔", Admin.logined)
async def go_mailing_about_event(message:Message, state: FSMContext):
    data = await state.get_data()
    data_name = str(data.get('name'))
    data_start_time = str(data.get('start_time'))
    data_end_time = str(data.get('end_time'))
    users = await users_list()
    data_message = (f'Уважаймые посетители музея, только что появилась информация о новом мероприятии:***{data_name}***🔥\n'
                    f'Оно начнется:***{data_start_time} и продлится до {data_end_time}***\n⏳'
                    f'Узнать подробности и установить напоминание можно в прямо здесь календаре мероприятий!📋')
    await message.answer('***Выполняем рассылку***⏳', parse_mode='Markdown')
    try:
        await send_message_to_malling(users, data_message)
    except exceptions.TelegramForbiddenError:
        print('ban')
    except Exception as e:
        print(f'warning')
    await message.answer(f'***Сообщение доставлено всем*** ***пользователям***📧', parse_mode='Markdown',
                         reply_markup=kb.admin_kb)
    await state.clear()
    await state.set_state(Admin.logined)
@router_admin_panel.message(F.text == "Не делать рассылку", Admin.logined)
async def no_mailing_about_event(message:Message, state: FSMContext):
    await state.clear()
    await state.set_state(Admin.logined)
    await message.answer('Хорошо, в этот раз не будет ничего рассылать!', reply_markup=kb.admin_kb)

@router_admin_panel.callback_query(lambda c: c.data.startswith("delete_event"))
async def list_event(cq: CallbackQuery):
    await get_del_unnecessary_review()
    await cq.message.edit_text('Выбирайте мероприятие, которое собираетесь удалить!',
                               reply_markup=kb.create_admin_event_list())
@router_admin_panel.callback_query(lambda c: c.data.startswith("to_admin"))
async def to_admin_panel(cq: CallbackQuery):
    await cq.message.delete()
    await cq.message.answer('Возвращаемся в панель администратора!', reply_markup=kb.admin_kb)

@router_admin_panel.callback_query(lambda c: c.data.startswith("to_delete"))
async def event_del(cq: CallbackQuery):
    event_index = cq.data.split(":")[1]
    event_name = list(events_data.keys())[int(event_index)]
    event_describe = events_data[event_name]
    event_avg_mark = await avg_mark_review(event_name)
    event_count_review = await count_review(event_name)
    await cq.message.edit_text(f'Хотите удалить это мероприятие?\n'
                               f'{event_name}\n{event_describe}\n'
                               f'Количество отзывов: {event_count_review} Средняя оценка: {event_avg_mark}/5',
                               reply_markup=kb.create_del_or_no_kb(event_index)
                               )

@router_admin_panel.callback_query(lambda c: c.data.startswith("go_del"))
async def delete(cq: CallbackQuery):
    event_index = cq.data.split(":")[1]
    event_name = list(events_data.keys())[int(event_index)]
    await delete_event(event_name)
    await cq.message.edit_text('Удаление завершено!', reply_markup=kb.create_admin_event_list())
    await get_del_unnecessary_review()

@router_admin_panel.callback_query(lambda c: c.data.startswith("to_list"))
async def to_list(cq: CallbackQuery):
    await cq.message.edit_text('Хорошо, возвращаемся к списку', reply_markup=kb.create_admin_event_list())

@router_admin_panel.callback_query(lambda c: c.data.startswith("to_events"))
async def list_review(cq: CallbackQuery):
    await get_del_unnecessary_review()
    await debug_index()
    await cq.message.edit_text('Вам представлены все мероприятия с отзывами!',reply_markup=kb.create_admin_event_with_review())


class Exel(StatesGroup):
    update = State()
@router_admin_panel.callback_query(lambda c: c.data.startswith("edit_excel"))
async def edit_exel(cq: CallbackQuery, state: FSMContext):
    file_path = "BotData/events.xlsx"
    await cq.message.edit_text('Вот Excel-файл со списком мероприятий')
    file_to_send = FSInputFile(file_path)
    await cq.message.answer('Сохраняйте его структуру: заполняйте строки полностью, не добавляте лишних столбцов. Иначе вам не получится изменить список мероприятий',
                            reply_markup=kb.excel_kb)
    await bot.send_document(chat_id=cq.message.chat.id, document=file_to_send)
    await state.set_state(Exel.update)

@router_admin_panel.message(F.content_type.in_({'text'}),Exel.update)
async def exel_message(message: Message, state: FSMContext):
    if message.text == 'Не менять список мероприятий':
        await message.answer('Хорошо ничего не меняем!',reply_markup=kb.admin_kb)
        await state.set_state(Admin.logined)
    else:
        await message.answer('Если вы хотите изменить что-либо то пришлите файл, не хотите что-то менять, '
                             'то нажмите на кнопку \'Не менять список мероприятий\'')


@router_admin_panel.message(F.content_type.in_({'document'}),Exel.update)
async def handle_document(message: Message, state: FSMContext):
    document = message.document
    if document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        file_id = document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_name = 'user_events.xlsx'
        saved_file_path = f"BotData/{file_name}"
        await bot.download_file(file_path, saved_file_path)
        #time.sleep(2)
        is_ok = await cheсk_user_exel()
        if is_ok:
            await update_excel()
            await message.answer('Список успешно обновлен!!!\n', reply_markup=kb.admin_kb)
            await state.set_state(Admin.logined)
            df = init_table()
            new_slovar(df)
            globals.arr_event_in_str = (rows_to_arr_str(df))
        else:
            await message.answer('Вы не полностью заполнили информацию о мерприятии/ях либо добавили в файл лишние столбцы!!!\n'
                                 'Исправьте пожалуйста ваш Excel файл и пришлите заново!!!')
    else:
        await message.reply("Это не Excel файл. Пожалуйста, отправьте файл с расширением .xlsx")



@router_admin_panel.message(F.text == 'Удалить отзывы💬', Admin.logined)
async def list_review(message: Message):
    #df = init_table()
    await get_del_unnecessary_review()
    await debug_index()
    await message.answer('Вам представлены все мероприятия с отзывами!',reply_markup=kb.create_admin_event_with_review())

@router_admin_panel.callback_query(lambda c: c.data.startswith("look_rev"))
async def look_reviews(cq: CallbackQuery):
    event_index = cq.data.split(":")[1]
    collection_reviews = await get_all_review_about(int(event_index))
    reviews_list = [i[0] for i in collection_reviews]
    marks_list = [i[1] for i in collection_reviews]
    event_name = await name_by_index(event_index)
    #print(event_index, reviews_list, list(events_data.keys()))
    await cq.message.edit_text(f'Вот отзывы о {event_name}, чтобы удалить отзыв, выберите его!',
                               reply_markup=kb.create_admin_reviews_by_event(event_index,reviews_list,marks_list))

@router_admin_panel.callback_query(lambda c: c.data.startswith("rowid_del"))
async def look_review(cq: CallbackQuery):
    event_rowid = cq.data.split(":")[1]
    collection_reviews = await by_rowid_get_review(event_rowid)
    event_name = collection_reviews[0][0]
    event_review = collection_reviews[0][1]
    event_mark = collection_reviews[0][2]
    await cq.message.edit_text(f'Вы действиетельно хотите удалить этот отзыв?\n'
                         f'Название: {event_name}\n'
                         f'Отзыв: {event_review}\n'
                         f'Оценка: {event_mark}',reply_markup=kb.create_del_or_no_rev_kb(event_rowid))

@router_admin_panel.callback_query(lambda c: c.data.startswith("go_kill"))
async def del_review(cq: CallbackQuery):
    event_rowid = cq.data.split(":")[1]
    event_col = await by_rowid_get_review(event_rowid)
    event_name = event_col[0][0]
    event_index = event_col[0][3]
    await delete_rowid(event_rowid)
    collection_reviews = await get_all_review_about(int(event_index))
    await cq.message.answer('Отзыв успешно удален!')
    if len(collection_reviews[0]):
        reviews_list = [i[0] for i in collection_reviews]
        marks_list = [i[1] for i in collection_reviews]
        await cq.message.answer('Отзыв успешно удален!')
        await cq.message.edit_text(f'Вот отзывы о {event_name}, чтобы удалить отзыв, выберите его!',
                                   reply_markup=kb.create_admin_reviews_by_event(event_index, reviews_list, marks_list))
    else:
        await cq.message.answer('Так как у прошлого мероприятия больше нет отзывов, вам представлены все мероприятия с отзывами!',
                             reply_markup=kb.create_admin_event_with_review())

@router_admin_panel.callback_query(lambda c: c.data.startswith("to_review"))
async def no_del_review(cq: CallbackQuery):
    event_rowid = cq.data.split(":")[1]
    event_col = await by_rowid_get_review(event_rowid)
    event_name = event_col[0][0]
    event_index = event_col[0][3]
    collection_reviews = await get_all_review_about(int(event_index))
    reviews_list = [i[0] for i in collection_reviews]
    marks_list = [i[1] for i in collection_reviews]
    await cq.message.answer('Отзыв не трогаем!')
    await cq.message.edit_text(f'Вот отзывы о {event_name}, чтобы удалить отзыв, выберите его!',
                               reply_markup=kb.create_admin_reviews_by_event(event_index, reviews_list, marks_list))

@router_admin_panel.message(F.text == 'Выйти из режима администратора⚙️', Admin.logined)
async def exit_admin(message: Message, state: FSMContext):
    await message.answer('Вы вышли из режима администратора',reply_markup=kb.main)
    tg_id = message.from_user.id
    await admin_out(tg_id)
    await state.clear()
