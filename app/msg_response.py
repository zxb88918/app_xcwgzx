# -*- coding: UTF-8 -*-
import re
from cnu import from_ceview_get_data, from_wocweb_get_rssi, from_wocweb_set_rssi, from_wanggezhicheng_get_data, from_jierurenzheng_get_data
import threading


ceview_format = u'''
【链路信息】
-----------------------
分前端：%s
高频ip：%s
高频mac：%s
设备类型：%s
物理带宽：%s
接受rssi：%s
发送rssi：%s
链路衰减：%s
工作模式：%s
信道：%s
上线时间：%s
活动状态：%s
-----------------------
'''


def content_handle(content):
	ip_re = re.compile(r'^([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])$')
	mac_re = re.compile(r'^[0-9a-f]{12}$', re.I)
	if mac_re.match(content):
		# threads = []
		# t1 = threading.Thread(target=from_ceview_get_data, args=(content,))
		# t2 = threading.Thread(target=from_wanggezhicheng_get_data, args=(content,))
		# t3 = threading.Thread(target=from_jierurenzheng_get_data, args=(content, jrrz_data))
		# threads.append(t1)
		# threads.append(t2)
		# threads.append(t3)
		# for t in threads:
		# 	t.start()
		# 	t.join()
		ceview_data = from_ceview_get_data(content)
		user_data = from_wanggezhicheng_get_data(content)
		# jrrz_data = from_jierurenzheng_get_data(content)
		return {'data': [ceview_data, user_data], 'type': 'cnu'}

	elif ip_re.match(content):
		rssi_data = from_wocweb_get_rssi(content)
		if rssi_data == '0':
			return {'data': u'【rssi抑制状态】：关闭', 'type': 'ip'}
		elif rssi_data == '1':
			set_status = from_wocweb_set_rssi(content)
			print set_status
			if set_status == '1':
				return {'data': u'【rssi抑制状态】：开启\r\n已发送rssi关闭请求，请再次查询rssi状态！', 'type': 'ip'}
			elif set_status == '0':
				return {'data': u'【rssi抑制状态】：开启\r\n已发送rssi关闭请求，但rssi抑制关闭失败，请稍后再试', 'type': 'ip'}
			else:
				return {'data': u'【rssi抑制状态】：开启\r\n已发送rssi关闭请求，但连接超时，请稍后再试！', 'type': 'ip'}
		elif rssi_data == u'不是高频ip或未升级':
			return {'data': u'【状态】：不是高频ip或未升级\r\n【故障分析】：1、您输入的ip地址不是cbat高频模块ip；2、cbat的高频模块未升级至最新版本，老版本cbat高频模块无rssi抑制设置，不会受到rssi抑制的影响。', 'type': 'ip'}
		elif rssi_data == u'连接超时':
			return {'data': u'【状态】：连接超时\r\n【故障分析】：此ip不通，请联系后台人员确认此cbat状态！', 'type': 'ip'}
	else:
		return {'data': u'【提示】\r\n暂开放功能：\r\n1、输入用户宽带猫mac地址，查询用户宽带状态及所在高频cbat的ip地址。\r\n2、输入高频cbat的ip地址，查询rssi抑制状态及修改。', 'type': 'else'}




if __name__ == "__main__":
	pass

