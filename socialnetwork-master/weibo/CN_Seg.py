#-*-coding:utf-8-*-
#!/usr/bin/python


import sys
import os
import jieba
import goods_recognize
from jieba import posseg

class CN_Seg:
	_instalce = ''
	_init = 0
	@classmethod  
	def instance(cls):  
		if not cls._instalce:  
			cls._instalce = cls()
		return cls._instalce 
	
	
	def init(self):
		jieba.load_userdict(os.path.dirname(os.path.abspath(__file__))+'/resource/Lib.dic')
		self._init=1
	
	def cut(self,string):
		word_list = []
		seg_list=jieba.posseg.cut(string)
		for seg in seg_list:
			word_dict = {'word': '', 'flag': ''} 
			word_dict['word'] = seg.word.encode('UTF-8')
			word_dict['flag'] = seg.flag.encode('UTF-8')
			word_list.append(word_dict)
		return word_list
	def cut_filter(self,string):
		jsonresult = {'goods':[],'noun':[],'adj':[]}
		word_list = self.cut(string)
		recognizer = goods_recognize.Recognize()
		for word in word_list:
			if(word['flag'].find('n') == 0):
				count = recognizer.recognize(word['word'])
				if count:
					jsonresult['goods'].append(word['word'])
				else:
					jsonresult['noun'].append(word['word'])
			else:
				if (word['flag'].find('a') == 0):
					jsonresult['adj'].append(word['word'])
		
		return jsonresult
			