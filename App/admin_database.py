import sqlite3 as sq
from database import db, cur
from globals import events_data
from excel import init_table

def get_all_event_name_with_review():
    collection_review = cur.execute('SELECT DISTINCT event_name, event_index FROM review ORDER by event_name').fetchall()
    return collection_review

async def get_all_review_about(event_index):
    collection_reviews = cur.execute('SELECT event_review, event_review_mark FROM review WHERE event_index == ? '
                                     'ORDER by event_review_mark DESC',(event_index,)).fetchall()
    if collection_reviews:
        return collection_reviews
    else:
        return [()]

async def name_by_index(index):
    name = cur.execute('SELECT event_name FROM review WHERE event_index == ?',(index,)).fetchone()
    if name:
        return name[0]
    else:
        return 'NONAME'


async def name_by_index(index):
    name = cur.execute('SELECT event_name FROM review WHERE event_index == ?',(index,)).fetchone()
    if name:
        return name[0]
    else:
        return 'NONAME'

def get_rowid(index, review, mark):
    rowid = cur.execute('SELECT rowid FROM review WHERE event_index == ? and event_review == ? and event_review_mark == ?',(index,review,mark)).fetchone()
    if rowid:
        return rowid[0]
    else:
        return 'None'

async def delete_rowid(rowid):
    cur.execute('DELETE FROM review WHERE rowid == ?',(rowid,))
    db.commit()

async def by_rowid_get_review(rowid):
    collection_reviews = cur.execute('SELECT event_name, event_review, event_review_mark, event_index FROM review WHERE rowid == ? '
                                     'ORDER by event_review_mark DESC', (rowid,)).fetchall()
    if collection_reviews:
        return collection_reviews
    else:
        return [()]


#Функция удаляет отзывы о мероприятиях, которых больше нет в календаре
async def get_del_unnecessary_review():
    df = init_table()
    collection_review = get_all_event_name_with_review()
    for_deletion = []
    for i in range(len(collection_review)):
        if not(collection_review[i][0] in list(events_data.keys())):
            for_deletion += [collection_review[i][0]]

    for i in range(len(for_deletion)):
        cur.execute('DELETE FROM review WHERE event_name == ?', (for_deletion[i],))
        db.commit()

async def add_authorized_admin(tg_id, date):
    if not(cur.execute('SELECT * FROM authorized_admins WHERE tg_id == ?', (tg_id,)).fetchone()):
        cur.execute('INSERT INTO authorized_admins VALUES(?, ?, ?)', (tg_id, date, 1))
        db.commit()
    else:
        is_admin_now = check_admin(tg_id)
        if not(is_admin_now):
            cur.execute('UPDATE authorized_admins set now_admin = 1, date = ? WHERE now_admin = 0 and tg_id = ?',(date, tg_id))
            db.commit()

def check_admin(tg_id):
    is_authorized = False
    admin = (cur.execute('SELECT * FROM authorized_admins WHERE tg_id == ?', (tg_id,)).fetchone())
    if admin:
        is_authorized = bool(admin[2])
    return is_authorized

async def admin_out(tg_id):
    admin = (cur.execute('SELECT * FROM authorized_admins WHERE tg_id == ?', (tg_id,)).fetchone())
    if admin:
        cur.execute('UPDATE authorized_admins set now_admin = 0 WHERE now_admin = 1 and tg_id = ?', (tg_id,))
        db.commit()

async def debug_index():
    collection_review = get_all_event_name_with_review()
    df = init_table()
    events_names = [i[0] for i in collection_review]
    events_index = [i[1] for i in collection_review]
    events_list = list(events_data.keys())
    events_with_problem = []
    for i in range(len(events_names)):
        if events_list.index(events_names[i]) != events_index[i]:
            events_with_problem += [events_names[i]]
    for i in range(len(events_with_problem)):
        true_index = events_list.index(events_with_problem[i])
        cur.execute('UPDATE review set event_index = ? WHERE event_name = ?',(true_index, events_with_problem[i]))
        db.commit()



