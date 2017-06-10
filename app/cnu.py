# -*- coding: UTF-8 -*-
import telnetlib
import re
import requests
import pytesseract
from PIL import Image
import json
import time

fqd = {
		'0': '172.31.10.3',
		'1': '172.31.10.112',
		'2': '172.31.10.96',
		'3': '172.31.10.80',
		'4': '172.31.10.64'
		}


def format_mac(mac, seq):
	# 输入的mac地址为12位中间无分割符的标准mac
	#
	if seq == '9303':
		newmac = mac[0:4]+'-'+mac[4:8]+'-'+mac[8:12]
		return newmac
	elif seq == 'olt':
		newmac = mac[0:4]+'.'+mac[4:8]+'.'+mac[8:12]
		return newmac
	elif seq == 'ceview':
		newmac = mac[0:2]+'-'+mac[2:4]+'-'+mac[4:6]+'-'+mac[6:8]+'-'+mac[8:10]+'-'+mac[10:12]
		return newmac
	else:
		return mac


def from_9303_get_data(cnumac, fqd_num):
	try:
		con = telnetlib.Telnet()
		con.open('172.21.34.251', timeout=5)
	except Exception, e:
		print e
		return {'ip': 'er-timeout'}
	else:
		con.read_until('Username:', 5)
		con.write("huawei\r\n")
		con.read_until('Password:', 5)
		con.write("huawei\r\n")
		if '<XC-QJL-WG-QS2352-1>' in con.read_until('<XC-QJL-WG-QS2352-1>', 5):
			print fqd.get(fqd_num)
			con.write('telnet %s\r\n' % fqd.get(fqd_num))
			if 'Username:' in con.read_until('Username:', 5):
				con.write("huawei\r\n")
				con.read_until('Password:', 5)
				con.write("huawei\r\n")
				con.read_until('MV-QS9303-1>', 5)
				con.write("su\r\n")
				con.read_until('Password:', 5)
				con.write("9303dateMAN\r\n")
				con.read_until('MV-QS9303-1>', 5)
				con.write("sys\r\n")
				con.read_until('MV-QS9303-1]', 5)
				mac_new = format_mac(cnumac, '9303')
				print mac_new
				con.write('dis arp interface Eth-Trunk 1 | include %s\r\n' % mac_new.encode('ascii'))
				temp_1 = con.read_until('MV-QS9303-1]', 5)
				print temp_1
				# return re.findall(r'(10.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(Eth-Trunk1)', temp_1)
				temp_2 = re.findall(r'(10.+?)\s+.+?\s+.+?\s+.+?\s+Eth-Trunk1', temp_1)
				if temp_2 == []:
					return {'ip': 'have no ip'}
				else:
					print temp_2
					temp_3 = "/".join(temp_2)
					return {'ip': temp_3}
			else:
				return {'ip': 'er-9303timeout'}
		else:
			return {'ip': 'er-2352timeout'}

	finally:
		con.close()


def from_ceview_get_data(cnumac):
	url_img = 'http://172.21.34.240:8033/ems/secu/jsp/validatecode.jsp'
	url_login = 'http://172.21.34.240:8033/ems/findUserByNameAndPwd.action'
	url_query = 'http://172.21.34.240:8033/ems/common/ajax/deviceQuery!getDevice.action'
	url_quit = 'http://172.21.34.240:8033/ems/secu/jsp/deleteRonline.action'
	data_quit = {
				'logInfo': '47%2C3',
				'ronline.userid': '3'
				}
	ceview_format = u'''
	【链路信息】
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
	'''
	r = requests.Session()
	try:
		mac_new = format_mac(cnumac, 'ceview')
		data_query = {
					'start': '0',
					'limit': '20',
					'searchBean.ip': '',
					'searchBean.type': '-1',
					'searchBean.ne_neid': '',
					'searchBean.netype': '',
					'searchBean.mac': mac_new,
					'searchBean.nename': '',
					'searchBean.groupid': '',
					'searchBean.typename': '',
					'searchBean.vparentname': '',
					'searchBean.dsCfgOpRadioChnn': '',
					'searchBean.softversion': '',
					'searchBean.recivepwl_from': '',
					'searchBean.recivepwl_to': '',
					'searchBean.sentpwl_from': '',
					'searchBean.sentpwl_to': '',
					'searchBean.txrate_from': '',
					'searchBean.txrate_to': '',
					'searchBean.rxrate_from': '',
					'searchBean.rxrate_to': '',
					'searchBean.mgm_ip': '',
					'searchBean.nestatus': '-1',
					'searchBean.active': '-1'
					}
		r_img = r.get(url_img, timeout=2)
		with open('img_ceview.jpg', 'wb') as t:
			t.write(r_img.content)
		img = Image.open(r'img_ceview.jpg')
		str_ceview = pytesseract.image_to_string(img)
		data_login = {
					'jsonData': 'undefined,' + str_ceview,
					'ruser.name': 'test',
					'ruser.userpassword': '4c9184f37cff01bcdc32dc486ec36961'
					}
		r_login = r.post(url_login, data_login)
		r_query = r.post(url_query, data_query)
		r_query_data = json.loads(r_query.content)
		if r_query_data.get('total') != 0:
			ceview_records = r_query_data.get('records')[0]
			ip = ceview_records.get('ipAddr')
			atten = ceview_records.get('attenuation')
			phy = ceview_records.get('phyuprate')
			rec = ceview_records.get('recivepwl')
			sent = ceview_records.get('sentpwl')
			mode = ceview_records.get('workmodel')
			group = ceview_records.get('group')
			topmac = ceview_records.get('topmac')
			dev = ceview_records.get('devicetype')
			act = ceview_records.get('active')
			signal = ceview_records.get('signal')
			runtime = ceview_records.get('runtime')
			return ceview_format % (group, ip, topmac, dev, phy, rec, sent, atten, mode, signal, runtime, act)
		else:
			return u'''
			【链路信息】
			系统中无此数据,可能是所在cbat未登记到ceview网管中！
			'''
	except Exception, e:
		return u'''
		【链路信息】
		连接超时或错误,可能是同时使用的人数过多，请稍后再试！
		'''
	finally:
		r.post(url_quit, data_quit)


def from_wocweb_get_topo(woc_ip):
	url_topology = 'http://%s/netTopology.asp' % woc_ip
	url_rssi = 'http://10.179.11.49/terninal_access_control.asp'
	w = requests.Session()
	try:
		w_topo = w.get(url_topology, timeout=1.5)
		w_topo_data = w_topo.content
		temp_1 = re.findall(r'var info=new Array\((.*)\);', w_topo_data)
		# 转化为list
		print temp_1
		temp_2 = list(eval(temp_1[0]))
		print temp_2
		temp_len = len(temp_2)/13
		if temp_len >= 1:
			# 将第一个元素去掉
			temp_cut = []
			for i in temp_2[1:]:
				# print i.en
				temp_cut.append(i.decode('gbk'))
			print temp_cut
			temp_data = []
			for i in range(0, temp_len):
				temp_data.append(temp_cut[i*13+2:(i+1)*13])
			return temp_data
		else:
			# 返回一个2个参数的list，主要是为后面将参数传给view后，容易做判断，后面同样
			return ['', u'高频模块下未带终端']
	except IndexError, e:
		# print 'IndexError'
		# print e
		return ['', u'不是高频ip或未升级']
	except Exception, e:
		# print 'timeout'
		# print e
		return ['', u'连接超时']
	finally:
		w.close()


def from_wocweb_get_rssi(woc_ip):
	url_rssi = 'http://%s/terninal_access_control.asp' % woc_ip
	w = requests.Session()
	try:
		w_rssi = w.get(url_rssi, timeout=1.5)
		print '1'
		w_rssi_data = w_rssi.content
		print w_rssi.request.url
		print '2'
		temp_1 = re.findall(r'var rssiskip  = new Array\(\'(.)\'.*\);', w_rssi_data)
		print '3'
		temp_2 = temp_1[0]
		print temp_2
		return temp_2
		# 转化为list
		# temp_2 = list(eval(temp_1[0]))
		# print temp_2

	except IndexError, e:
		# print 'IndexError'
		# print e
		return u'不是高频ip或未升级'
	except Exception, e:
		# print 'timeout'
		# print e
		return u'连接超时'
	finally:
		w.close()


def from_wocweb_set_rssi(woc_ip):
	url_set_rssi = "http://%s/goform/cvn_web_setRssiSkip" % woc_ip
	w = requests.Session()
	rssi_data = {"rssienable": "0", "rssiperiod": "3600", "highrssi": "80", "lowrssi": "20"}
	try:
		w_set = w.post(url_set_rssi, rssi_data)
		set_status = w_set.status_code
		if set_status == 200:
			return '1'
		else:
			return '0'
	except Exception, e:
		# print 'timeout'
		# print e
		return u'超时或未知错误！'
	finally:
		w.close()


def from_wanggezhicheng_get_data(cnumac):
	url_login = 'http://172.30.67.204:8080/wg/LoginAction.action'
	login_data = {'submitData': '{"username":"13937468716","pwd":"1"}'}
	query_url = 'http://172.30.67.204:8080/wg/getYhxxOfReportAction.action'
	logout_url = 'http://172.30.67.204:8080/wg/mpssLogoutAction.action'
	query_data = {
				'xqbm': '',
				'zjhm': '',
				'zjxm': '',
				'sbhm': cnumac,
				'ywhm': '',
				'phone': '',
				'city': '许昌',
				'pageIndex': '0',
				'pageSize': '20'
				}
	header = {
		'Accept': '*/*',
		'Accept-Encoding': 'gzip',
		'Accept-Language': 'zh-CN,zh;q=0.8',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Connection': 'keep-alive',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
		'X-Requested-With': 'XMLHttpRequest'
	}
	try:
		s = requests.Session()
		# 登录网格支撑系统
		login = s.post(url_login, data=login_data, headers=header)
		login_status = login.text
		if login_status == u'登录成功':
			print 'success'
			query = s.post(query_url, data=query_data)
			query_result = json.loads(query.text)
			data_num = query_result.get('total')
			if data_num > 0:
				users_data = query_result.get('data')
				text_data = ''
				text_format = u'''
【用户信息】
用户姓名：%s
证件号码：%s
电话：%s
业务号码：%s
useid：%s
设备号码：%s
订购产品：%s
融合套餐：%s
账户余额：%s
账户状态：%s
业务状态：%s
用户状态：%s
用户地址：%s
入网时间：%s
'''
				print users_data
				for user_data in users_data:
					user_data_name = user_data.get('client_name')
					user_data_sfz = user_data.get('card_no')
					user_data_phone = user_data.get('phone')
					user_data_ywhm = user_data.get('ywhm')
					user_data_userid = user_data.get('userid')
					user_data_sbhm = user_data.get('sbhm')
					user_data_ywmc = user_data.get('product_name')
					user_data_rhtc = user_data.get('product_rhtc')
					user_data_money = user_data.get('fee_money')
					user_data_zhzt = user_data.get('fee_type')
					user_data_state = user_data.get('current_state')
					user_data_yhzt = user_data.get('user_status')
					user_data_address = user_data.get('address')
					user_data_time = user_data.get('create_time')
					text_data = text_data + text_format % (user_data_name, user_data_sfz, user_data_phone, user_data_ywhm, user_data_userid, user_data_sbhm, user_data_ywmc, user_data_rhtc, user_data_money, user_data_zhzt, user_data_state, user_data_yhzt, user_data_address, user_data_time)
				return text_data

			else:
				return u'''
				【用户信息】
				未查询到用户数据，数据取自于网格化支撑系统，数据更新大约滞后1天，如是新装用户，可能查询不到信息。
				'''
		else:
			return u'''
				【用户信息】
				登录网格支撑系统失败，受限于网络状况及服务器稳定性，稍后重试即可。
				'''

	except Exception,e:
		print e
	finally:
		s.get(logout_url)


def from_jierurenzheng_get_data(cnumac):
	url_validate = 'http://172.30.64.21/randimage.jsp'
	url_login = 'http://172.30.64.21/userLogin.do?method=userLogin'
	url_post = 'http://172.30.64.21/newfunc.do?method=positionSys'
	url_logout = 'http://172.30.64.21/logout.jsp'
	data_post = {'mac': cnumac, 'tvn': '', 'userid': ''}
	data_format = u'''
	【接入认证信息】
	CnuMac：%s
	业务号码：%s
	UserID：%s
	CCName：%s
	业务状态：%s
	激活状态：%s
	认证状态：%s
	'''
	s = requests.Session()
	try:
		# 1、get验证码地址，获取cookies并存入session中
		tep_s1 = s.get(url_validate)
		validate_data = tep_s1.content

		# 2、将验证码图片存储到本地目录下命名jrrz_image.jpg
		with open('jrrz_image.jpg', 'wb') as t:
			t.write(validate_data)

		# 3、读取存储的验证码图片并识别验证码
		img = Image.open(r'jrrz_image.jpg')
		validate_str = pytesseract.image_to_string(img)
		# 4、组合post数据
		data_login = {'userName': u'张磊'.encode('gbk'), 'passWord': '666666', 'verificationCode': validate_str, 'imageField.x': '0', 'imageField.y': '0'}
		login = s.post(url_login, data=data_login)
		login_res = login.text
		if u'用户名' in login_res:
			return u'''
			【接入认证信息】
			登录接入认证系统失败,受限于网络状况及服务器稳定性，稍后重试即可。
			'''
		else:
			post = s.post(url_post, data=data_post)
			post_res = post.text
			if u'<font color="red">无' in post_res:
				return u'''
				【接入认证信息】
				未能查询到数据,请确认您输入的mac地址正确。
				'''
			else:
				temp_1 = re.findall(r'<td\s+align="center"\s*>(.*)</td>', post_res)
				temp_2 = re.findall(u'状态：(.*)(?=;|\.)', post_res)
				if len(temp_1) >= 5 and len(temp_2) >= 3:
					ywhm = temp_1[0]
					userid = temp_1[2]
					CCName = temp_1[3]
					mac = temp_1[1]
					ywzt = temp_2[0]
					jhzt = temp_2[1]
					rzzt = temp_2[2]

					return data_format % (mac, ywhm, userid, CCName, ywzt, jhzt, rzzt)
	except:
		return u'''
		【接入认证信息】
		连接错误或者超时，受限于服务器的性能与稳定性，稍后重试即可。
		'''
	finally:
		s.get(url_logout)
		s.close()
		print 'jrrz'


if __name__ == "__main__":
	from_jierurenzheng_get_data('fc19d01a6b67')

