#!/usr/bin/python3
# coding: utf-8
'''
主要是一个端口发现的线程池
'''
from threading import *
import time
import nmap
from databaseHelper import DatabaseHelper
import datetime
import socket
import struct

class ScanPortWorkInfo:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.dbHelper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')

  def workThread(self, threadLock):
    try:
      scanner = nmap.PortScanner()
      result = scanner.scan(self.host, self.port)
      state = result['scan'][self.host]['tcp'][int(self.port)]['state']
      if state == 'open':
        self._saveWorkInfo(state)
    except Exception as e:
      print('[-] Error: ' + str(e))
    finally:
      threadLock.release()
    
    def _saveWorkInfo(self, state):
      sql = 'insert into crackResult(host, state, scanTime) value(%s, %s, %s)'
      param = (self.host, state, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
      self.dbHelper.nonQuery(sql, param)

class ScanPortThreadPool:
  '''
  主要维护线程池，进行任务调配
  '''
  def __init__(self, count):
    self.threadLock = BoundedSemaphore(value=count)
    self._scheduler = ScanPortScheduler()

  def startThreadPool(self):
    while True:
      self.threadLock.acquire()
      # 开启一个线程去处理
      workInfo = self._scheduler.getNextWork()
      if workInfo == None:
        self.threadLock.release()
        continue
      t = Thread(target=workInfo.workThread, args=(self.threadLock,))
      t.start()

class ScanPortScheduler:
  def __init__(self):
    self.dbHelper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')
  
  def getNextWork(self):
    dictResult = self.dbHelper.queryOne('select currentAddr from schedule')
    if (dictResult == None):
      self.dbHelper.nonQuery('insert into schedule(currentAddr) values(%s)', ('0.0.0.0',))
      return None
    host = dictResult['currentAddr']
    int_ip = socket.ntohl(struct.unpack('I', socket.inet_aton(host))[0])
    int_ip += 1
    nextHost = socket.inet_ntoa(struct.pack('I',socket.htonl(int_ip)))
    self.dbHelper.nonQuery('update schedule set currentAddr = %s', (nextHost,))
    return ScanPortWorkInfo(host, 22)

if __name__ == '__main__':
  scanPort = ScanPortThreadPool(5)
  scanPort.startThreadPool()
