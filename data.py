#-*-coding:utf-8-*-

import requests
import re
import pickle
import traceback
import math
import threading
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36",
    'Upgrade-Insecure-Requests':'1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'bangumi.tv'
}

def getItem(sess,url):
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

def getUrl(sess,url,domin):
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

def collectsubject():
    failpage = []
    failsubject = []
    sess = requests.session()
    with open('bgm.dat','wb') as f:
        for i in range(1,205):
            animelist = 'https://bangumi.tv/anime/browser?sort=rank&page=%d' % i
            l = getUrl(sess,animelist,'https://bangumi.tv')
            if l:
                ll = []
                for j in l:
                    item = getItem(sess,j)
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

def collectUser(sess,user):
    combine = lambda x,y: [(x[i],y[i]) for i in range(0,len(x) if len(x)<=len(y) else len(y))]
    currentuser = [user]#初始化用户id
    for type in ['/wish','/collect','/do','/on_hold','/dropped']:
        page = 0
        total = 1
        url = 'https://bangumi.tv/anime/list/%d%s'% (user,type)
        while page <= total:
            page += 1
            loop = 0
            while loop < 3:#如果获取失败则循环三次，如果还是失败那就放弃这个页面
                try:
                    s = sess.get(url+'?page=%d'% page,headers=headers,timeout = 30)
                    loop = 10
                except Exception:
                    # traceback.print_exc()
                    sess.close()
                    time.sleep(60)
                    loop+=1
            if loop != 10:
                print("fetch error")
                continue
            s.encoding = 'utf-8'
            if page == 1:
                watched = re.search(r'<span>看过\s*\((\d+)\)</span>',s.text)
                itemcount = re.findall(r'<a href="/subject/(\d+)" class="l">',s.text)
                if watched and itemcount:
                    watched = int(watched.group(1))
                    total = math.ceil(watched/len(itemcount))
                    url = s.url
                else:
                    break
            rate = re.findall(r'<a href="/subject/(\d+)" class="l">.+\n.+\n.+\n.+\n.+\n.+\n.+\n.+\n<span class="sstars([.\d]+) starsinfo">',s.text)
            currentuser+=rate
    return currentuser

def collectUserToFile(file,start,end):
    sess = requests.session()
    with open(file,'ab') as f:
        for i in range(start,end):#目前看来有440000的用户
            user = collectUser(sess,i)
            if len(user)>3:
                print('Thread %s collectUser %d,stars anime %d' % (threading.current_thread().getName(), i, len(user) - 1))
                pickle.dump(user,f)

# threading.Thread(target=collectUser,args=('1-100000',1,100000))
UserCount = 440000
ThreadCount = 10
threads = []
for i in range(1,ThreadCount+1):
    file = 'BangumiUser%d.dat' %(i)
    start = int((i-1)*UserCount/ThreadCount +1)
    end = int(i*UserCount/ThreadCount)
    threads.append(threading.Thread(target=collectUserToFile,name=str(i),args=(file,start,end)))

for i in threads:
    i.start()
for i in threads:
    i.join()