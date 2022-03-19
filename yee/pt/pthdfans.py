# -!- coding: utf-8 -!-
import cgi
import copy
import logging
import re
import datetime
from urllib.parse import unquote
from bs4 import BeautifulSoup

from yee.pt.nexusprogramsite import NexusProgramSite
from yee.pt.torrentmodels import Torrents, TorrentType, Torrent, PtUserinfo
from yee.pt.ptsiteparser import PTSiteParser


class PTHDFansV1(NexusProgramSite):
    def parse_userinfo(self, text) -> PtUserinfo:
        bs = BeautifulSoup(text, features="lxml")
        info_tr = bs.find('table', id='info_block').find_all('tr')[-1]
        user = PtUserinfo()
        user.username = info_tr.a.text
        user.uid = int(info_tr.a['href'].split('=')[-1])
        user.user_group = info_tr.a['class'][0]
        for font_tag in info_tr.find_all('font'):
            arr = str(font_tag.next_sibling).strip().split(' ')
            if font_tag.text.strip().startswith('分享率'):
                try:
                    if arr[0]:
                        user.share_rate = float(arr[0].replace(',', ''))
                    else:
                        user.share_rate = 0
                except Exception as e:
                    logging.error('分享率解析失败：%s' % font_tag.next_sibling)
                    user.share_rate = 0
            elif font_tag.text.strip().startswith('上传'):
                try:
                    user.upload_size = PTSiteParser.trans_unit_to_mb(float(arr[0]), arr[1])
                except Exception as e:
                    logging.error('上传量解析失败：%s' % font_tag.next_sibling)
                    user.upload_size = 0
            elif font_tag.text.strip().startswith('下载'):
                try:
                    user.download_size = PTSiteParser.trans_unit_to_mb(float(arr[0]), arr[1])
                except Exception as e:
                    logging.error('下载量解析失败：%s' % font_tag.next_sibling)
                    user.download_size = 0
        if user.user_group.startswith('VIP'):
            user.vip = True
        return user

    def get_site(self):
        """
        返回pt站的网址
        :return:
        """
        return 'https://hdfans.org/'

    def get_site_name(self):
        """
        这是pt网站的名称，确保唯一即可，集成到主程序时用作配置项
        :return:
        """
        return 'pthdfans'

    def parse_torrents(self, text: str) -> Torrents:
        """
        通过返回的网页代码，解析列表页种子的所有信息
        :param text: 网页源代码
        :return:
        """
        soup = BeautifulSoup(text, features="lxml")
        search_result = []
        if not soup.find('table', class_='torrents'):
            return []
        try:
            find_tr = soup.find('table', class_='mainouter').find('table', class_='torrents').findAll('tr')[1:]
        except Exception as e:
            find_tr = []
        for i, item in enumerate(find_tr):
            rowfollow_tag = item.findAll('td', 'rowfollow')
            if len(rowfollow_tag) != 0:
                t = Torrent()
                t.site_name = self.get_site_name()
                t.site = self.get_site()
                # 获取type/media_source
                find_imgs = rowfollow_tag[0].findAll('img')
                # 获取类型
                t.primitive_type = find_imgs[0].get('alt')
                if t.primitive_type == 'Movies/电影':
                    t.type = TorrentType.Movie
                    t.cate = TorrentType.Movie.value
                elif t.primitive_type in ['TV Series/电视剧', 'TV Shows/综艺']:
                    t.type = TorrentType.Series
                    t.cate = TorrentType.Series.value
                elif t.primitive_type == 'Music/音乐':
                    t.type = TorrentType.Music
                    t.cate = TorrentType.Music.value
                elif t.primitive_type == 'Documentaries/纪录片':
                    t.type = TorrentType.Other
                    t.cate = '纪录片'
                elif t.primitive_type == 'Animations/动漫、动画':
                    t.type = TorrentType.Other
                    t.cate = '动漫'
                else:
                    t.type = TorrentType.Other
                    t.cate = TorrentType.Other.value
                # 获取 id/name/url
                a_label = rowfollow_tag[1].find('a')
                t_id = a_label.get('href').split('&')[0][15:]
                t.id = int(t_id)
                t.name = a_label.get('title')
                t.url = self.get_site() + '/' + 'download.php?id=' + t_id
                # 获取object
                if "Free" in rowfollow_tag[1].findAll('img')[0].get('alt'):
                    t_free_deadline = re.findall('剩余时间：<span title="([^"]+)"', str(rowfollow_tag[1]))
                    if len(t_free_deadline) == 0:
                        t.free_deadline = datetime.datetime.max
                    else:
                        t.free_deadline = datetime.datetime.strptime(t_free_deadline[0], '%Y-%m-%d %H:%M:%S')
                object_tag = copy.copy(rowfollow_tag[1])
                [s.extract() for s in rowfollow_tag[1].find_all("a")]
                [s.extract() for s in rowfollow_tag[1].find_all("b")]
                [s.extract() for s in rowfollow_tag[1].find_all("div")]
                [s.extract() for s in rowfollow_tag[1].find_all("img")]
                [s.extract() for s in rowfollow_tag[1].find_all("span")]
                subject = rowfollow_tag[1].text.replace('剩余时间：', '').strip()
                if subject == '':
                    subject = object_tag.find('b').text
                t.subject = subject
                # 获取种子发布时间
                t.publish_time = datetime.datetime.strptime(rowfollow_tag[3].find('span').get('title'),
                                                            '%Y-%m-%d %H:%M:%S')
                # 获取文件大小
                t_file_size_re = re.findall('([1-9]\d*\.?\d*)(TiB|GiB|MiB|KiB|TB|GB|MB|KB)', rowfollow_tag[4].text)
                t.file_size = PTSiteParser.trans_unit_to_mb(float(t_file_size_re[0][0]), t_file_size_re[0][1])
                # 做种人数
                t.upload_count = int(rowfollow_tag[5].text.replace(',', ''))
                if rowfollow_tag[5].find('span') is not None or rowfollow_tag[5].find('font') is not None:
                    t.red_seed = True
                # 下载人数
                t.download_count = int(rowfollow_tag[6].text.replace(',', ''))
                search_result.append(t)
        return search_result

    def parse_download_filename(self, response):
        if 'Content-Disposition' not in response.headers:
            print(response.headers)
            return None
        value, params = cgi.parse_header(unquote(response.headers['Content-Disposition']))
        return params['filename']
