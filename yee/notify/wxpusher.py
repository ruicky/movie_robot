import logging

from yee.core.httputils import RequestUtils
from yee.core.stringutils import StringUtils
from yee.notify.notify import Notify

"""
wxpusher 通知
"""


class WxpusherNotify(Notify):
    req = RequestUtils(request_interval_mode=False)

    def __init__(self, **args):
        args.setdefault('appToken', None)
        self.args = args
        self.appToken = args['appToken']
        self.message_template = args['message_template']

    def getUids(self, context: dict):
        context.setdefault('nickname', None)
        uids = []
        if 'uid' in self.args.keys():
            uids.append(self.args['uid'])
        users = self.args.get('users')
        if users is not None and len(users) > 0:
            for user in users:
                user.setdefault('nickname', None)
                user.setdefault('uid', None)
                if user['uid'] is not None and user['nickname'] == context['nickname']:
                    uids.append(user['uid'])
        if len(uids) > 0:
            return list(dict.fromkeys(uids))
        else:
            return None

    def send(self, message_template: str, context: dict):
        if message_template not in self.message_template:
            logging.error('找不到通知消息模版：%s' % (message_template))
            return
        if self.appToken is None:
            logging.error('请设置appToken')
            return
        mt = self.message_template[message_template]
        title = mt['title']
        message_pattern = mt['message']
        uids = self.getUids(context)
        if uids is None or len(uids) < 1:
            logging.error('没有可用的uid，无法推送')
            return
        res = self.req.post_json('http://wxpusher.zjiecode.com/api/send/message', json={
            'appToken': self.appToken,
            'uids': uids,
            'contentType': 3,
            'summary': StringUtils.replace_var(title, context),
            'content': StringUtils.replace_var(message_pattern, context),
            'url': context['url']
        }).json()
        if res['code'] != 1000:
            logging.error('wxpusher推送失败：%s' % res.json())
