#-*-coding:utf-8-*-

import pickle
import numpy as np
import requests
import json
import time

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
    for user in data:
        for i in user[1:]:
            mat[count][subject[i[0]]] = int(i[1])
        count+=1
    return mat


def caculate(usertb,subject,user):
    index = []
    curuser = []
    #生成用户的向量
    for item in user.items():
        index.append(subject[item[0]])
        curuser.append(item[1])
    curuser = np.array(curuser,dtype=np.float64)
    #生成所有用户对应当前用户的矩阵
    temptb = usertb[:,[subject[i[0]] for i in user.items()]]
    # dis = 1/(1+np.linalg.norm(temptb-curuser,axis = -1))
    dis = np.zeros((len(temptb),))
    for i in range(0,len(temptb)):
        if sum(temptb[i]) != 0:
            try:
                dis[i] = 0.5 + 0.5 * np.corrcoef(temptb[i],curuser, rowvar = False)[0][1]
            except Exception:
                print(i)
            # print(i)
        else:
            dis[i] = 0
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
usertb = genUserTable(data,subject)

def genlist(zhuhao,num):
    sim = 5
    dis = caculate(usertb,subject,zhuhao)
    simuser = genmaxlist(dis,30)
    # simuser = np.nan_to_num(simuser)
    # print(simuser)
    a = np.zeros((len(subject),),dtype=np.float64)
    for user in simuser[:sim]:
        a += usertb[user[0]]*user[1]
    a = a/sim
    xx = []
    for i in range(0,len(a)):
        if not resubject[i] in zhuhao:
            xx.append((resubject[i],a[i]))
    ff = sorted(xx,key = lambda s:s[1],reverse=True)
    t2 = time.time()
    for i in ff[:num]:
        print('%s  simlarity:%f'%(getName(i[0]),i[1]))

guzi = {'100449':9,'211936':7,'91986':7,'793':6,'231722':6,'112146':6}
yaoyao = {'9717':9.7,'10639':9.7,'10380':9.6,'88287':9.4,'1428':9.5,'140001':9.3,'10440':9,'172498':6,'204855':6}
zhuhao = {'112146':8,'5436':9,'211936':8,'214265':8,'110467':10,'805':9}
genlist(zhuhao,20)