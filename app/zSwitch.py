# -*- coding: utf-8 -*-
import telnetlib
import re
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

olt_ip_address = ['']


# telnet类，登录、发送命令、关闭方法##########################################
class TelnetType(object):
	def __init__(self, con=telnetlib.Telnet()):
		self.con = con

	# 登录高频
	def login_woc(self, wocip):
		try:
			print '1'
			self.con.open(wocip, timeout=3)
			print '2'
			if 'login:' in self.con.read_until('login:', 3):
				print '3'
				self.con.write("root\r\n")
				self.con.read_until('Password:', 3)
				self.con.write("cvn\r\n")
				temp_1 = self.con.read_until('->', 5)
				if '->' in temp_1:
					return u'登陆成功'
				elif 'incorrect' in temp_1:
					self.con.write("root\r\n")
					self.con.read_until('Password:', 3)
					self.con.write("admin\r\n")
					temp_2 = self.con.read_until('->', 3)
					if '->' in temp_2:
						return u'登陆成功'
					elif 'incorrect' in temp_2:
						return u'帐号密码错误或不是高频ip'
				elif '#' in temp_1:
					return u'不是高频ip'
			else:
				return u'ip不通'
		except:
			return u'未知错误'

	def get_topology(self):
		try:
			self.con.write(':show-topology;\r\n')
			msg = self.con.read_until('->', 5)
			if 'RX/TX Rate Score' in msg:
				print re.findall(r'CPE\s+([\d]+)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*', msg)
				return 'error'
			else:
				print re.findall(r'CPE\s+([\d]+)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*', msg)
		except:
			return u'可能网络连接错误'

	def close(self):
		self.con.close()


def from_olt_get_pon(cnumac, oltip):
	finish = 'ZTEC220-001#'
	newmac = format_mac(cnumac, 'olt')
	try:
		con = telnetlib.Telnet()
		con.open(oltip, timeout=5)
	except Exception, e:
		return {'data': '', 'status': False}
	else:
		con.read_until('Username:', 5)
		con.write("zte\r\n")
		con.read_until('Password:', 5)
		con.write("zte\r\n")
		if 'ZTEC220-001#' in con.read_until(finish, 5):
			con.write('show mac %s\r\n' % newmac.encode('ascii'))
			res_text = con.read_until(finish, 5)
			pon = re.search(r'epon-onu_[^\s]+', res_text)
			if pon:
				print pon.group()
				return {'data': pon.group(), 'status': True}
			else:
				return {'data': u"olt:未查询到数据", 'status': False}
		else:
			return {'data': u'olt:登录失败', 'status': False}

	finally:
		con.close()


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
		mac_lower = mac.lower()
		newmac = mac_lower[0:2]+'-'+mac_lower[2:4]+'-'+mac_lower[4:6]+'-'+mac_lower[6:8]+'-'+mac_lower[8:10]+'-'+mac_lower[10:12]
		return newmac
	else:
		return mac


def from_woc_get_rssi(wocip):
	woc_login_info = [['root', 'cvn'], ['root', 'admin']]
	finish = '->'
	try:
		con = telnetlib.Telnet()
		print '1'
		con.open(wocip, timeout=3)
		print '2'
		if 'login:' in con.read_until('login:', 3):
			con.write("root\r\n")
			con.read_until('Password:', 3)
			con.write("admin\r\n")
			print '3'
			temp_1 = con.read_until(finish, 5)
			print '4'
			if finish in temp_1:
				print u'登陆成功'
				print '11'
				con.write(':show-topology;\r\n')
				print '22'
				msg = con.read_until(finish, 5).decode('gb2312')
				print '5'
				if 'RX/TX Rate Score' in msg:
					print'6'
					res_data = re.findall(r'CPE\s+([\d]+)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*',msg)
					if res_data:
						data = format_for_rssi(res_data)
						return {'data':data,'status':True}
					else:
						return {'data': u'没有在线终端', 'status': False}
				else:
					print '6'
					res_data = re.findall(r'CPE\s+([\d]+)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*',msg)
					if res_data:
						data = format_for_rssi(res_data)
						return {'data':data,'status':True}
					else:
						return {'data': u'没有在线终端', 'status': False}
			elif '#' in temp_1:
				return {'data':u'不是高频ip','status':False}
			elif 'incorrect' in temp_1:
				con.write("root\r\n")
				con.read_until('Password:', 3)
				con.write("cvn\r\n")
				temp_2 = con.read_until(finish, 3)
				if finish in temp_2:
					print u'登陆成功'
					print '2-11'
					con.write(':show-topology;\r\n')
					msg = con.read_until(finish, 5).decode('gb2312')
					print '2-22'
					if 'RX/TX Rate Score' in msg:
						print '2-33'

						res_data = re.findall(r'CPE\s+([\d]+)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*',msg)
						if res_data:
							data = format_for_rssi(res_data)
							return {'data': data, 'status': True}
						else:
							return {'data': u'没有在线终端', 'status': False}
					else:
						print '2-3'
						res_data = re.findall(r'CPE\s+([\d]+)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*',msg)
						print '2-4'
						if res_data:
							print '2-5'
							data = format_for_rssi(res_data)
							print '2-6'
							return {'data': data, 'status': True}
							# return {}
						else:
							return {'data': u'没有在线终端', 'status':False}
				elif 'incorrect' in temp_2:
					return {'data':u'帐号密码错误或不是高频ip','status':False}

		else:
			return {'data':u'ip地址不通','status':False}
	except Exception, e:
		print e
		print 'aasdad'
		return {'data':u'未知错误','status':False}
	finally:
		con.close()

def from_woc_get_cnurssi(wocip,cnumac):
	woc_login_info = [['root', 'cvn'], ['root', 'admin']]
	finish = '->'
	try:
		con = telnetlib.Telnet()
		print '1'
		con.open(wocip, timeout=3)
		print '2'
		if 'login:' in con.read_until('login:', 3):
			con.write("root\r\n")
			con.read_until('Password:', 3)
			con.write("admin\r\n")
			print '3'
			temp_1 = con.read_until(finish, 5)
			print '4'
			if finish in temp_1:
				print u'登陆成功'
				print '11'
				con.write(':show-topology;\r\n')
				print '22'
				msg = con.read_until(finish, 5).decode('gb2312')
				print '5'
				if 'RX/TX Rate Score' in msg:
					print'6'
					res_data = re.findall(r'CPE\s+([\d]+)\s+(%s)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*' % format_mac(cnumac,'ceview'),msg)
					if res_data:
						return {'data':res_data[0][6],'status':True}
					else:
						return {'data': u'此cnu不在线', 'status': False}
				else:
					print '6'
					res_data = re.findall(r'CPE\s+([\d]+)\s+(%s)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*' % format_mac(cnumac,'ceview'),msg)
					if res_data:
						return {'data':res_data[0][6],'status':True}
					else:
						return {'data': u'此cnu不在线', 'status': False}
			elif '#' in temp_1:
				return {'data':u'不是高频ip','status':False}
			elif 'incorrect' in temp_1:
				con.write("root\r\n")
				con.read_until('Password:', 3)
				con.write("cvn\r\n")
				temp_2 = con.read_until(finish, 3)
				if finish in temp_2:
					print u'登陆成功'
					print '2-11'
					con.write(':show-topology;\r\n')
					msg = con.read_until(finish, 5).decode('gb2312')
					print '2-22'
					if 'RX/TX Rate Score' in msg:
						print'6'
						res_data = re.findall(
							r'CPE\s+([\d]+)\s+(%s)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*' % format_mac(cnumac, 'ceview'), msg)
						if res_data:
							return {'data': res_data[0][6], 'status': True}
						else:
							return {'data': u'此cnu不在线', 'status': False}
					else:
						print '6'
						res_data = re.findall(
							r'CPE\s+([\d]+)\s+(%s)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+[t\)])\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+([\S]+)\s*' % format_mac(cnumac, 'ceview'), msg)
						if res_data:
							return {'data': res_data[0][6], 'status': True}
						else:
							return {'data': u'此cnu不在线', 'status': False}
				elif 'incorrect' in temp_2:
					return {'data':u'帐号密码错误或不是高频ip','status':False}

		else:
			return {'data':u'ip地址不通','status':False}
	except Exception, e:
		print e
		return {'data':u'未知错误','status':False}
	finally:
		con.close()


def format_for_rssi(datas):
	res_data = []
	for data in datas:
		res_data.append(list(data))
	return res_data

if __name__ == "__main__":
	# pass
	# aad = TelnetType()
	# print aad.login_woc('10.179.24.115')
	# aad.get_topology()
	# aad.close()
	# print from_olt_get_pon('fc19d04dd953',)
	# format_for_rssi(from_woc_get_rssi('10.179.27.57'))
	print from_woc_get_cnurssi('10.179.15.249','fc19d01b10ef')

