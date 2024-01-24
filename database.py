import json
from typing import Optional

import pymysql


class UseDateBase:
    def __init__(self, config: dict):
        self.config = config
        self.cursor = None

    def __enter__(self) -> Optional[pymysql.cursors.Cursor]:
        try:
            self.con = pymysql.connect(**self.config)
            self.con.begin()
            self.cursor = self.con.cursor()
            if self.cursor is None:
                raise ValueError('Курсор не создан')
            return self.cursor
        except pymysql.err.OperationalError as err:
            if err.args[0] == 2003:
                print('Неверный формат host\n')
            if err.args[0] == 1045:
                print('Неверное имя пользователя или пароль\n')
            if err.args[0] == 1049:
                print('Не найдена база данных\n')
            print(err.args[1])
            return err
        except TypeError as err:
            print('Неверный формат конфига\n')
            return err

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_val:
            if exc_val.args[0] == 1146:
                print('Таблицы не существует\n')
            if exc_val.args[0] == 1064:
                print('Неверный синтаксис запроса\n')
            if exc_val.args[0] == 1054:
                print('Столбец не найден\n')
            return False
        if self.con and self.cursor:
            if exc_type:
                self.con.rollback()
            else:
                self.con.commit()
            self.cursor.close()
            self.con.close()
        return True


def correct(config, sql):
    with UseDateBase(config) as cursor:
        cursor.execute(sql)
        res = cursor.fetchall()
    return res


def get_db_config() -> dict:
    try:
        with open("configs/config.json", 'r') as config:
            db_config = json.load(config)
            a = 5
    except FileNotFoundError as err:
        if err.args[0] == 2:
            print('Такой файл не найден\n')
        print(err.args[1])
        exit(0)
    except json.decoder.JSONDecodeError:
        print('Не является файлом .json\n')
        exit(0)

    return db_config


def work_with_db(config: dict, sql: str) -> list:
    with UseDateBase(config) as cursor:
        cursor.execute(sql)

        schema = [column[0] for column in cursor.description]

        result = []

        for string in cursor.fetchall():
            result.append(dict(zip(schema, string)))
        return result


def make_request(config: dict, sql: str) -> list:
    items = []
    with UseDateBase(config) as cursor:
        cursor.execute(sql)

        schema = [column[0] for column in cursor.description]

        for item in cursor.fetchall():
            items.append(dict(zip(schema, item)))
        return items


def make_update(config: dict, sql: str) -> bool:
    success = False
    with UseDateBase(config) as cursor:
        if cursor is None:
            raise ValueError('is None')
        cursor.execute(sql)
        success = True
    return success


def select_dict(config: dict, _sql: str):
    with UseDateBase(config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        else:
            cursor.execute(_sql)
            result = cursor.fetchall()
            if result:
                schema = [item[0] for item in cursor.description]  # description is a set, here are names etc
                result_dict = [dict(zip(schema, product)) for product in result]
                return result_dict
            else:
                return None


def call_proc(config: dict, proc_name: str, *args):
    with UseDateBase(config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        param_list = []
        for arg in args:
            param_list.append(arg)
        res = cursor.callproc(proc_name, param_list)
        return res


def insert_into_db(config, _sql):
    with UseDateBase(config) as cursor:
        cursor.execute(_sql)
        return cursor.lastrowid


def multi_insert(config, sql):
    res = False
    with UseDateBase(config) as cursor:
        for _sql in sql:
            cursor.execute(_sql)
        res = True
    return res
