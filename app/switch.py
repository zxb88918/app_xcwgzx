# -*- coding: utf-8 -*-
import telnetlib
import re
import threading
import time

fqd = {'qjl': '172.31.10.3',
		'jadd': '172.31.10.112',
		'ldl': '172.31.10.96',
		'gml': '172.31.10.80',
		'syhc': '172.31.10.64'
		}


def from_9303_count_arp(ip_9303, address_9303):
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
			con.write('telnet %s\r\n' % ip_9303)
			if 'Username:' in con.read_until('Username:', 5):
				con.write("huawei\r\n")
				con.read_until('Password:', 5)
				con.write("huawei\r\n")
				con.read_until('MV-QS9303-1>', 5)
				con.write('dis arp | include xxxx\r\n')
				temp_1 = con.read_until('MV-QS9303-1]', 5)
				con.write('quit\r\nquit\r\n')
				con.read_until('<XC-QJL-WG-QS2352-1>', 5)
				temp_2 = re.findall(r'Total:(\d*?)\s', temp_1)
				if temp_2 != []:
					with open('arp.txt','a') as text:
						text.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+address_9303.encode('gbk') + "-" + ip_9303 + u":   ".encode('gbk') + temp_2[0] + '\r\n')
				else:
					with open('arp.txt', 'a') as text:
						text.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + address_9303.encode('gbk') + "-" + ip_9303 + u":   未获取数据".encode('gbk') + '\r\n')

			else:
				with open('arp.txt', 'a') as text:
					text.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + address_9303.encode('gbk') + "-" + ip_9303 + u":   连接9303错误".encode('gbk') + '\r\n')
		else:
			with open('arp.txt', 'a') as text:
				text.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + address_9303.encode('gbk') + "-" + ip_9303 + u":   连接2352错误".encode('gbk') + '\r\n')

	finally:
		con.close()


if __name__ == "__main__":
	# print from_9303_count_arp('172.31.10.3', u'前进路分前端')
	# threads = []
	# t1 = threading.Thread(target=from_9303_count_arp, args=('172.31.10.3', u'前进路分前端'))
	# threads.append(t1)
	# t2 = threading.Thread(target=from_9303_count_arp, args=('172.31.10.112', u'建安大道分前端'))
	# threads.append(t2)
	# t3 = threading.Thread(target=from_9303_count_arp, args=('172.31.10.96', u'劳动路分前端'))
	# threads.append(t3)
	# t4 = threading.Thread(target=from_9303_count_arp, args=('172.31.10.80', u'光明路分前端'))
	# threads.append(t4)
	# t5 = threading.Thread(target=from_9303_count_arp, args=('172.31.10.64', u'水语花城分前端'))
	# threads.append(t5)
	# for t in threads:
	# 	t.setDaemon(True)
	# 	t.start()
	# t.join()
	print from_9303_count_arp('172.31.10.3', u'前进路分前端')
	print from_9303_count_arp('172.31.10.112', u'建安大道分前端')
	print from_9303_count_arp('172.31.10.96', u'劳动路分前端')
	print from_9303_count_arp('172.31.10.80', u'光明路分前端')
	print from_9303_count_arp('172.31.10.64', u'水语花城分前端')