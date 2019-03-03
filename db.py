#!/usr/bin/env python
import yaml
import pdb
import time
import sqlite3
from sqlite3 import Error

class Db:
    def __init__(self):
        cfg = self.get_config()
        self.db_file = cfg.get('db').get('location')

    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_file)
            return conn

        except Error as e:
            print(e)
            return None
        finally:
            return None

    def create_db(self):
        try:
            conn = sqlite3.connect(self.db_file)
            try:
                with open('.schema') as f:
                    c = conn.cursor()
                    c.execute(f.read())
            except Error as e:
                print(e)

        except Error as e:
            print(e)
        finally:
            conn.close()

    def get_config(self):
        with open("config.yaml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        return cfg

if __name__ == '__main__':
    db = Db()
    db.create_db()

