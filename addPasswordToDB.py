#!/usr/bin/python3
# coding: utf-8

from databaseHelper import DatabaseHelper

if __name__ == '__main__':
  dbHelper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')
  with open('password.txt', 'r') as f:
    for line in f:
      try:
        line = line.strip('\n').strip()
        dbHelper.nonQuery('insert into password(val) value(%s)', (line,))
      except Exception as e:
        print(str(e))