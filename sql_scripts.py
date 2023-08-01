import sqlite3
from config import *


def change_work_status(status):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE bot_status SET status = ? WHERE operation = ?", (status, "Work_Status",))

    conn.commit()
    conn.close()


def get_bot_work_status():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT status FROM bot_status WHERE operation = ?", ("Work_Status",))
    result = result.fetchone()[0]

    conn.close()

    return result

