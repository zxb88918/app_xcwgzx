# -*- coding: utf-8 -*-
import telnetlib
import re


class TelnetType(object):
	def __init__(self, con=telnetlib.Telnet()):
		self.con = con

	# 登录2352，再telnet到9303上获取ip
	def get_9303data(self, cnumac, ip_9303):
		try:
			self.con.open('172.21.34.251', timeout=5)
			self.con.read_until('Username:', 5)
			self.con.write("huawei\r\n")
			self.con.read_until('Password:', 5)
			self.con.write("huawei\r\n")
			if '<XC-QJL-WG-QS2352-1>' in self.con.read_until('<XC-QJL-WG-QS2352-1>', 5):
				print '2222'
				self.con.write('telnet %s\r\n' % ip_9303)
				if 'Username:' in self.con.read_until('Username:', 5):
					self.con.write("huawei\r\n")
					self.con.read_until('Password:', 5)
					self.con.write("huawei\r\n")
					self.con.read_until('MV-QS9303-1>', 5)
					self.con.write("su\r\n")
					self.con.read_until('Password:', 5)
					self.con.write("9303dateMAN\r\n")
					self.con.read_until('MV-QS9303-1>', 5)
					self.con.write("sys\r\n")
					print '333'
					self.con.read_until('MV-QS9303-1]', 5)
					self.con.write('dis arp interface Eth-Trunk 1 | include %s\r\n' % cnumac)
					temp_1 = self.con.read_until('MV-QS9303-1]', 5)
					return re.findall(r'(10.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(Eth-Trunk1)', temp_1)
					# return re.findall(r'(10.+?)\s+.+?\s+.+?\s+.+?\s+Eth-Trunk1', temp_1)
				else:
					print 'error-9303'
			else:
				return 'error-2352'
		except Exception as e:
			return 'error-timeout'
		finally:
			self.con.close()
			print 'ces'

if __name__ == "__main__":
	aad = TelnetType()
	print aad.get_9303data('881', '172.31.10.3')
	print aad
