#-*-coding:utf-8-*-

import pickle
import time
def taglist(l):
    dic = {}
    redic = {}
    count = 0
    for i in l:
        for item in i:
            for tag in item['tag']:
                if int(tag[1]) > 50:
                    if not tag[0] in dic:
                        dic[tag[0]] = count
                        redic[count] = tag[0]
                        count+=1
    return dic,redic

def genanimelist(dic,anilist):
    l = []
    for bunch in anilist:
        for item in bunch:
            newtag = [0 for i in range(0,len(dic))]
            for tag in item['tag']:
                if tag[0] in dic:
                    newtag[dic[tag[0]]] = int(tag[1])
            item['tag'] = newtag
            l.append(item)
    return l


l = []

with open('bgm.dat','rb')as f:
    try:
        while True:
            x = pickle.load(f)
            l.append(x)
    except Exception:
        pass

dic,redic = taglist(l)
all = genanimelist(dic,l)
# for i in all:
#     print(i)
#     time.sleep(0.2)
with open('anime.dat','wb') as f:
    pickle.dump(dic,f)
    pickle.dump(redic,f)
    pickle.dump(all,f)