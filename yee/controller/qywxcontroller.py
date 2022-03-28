import logging
import threading
import xml.etree.ElementTree as ET

from cacheout import Cache
from flask import Blueprint, request

from yee.common.apiresult import api_result
from yee.pt.torrentmodels import Torrents
from yee.register.config_register import base_config
from yee.register.service_register import download_service, movie_service, notify_service
from yee.service.movieservice import MovieService
from yee.service.notifyservice import NotifyService
from yee.service.siteservice import UseSource

qywx = Blueprint('qywx', __name__)
token_cache = Cache(maxsize=256, ttl=3600, default=None)

"""
企业微信搜索处理线程
"""


class QywxSearchThread(threading.Thread):
    def __init__(self, movie_service: MovieService, notify_service: NotifyService, keyword: str,
                 touser: str, agent_id: str, server_url):
        threading.Thread.__init__(self)
        self.name = 'qywx-search'
        self.keyword = keyword
        self.movie_service = movie_service
        self.notify_service = notify_service
        self.touser = touser
        self.agent_id = agent_id
        self.server_url = server_url

    def run(self):
        try:
            """
            搜索后调用机器人的策略排序接口进行排序，控制返回给微信的搜索结果在5条
            取3条compress排序结果，2条compact排序结果
            """
            result: Torrents = self.movie_service.search_keyword(self.keyword, use_source=UseSource.WEB_SEARCH,
                                                                 torrent_cache=True)
            if result is None or len(result) == 0:
                self.notify_service.get_qywx().send_text(self.touser, f'{self.keyword} 搜索不到任何结果',
                                                         agent_id=self.agent_id)
                return
            push_result: Torrents = []
            push_resids: set = set()
            if len(result) <= 5:
                push_result = result
            else:
                """
                取3条compress结果，2条compact结果
                """
                self.movie_service.sort_utils.sort(None, result, rule_name='compress', search_keyword=self.keyword)
                i = 0
                while i < 3:
                    t = result[i]
                    i += 1
                    if t.id in push_resids:
                        continue
                    push_result.append(t)
                    push_resids.add(t.id)
                self.movie_service.sort_utils.sort(None, result, rule_name='compact', search_keyword=self.keyword)
                i = 0
                while i < 2:
                    t = result[i]
                    i += 1
                    if t.id in push_resids:
                        continue
                    push_result.append(t)
                    push_resids.add(t.id)
            for t in push_result:
                # 调用企业微信通知接口发送文本卡片通知
                self.notify_service.get_qywx().send_textcard(
                    self.touser, {
                        "title": f"{self.keyword} 来自{t.site_name}的搜索结果",
                        "description": f"<div>标题：{t.subject}</div><div>种子：{t.name}</div><div>尺寸：{round(t.file_size / 1024, 2)}GB</div><div>做种：{t.upload_count} 下完：{t.download_count}</div><div class=\"highlight\">点击立即开始下载</div>",
                        "url": f'{self.server_url}/api/qywx/download_torrent?id={t.id}&site_name={t.site_name}&token={token_cache.get("token")}',
                        "btntxt": "点击立即开始下载"
                    },
                    agent_id=self.agent_id
                )

        except Exception as e:
            logging.error('企业微信搜索失败：%s' % e, exc_info=True)


@qywx.route('/download_torrent', methods=["GET", "POST"])
def download_torrent():
    token = request.args.get('token')
    if token is None or token == '':
        return api_result(code=1, message='无权访问')
    if token != token_cache.get("token"):
        return api_result(code=1, message='已经无法下载，微信搜索仅支持下载最新关键字的搜索结果。')
    id = request.args.get('id')
    if id is None or id == '':
        return api_result(code=1, message='id为空')
    site_name = request.args.get('site_name')
    if site_name is None or site_name == '':
        return api_result(code=1, message='site_name为空')
    torrent = movie_service.get_torrent_by_id(site_name, id)
    if not torrent:
        return api_result(code=1, message='搜索结果太久没有点击下载会过期，请重新搜索后再下点击下载！')

    t = threading.Thread(target=download_service.free_download,
                         args=(torrent,))
    t.start()
    return api_result(code=0, message='提交下载任务成功，几秒后便可在下载记录查看。')


@qywx.route('/receive', methods=["GET", "POST"])
def receive():
    try:
        wxcpt = notify_service.get_wxcpt()
        if wxcpt is None:
            logging.error('没有配置企业微信的接收消息设置，不能使用此功能。')
            return '', 500
        sign = request.args.get('msg_signature')
        ts = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        if request.method == 'GET':
            """
            GET请求为应用设置接收API时的验证请求
            """
            verify_echo_str = request.args.get('echostr')
            ret, raw_echo_str = wxcpt.VerifyURL(sign, ts, nonce, verify_echo_str)
            if ret != 0:
                logging.error("ERR: VerifyURL ret: " + str(ret))
                return '', 401
            return raw_echo_str
        elif request.method == 'POST':
            post_data = request.data
            ret, rmsg = wxcpt.DecryptMsg(post_data, sign, ts, nonce)
            if ret != 0:
                logging.error("ERR: DecryptMsg ret: " + str(ret))
                return '', 401
            else:
                xml_tree = ET.fromstring(rmsg)
                content = xml_tree.find("Content").text
                touser = xml_tree.find('ToUserName').text
                fromuser = xml_tree.find('FromUserName').text
                agent_id = xml_tree.find('AgentID').text
                # 直接回复一条消息，提示搜索中，这个回复必须5秒内完成，不能做太多操作，不然微信会处理超时
                res_msg = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{xml_tree.find('CreateTime').text}</CreateTime><MsgType>{xml_tree.find('MsgType').text}</MsgType><Content>{content} 搜索中...</Content><MsgId>{xml_tree.find('MsgId').text}</MsgId><AgentID>{agent_id}</AgentID></xml>"
                ret, encrypt_msg = wxcpt.EncryptMsg(res_msg, nonce, ts)
                if ret != 0:
                    logging.error("ERR: EncryptMsg ret: " + str(ret))
                    return '', 401
                token_cache.set('token', sign)
                st = QywxSearchThread(movie_service, notify_service, content, fromuser,
                                      agent_id,
                                      base_config.web.get('server_url'))
                st.start()
                return encrypt_msg, 200
    except Exception as e:
        logging.error('处理微信消息出错。', exc_info=True)
        return '', 200
