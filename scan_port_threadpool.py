#!/usr/bin/python3

'''
主要是一个端口发现的线程池
'''
from threading import *
import time
import nmap

class ScanPortParam:
    def __init__(self, host, port):
        self.host = host
        self.port = port

class ScanPortThreadPool:
    def __init__(self, count):
        self._count = count
        self._threadParam = []
        self.hostList = []
        self._threadLock = Semaphore(value=1)
        self.hostListLock = Semaphore(value=1)

    def addScanPortThreadParam(self, threadParam):
        self._threadLock.acquire()
        self._threadParam.append(threadParam)
        self._threadLock.release()

    def startThreadPool(self):
        for i in range(self._count):
            print('create thread %d'%i)
            t = Thread(target=self.workThread)
            t.start()

    def workThread(self):
        while True:
            time.sleep(1)
            try:
                self._threadLock.acquire()
                param = self._threadParam.pop()
                if isinstance(param, ScanPortParam):
                    try:
                        scanner = nmap.PortScanner()
                        result = scanner.scan(param.host, param.port)
                        state = result['scan'][param.host]['tcp'][int(param.port)]['state']
                        if state == 'open':
                            self.hostListLock.acquire()
                            self.hostList.append(param.host)
                            self.hostListLock.release()
                    except Exception as e:
                        print(e)
                    
            except:
                pass
            finally:
                self._threadLock.release()

if __name__ == '__main__':
    scanPort = ScanPortThreadPool(5)
    scanPort.addScanPortThreadParam(ScanPortParam('192.168.1.102', '22'))
    scanPort.addScanPortThreadParam(ScanPortParam('192.168.1.101', '22'))
    scanPort.startThreadPool()
    while True:
        print(scanPort.hostList)
        time.sleep(1)
