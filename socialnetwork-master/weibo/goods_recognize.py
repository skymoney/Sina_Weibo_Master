#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

__author__ = 'Dou Mengyu'


class Recognize:
    goods_list = []
    def __init__(self):
        self.get_goods('/resource/commodity.txt',self.goods_list)
        
    def get_goods(self,filename,goods_list):
        fread = file(os.path.dirname(os.path.abspath(__file__))+filename)
        for line in fread:
            goods_list.append(line.strip())
    
    def recognize(self,string):
        count = string in self.goods_list
        return count


if __name__=='__main__':
    rec = Recognize()
    print rec.recognize('移动硬盘')