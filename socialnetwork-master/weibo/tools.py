#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weibo import APIClient
import weiboconfig as config
from getpincode import get_pincode
import urllib2
import simplejson
import math


#code = get_pincode()
#client = APIClient(app_key=config.APP_KEY, app_secret=config.APP_SECRET, redirect_uri=config.CALLBACK_URI)
#r = client.request_access_token(code)
#print r
#access_token = r.access_token # 新浪返回的token，类似abc123xyz456
#expires_in = r.expires_in # token过期的UNIX时间：http://zh.wikipedia.org/wiki/UNIX%E6%97%B6%E9%97%B4
# TODO: 在此可保存access token
#client.set_access_token(access_token, expires_in)
#res = client.get.statuses__user_timeline()
#for s in res.statuses:
#    print s.text
#print client.post.statuses__update(status=u'真内拉')
#print client.upload.statuses__upload(status=u'晒晒国米球衣样板', pic=open('/Users/donaldhjw/Desktop/inter.png'))


class WeiboSpreadPath:
    def __init__(self, pincode, url):
        self.client = APIClient(app_key=config.APP_KEY, app_secret=config.APP_SECRET, redirect_uri=config.CALLBACK_URI)
        r = self.client.request_access_token(pincode)
        access_token = r.access_token
        expires_in = r.expires_in
        #set access_token
        self.client.set_access_token(access_token, expires_in)
        self.url = url

    def get_weiboid_from_url(self):
        url = self.url
        string_mid = url.split('/')[-1]
        mid = string_mid.split('?')[0]
        return self.client.statuses.queryid.get(mid=mid, type=1, isBase62=1)['id']
        #return self.__queryid(mid)

    #weibo API statuses/queryid didn't do well for python sdk, so do it self
    def __queryid(self, mid):
        url = 'https://api.weibo.com/2/statuses/queryid.json?mid='+mid+'&type=1&isBase62=1&access_token='+self.client.access_token        
        print url
        json_id = urllib2.urlopen(url).read()
        pydata_id = simplejson.loads(json_id)
        id = pydata_id['id']
        return id

    def get_repost_timeline(self, id, count=200, page=1, max_id=0):
        return self.client.statuses.repost_timeline.get(id=id, count=count, page=page, max_id=max_id)

    def get_show(self, id):
        return self.client.statuses.show.get(id=id)

    def get_edges(self, post_id, edges={}):
        total_number=self.get_repost_timeline(id=post_id,count=200)['total_number']
        ##    print 'Total Number:',total_number
        reposts=[]
        page_reposts=self.get_repost_timeline(id=post_id,count=200)['reposts']
        reposts+=page_reposts
        page_number=int(math.ceil(total_number/200))
        ##    print 'Total Page Number:',page_number
        if page_number>1:
            for i in range(page_number):
                ##            print 'page_number:',i
                reposts+=self.get_repost_timeline(id=post_id,count=200,page=i+2)['reposts']
        reposts=[repost for repost in reposts if repost.has_key('reposts_count')]##有些微博是删除的
        ##    print 'Total Reposts:',len(reposts)
        reposted=self.get_show(id=post_id)['user']['screen_name']
        if reposted=='':
            reposted=str(self.get_show(id=post_id)['user']['id'])##存在Screen_name为空的情况
        for repost in reposts:
            if repost['user']['screen_name']=='':
                edges[repost['id']]={'poster':str(repost['user']['id']),'reposted':reposted,\
                        'content':repost['text'],'created_at':repost['created_at'],\
                        'reposts':repost['reposts_count'],'comments':repost['comments_count']}
            else:
                edges[repost['id']]={'poster':repost['user']['screen_name'],'reposted':reposted,\
                        'content':repost['text'],'created_at':repost['created_at'],\
                        'reposts':repost['reposts_count'],'comments':repost['comments_count']}##存在Screen_name为空的情况
        reposts=[repost for repost in reposts if repost['reposts_count']>0]
        for repost in reposts:
            self.get_edges(repost['id'])
        return edges

    def generate_dot(self, file_name, edges):
        OUT = file_name+'.dot'
        dot = ['"%s" -> "%s" [weibo_id=%s]' % ( edges[weibo_id]['reposted'].encode('gbk','ignore'),\
                edges[weibo_id]['poster'].encode('gbk','ignore'), weibo_id) for weibo_id in edges.keys()]
        with open(OUT,'w') as f:
            f.write('strict digraph {\nnode [fontname="FangSong"]\n%s\n}' % (';\n'.join(dot),))
            print 'dot file export'

    def generate_gexf(self, file_name, __edges):
        OUT = file_name+'.gexf'
		#print OUT
        nodes = []
        edges = []
        #i = 0
        for weibo_id in __edges.keys():
            if nodes.count(__edges[weibo_id]['reposted'].encode('gbk','ignore')) == 0:
                nodes.append(__edges[weibo_id]['reposted'].encode('gbk','ignore'))
            if nodes.count(__edges[weibo_id]['poster'].encode('gbk','ignore')) == 0:
                nodes.append(__edges[weibo_id]['poster'].encode('gbk','ignore'))
            edge = []
            edge.append(__edges[weibo_id]['reposted'].encode('gbk','ignore'))
            edge.append(__edges[weibo_id]['poster'].encode('gbk','ignore'))
            edges.append(edge)
            #edges.append('<edge id="%.1f" source="%.1f" target="%.1f"/>\n' % (i, \
            #        nodes.index(__edges[weibo_id]['reposted'].encode('gbk','ignore')), \
            #        nodes.index(__edges[weibo_id]['poster'].encode('gbk','ignore'))))
            #i = i + 1
        with open(OUT,'w') as f:
            f.write('<?xml version="1.0" encoding="gbk"?>\n')
            f.write('<gexf xmlns:viz="http:///www.gexf.net/1.1draft/viz" version="1.1" \
                    xmlns="http://www.gexf.net/1.1draft">\n')
            f.write('<graph defaultedgetype="directed" idtype="string" type="static">\n')
            #nodes
            f.write('<nodes count="%d">\n' % len(nodes))
            for node in nodes:
                f.write('<node id="%.1f" label="%s"/>\n' % (nodes.index(node), node))
            f.write('</nodes>\n')
            #edges
            f.write('<edges count="%d">\n' % len(edges))
            i = 0
            for edge in edges:
                f.write('<edge id="%.1f" source="%.1f" target="%.1f"/>\n' % \
                        (i, nodes.index(edge[0]), nodes.index(edge[1])))
                i = i + 1
            f.write('</edges>\n')
            f.write('</graph>\n')
            f.write('</gexf>\n')
            print 'gexf file export'
        return nodes, edges
            
    def analysis(self, nodes, edges):
    	url = self.url
        uid = url.split('/')[-2]
        rootnode = self.client.users.show.get(uid=uid)['screen_name'].encode('gbk','ignore')
        nodes.pop(nodes.index(rootnode))
        #first level
        #two elements:number of reposts, nodes
        onelnodes = [0,[]]
        for edge in edges:
        	#some edges may be the same
        	if edge[0] == rootnode:
        		#print edge
        		onelnodes[0] = onelnodes[0] + 1
        		if rootnode != edge[1] and onelnodes[1].count(edge[1]) == 0:
        			#print edge
        			onelnodes[1].append(edge[1])
        			nodes.pop(nodes.index(edge[1]))
        		#edges.pop(edges.index(edge))
        #second level
        twolnodes = [0,[]]
        for edge in edges:
        	if onelnodes[1].count(edge[0]) == 1:
        		twolnodes[0] = twolnodes[0] + 1
        		if rootnode != edge[1] and onelnodes[1].count(edge[1]) == 0 \
        		        and twolnodes[1].count(edge[1]) == 0:
        			twolnodes[1].append(edge[1])
        			nodes.pop(nodes.index(edge[1]))
        #third level
        threelnodes = [0,[]]
        for edge in edges:
        	if twolnodes[1].count(edge[0]) == 1:
        		threelnodes[0] = threelnodes[0] + 1
        		if rootnode != edge[1] and onelnodes[1].count(edge[1]) == 0 \
        		        and twolnodes[1].count(edge[1]) == 0 \
        		        and threelnodes[1].count(edge[1]) == 0:
        			threelnodes[1].append(edge[1])
        			nodes.pop(nodes.index(edge[1]))
        #fourth+ level
        fourlnodes = [len(nodes),nodes]
		
        print onelnodes, twolnodes, threelnodes, fourlnodes


if __name__ == '__main__':
    path = WeiboSpreadPath(get_pincode(), 'http://weibo.com/1733745982/z4BcwqmBa')
    #path = WeiboSpreadPath('2.00sWc1tBRbe3eC1c3a09166cP6fhRE', 'http://weibo.com/1400229064/zdwGs7kqZ')
    id = path.get_weiboid_from_url()
    #path.generate_dot('example', path.get_edges(post_id=id))
    nodes, edges = path.generate_gexf('gexf/example', path.get_edges(post_id=id))
    path.analysis(nodes, edges)
