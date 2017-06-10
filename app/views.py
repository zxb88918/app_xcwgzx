# -*- coding: UTF-8 -*-
from app import app
from flask import render_template, request, make_response, url_for,jsonify
from flask import redirect, session
from form import testform, rssiform, cnuform
from cnu import from_9303_get_data, from_ceview_get_data, from_wocweb_get_topo, from_wocweb_get_rssi, from_wanggezhicheng_get_data
import hashlib
import time
import xml.etree.ElementTree as ET
from msg_response import content_handle
from my_model import from_ceview_get_data1, from_wanggezhicheng_get_data1, from_jierurenzheng_get_data1,from_wocweb_get_rssi1, from_wocweb_set_rssi1, get_yanling_transceiver, get_yanling_status, from_ceview_get_wocip,from_ceview_get_data2
import time
import json
from test import get_news
from myModel_wgzc import from_wanggezhicheng_get_address, from_wanggezhicheng_get_userdata
from my_db import db_login,db_get_cnudatas_from_database ,db_get_wocip_from_cbat
from zSwitch import from_olt_get_pon,from_woc_get_rssi, from_woc_get_cnurssi

@app.route('/', methods=('GET', 'POST'))
def index():
    return u'测试-ok'


# 微信订阅号认证及消息回复路由
@app.route('/weixin/auth/zhangxiaobo_8888', methods=('GET', 'POST'))
def weixin_auth():
    if request.method == 'GET':
        token = 'woxianggaibianshijie'
        query = request.args
        signature = query.get('signature', '')
        print signature
        timestamp = query.get('timestamp', '')
        print timestamp
        nonce = query.get('nonce', '')
        print nonce
        echostr = query.get('echostr', '')
        print echostr
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        print s
        if (hashlib.sha1(s).hexdigest() == signature):
            print echostr
            return make_response(echostr)
    else:
        rec = request.stream.read()
        xml_rec = ET.fromstring(rec)
        print xml_rec
        msg_type = xml_rec.find('MsgType').text
        tou = xml_rec.find('ToUserName').text
        fromu = xml_rec.find('FromUserName').text
        news_rep = u'''
                    <xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[news]]></MsgType>
                    <ArticleCount>1</ArticleCount>
                    <Articles>
                    <item>
                    <Title><![CDATA[查询结果-%s]]></Title>
                    <Description><![CDATA[%s]]></Description>
                    </item>
                    </Articles>
                    </xml>
                  '''
        news_cnu = u'''
        <xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[news]]></MsgType>
            <ArticleCount>1</ArticleCount>
            <Articles>
                <item>
                    <Title><![CDATA[查询结果-%s]]></Title>
                    <Description><![CDATA[%s]]></Description>
                    <PicUrl><![CDATA[%s]]></PicUrl>
                    <Url><![CDATA[%s]]></Url>
                </item>
            </Articles>
        </xml>
        '''
        multi_news = u'''
                    <xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[news]]></MsgType>
                    <ArticleCount>4</ArticleCount>
                    <Articles>
                    <item>
                    <Title><![CDATA[您的查询结果-[%s]]]></Title>
                    </item>
                    <item>
                    <Title><![CDATA[%s]]></Title>
                    </item>
                    <item>
                    <Title><![CDATA[%s]]></Title>
                    </item>
                    <item>
                    <Title><![CDATA[【接入认证信息】\r\n调试中......]]></Title>
                    </item>
                    </Articles>
                    </xml>
                    '''
        text_rep = '''
                    <xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[%s]]></Content>
                    <FuncFlag>0</FuncFlag>
                    </xml>
                  '''
        news_img_url = 'http://www.zhangxiaobo.net/static/img/cnu.jpg'

        print msg_type
        # 判断微信发送的消息类型为‘text’
        if msg_type == 'text':
            content = xml_rec.find('Content').text
            res_content = content_handle(content)
            url_ip_rep = 'http://www.zhangxiaobo.net/cbat/woc/%s' % content
            url_cnu_rep = 'http://www.zhangxiaobo.net/cbat/cnu/%s' % content
            # 判断用户输入的是ip地址还是mac地址

            if res_content.get('type') == 'cnu':
                text_response = make_response(news_cnu % (fromu, tou, str(int(time.time())), content, u'温馨提示：受限于部分数据响应时间较慢，超过微信公众平台5s重传的限制，造成【该公众号暂时无法提供服务，请稍后再试】的回复，为了给您更好的体验，请点击本消息查看详细信息，点击后自动跳转到查询结果页面，请耐心等待！', news_img_url, url_cnu_rep))
                print url_cnu_rep
                text_response.content_type = 'application/xml'
                return text_response
            elif res_content.get('type') == 'ip':
                news_ip_response = make_response(news_rep % (fromu, tou, str(int(time.time())), content, res_content.get('data')))
                news_ip_response.content_type = 'application/xml'
                return news_ip_response
            else:
                text_response = make_response(text_rep % (fromu, tou, str(int(time.time())), res_content.get('data')))
                text_response.content_type = 'application/xml'
                return text_response
        # 判断微信传来的消息类型为事件
        elif msg_type == 'event':
            event_content = xml_rec.find('Event').text
            if event_content == 'subscribe':
                print news_img_url
                event_response_news = make_response(news_rep % (fromu, tou, str(int(time.time())), u'这里是【张晓波api测试】\r\n感谢您的关注！', u'暂开放功能：\r\n1、输入高频mac地址查询链路信息及用户信息；\r\n2、输入高频ip查询当前rssi抑制状态，并自动消除rssi抑制状态。'))
                event_response_news.content_type = 'application/xml'
                return event_response_news

        elif msg_type == 'image':
            img_response = make_response(text_rep % (fromu, tou, str(int(time.time())), u'别没事发图片！'))
            img_response.content_type = 'application/xml'
            return img_response
        elif msg_type == 'voice':
            voi_response = make_response(text_rep % (fromu, tou, str(int(time.time())), u'别没事发语音！'))
            voi_response.content_type = 'application/xml'
            return voi_response
        elif msg_type == 'video':
            vid_response = make_response(text_rep % (fromu, tou, str(int(time.time())), u'别没事发图片！'))
            vid_response.content_type = 'application/xml'
            return vid_response
        elif msg_type == 'shortvideo':
            short_response = make_response(text_rep % (fromu, tou, str(int(time.time())), u'别没事发短视频！'))
            short_response.content_type = 'application/xml'
            return short_response
        elif msg_type == 'location':
            loc_response = make_response(text_rep % (fromu, tou, str(int(time.time())), u'别没事发位置信息！'))
            loc_response.content_type = 'application/xml'
            return loc_response
        elif msg_type == 'link':
            link_response = make_response(text_rep % (fromu, tou, str(int(time.time())), u'别没事发链接！'))
            link_response.content_type = 'application/xml'
            return link_response
    return 'Hello weixin!'


@app.route('/test1', methods=('GET', 'POST'))
def test1():
    fqd = None
    cnumac = None
    ip_data = None
    ceview_data = {"mac": ''}
    form = testform()
    if form.validate_on_submit():

        fqd = form.fqd.data
        cnumac = form.cnumac.data
        form.cnumac.data = ""
        ceview_data = from_ceview_get_data(cnumac)
        ip_data = from_9303_get_data(cnumac, str(fqd)).get('ip')
    return render_template('test1.html', form=form, cnumac=cnumac, fqd=fqd, ip_data=ip_data, ceview_data=ceview_data)

@app.route('/app/login', methods=('GET', 'POST'))
def app_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return jsonify(db_login(username,password))

@app.route('/cbat/woc/<wocip>', methods=('GET', 'POST'))
def cbat_woc(wocip):
    return render_template('cnu.html')

@app.route('/app/wy/cnudatas/all', methods=('GET', 'POST'))
def app_wy_cnudatas_all():
    if request.method == 'POST':
        address = request.form.get('address')
        return jsonify(db_get_cnudatas_from_database(address,0))

@app.route('/app/wy/cnudatas/unqualified', methods=('GET', 'POST'))
def app_wy_cnudatas_unqualified():
    if request.method == 'POST':
        address = request.form.get('address')
        return jsonify(db_get_cnudatas_from_database(address,1))

@app.route('/cbat/cnu/<cnumac>', methods=('GET', 'POST'))
def cnu(cnumac):
    # ceview_data = None
    t1 = time.time()
    ceview_data = from_ceview_get_data1(cnumac)
    wgzc_data = from_wanggezhicheng_get_data1(cnumac)
    jrrz_data = from_jierurenzheng_get_data1(cnumac)
    print ceview_data
    print wgzc_data
    print jrrz_data
    t2 = time.time()
    print t2-t1
    # print ceview_data
    return render_template('cnu.html', cnumac=cnumac, ceview_data=ceview_data, wgzc_data=wgzc_data, jrrz_data=jrrz_data)


@app.route('/cbat/woc/topo/<woc_ip>', methods=('GET', 'POST'))
def topo(woc_ip):
    pass


@app.route('/cbat/cc/<cnumac>', methods=('GET', 'POST'))
def cc(cnumac):
    ceview_data = from_ceview_get_data1(cnumac)
    wgzc_data = from_wanggezhicheng_get_data1(cnumac)
    jrrz_data = from_jierurenzheng_get_data1(cnumac)
    ceview_list = []
    wgzc_list = []
    jrrz_list = []
    ceview_list.append(json.loads(ceview_data))
    wgzc_list.append(json.loads(wgzc_data))
    jrrz_list.append(json.loads(jrrz_data))
    data = {'ceview': ceview_list, 'wgzc': wgzc_list, 'jrrz': jrrz_list}
    res = make_response(json.dumps(data))
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    print jrrz_data
    return res


@app.route('/app/rssi/getwocip/<cnumac>', methods=('GET', 'POST'))
def rssi_get_wocip(cnumac):
    wocip = from_ceview_get_wocip(cnumac)
    print wocip
    return jsonify(wocip)


@app.route('/app/rssi/getrssi/<wocip>', methods=('GET', 'POST'))
def rssigetrssi(wocip):
    rssi_status = from_wocweb_get_rssi1(wocip)
    print type(rssi_status)
    print rssi_status
    return jsonify(rssi_status)


@app.route('/app/rssi/setrssi/on/<wocip>', methods=('GET', 'POST'))
def set_rssi_on(wocip):
    rssi_status = from_wocweb_set_rssi1(wocip, 'on')
    return jsonify(rssi_status)


@app.route('/app/rssi/setrssi/off/<wocip>', methods=('GET', 'POST'))
def set_rssi_off(wocip):
    rssi_status = from_wocweb_set_rssi1(wocip, 'off')
    print type(rssi_status)
    print rssi_status
    return jsonify(rssi_status)


@app.route('/app/update', methods=('GET', 'POST'))
def updata():
    print request.args.get('version')
    if request.args.get('version') == '1.0.2.20170525':
        return jsonify({'update': True})
    else:
        return jsonify({'update': False, 'url_update': 'http://www.zhangxiaobo.net:39022/static/app/H547299E0_0524031036.apk'})


@app.route('/app/news', methods=('GET', 'POST'))
def news():
    if request.method == 'POST':
        data = get_news()
        print data
        return jsonify(data)


@app.route('/app/yanling', methods=('GET', 'POST'))
def yanling():
    status = get_yanling_status()
    transcevier = get_yanling_transceiver()
    return jsonify({'status':status, 'transcevier':transcevier})


@app.route('/app/wgzc/address/<address>', methods=('GET', 'POST'))
def wgzx_address(address):
    data = from_wanggezhicheng_get_address(address)
    return jsonify(data)


@app.route('/app/wgzc/userdata/<addresscode>', methods=('GET', 'POST'))
def wgzx_userdata(addresscode):
    data = from_wanggezhicheng_get_userdata(addresscode)
    return jsonify(data)


@app.route('/app/cnu/info/<cnumac>', methods=('GET', 'POST'))
def get_cnu_info(cnumac):
    cableInfo = from_ceview_get_data1(cnumac)
    userInfo = from_wanggezhicheng_get_data1(cnumac)
    authInfo = from_jierurenzheng_get_data1(cnumac)
    print cableInfo
    return jsonify({'cableinfo': cableInfo, 'userinfo': userInfo, 'authinfo': authInfo, 'success': 'success'})

@app.route('/app/cnu/rssi', methods=('GET', 'POST'))
def get_cnu_rssi():
    if request.method == 'POST':
        cableInfo = from_ceview_get_data2(request.form.get('cnumac'))

        return jsonify(cableInfo)


@app.route('/app/wy/getwyinfo', methods=('GET', 'POST'))
def get_wy_info():
    if request.method == 'POST':
        print request.form.get('nickname')
        print request.form.get('cnumac')
        print request.form.get('oldrssi')
        return jsonify({'status':True})

@app.route('/app/wy/fromoltgetwocip', methods=('GET', 'POST'))
def from_olt_get_wocip():
    if request.method == 'POST':
        olt_ip = ['172.21.0.30','172.21.7.18','172.21.6.18','172.21.5.18','172.21.4.18']
        table_name = ['cbat_qjl','cbat_jadd','cbat_ldl','cbat_gml','cbat_syhc']
        cnumac = request.form.get('cnumac')
        fqd_num = request.form.get('fqd')

        print olt_ip[int(fqd_num)]
        pon_num = from_olt_get_pon(cnumac, olt_ip[int(fqd_num)])
        if pon_num.get('status'):
            data = db_get_wocip_from_cbat(pon_num.get('data'),table_name[int(fqd_num)])
            return jsonify(data)
        else:
            return jsonify(pon_num)

@app.route('/app/wy/getwytopology', methods=('GET', 'POST'))
def get_wy_topology():
    if request.method == 'POST':
        wocip = request.form.get('wocip')
        print wocip
        data = from_woc_get_rssi(wocip)
        print 'aaa'
        print data
        return jsonify(data)

@app.route('/app/wy/getcnurssi', methods=('GET', 'POST'))
def get_wy_getcnurssi():
    if request.method == 'POST':
        wocip = request.form.get('wocip')
        cnumac = request.form.get('cnumac')
        print wocip
        data = from_woc_get_cnurssi(wocip,cnumac)
        return jsonify(data)

