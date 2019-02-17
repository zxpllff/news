#!/usr/bin/python
# -*- coding: UTF-8 -*-

import  requests
from bs4 import BeautifulSoup
import re
import time, datetime
import  json
import codecs
# 导入MySQL驱动:
import mysql.connector

#python2.6
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8') 
  
def table_exists(con,table_name):        #这个函数用来判断表是否存在
    sql = "show tables;"
    con.execute(sql)
    tables = [con.fetchall()]
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
    if table_name in table_list:
        return 1        #存在返回1
    else:
        return 0        #不存在返回0


def data_callback(lists):
    return lists

def get_articles(listUrl):              
    headers = {
            'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'Keep-Alive',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    payload = {'wd': 'GitHub'}  # 搜索的关键字是GitHub
    html = requests.get(listUrl, params=payload, headers=headers)

    JSONP = html.text.encode('utf-8')
    try:
        lists = eval(JSONP)
    except:
        return
    # print(lists)
    for index,value in enumerate(lists):
        articleUrl = value['docurl']

        # 注意把password设为你的root口令:
        conn = mysql.connector.connect(user='root', password='root', database='laravel', use_unicode=True)
        cursor = conn.cursor()
        isexist = table_exists(cursor,'articles')

        if isexist != 1:
            # 创建user表:
            cursor.execute('create table articles (id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT "主键", title varchar(100) NOT NULL comment "标题", type_id int(10) NOT NULL comment "类型id", content varchar(200) NULL comment "简介", imgs varchar(200) NULL comment "图片", text text NULL comment "内容", published_time timestamp NULL comment "发布时间", resoure varchar(255) NULL comment "来源", url varchar(100) NOT NULL comment "来源url", create_time timestamp NOT NULL comment "创建时间")')

        cursor.execute('select * from articles where url = %s', (articleUrl,))
        rest = cursor.fetchall()
        if len(rest):
            continue
        else:
            pass
        if value['imgurl']=='':
            articlImg = ''
        else:
            articlImgArr=[value['imgurl']]
            articlImg = json.dumps(articlImgArr)
        headers = {
                'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection' : 'Keep-Alive',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        payload = {'wd': ''}
        response = requests.get(articleUrl, params=payload, headers=headers)

        res = r'<div.*?epContentLeft">.*?<h1>(.*?)</h1>.*?<div.*?post_time_source">[\s]*?(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})\s*?.*?<a.*?href=.*?">(.*?)<\/a>.*?</div>.*?(<div class="post_text" id="endText".*?)[\s]*?<div class="post_btmshare">'
        items = re.findall(res, response.text, re.S | re.M)
        for item in items:
            print(item[0])

        now = datetime.datetime.now()
        create_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # 插入一行记录，注意MySQL的占位符是%s:
        cursor.execute('insert into articles (title, type_id, text, imgs, published_time, resoure, url, create_time) values ( %s, %s, %s, %s, %s, %s, %s, %s)', [item[0], 1, item[3], articlImg, item[1], item[2], articleUrl, create_time])
        cursor.rowcount
        # 提交事务:
        conn.commit()
        cursor.close()

#listUrl = 'http://temp.163.com/special/00804KVA/cm_guonei.js?callback=data_callback'
print ('————————程序开始————————')
i = 1
while i>=1 and i <= 3:
    if i==1:
        num = ''
    elif i==10:
        num = '_10'
    else:
        num = '_0' + str(i)
    listUrl = 'http://temp.163.com/special/00804KVA/cm_guonei%(num)s.js?callback=data_callback' % {'num':num}
    print('————————文章列表————————' + listUrl)
    get_articles(listUrl)
    i = i + 1
else:
   print ('————————程序结束————————')
