#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import MySQLdb

def db_con():
    db = MySQLdb.connect('localhost','admin','admin','xc_net')
    cur = db.cursor()
    return cur

def db_login(username,password):
    db = MySQLdb.connect('localhost', 'admin', 'admin', 'xc_net',charset='utf8')
    cur = db.cursor()
    sql = "select * from app_login where username='%s' and password='%s'" % (username,password)
    try:
        cur.execute(sql)
        data = cur.fetchone()
        # print cur.fetchone()
        # print data
        print data
        if data:
            user = {}
            user['username'] = data[1]
            user['password'] = data[2]
            user['nickname'] = data[3]
            user['auth'] = data[4]
            print user['auth']
            return {'status':True,'data':[user]}

        else:
            return {'status':False,'data':u'认证失败-账户密码错误'}
    except:
        return {'status':False,'data':u'认证失败-未知错误'}
    db.close()

#从cnu扫描数据库中筛选出合格或者不合格的cnu
def db_get_cnudatas_from_database(address, num):
    db = MySQLdb.connect('localhost', 'admin', 'admin', 'xc_net',charset='utf8')
    cur = db.cursor()
    if num == 0:
        sql = "SELECT * from cnu_total_0607 WHERE ADDRESS LIKE '%%%s%%' ORDER BY ADDRESS ASC;" % address
    elif num == 1:
        sql = "SELECT * from cnu_total_0607 WHERE ADDRESS LIKE '%%%s%%'  AND (AVG_RX_RSSI > 60 OR AVG_RX_RSSI < 43 ) ORDER BY ADDRESS ASC;" % address
    else:
        sql = "SELECT * from cnu_total_0607 WHERE ADDRESS LIKE '%%%s%%'  AND (AVG_RX_RSSI > 60 OR AVG_RX_RSSI < 43 ) ORDER BY ADDRESS ASC;" % address
    try:
        cur.execute(sql)
        infos = cur.fetchall()
        if infos:
            data = []
            for info in infos:
                data.append(list(info))
            return {'status': True, 'data': data}
        else:
            return {'status': False, 'data': u'未查询到数据'}
    except:
        return {'status':False,'data':u'未知错误'}
    finally:
        db.close()


def db_get_wocip_from_cbat(pon, table_name):
    db = MySQLdb.connect('localhost', 'admin', 'admin', 'xc_net',charset='utf8')
    cur = db.cursor()
    sql = "SELECT WOC_IP_1 from %s WHERE PON ='%s';" % (table_name, pon)
    try:
        cur.execute(sql)
        infos = cur.fetchall()
        print infos
        if infos:
            data = []
            for info in infos:
                print info
                print list(info)
                data = data + list(info)
            return {'status': True, 'data': data}
        else:
            return {'status': False, 'data': u'cbat表:未查询到数据'}
    except Exception,e:
        print e
        return {'status':False,'data':u'cbat表:未知错误'}
    finally:
        db.close()

if __name__ == "__main__":
    print db_get_wocip_from_cbat('epon-onu_0/2/2:2','cbat_qjl')
    a=['q']
    b=['b']
    print a+b