#-*-coding:utf-8-*-

import urllib
import os
import requests
import re
import pickle
import traceback
from lxml import etree
import time
import datetime
import math
import sqlite3

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36",
    'Upgrade-Insecure-Requests':'1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'bangumi.tv'
}
sess = requests.session()
def getItem(url):
    try:
        s = sess.get(url, headers=headers,timeout=30)
    except:
        traceback.print_exc()
        return None
    s.encoding = 'utf-8'
    id = re.search(r'(\d+)',url)
    title = re.search(r'<title>(.+) \| Bangumi 番组计划</title>', s.text)
    score = re.search(r'<span class="number" property="v:average">([.\d]+)</span>', s.text)
    tag = re.search(r'标注为</h2>\n(.+)', s.text)
    rank = re.search(r'Bangumi Anime Ranked:</small><small class="alarm">#(\d+)</small></div>', s.text)
    popularity = re.search(
        r' <div class="chart_desc" style=""><small class="grey"><span property="v:votes">(\d+)</span> votes</small></div>',
        s.text)
    item = None
    if id and tag and rank and score and title and popularity:
        tag = re.findall(r'<span>(.*?)</span> <small class="grey">(\d+)</small>', tag.group(1))
        item = {'id': id.group(1), 'title': title.group(1), 'score': score.group(1), 'rank': rank.group(1),
                'popularity': popularity.group(1), 'tag': tag,'url':url}
    return item

def getUrl(url,domin):
    try:
        s = sess.get(url,headers=headers,timeout=30)
    except:
        traceback.print_exc()
        return None
    s.encoding = 'utf-8'
    l1 = re.findall(r'/subject/\d+',s.text)
    if l1:
        l2 = []
        for i in l1:
            if not i in l2:
                l2.append(i)
        l1 = [domin+x for x in l2]
    return l1

failpage = []
failsubject = []

with open('bgm.dat','wb') as f:
    for i in range(1,205):
        animelist = 'https://bangumi.tv/anime/browser?sort=rank&page=%d' % i
        l = getUrl(animelist,'https://bangumi.tv')
        if l:
            ll = []
            for j in l:
                item = getItem(j)
                if item:
                    ll.append(item)
                else:
                    failsubject.append(item)
            if ll != []:
                pickle.dump(ll,f)
        else:
            failpage.append(animelist)
        print('page %d is done'% i)

with open('failpage.txt','wb') as f:
    pickle.dump(failpage,f)

with open('failsub.txt','wb') as f:
    pickle.dump(failsubject,f)