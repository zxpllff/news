#!/usr/bin/python
#!coding=utf-8
import flask
import json
# 导入MySQL驱动:
import mysql.connector
import collections
import datetime

#python2.6
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')   

class DateEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj,date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self,obj)

server=flask.Flask(__name__)#__name__代表当前的python文件。把当前的python文件当做一个服务启动
@server.route('/index',methods=['get','post'])
def index():
    res={'msg':'调试成功','msg_code':0}
    return json.dumps(res,ensure_ascii=False)

@server.route('/getTypeList',methods=['get','post'])
def getTypeList():
    conn = mysql.connector.connect(user='root', password='root', database='laravel', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute('select * from article_type')
    rows = cursor.fetchall()
    # 关闭Cursor和Connection:
    cursor.close()
    conn.close()
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['type'] = row[1]
        objects_list.append(d)
        
    res={'msg':'成功','msg_code':0,'data':objects_list}
    return json.dumps(res, ensure_ascii=False, cls=DateEncoder)

@server.route('/getList',methods=['get','post'])
def getList():
    typeId=int(flask.request.values.get('typeId'))
    page=int(flask.request.values.get('page'))
    pageSize=int(flask.request.values.get('pageSize'))
    offset=(page-1)*pageSize
    if page and pageSize:
        # # 运行查询:
         # 注意把password设为你的root口令:
        conn = mysql.connector.connect(user='root', password='root', database='laravel', use_unicode=True)
        cursor = conn.cursor()
        cursor.execute('select * from articles where type_id=%s order by published_time desc limit %s, %s', (typeId,offset,pageSize,))
        rows = cursor.fetchall()
        # 关闭Cursor和Connection:
        cursor.close()
        conn.close()
        objects_list = []
        for row in rows:
            d = collections.OrderedDict()
            d['id'] = row[0]
            d['title'] = row[1]
            d['type'] = row[2]
            d['content'] = row[3]
            if row[4]=='':
                d['imgs'] = []
            else:
                d['imgs'] = json.loads(row[4])
            d['published_time'] = row[6]
            d['resoure'] = row[7]
            d['create_time'] = row[9]
            objects_list.append(d)
         
        res={'msg':'成功','msg_code':0,'data':objects_list}
        return json.dumps(res, ensure_ascii=False, cls=DateEncoder)

@server.route('/getDetail',methods=['get','post'])
def getDetail():
    id=int(flask.request.values.get('uid'))
    print(id)
    if id:
        # # 运行查询:
         # 注意把password设为你的root口令:
        conn = mysql.connector.connect(user='root', password='root', database='laravel', use_unicode=True)
        cursor = conn.cursor()
        cursor.execute('select * from articles where id = %s', (id,))
        rows = cursor.fetchall()
        # 关闭Cursor和Connection:
        cursor.close()
        conn.close()
        for row in rows:
            d = collections.OrderedDict()
            d['id'] = row[0]
            d['title'] = row[1]
            d['type'] = row[2]
            d['content'] = row[3]
            if row[4]=='':
                d['imgs'] = []
            else:
                d['imgs'] = json.loads(row[4])
            d['text'] = row[5]
            d['published_time'] = row[6]
            d['resoure'] = row[7]
            d['create_time'] = row[9]
         
        res={'msg':'成功','msg_code':0,'data':d}
        return json.dumps(res, ensure_ascii=False, cls=DateEncoder)
    else:
        res={'msg':'失败','msg_code':0,'data':{}}
        return json.dumps(res, ensure_ascii=False)

server.run(port=8000,debug=True,host='0.0.0.0')
