import sqlite3

from main import init_db

DATABASE = 'sqlite.db'


def db_init(path):
    """
    Initialize the database
    :param path: SQL file path
    :return:
    """
    conn = sqlite3.connect(DATABASE)
    with open(path) as f:
        conn.executescript(f.read())
    conn.close()


if __name__ == '__main__':
    db_init('init_db.sql')
