#!/usr/bin/python3
# coding: utf-8

from databaseHelper import DatabaseHelper
import sys

if __name__ == '__main__':
  if len(sys.argv) <= 1:
    print('usage ' + __file__ + ' <password.txt>')
    exit
  filename = sys.argv[1]
  dbHelper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')
  # numCount = dbHelper.queryOne('select count(*) as num from password')['num']
  with open(filename, 'r') as f:
    for line in f:
      '''
      if (numCount == 0):
        try:
          line = line.strip('\n').strip()
          dbHelper.nonQuery('insert into password(val) value(%s)', (line,))
        except Exception as e:
          print(str(e))
      else:
        numCount -= 1
      '''
      try:
        line = line.strip('\n').strip()
        dbHelper.nonQuery('insert into password(val) value(%s)', (line,))
      except Exception as e:
        print(str(e))
    
    with open('addPassword.log', 'a') as f:
      f.write('%s finish \n' % filename)
      f.flush()

