# -*- coding: utf-8 -*-
import requests
import json


def from_wanggezhicheng_get_address(sAddress):
	url_login = 'http://172.30.67.204:8080/wg/LoginAction.action'
	login_data = {'submitData': '{"username":"13937468716","pwd":"1"}'}
	address_url = 'http://172.30.67.204:8080/wg/getXqListOfBossAction.action'
	logout_url = 'http://172.30.67.204:8080/wg/mpssLogoutAction.action'
	address_data = {
				'city': '许昌',
				'xqmc': sAddress,
				'pageIndex': '0',
				'pageSize': '400'
				}
	try:
		s = requests.Session()
		# 登录网格支撑系统
		login = s.post(url_login, data=login_data)
		login_status = login.text
		if login_status == u'登录成功':
			address = s.post(address_url, data=address_data)
			data_address = address.text
			print data_address
			return json.loads(data_address)
		else:
			return {'total': -1}

	except Exception,e:
		return {'total': -2}
	finally:
		s.get(logout_url)


def from_wanggezhicheng_get_userdata(addresscode):
	url_login = 'http://172.30.67.204:8080/wg/LoginAction.action'
	login_data = {'submitData': '{"username":"13937468716","pwd":"1"}'}
	address_url = 'http://172.30.67.204:8080/wg/getYhxxOfReportAction.action'
	logout_url = 'http://172.30.67.204:8080/wg/mpssLogoutAction.action'
	address_data = {
				'xqbm': addresscode,
				'zjhm':'',
				'zjxm':'',
				'sbhm':'',
				'ywhm':'',
				'phone':'',
				'city':'许昌',
				'pageIndex':'0',
				'pageSize':'200',
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
			address = s.post(address_url, data=address_data)
			print address.text
			temp1 = json.loads(address.text).get('data')
			print temp1
			datas = []
			# 重新梳理数据，减去不必要的信息，合并类似信息
			for index, item in enumerate(temp1):
				data = {}
				if item.get('zcj') == u'宽带':
					# print item.get('address').split(item.get('floor_name'))[1]
					data['dz'] = item.get('address').split(item.get('area_name'))[1]
					data['floor'] = item.get('floor_name')
					data['name'] = item.get('client_name')
					data['phone'] = item.get('phone')
					data['ywzt'] = item.get('current_state')
					data['yhzt'] = item.get('user_status')
					data['zcj'] = u'宽带-%s' % item.get('product_name')
					data['zh'] = '%s-%s' % (item.get('fee_type'), item.get('fee_money'))
					datas.append(data)
				elif item.get('zcj') == u'主机':
					data['dz'] = item.get('address').split(item.get('area_name'))[1]
					data['floor'] = item.get('floor_name')
					data['name'] = item.get('client_name')
					data['phone'] = item.get('phone')
					data['ywzt'] = item.get('current_state')
					data['yhzt'] = item.get('user_status')
					data['zcj'] = u'主机-%s' % item.get('product_name')
					data['zh'] = '%s-%s' % (item.get('fee_type'), item.get('fee_money'))
					data['jh'] = item.get('sfjh')
					datas.append(data)
			datas_f = []
			counted_list = []
			floor_list = []
			for index, i in enumerate(datas):
				data_f = {}
				repeat_list = []
				if index in counted_list:
					continue
				else:
					repeat_list.append(index)
					for index1, i1 in enumerate(datas):
						if i1.get('dz') == i.get('dz') and index1 > index:
							repeat_list.append(index1)
					if len(repeat_list) == 1:
						cur_ind = repeat_list[0]
						if u'宽带' in datas[cur_ind].get('zcj'):
							data_f['dz'] = datas[cur_ind].get('dz')
							data_f['zcj'] = datas[cur_ind].get('zcj')
							data_f['zh'] = datas[cur_ind].get('zh')
							data_f['floor'] = datas[cur_ind].get('floor')
							data_f['name'] = datas[cur_ind].get('name')
							data_f['phone'] = datas[cur_ind].get('phone')
							data_f['ywzt'] = datas[cur_ind].get('ywzt')
							data_f['yhzt'] = datas[cur_ind].get('yhzt')
							floor_list.append(data_f.get('floor'))
							datas_f.append(data_f)
						elif u'主机' in datas[cur_ind].get('zcj'):
							data_f['dz'] = datas[cur_ind].get('dz')
							data_f['zcj'] = datas[cur_ind].get('zcj')
							data_f['zh'] = datas[cur_ind].get('zh')
							data_f['jh'] = datas[cur_ind].get('jh')
							data_f['floor'] = datas[cur_ind].get('floor')
							data_f['name'] = datas[cur_ind].get('name')
							data_f['phone'] = datas[cur_ind].get('phone')
							data_f['ywzt'] = datas[cur_ind].get('ywzt')
							data_f['yhzt'] = datas[cur_ind].get('yhzt')
							floor_list.append(data_f.get('floor'))
							datas_f.append(data_f)
					elif len(repeat_list) > 1:
						fir_ind = repeat_list[0]
						data_f['dz'] = datas[fir_ind].get('dz')
						data_f['zh'] = datas[fir_ind].get('zh')
						data_f['floor'] = datas[fir_ind].get('floor')
						data_f['name'] = datas[fir_ind].get('name')
						data_f['phone'] = datas[fir_ind].get('phone')
						data_f['ywzt'] = datas[fir_ind].get('ywzt')
						data_f['yhzt'] = datas[fir_ind].get('yhzt')
						tmp_zcj = "|"
						for i2 in repeat_list:
							tmp_1 = datas[i2].get('zcj')
							tmp_zcj = tmp_zcj + tmp_1 + "|"
							if datas[i2].get('jh'):
								data_f['jh'] = datas[i2].get('jh')
						data_f['zcj'] = tmp_zcj
						floor_list.append(data_f.get('floor'))
						datas_f.append(data_f)
					counted_list += repeat_list
			total = len(datas_f)
			floor_list = list(set(floor_list))
			floor_list.sort()
			print floor_list
			return {'data': datas_f, 'total': total,'floor': floor_list}
		else:
			return {'total': -1}
	except Exception,e:
		return {'total': -2}
	finally:
		s.get(logout_url)

def from_wanggezhicheng_get_xiaoqu(sAddress):
	url_login = 'http://172.30.67.204:8080/wg/LoginAction.action'
	login_data = {'submitData': '{"username":"13937468716","pwd":"1"}'}
	address_url = 'http://172.30.67.204:8080/wg/getXqListOfBossAction.action'
	address_url1 = 'http://172.30.67.204:8080/wg/getfloorWebAction.action'
	logout_url = 'http://172.30.67.204:8080/wg/mpssLogoutAction.action'
	address_data = {
				'city': '许昌',
				'xiaoqu': sAddress,
				'pageIndex': '0',
				'pageSize': '100',
				'area_code': 'all',
				'grid_code': "'374010001','374010002','374010003','374010004','374010005','374010006','374010007','374010008','374010009','374010010','374010011','374010012','374010013','374010014','374010015','374010016','374010017','374010018','374010019','374010020','374010021','374010022'"
				}
	try:
		s = requests.Session()
		# 登录网格支撑系统
		login = s.post(url_login, data=login_data)
		login_status = login.text
		if login_status == u'登录成功':
			print u'登陆成功'
			address = s.post(address_url1, data=address_data)
			data_address = json.loads(address.content)
			aad =  data_address.get('data')[0]
			print len(aad)
			for i in aad:
				print i
			print len(data_address.get('data'))

			print data_address
			# return json.loads(data_address)
		else:
			pass
			# return {'total': -1}

	except Exception,e:
		print e
		# return {'total': -2}
	finally:
		s.get(logout_url)

if __name__ == "__main__":
	from_wanggezhicheng_get_xiaoqu(u'')
	# from_wanggezhicheng_get_userdata('152100001740')