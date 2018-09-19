#-*-coding:utf-8-*-

import pickle
import numpy as np
import requests
import json
import time
import tensorflow as tf

def readData(filesource,start,end):
    data = []
    for i in range(start,end+1):
        file = '%s%d.dat' %(filesource,i)
        with open(file,'rb') as f:
            try:
                while True:
                    data.append(pickle.load(f))
            except Exception:
                pass
    return data

def genDic(data):
    resubject = {}  # {index:subject}
    subject = {}  # {subject:index}
    count = 0
    for user in data:
        for sub in user[1:]:
            if not sub[0] in subject:
                subject[sub[0]] = count
                resubject[count] = sub[0]
                count+=1
    return subject,resubject

#overlord 112146 ，月刊少女野崎君 100449 ，prpr 211936
#生成用户向量，好像挺费时的
def genUserTable(data,subject):
    n = len(subject)
    m = len(data)
    # vec = {}#{userid:animevector}
    # for user in data:
    #     u = [0 for i in range(0,veclen)]
    #     for i in user[1:]:
    #         u[subject[i[0]]] = int(i[1])
    #     vec[user[0]] = u
    mat = np.zeros((m,n))
    count = 0
    us = []
    for user in data:
        for i in user[1:]:
            mat[count][subject[i[0]]] = int(i[1])
        us.append(user[0])
        count+=1
    return mat,np.array(us)


def caculate(usertb,subject,user):
    index = []
    curuser = []
    caltime = [time.time()]
    #生成用户的向量
    for item in user.items():
        index.append(subject[item[0]])
        curuser.append(item[1])
    curuser = np.array(curuser,dtype=np.int8)
    caltime.append(time.time())
    #生成所有用户对应当前用户的矩阵
    temptb = usertb[:,[subject[i[0]] for i in user.items()]]
    caltime.append(time.time())
    dis = 1/(1+np.linalg.norm(temptb-curuser,axis = -1))
    caltime.append(time.time())
    for i in range(1,len(caltime)):
        print("time is %s"% (caltime[i] - caltime[i-1]))
    return dis

def genmaxlist(dis,n):
    index = dis.argsort()[-n:][::-1]
    l = []
    for i in index:
        l.append((i,dis[i]))
    return l

def getName(id):
    s = requests.get('https://api.bgm.tv/subject/'+id)
    data = json.loads(s.text)
    if 'name_cn' in data and data['name_cn'] != '':
        return data['name_cn']
    else:
        return data['name']

data = readData('userdata/BangumiUser',1,10)
subject,resubject = genDic(data)

usertb,us = genUserTable(data,subject)

t1 = time.time()
zhuhao = {}
zhuhao['112146'] = 8
zhuhao['100449'] = 9
zhuhao['211936'] = 9
zhuhao['110467'] = 10
zhuhao['102134'] = 9

dis = caculate(usertb,subject,zhuhao)
simuser = genmaxlist(dis,30)

a = np.zeros((len(subject),),dtype=np.float64)
for user in simuser[:10]:
    a += usertb[user[0]]*user[1]
a = a/10

xx = []
for i in range(0,len(a)):
    if not resubject[i] in zhuhao:
        xx.append((resubject[i],a[i]))

ff = sorted(xx,key = lambda s:s[1],reverse=True)
t2 = time.time()
print(t2-t1)
for i in ff[:20]:
    print('%s  subject:%s simlarity:%f'%(getName(i[0]),i[0],i[1]))