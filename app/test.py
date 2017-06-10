# -*- coding: utf-8 -*-
import requests, re


def get_news():
	url_ccbn = 'http://www.ccbn.com.cn/zx_ccbn/'
	w = requests.session()
	s = w.get(url_ccbn)
	tex = s.content
	com = re.compile(r'<div class="new_pic">.+?src="(.*?)".*?<h2><a href="(.*?)".+?style="">(.*?)</a> </h2>\s*(.*?)\s*<div class="new_info">.*?class="new_time">(.*?)</span>', re.S | re.M)
	match = com.findall(tex)
	print match
	if match:
		news_url = []
		news_img_url = []
		news_title = []
		news_content = []
		news_time = []
		data = []
		for i in match:
			k = w.get(i[1])
			news_detail = k.content
			com1 = re.compile(r'<td id="article_content">.*?(\S.+?)</td>.*?</tr>.*?</table>', re.S | re.M)
			match1 = com1.findall(news_detail)
			# print i[1]
			# print match1[0].decode('gbk')
			print type(match1[0].decode('gbk'))
			print type(i[2].decode('gbk'))
			temp = [i[0], i[1], i[2].decode('gbk'), i[3].decode('gbk'), i[4], match1[0].decode('gbk')]
			print len(temp)
			data.append(temp)
		return {'news':data}
	return 'error'

if __name__ == "__main__":
	print get_news()
