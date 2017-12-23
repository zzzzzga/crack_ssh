#!/usr/bin/python3
# coding: utf-8

from databaseHelper import DatabaseHelper

if __name__ == '__main__':
  dbHelper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')
  numCount = dbHelper.queryOne('select count(*) as num from password')['num']
  with open('password.txt', 'r') as f:
    for line in f:
      if (numCount == 0):
        try:
          line = line.strip('\n').strip()
          dbHelper.nonQuery('insert into password(val) value(%s)', (line,))
        except Exception as e:
          print(str(e))
      else:
        numCount -= 1