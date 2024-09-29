import asyncio
from datetime import datetime, timedelta
from globals import events_data, user_data
import smpt
import random
from gpt import *
from create_way_to_museum import *
from database import *
from excel import event_isnt_going_now, event_state
from helpful_function import counter_future_event
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton

from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from aiogram import exceptions
from aiogram.exceptions import TelegramAPIError
from aiogram.utils import chat_action
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.chat_action import ChatActionSender
import keyboards as kb
router = Router()

bot = Bot(token='6971765827:AAGGYCGi7ouJ_0A5ZKwFX-VPbm5Cl_sSI68')
emojis = ['🟦','🟨','🟪','🟩','🟥','🟧','🟫','⬜️','⬛️']
class Gpt(StatesGroup):
    prompt = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply('Привет! Задавай любой вопрос о нашем музее MuseumGPT и обязательно узнаешь ответ)\n'
                        'А также пользуйся другими функциями, чтобы узнать о них подробнее, пропиши /help', reply_markup=kb.main)
    await cmd_start_db(message.from_user.id)
@router.message(Command('main'))
async def cmd_main(message: Message):
    await message.answer('Перед вами основное меню!', reply_markup=kb.main)
    await cmd_start_db(message.from_user.id)
@router.message(Command('help'))
async def helper(message: Message):
    await message.answer('Для начала работы с ботом введите команду - /start, для вызова основного меню - /main')
    await message.answer(
        'Этот бот создан для тех, кто планирует посетить Каменский музей. Любой вопрос о музее можно задать нейросети, которая обязательно найдет правильный ответ!\n'
        'Также в боте доступны следующие функции:\n'
        '1. MuseumGPT: ИИ-помощник музея. Задавайте ему любые вопросы, и он постарается ответить.\n'
        '2. Календарь мероприятий: здесь вы сможете узнать, какие мероприятия проходили в музее, какие проходят сейчас, посмотреть отзывы о них или оставить свой.\n'
        '3. Напомнить о мероприятии: функция, позволяющая установить напоминание о предстоящем мероприятии в удобный для вас момент.\n'
        '4. Перейти на сайт музея: вы сможете перейти на сайт музея в два клика.\n'
        '5. Купить билеты: вы сможете купить билеты в два клика.\n'
        '6. Ближайший маршрут до музея: с помощью этой функции вы получите маршрут до музея, построенный в Яндекс.Картах, с использованием геолокации.\n'
        '7. Написать сотрудникам музея: вы сможете отправить любое текстовое сообщение сотрудникам музея\n')

@router.message(F.text == 'Календарь мероприятий📅')
async def calendar(message: Message):
    await message.reply('Выберете приглянувшееся мероприятие и узнайте подробнее:',reply_markup= kb.create_keyboard())

@router.callback_query(lambda c: c.data.startswith("previous"))
async def previous_events(callback_query: CallbackQuery):
    start = int(callback_query.data.split(":")[1])-3
    await callback_query.message.edit_reply_markup(reply_markup=kb.create_keyboard(start))

@router.callback_query(lambda c: c.data.startswith("show_more"))
async def show_more_callback(callback_query: CallbackQuery):
    start = int(callback_query.data.split(":")[1])
    await callback_query.message.edit_reply_markup(reply_markup=kb.create_keyboard(start))

@router.callback_query(lambda c: c.data.startswith("event") or c.data.startswith("back_to_event_info"))
async def event_callback(callback_query: CallbackQuery):
    index = int(callback_query.data.split(":")[1])
    keys = list(events_data.keys())
    event_name = keys[index]
    event_info = events_data[event_name]
    list_discribe_state = ['🟥Мероприятие завершено, но вы можете посмотреть отзывы о нем!!!\n','🟩Мероприятие идет прямо сейчас, успейте посетить!!!\n', '🟨Мерприятие скоро начнется, поставьте уведомление, чтобы не забыть о его начале!!!\n',]
    await callback_query.message.edit_text(
        text=f"{list_discribe_state[event_state(index)]}Ваш выбор: \"{event_name}\"\n\n{event_info}",
        reply_markup= kb.create_info_event_keyboard(index)
    )
 
@router.callback_query(lambda c: c.data.startswith("back"))
async def backward(callback_query: CallbackQuery):
    await callback_query.message.edit_text('Вот все мероприятия📅')
    index = int(callback_query.data.split(":")[1])
    start = (index // 3) * 3
    await callback_query.message.edit_reply_markup(reply_markup=kb.create_keyboard(start))

@router.callback_query(lambda c: c.data.startswith("review"))
async def review_callback(callback_query: CallbackQuery):
    event_index = str(callback_query.data.split(":")[1])
    event_name = list(events_data.keys())[int(event_index)]
    event_avg_mark = await avg_mark_review(event_name)
    event_count_review = await count_review(event_name)
    if not (event_isnt_going_now(int(event_index))):
        await callback_query.message.edit_text(text=f"Ваш выбор:\"{event_name}\"\n Средняя оценка мероприятия: ***{event_avg_mark}/5*** , Количество отзывов: ***{event_count_review}***",
                                           reply_markup=kb.create_review_keyboard(event_index), parse_mode='Markdown')
    else:
        await callback_query.message.edit_text(
            text="Мероприятие еще не началось, поэтому у него еще нет отзывов😊\nВозращайтесь, чтобы посмотреть отзывы или написать свой, когда мероприятие стартует",
            reply_markup=kb.create_review_keyboard(event_index, False))
   
@router.callback_query(lambda c: c.data.startswith("future_event"))
async def future_event_callback(callback_query: CallbackQuery):
    index = int(callback_query.data.split(":")[1])
    keys = list(events_data.keys())
    event_name = keys[index]
    event_info = events_data[event_name]
    await callback_query.message.edit_text(
        text=f"Ваш выбор: \"{event_name}\"\n\n{event_info}",
        reply_markup= kb.future_create_info_event_keyboard(index)
    )
    
@router.callback_query(lambda c: c.data.startswith("future_back"))
async def future_backward(callback_query: CallbackQuery):
    await callback_query.message.edit_text('Вот будущие мероприятия📅')
    index = int(callback_query.data.split(":")[1])
    start = (index // 3) * 3
    await callback_query.message.edit_reply_markup(reply_markup=kb.future_create_keyboard(start))

class Review(StatesGroup):
    index = State()
    message = State()
    mark = State()
    capch = State()
    capch_is_true = State()

@router.callback_query(lambda c: c.data.startswith("check_review"))
async def chek_review_callback(callback_query: CallbackQuery):
    event_index = str(callback_query.data.split(":")[1])
    #print(event_index)
    event_name = list(events_data.keys())[int(event_index)]
    review_collection = await look_review(event_name)
    if len(review_collection[0]):
        review_list = [i[0] for i in review_collection]
        mark_list = [i[1] for i in review_collection]
        output_str = f"Отзывы о {event_name}\n"
        for i in range(len(review_list)):
            output_str += "⁘— " + " Отзыв посетителя: " + str(review_list[i]) + ". Оценка: " + str(mark_list[i]) + "★" +"\n"
        await callback_query.message.edit_text(text=output_str, reply_markup=kb.create_review_keyboard(event_index))
    else:
        await callback_query.message.edit_text(text="У этого мероприятия еще нет отзывов, вы можете оставить первый😊",
                                               reply_markup=kb.create_review_keyboard(event_index))


@router.callback_query(lambda c: c.data.startswith("write_review"))
async def get_review_callback(callback_query: CallbackQuery, state: FSMContext):
    event_index = str(callback_query.data.split(":")[1])
    await state.update_data(index=int(event_index))
    await state.set_state(Review.message)
    await callback_query.message.edit_text(text="Записываем ваш отзыв")
    await callback_query.message.answer(text="Напишите ваш отзыв о мероприятии")

@router.message(Review.message)
async def get_mark_callback(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.set_state(Review.mark)
    await message.answer('Выберите оценку мероприятию',reply_markup=kb.marks_keyboard)

@router.message(Review.mark)
async def set_capth(message: Message, state: FSMContext):
    await state.update_data(mark=message.text)
    await message.answer('Чтобы отправить отзыв, пройдите каптчу')
    correct_emoji = random.choice(emojis)
    await state.update_data(capch=correct_emoji)
    await state.set_state(Review.capch)
    await message.reply(f'Выбери: "{correct_emoji}"', reply_markup=kb.capch_kbr(emojis))
@router.callback_query(Review.capch)
async def check_capth(cq: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    capch_color = data.get('capch')
    if (cq.data == capch_color):
        await cq.message.edit_text('Верно! Capcha пройдена')
        await cq.message.reply('Что делаем дальше?', reply_markup=kb.submit_kb)
        await state.set_state(Review.capch_is_true)
    else:
        correct_emoji = random.choice(emojis)
        await state.update_data(capch=correct_emoji)
        await cq.message.edit_text(f'Другой цвет! "{correct_emoji}"', reply_markup=kb.capch_kbr(emojis))



async def send_message_to_admin(admins, data_name, data_mark,data_message):
    for admin in admins:
        try:
            async with ChatActionSender.typing(bot=bot, chat_id=admin):
                await bot.send_message(admin, f'На мероприятие {data_name} оставлен отзыв\nОценка:{data_mark}\n'
                                              f'Содержание: \"{data_message}\"\n'
                                              f'Если отзыв содержит нецензурную лексики или с ним что-то не так, то вы можете его удалить в панели администратора')
        except exceptions.TelegramForbiddenError:
            print("Admin error")
        except Exception as e:
            print("Admin error")


@router.message(Review.capch_is_true)
async def check_capth(message: Message, state: FSMContext):
    await state.update_data(capch_is_true=message.text)
    data = await state.get_data()
    submit = data.get('capch_is_true')
    if submit == 'Отправить':
        data_index = data.get('index')
        data_message = data.get('message')
        data_mark = data.get('mark')
        data_name = list(events_data.keys())[int(data_index)]
        tg_id = message.from_user.id
        is_id_unique = await add_event_review(tg_id, data_index, data_name, data_message, data_mark)
        if (is_id_unique):
            await message.answer('***Идет отправка***⏳', parse_mode='Markdown',reply_markup=kb.main)
            await message.answer('Отзыв успешно отправлен!',reply_markup=kb.create_keyboard())
            admins = await admins_list()
            #print(admins)
            try:
                await send_message_to_admin(admins, data_name, data_mark, data_message)
            except exceptions.TelegramForbiddenError:
                print("Admin error")
            except Exception as e:
                print("Admin error")

        else:
            await message.answer('Так...', reply_markup=kb.main)
            await message.answer('Вы уже оставляли отзыв на это мероприятие', reply_markup=kb.create_keyboard())
    else:
        await message.answer('Хорошо!', reply_markup=kb.main)
        await message.answer('Как вам угодно!', reply_markup=kb.create_keyboard())

    await state.clear()

@router.message(F.text == 'MuseumGPT֎')
async def gpt(message: Message, state: FSMContext):
    await state.set_state(Gpt.prompt)
    await message.answer('Введите запрос...', reply_markup=kb.gptboard, parse_mode='markdown')

@router.message(Gpt.prompt)
async def get_prompt(message: Message, state: FSMContext):
    await state.update_data(prompt=message.text)
    data = await state.get_data()
    user_prompt = str(data.get('prompt'))
    #print('Запрос пользователя: ', user_prompt)
    if user_prompt == 'Вернуться в меню':
        await state.clear()
        await message.reply('Хорошо!', reply_markup= kb.main)
    else:
        await message.answer('***Ожидайте ответа***⏳',parse_mode='Markdown')
        answer = message_to_chat_gpt(user_prompt)
        await message.reply(answer, reply_markup= kb.gptboard)
        #print('Ответ ИИ: ', answer)
        await state.clear()
        await state.set_state(Gpt.prompt)



@router.message(F.text == 'Напомнить о мероприятии🔔')
async def add_notifications_about_event(message: Message):
    if(counter_future_event()):
        await message.reply('Выберите мероприятие, о начале которого хотите установить напоминание', reply_markup=kb.future_create_keyboard())
    else:
        await message.reply('К сожалению, на данный момент нет не начавшихся мероприятий.\nНо вы можете ознакомится с уже идущими мероприятиями в календаре мероприятий',
                            reply_markup=kb.main)


@router.message(F.text == 'Перейти на сайт музея🌐')
async def to_web(message: Message):
    await message.reply('Наш сайт: каменский-музей.рф', reply_markup=kb.to_site)

@router.message(F.text == 'Купить билеты💸')
async def to_afisha(message: Message):
    await message.reply('Вы можете купить билеты для вас и ваших близких тут:', reply_markup=kb.to_afisha_site)


@router.message(F.content_type == 'location')
async def create_way(message: Message):
    user_latitude = message.location.latitude
    user_longitude = message.location.longitude
    start_coord = (user_latitude, user_longitude)
    yandex_map_url = create_yandex_route_link(start_coord)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text='Перейти к маршруту', url=yandex_map_url)
    )

    await message.answer('Ваш маршрут построен:', reply_markup=builder.as_markup())
    await message.reply('Что еще хотите узнать ?', reply_markup=kb.main)

@router.message(F.text == 'Ближайший маршрут до музея🛣️')
async def get_location(message: Message):
    await message.reply('Чтобы мы смогли построить маршрут, нужно знать где вы находитесь сейчас)', reply_markup=kb.location)

@router.message(F.text == 'Выход в меню⬅️')
async def not_get_location(message: Message):
    await message.reply('Окей, если что построим тебе маршрут до нашего музея)', reply_markup=kb.main)

class Message_to_email(StatesGroup):
    message = State()
    capch = State()
    capch_is_true = State()

@router.message(F.text == 'Написать сообщение сотрудникам музея✉️')
async def start_msg(message: Message, state: FSMContext):
    await state.set_state(Message_to_email.message)
    await message.answer('Пишите сообщение', reply_markup=kb.send_mail)

@router.message(Message_to_email.message)
async def get_message_to_email(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    data = await state.get_data()
    user_message = (data.get('message'))
    #print("Сообщение, которое собирается отослать пользователь:", user_message)
    if user_message == 'Вернуться в меню':
        await state.clear()
        await message.reply('Хорошо!', reply_markup= kb.main)
    else:
        await message.reply('Для отправки сообщения пройдите капчу')
        correct_emoji = random.choice(emojis)
        await state.update_data(capch=correct_emoji)
        await state.set_state(Message_to_email.capch)
        await message.reply(f'Выбери: "{correct_emoji}"', reply_markup=kb.capch_kbr(emojis))


@router.callback_query(Message_to_email.capch)
async def checked_correct(cq: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    capch_color = data.get('capch')
    #print('Сравнение для каптчи: ', cq.data, capch_color)
    if(cq.data == capch_color):
        await cq.message.edit_text('Верно! Capcha пройдена')
        await cq.message.reply('Что делаем дальше?', reply_markup=kb.submit_kb)
        await state.set_state(Message_to_email.capch_is_true)
    else:
        correct_emoji = random.choice(emojis)
        await state.update_data(capch=correct_emoji)
        await cq.message.edit_text(f'Другой цвет! "{correct_emoji}"', reply_markup=kb.capch_kbr(emojis))

@router.message(Message_to_email.capch_is_true)
async def submit_message_to_email(message: Message, state: FSMContext):
    await state.update_data(capch_is_true=message.text)
    data = await state.get_data()
    user_message = (data.get('message'))
    user_choice = (data.get('capch_is_true'))
    if user_choice != 'Отменить отправку':
        await message.answer('***Идет отправка***📩', parse_mode='Markdown')
        await smpt.send_mail(user_message)
        await message.reply('Сообщение успешно отправлено!', reply_markup=kb.main)
        admins = await admins_list()
        counter = 0
        for admin in admins:
            await bot.send_message(admin, f'Только что пользователь отправил сообщение на почту\n'
                                          f'Содержание: \"{user_message}\"\n')
            counter += 1
        #print('Сообщение доставлено')
        await state.clear()
    else:
        await message.reply('Отправка сообщения отменена!', reply_markup=kb.main)
        await state.clear()

@router.callback_query(lambda c: c.data.startswith("how_notify_event"))
async def how_notify_event(callback_query: CallbackQuery):
    index= int(callback_query.data.split(":")[1])
    df = init_table()
    event_start = pd.to_datetime(df.iloc[index]['Дата начала'])
    
    current_time = datetime.now()
    delay = (event_start - current_time).total_seconds()
    if delay > 0:
        await callback_query.message.edit_reply_markup(reply_markup= kb.create_notification_keyboard(index))
    else:
        
        await callback_query.message.edit_text("Мероприятие уже идёт, приходите к нам! Часы работы музея: ежедневно с 10:00 до 18:00, кроме понедельника. \n Приобрести билеты вы можете зарание, перейдя на сайт🎫:",
                            reply_markup=kb.back_to_and_tickets(index))


class Notify(StatesGroup):
    get = State()
    future_get = State()

@router.callback_query(lambda c: c.data.startswith("notify_event"))
async def handle_notification_query(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    data = callback_query.data.split(':')
    curr_index = int(data[1])
    action = data[2]
    df = init_table()
    event = df.iloc[curr_index]
    event_name = event['Название мероприятия']
    event_start = pd.to_datetime(event['Дата начала'])

    remind_time = None
    if action == "3days":
        remind_time = event_start - timedelta(days=3)
        await schedule_notification(callback_query.from_user.id, event_name, remind_time, bot)

    elif action == "1day":
        remind_time = event_start - timedelta(days=1)
        await schedule_notification(callback_query.from_user.id, event_name, remind_time, bot)

    elif action == "custom":
        await state.set_state(Notify.get)
        user_data[callback_query.from_user.id] = {'event_name': event_name, 'curr_index': curr_index}
        await callback_query.message.answer("Пожалуйста, введите дату в формате ДД-ММ-ГГГГ, когда вы хотите получить напоминание:")

    await callback_query.answer()

@router.message(Notify.future_get)
async def custom_time_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_data:
        user_input = user_data[user_id]
        if 'remind_date' not in user_input:
            try:
                remind_date = datetime.strptime(message.text, '%d-%m-%Y').date()
                user_data[user_id]['remind_date'] = remind_date
                await message.answer("Теперь введите время в формате ЧЧ:ММ, когда вы хотите получить напоминание:")
            except ValueError:
                await message.answer("Пожалуйста, введите корректную дату в формате ДД-ММ-ГГГГ.")
        else:
            try:
                remind_time_str = message.text
                remind_time = datetime.strptime(remind_time_str, '%H:%M').time()
                remind_datetime = datetime.combine(user_input['remind_date'], remind_time)
                df = init_table()
                event_start = pd.to_datetime(df.iloc[user_input['curr_index']]['Дата начала'])
                
                if remind_datetime < event_start:
                    await schedule_future_notification(user_id, user_input['event_name'], remind_datetime, message.bot)
                else:
                    await message.answer("Время напоминания не может быть после начала мероприятия. Пожалуйста, попробуйте снова. Если же хотите вернуться обратно ко всем мероприятиям нажммите на кнопку:",
                                         reply_markup=kb.back_to_events(0))
                del user_data[user_id]
                await state.clear()
            except ValueError:
                await message.answer("Пожалуйста, введите корректное время в формате ЧЧ:ММ.")


@router.message(Notify.get)
async def custom_time_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_data:
        user_input = user_data[user_id]
        if 'remind_date' not in user_input:
            try:
                remind_date = datetime.strptime(message.text, '%d-%m-%Y').date()
                user_data[user_id]['remind_date'] = remind_date
                await message.answer("Теперь введите время в формате ЧЧ:ММ, когда вы хотите получить напоминание:")
            except ValueError:
                await message.answer("Пожалуйста, введите корректную дату в формате ДД-ММ-ГГГГ.")
        else:
            try:
                remind_time_str = message.text
                remind_time = datetime.strptime(remind_time_str, '%H:%M').time()
                remind_datetime = datetime.combine(user_input['remind_date'], remind_time)
                df = init_table()
                event_start = pd.to_datetime(df.iloc[user_input['curr_index']]['Дата начала'])

                if remind_datetime < event_start:
                    await schedule_notification(user_id, user_input['event_name'], remind_datetime, message.bot)
                else:
                    await message.answer(
                        "Время напоминания не может быть после начала мероприятия. Пожалуйста, попробуйте снова. Если же хотите вернуться обратно ко всем мероприятиям нажммите на кнопку:",
                        reply_markup=kb.back_to_events(0))
                del user_data[user_id]
                await state.clear()
            except ValueError:
                await message.answer("Пожалуйста, введите корректное время в формате ЧЧ:ММ.")

async def schedule_notification(user_id: int, event_name: str, remind_time: datetime, bot: Bot):
    current_time = datetime.now()
    delay = (remind_time - current_time).total_seconds()

    if delay > 0:
        asyncio.get_event_loop().call_later(delay, lambda: asyncio.create_task(send_notification(user_id, event_name, bot)))
        await bot.send_message(user_id, f"Напоминание о мероприятии \"{event_name}\" установлено на {remind_time}.",
                               reply_markup=kb.main)
        await bot.send_message(user_id, "Если хотите вернуться обратно ко всем мероприятиям нажммите на кнопку:",
                               reply_markup=kb.back_to_events(0))
    else:
        await bot.send_message(user_id, "Время напоминания уже прошло. Пожалуйста, выберите другое время. Если же хотите вернуться обратно ко всем мероприятиям нажммите на кнопку:",
                               reply_markup=kb.back_to_events(0))

async def send_notification(user_id: int, event_name: str, bot: Bot):
    await bot.send_message(user_id, f"🎉Напоминаем о начале мероприятия: {event_name}! \n Вы можете купить билеты для вас и ваших близких тут🎫:",
                            reply_markup=kb.to_afisha_site)


@router.callback_query(lambda c: c.data.startswith("future_how_notify_event"))
async def how_notify_event(callback_query: CallbackQuery):
    index= int(callback_query.data.split(":")[1])
    await callback_query.message.edit_reply_markup(reply_markup= kb.future_create_notification_keyboard(index))
    

@router.callback_query(lambda c: c.data.startswith("fnotify_event"))
async def handle_notification_query(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    data = callback_query.data.split(':')
    curr_index = int(data[1])
    action = data[2]
    df = init_table()
    event = df.iloc[curr_index]
    event_name = event['Название мероприятия']
    event_start = pd.to_datetime(event['Дата начала'])

    remind_time = None
    if action == "3days":
        remind_time = event_start - timedelta(days=3)
        await schedule_future_notification(callback_query.from_user.id, event_name, remind_time, bot)

    elif action == "1day":
        remind_time = event_start - timedelta(days=1)
        await schedule_future_notification(callback_query.from_user.id, event_name, remind_time, bot)

    elif action == "custom":
        await state.set_state(Notify.future_get)
        user_data[callback_query.from_user.id] = {'event_name': event_name, 'curr_index': curr_index}
        await callback_query.message.answer("Пожалуйста, введите дату в формате ДД-ММ-ГГГГ, когда вы хотите получить напоминание:")

    await callback_query.answer()

async def schedule_future_notification(user_id: int, event_name: str, remind_time: datetime, bot: Bot):
    current_time = datetime.now()
    delay = (remind_time - current_time).total_seconds()

    if delay > 0:
        asyncio.get_event_loop().call_later(delay, lambda: asyncio.create_task(send_notification(user_id, event_name, bot)))
        await bot.send_message(user_id, f"Напоминание о мероприятии \"{event_name}\" установлено на {remind_time}.",
                               reply_markup=kb.main)
        await bot.send_message(user_id, "Вы можете установить уведомления на другие мероприятия, если хотите",
                               reply_markup=kb.future_create_keyboard())

    else:
        await bot.send_message(user_id, "Время напоминания уже прошло. Пожалуйста, выберите другое время.")
        await bot.send_message(user_id, "Вы можете установить уведомления на другие мероприятия, если хотите",
                               reply_markup=kb.future_create_keyboard())
