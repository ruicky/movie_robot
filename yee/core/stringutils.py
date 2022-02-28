import datetime
import math
import re

import cn2an
from lxml import etree
import emoji


class StringUtils:
    @staticmethod
    def str_to_date(strdate, pattern: str) -> datetime:
        if strdate is None or strdate == '':
            return None
        return datetime.datetime.strptime(strdate, pattern)

    @staticmethod
    def str_to_year(strdate, pattern: str) -> datetime:
        if strdate is None or strdate == '':
            return None
        try:
            date = datetime.datetime.strptime(strdate, pattern)
            return date.year
        except Exception as e:
            return None

    @staticmethod
    def trim_emoji(text):
        return emoji.demojize(text)

    @staticmethod
    def trans_number(numstr: str):
        if numstr.isdigit():
            return int(numstr)
        else:
            return cn2an.cn2an(numstr)

    @staticmethod
    def noisestr(text):
        if text is None or len(text) == 0:
            return text
        if len(text) > 2:
            s = 2
        else:
            s = 0
        e = s + math.ceil(len(text) / 2)
        if e == s:
            e += 1
        n = []
        i = 0
        while i < (e - s):
            n.append('*')
            i += 1
        return text.replace(text[s:e], ''.join(n))

    @staticmethod
    def trimhtml(htmlstr):
        try:
            html = etree.HTML(text=htmlstr)
            return html.xpath('string(.)')
        except Exception as e:
            return htmlstr

    @staticmethod
    def replace_var(text, context):
        for m in re.findall(r'\$\{([^\}]+)\}', text):
            var_name = m
            text = text.replace('${%s}' % var_name,
                                str(context[var_name]) if var_name in context else '')
        return text
    @staticmethod
    def split(text, delimiter = '||'):
        if text is None or len(text) == 0:
            return []
        return text.split(delimiter)
    @staticmethod
    def join(arr, delimiter = '||'):
        if arr is None or len(arr) == 0:
            return None
        return delimiter.join(arr).strip()
