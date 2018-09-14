#-*-coding:utf-8-*-

import pickle
import numpy as np
import time

with open('anime.dat','rb') as f:
    dic = pickle.load(f)
    redic = pickle.load(f)
    alldata = pickle.load(f)

def getAlltag(items):
    l = []
    for item in items:
        for i in range(0,len(item['tag'])):
            if item['tag'][i] > 0:
                l.append(i)
    return l

zhuhao = [['100449',5],['211936',5],['230176',2],['225843',1],['236900',5],['110467',5],['79227',5],['126173',5],['5436',5]]
#zhuhao = [['112146',5],['79227',5],['187276',4]]

items = []

for item in alldata:
    for i in zhuhao:
        if i[0] == item['id']:
            items.append(item)

total = 0
for x in zhuhao:
    total+=x[1]
avg = total/5/len(zhuhao)

alltag = getAlltag(items)
usertag = [0 for i in range(0,len(dic))]
for i in alltag:
    count = 0
    tagscore = 0
    for j in range(0,len(items)):
        if items[j]['tag'][i] > 0:
            count+=1
            tagscore+=(zhuhao[j][1]/5-avg)
    tagscore = tagscore/count
    usertag[i] = tagscore
print(usertag)

usertag = np.array([usertag])
ll = []
for item in alldata:
    itemtag = np.array(item['tag'])
    value = np.dot(usertag, itemtag) / (np.linalg.norm(usertag) * (np.linalg.norm(itemtag)))
    item['sim'] = value
def sim(s):
    return s['sim']
ff = sorted(alldata,key = sim,reverse=True)
for i in ff:
    i['tag'] = None
    print(i)
    time.sleep(0.5)