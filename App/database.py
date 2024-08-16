import sqlite3 as sq

db = sq.connect('BotData/km_tg.db')
cur = db.cursor()

async def db_start():
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER)
                ''')
    cur.execute("CREATE TABLE IF NOT EXISTS admins ("
                "login TEXT NOT NULL, "
                "password TEXT NOT NULL)")
    cur.execute('''CREATE TABLE IF NOT EXISTS review(
                event_review_tg_id INTEGER,
                event_index INTEGER,
                event_name TEXT,
                event_review TEXT,
                event_review_mark INTEGER)
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS authorized_admins(
                tg_id INTEGER,
                date TEXT,
                now_admin INTEGER)
                ''')
    db.commit()

async def cmd_start_db(user_id):
    user = cur.execute("SELECT * FROM users WHERE tg_id == {key}".format(key=user_id)).fetchone()
    if not(user):
        cur.execute("INSERT INTO users (tg_id) VALUES ({key})".format(key=user_id))
        db.commit()

async def users_list():
    cur.execute('SELECT * FROM users')
    userl = cur.fetchall()
    return userl

async def admins_list():
    cur.execute('SELECT tg_id FROM authorized_admins WHERE now_admin == 1')
    adminsl = cur.fetchall()
    list_admins = [adminsl[i][0] for i in range(len(adminsl)) ]
    return list_admins

async def add_event_review(event_review_tg_id, event_index, event_name, event_review, event_review_mark):
    name = cur.execute('SELECT event_review_tg_id FROM review WHERE event_review_tg_id = ? and event_name = ?',(event_review_tg_id, event_name)).fetchone()

    if not(name):
        cur.execute("INSERT INTO review (event_review_tg_id,event_index, event_name, event_review, event_review_mark) VALUES(?,?,?,?,?)",
                    (event_review_tg_id,event_index,event_name,event_review,event_review_mark))
        db.commit()
        return True
    else:
        return False

async def avg_mark_review(event_name):
    name = cur.execute('SELECT event_name FROM review WHERE event_name = ?',(event_name,)).fetchone()
    if name:
        avg_mark = int((cur.execute("SELECT avg(event_review_mark) as avg_mark FROM review WHERE event_name == ?",
                                    (event_name,))).fetchone()[0])
        return avg_mark
    else:
        return 0

async def count_review(event_name):
    name = cur.execute('SELECT event_name FROM review WHERE event_name = ?', (event_name,)).fetchone()
    if name:
        count = int((cur.execute("SELECT count(event_name) as count FROM review WHERE event_name == ?",
                                 (event_name,))).fetchone()[0])
        return count
    else:
        return 0

async def look_review(event_name):
    name = cur.execute('SELECT event_name FROM review WHERE event_name = ?', (event_name,)).fetchone()
    if name:
        review_colletion = (cur.execute("SELECT event_review, event_review_mark FROM review WHERE event_name LIKE ?",(event_name,))).fetchall()
        return review_colletion
    else:
        return [()]

