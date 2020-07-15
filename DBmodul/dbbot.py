import sqlite3
import os
import sys


def command(func):
    def wrapper(self, *args, **kwargs):
        cursor = self._get_connection().cursor()              # открываем курсор
        res = func(self, *args, cursor = cursor, **kwargs)    # выполняем функцию
        self._get_connection().commit()                       # коммит при необходимости
        cursor.close()                                        # закрываем курсор
        return res
    return wrapper


class DbHelper():
    def __init__(self, db_name: str):
        self.db_name = db_name
        self._connection = None                                # connection object

    def _get_connection(self):
        if not self._connection:                               # ленивая инициализация соединения
            self._connection = sqlite3.connect(self.db_name, check_same_thread=False)
        return self._connection

    def __del__(self):
        if self._connection:                                    # закрытие соединения при удалении объекта как пример безопасной работы
            self._connection.close()

    @command
    def init_db(self, cursor, force: bool=False):
        if force:
            cursor.execute('DROP TABLE IF EXISTS catalog')
            cursor.execute('DROP TABLE IF EXISTS condition')
            self._connection.commit()

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS catalog (
                       id              INTEGER PRIMARY KEY,
                       user_id         INTEGER NOT NULL,
                       format          VARCHAR(5),
                       audio_file      BLOB, 
                       count_user_file INTEGER NOT NULL,
                       name_audio      TEXT)''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS condition (
                        id              INTEGER PRIMARY KEY,
                        user_id         INTEGER NOT NULL,
                        status          VARCHAR(7))''')

    @command
    def add_audio_message(self, cursor, user_id, format, audio_file, count_user_file, name_audio):
        cursor.execute('INSERT INTO catalog (user_id, format, audio_file, count_user_file, name_audio) VALUES (?,?,?,?,?)',
                       (user_id, format, audio_file, count_user_file, name_audio))

    @command
    def verify_user(self, cursor, user_id):
        res = cursor.execute('SELECT COUNT(user_id) FROM catalog WHERE user_id=?',(user_id,))
        return res.fetchone()

    @command
    def get_one_audio(self, cursor, user_id):
        res = cursor.execute('SELECT user_id, format, count_user_file, audio_file FROM catalog WHERE user_id=? LIMIT 1',(user_id,))
        return res.fetchone()

    @command
    def delete_all_catalog(self, cursor):
        cursor.execute('DELETE FROM catalog')

    @command
    def add_status(self, cursor, user_id, status):
        cursor.execute('INSERT INTO condition (user_id, status) VALUES (?,?)',
                       (user_id, status))

    @command
    def change_status(self, cursor, status, user_id):
        cursor.execute('UPDATE condition SET status=? WHERE user_id=?', (status, user_id))

    @command
    def get_status(self, cursor, user_id):
        result = cursor.execute('SELECT status FROM condition WHERE user_id=?', (user_id,)).fetchone()
        print(result)
        if result == None: return ('start')
        else: return result

    @command
    def delete_status(self, cursor, user_id):
        cursor.execute('DELETE FROM condition WHERE user_id=?', (user_id,))

    @command
    def verify_status(self, cursor, user_id):
        res = cursor.execute('SELECT COUNT(user_id) FROM condition WHERE user_id=?', (user_id,))
        return res.fetchone()




#if __name__=='__main__':
#
#    bd=DbHelper(os.path.abspath('../DBmodul/audiodb.db'))
#    bd.init_db()
#    res =bd.get_one_audio(user_id=479715437)
#
#    print(res)
#    with open(os.path.abspath('../fileaudio/' +'from_user' +f'{res[0]}'+'audio_message'+f'{res[2]}'+'.'+f'{res[1]}'), 'wb') as new_audio:
#        new_audio.write(res[3])


    #files = os.listdir(os.path.abspath('../model'))
    #myxml = sorted(tuple(filter(lambda x: x.endswith('.xml'), files)), reverse=True)