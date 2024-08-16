import globals
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

#Функция для инициализации таблицы
#Функция обновляет глобальные данные лишь тогда, когда были разночтения с предыдущим считыванием
def init_table():
    df = pd.read_excel("BotData/events.xlsx")
    df_num_indexes = len(df.index.unique())
    df_num_colums = df.shape[1]
    
    if (df_num_indexes != globals.num_indexes) or (df_num_colums != globals.num_colums):
        globals.num_indexes = int(len(df.index.unique()))
        globals.num_colums = int(df.shape[1])
        globals.arr_event_in_str = (rows_to_arr_str(df))
        new_slovar(df)
    return df

# Функция для создания массива объектов строк таблицы
def create_arr_rows(df):
    arr_rows = [df.loc[i] for i in range(globals.num_indexes)]
    return arr_rows

#Функции для сортировки массива строк таблицы по дате начала
def sorted_by_event_date(arr_rows):
    return sorted(arr_rows, key=lambda x: x['Дата начала'])

# Функция для создания массива строк, где каждая строка - описание одного мероприятия
from datetime import datetime

def rows_to_arr_str(df):
    arr_str = []
    arr_rows = create_arr_rows(df)
    for i in range(globals.num_indexes):
        current_event_str = ""
        for j in range(globals.num_colums):
            current_event_str += str(df.columns[j]) + ": " + str(arr_rows[i].iloc[j]) + ", "
        arr_str.append(current_event_str)
    return arr_str


def new_slovar(df):
    arr_rows = sorted_by_event_date(create_arr_rows(df))
    globals.events_data.clear()
    for i in range(globals.num_indexes):
        event_name = str(arr_rows[i].iloc[0])
        event_info = []
        for j in range(1, globals.num_colums):
            if not (j in [2, 3]):
                event_info.append(f"• {df.columns[j]}: {arr_rows[i].iloc[j]}")
            else:
                date_object = arr_rows[i].iloc[j]
                formatted_date = date_object.strftime("%d-%m-%Y %H:%M:%S")
                event_info.append(f"• {df.columns[j]}: {formatted_date}")
        globals.events_data[event_name] = "\n".join(event_info)
        
async def add_event_to_excel(name, describe, start_time, end_time, cost, url, file_path="BotData/events.xlsx", sheet_name="Лист1"):
    df = pd.read_excel(file_path)
    date_format = '%d:%m:%Y %H:%M:%S'
    start_time = pd.to_datetime(start_time, format=date_format, dayfirst=True)
    end_time = pd.to_datetime(end_time, format=date_format, dayfirst=True)
    new_row = pd.DataFrame([{
        'Название мероприятия': name,
        'Краткое описание': describe,
        'Дата начала': start_time,
        'Дата завершения': end_time,
        'Стоимость': cost,
        'Ссылка на покупку билета': url
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df = df.sort_values(by='Дата начала')

    with pd.ExcelWriter(file_path) as writer:
       df.to_excel(writer, sheet_name='Лист1', index=False)

async def delete_event(event_name, file_path="BotData/events.xlsx"):
    df = pd.read_excel(file_path)
    df = df[df['Название мероприятия'] != event_name]
    with pd.ExcelWriter(file_path) as writer:
       df.to_excel(writer, sheet_name='Лист1', index=False)


#Функция для нахожения ссылка на покупку билета по названию мепроятия
def url_to_ticket(event_name, file_path="BotData/events.xlsx"):
    df = pd.read_excel(file_path)
    index = list(df['Название мероприятия']).index(event_name)
    url = list(df['Ссылка на покупку билета'])[index]

    return url

#Функция проверяет стоимость похода на мероприятие,
# если мероприятие бесплатное, то true, иначе false
def check_ticket_cost(event_name, file_path="BotData/events.xlsx"):
    df = pd.read_excel(file_path)
    index = list(df['Название мероприятия']).index(event_name)
    cost = str(list(df['Стоимость'])[index]).lower()
    if 'бесплатно' in cost:
        return True
    else:
        return False

def event_isnt_going_now(curr_index):
    df = init_table()
    event = df.iloc[curr_index]
    event_start = pd.to_datetime(event['Дата начала'])
    current_time = datetime.now()
    delay = (event_start - current_time).total_seconds()
    if delay > 0:
        return True
    else:
        return False

#Функция возвращает текущее состояние события
#Если событие уже прошло, то функция возращает 0
#Если событие еще идет, то возращается 1
#Если событие еще не началось 2
def event_state(curr_index, file_path="BotData/events.xlsx"):
    df = pd.read_excel(file_path)
    current_time = datetime.now()
    event = df.iloc[curr_index]
    event_start = pd.to_datetime(event['Дата начала'])
    event_end = pd.to_datetime(event['Дата завершения'])
    delay_to_start = (event_start - current_time).total_seconds()
    delay_to_end = (event_end - current_time).total_seconds()
    state = 0
    if delay_to_end <= 0:
        state = 0
    if delay_to_start > 0:
        state = 2
    if delay_to_start <= 0 and delay_to_end >= 0:
        state = 1
    return state

async def cheсk_user_exel(file_path="BotData/user_events.xlsx"):
    df = pd.read_excel(file_path)
    colums_name = [
        'Название мероприятия',
        'Краткое описание',
        'Дата начала',
        'Дата завершения',
        'Стоимость',
        'Ссылка на покупку билета'
    ]
    flag = False
    if (colums_name == list(df.columns)):
        user_df_num_indexes = len(df.index.unique())
        user_df_num_colums = df.shape[1]
        for i in range(user_df_num_colums):
            for j in range(user_df_num_indexes):
                if str((df[colums_name[i]].iloc[j])).lower().startswith('na'):
                    return flag
        flag = True
    return flag

async def update_excel(file_path="BotData/events.xlsx",user_file_path="BotData/user_events.xlsx"):
    user_df = pd.read_excel(user_file_path)
    with pd.ExcelWriter(file_path) as writer:
        user_df.to_excel(writer, sheet_name='Лист1', index=False)


