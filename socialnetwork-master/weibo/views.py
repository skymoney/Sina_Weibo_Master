# -*- coding: UTF-8 -*- 
# Create your views here.
from __future__ import division #true division
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils import simplejson

from WeiboEntity import WeiboEntity

import weiboconfig as config
import CN_Seg
import weiboLogin
import search
import client
import time
import mysqlconn
from getpincode import get_pincode
from tools import WeiboSpreadPath
import os

def home(request):
    return render_to_response('index.html')

def scene_market(request):
    return render_to_response('scene_market.html')
    
    
def cut(request):
    depict = ''
    if request.GET.has_key('depict'):
        depict = request.GET['depict']
    cn_seg = CN_Seg.CN_Seg.instance()
    if cn_seg._init ==0:
        cn_seg.init()
    return HttpResponse(simplejson.dumps(cn_seg.cut_filter(depict),ensure_ascii=False))

#marketing to own fans
def own_fans_filter(request):
    page = 1
    tags = ''
    if request.GET.has_key('tags'):
        tags = request.GET['tags']
    if request.GET.has_key('page'):
        page = int(request.GET['page'])
    
    tag_1 = tags.split(',')
    user_list = []
    
    #connect to the mysql db
    conn = mysqlconn.dbconn()
    cursor = conn.cursor()
    
    #get all fans
    sql = 'select * from user;'
    cursor.execute(sql)
    fans = cursor.fetchall()
    
    for fan in fans:
        user_dict = dict(id=fan[0], screenname=fan[1], sex=fan[2], address=fan[3], description=fan[4], followersnumber=fan[5],fansnumber=fan[6],messagesnumber=fan[7],birthday=fan[9],matchcount = 0,tag=[],tagstring='')
        cursor.execute('select tag from user_tag where uid ='+fan[0])
        tags = cursor.fetchall()
        for tag in tags:
            user_dict['tag'].append(tag[0])
        user_list.append(user_dict)
    for user in user_list:
        for tag in user['tag']:
            user['tagstring'] = user['tagstring'] + tag+' '
            for tag_target in tag_1:
                if tag.find(tag_target)!=-1:
                    user['matchcount']=user['matchcount']+1
    user_list.sort(lambda p1,p2:cmp(p1['matchcount'],p2['matchcount']),reverse=True)
    #未来在这里添加分页
    
    #close the cursor
    cursor.close()
    #disconnet the link to mysql db
    mysqlconn.dbclose(conn)
    
    return render_to_response('own_fans_filter.html', {'fans':user_list[0:9]})

#get the global relate users from sina weibo    
def realtime_keyword_matching(request):
    tags = ''
    if request.GET.has_key('tags'):
        tags = request.GET['tags']
    username = config.ACCOUNT
    pwd = config.PASSWORD
    WBLogin = weiboLogin.weiboLogin.instance()
    if(WBLogin.login(username, pwd)=='servertime_error'):
       print 'login failed. check out your network.'
    
    tag_2 = tags.split(',')
    user_list = []
    SerachPage=search.Search()
    weibo_list = []
    for tag in tag_2:
        weibo_list.extend(SerachPage.get_weibo(tag))
    user_list = []
    Client = client.Client.instance()
    if Client._init ==0:
       Client.init()
    for weibo in weibo_list:
        user_dict = dict(id='', screenname='', sex='', address='', description='', followersnumber='',fansnumber='',messagesnumber='',isverified=0,weibo='')
        user = Client.get_users_show(weibo.uid)
        user_dict['id'] = user.id
        user_dict['screenname'] = user.screen_name
        user_dict['sex'] = user.gender
        user_dict['address'] = user.location
        user_dict['description'] = user.description
        user_dict['followersnumber'] = user.friends_count
        user_dict['fansnumber'] = user.followers_count
        user_dict['messagesnumber'] = user.statuses_count
        user_dict['isverified'] = user.verified
        user_dict['weibo'] = weibo.text
        user_list.append(user_dict)
    user_list_final = []
    for user in user_list: 
        if user['isverified'] == 'True':
            user_list_final.append(user)
            user_list.remove(user)   
    user_list.sort(lambda p1,p2:cmp(p1['fansnumber'],p2['fansnumber']),reverse=True)
    for user in user_list:
        user_list_final.append(user)
        
    return render_to_response('realtime_keyword_matching.html', {'fans':user_list_final[0:9]})


#get the status of the fans, do some simple analysis
def status_fans(request):
    #connect to the mysql db
    conn = mysqlconn.dbconn()
    cursor = conn.cursor()

    #get sum of the fans
    sql = 'select count(*) from user;'
    cursor.execute(sql)
    sum = cursor.fetchone()[0]
    #get the female num
    sql = 'select count(*) from user where sex="f";'
    cursor.execute(sql)
    fnum = cursor.fetchone()[0]
    #the percentage of female
    fperc = round(fnum / sum, 4) * 100
    mperc = round((sum - fnum) / sum, 4) * 100
   
    #get the top10 area
    sql = 'select address, count(*) as num from user where address <> "其他" group by address order by num desc limit 0,10;'
    cursor.execute(sql)
    areadic = cursor.fetchall()
    areaname = []
    areanum = []
    for area in areadic:
        areaname.append(area[0].encode('utf8'))
        areanum.append(int(area[1]))

    thisyear = time.strftime('%Y',time.localtime(time.time())) #this year, like '2012'
    #get the num of each age interval
    sql = 'select count(*) from user where birthday > ' + thisyear + '-18;'
    cursor.execute(sql)
    age1 = cursor.fetchone()[0]
    sql = 'select count(*) from user where birthday <= ' + thisyear + '-18 and birthday >= ' + thisyear + '-24;'
    cursor.execute(sql)
    age2 = cursor.fetchone()[0]
    sql = 'select count(*) from user where birthday < ' + thisyear + '-24 and birthday >= ' + thisyear + '-34;'
    cursor.execute(sql)
    age3 = cursor.fetchone()[0]
    sql = 'select count(*) from user where birthday < ' + thisyear + '-34;'
    cursor.execute(sql)
    age4 = cursor.fetchone()[0]
    sum = age1 + age2 + age3 + age4
    age = []
    age.append(round(age1 / sum, 4) * 100)
    age.append(round(age2 / sum, 4) * 100)
    age.append(round(age3 / sum, 4) * 100)
    age.append(round(age4 / sum, 4) * 100)

    #get the last weibo sent from where
    sql = 'select count(*) from user_source;'
    cursor.execute(sql)
    sum = cursor.fetchone()[0]
    sql = 'select source, count(*) as num from user_source group by source order by num desc limit 12;'
    cursor.execute(sql)
    sentfrom = []
    for source, num in cursor.fetchall():
        sentfrom.append((source, round(num / sum, 4) * 100))

    #the distribution of the fans' tag
    sql = 'select count(*) from user_tag;'
    cursor.execute(sql)
    sum = cursor.fetchone()[0]
    sql = 'select tag, count(*) as num from user_tag group by tag order by num desc limit 10;'
    cursor.execute(sql)
    tagdic = cursor.fetchall()
    tag = []
    for t in tagdic:
        tag.append((t[0].encode('utf8'), round(t[1] / sum, 4) * 100))

    #close the cursor
    cursor.close()
    #disconnet the link to mysql db
    mysqlconn.dbclose(conn)


    return render_to_response('status.html', {'male':mperc, 'female':fperc, 'areaname':areaname, 'areanum':areanum, 'age':age, 'source':sentfrom, 'tag':tag})

#have a global look at the fans
def management_fans(request):
    p = 0
    type = 'null'
    if request.GET.has_key('p'):
        p = request.GET['p']
    if request.GET.has_key('type'):
        type = request.GET['type']
    #connect to the mysql
    conn = mysqlconn.dbconn()
    cursor = conn.cursor()
    sql = 'select user.screenname, user.sex, user.address, user.fansnumber, user.id from user, user_vector where user.id = user_vector.uid order by '+type+' desc limit '+str(int(p)*20)+',20;'
    cursor.execute(sql)
    fans = cursor.fetchall()
    print fans

    #close the cursor
    cursor.close()
    #disconnet the link to mysql db
    mysqlconn.dbclose(conn)
    

    return render_to_response('management_fans.html', {'fans':fans, 'page':int(p), 'type':type})


def weibotools(request):
    #get url that need to be searched
    if request.GET.has_key('searchurl'):
        url = request.GET['searchurl']
        try:
            #path = WeiboSpreadPath(get_pincode(), url)
            #id = path.get_weiboid_from_url()
            #generate gexf file
            #filename = os.getcwd() + '/themes/gexf/' + str(id) + '_' + url.split('/')[-2]
            #gexfURI = '/themes/gexf/' + str(id) + '_' + url.split('/')[-2] + '.gexf'
            gexfURI = '/themes/gexf/example.gexf'
            #judge whether the gexf file is already existed
            #if os.path.exists(filename+'.gexf') is not True:
                #path.generate_gexf(filename, path.get_edges(post_id=id))
            return render_to_response('weibotools.html', {'gexfURI':gexfURI})
        except:
            errormsg = "Invalid url."
            return render_to_response('weibotools.html', {'error':errormsg})


    return render_to_response('weibotools.html')
