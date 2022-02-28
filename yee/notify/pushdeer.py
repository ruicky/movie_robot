import json
import logging

from yee.core.httputils import RequestUtils
from yee.core.stringutils import StringUtils
from yee.notify.notify import Notify

"""
Pushdeer通知
"""


class PushdeerNotify(Notify):
    req = RequestUtils(request_interval_mode=False)

    def __init__(self, **args):
        self.args = args
        self.api = args['api']
        self.message_template = args['message_template']

    def getPushkey(self, context: dict):
        context.setdefault('nickname', None)
        pushkey = []
        if 'pushkey' in self.args.keys():
            pushkey.append(self.args['pushkey'])
        users = self.args.get('users')
        if users is not None and len(users) > 0:
            for user in users:
                user.setdefault('nickname', None)
                user.setdefault('pushkey', None)
                if user['pushkey'] is not None and user['nickname'] == context['nickname']:
                    pushkey.append(user['pushkey'])
        if len(pushkey) > 0:
            return ','.join(list(dict.fromkeys(pushkey))).strip()
        else:
            return None

    def send(self, message_template: str, context: dict):
        if message_template not in self.message_template:
            logging.error('找不到通知消息模版：%s' % (message_template))
            return
        mt = self.message_template[message_template]
        title = mt['title']
        message_pattern = mt['message']
        pushkey = self.getPushkey(context)
        if pushkey is None:
            logging.error('没有可用的pushkey，无法推送')
            return
        res = self.req.get(self.api, params={
            'pushkey': pushkey,
            'type': 'markdown',
            'text': StringUtils.replace_var(title, context),
            'desp': StringUtils.replace_var(message_pattern, context)
        }).json()
        if res["content"]["result"]:
            result = json.loads(res["content"]["result"][0])
            if result["success"] != "ok":
                logging.error('pushdeer推送失败：%s' % res.json())
