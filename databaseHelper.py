#!/usr/bin/python3
# coding: utf-8

import pymysql

class DatabaseHelper:
  def __init__(self, host, db, user, password):
    self.config = {
      'host': host,
      'port': 3306,
      'user': user,
      'password': password,
      'db': db,
      'charset': 'utf8mb4',
      'cursorclass': pymysql.cursors.DictCursor
    }

  def getConnection(self):
    return pymysql.connect(**self.config)

  def queryOne(self, sql, param = None):
    '''
    单行查询
    '''
    result = None
    conn = self.getConnection()
    try:
      with conn.cursor() as cursor:
        cursor.execute(sql, param)
        result = cursor.fetchone()
      conn.commit()
    except Exception as e:
      raise e
    finally:
      conn.close()
    return result

  def queryAll(self, sql, param = None):
    '''
    查询所有
    '''
    result = None
    conn = self.getConnection()
    try:
      with conn.cursor() as cursor:
        cursor.execute(sql, param)
        result = cursor.fetchall()
      conn.commit()
    except Exception as e:
      raise e
    finally:
      conn.close()
    return result

  def pageQuery(self, sql, param = None, pageIndex = 1, pageSize = 10):
    '''
    分页查询
    '''
    sql = sql + ' limit {0}, {1}'.format(pageSize * (pageIndex-1), pageSize)
    return self.queryAll(sql, param)

  def nonQuery(self, sql, param = None):
    '''
    单条非查询语句
    '''
    num = 0
    conn = self.getConnection()
    try:
      with conn.cursor() as cursor:
        num = cursor.execute(sql, param)
    except Exception as e:
      conn.rollback()
      raise e
    else:
      conn.commit()
    finally:
      conn.close()
    return num > 0

  def nonQueryMany(self, sqls, params = None):
    '''
    多行非查询语句
    '''
    num = 0
    conn = self.getConnection()
    try:
      with conn.cursor() as cursor:
        for i in range(len(sqls)):
          if params != None and i < len(params):
            num += cursor.execute(sqls[i], params[i])
          else:
            num += cursor.execute(sqls[i])
    except Exception as e:
      conn.rollback()
      raise e
    else:
      conn.commit()
    finally:
      conn.close()
    return num > 0
    


if __name__ == '__main__':
  helper = DatabaseHelper('192.168.1.102', 'crack_ssh', 'root', '123456')
  print(helper.queryOne('select * from schedule where currentAddrId=%s', (1,)))
  print(helper.queryAll('select * from schedule where currentAddrId=%s', (1,)))
  print(helper.pageQuery('select * from schedule', pageIndex = 1))
  helper.nonQuery('update schedule set currentAddrId = %s', (1,))
  helper.nonQueryMany(['update schedule set currentAddrId = 1', 'update schedule set currentAddrId = 2', 'insert into schedule(currentAddrId) values(3)'])









