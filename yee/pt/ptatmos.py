import cgi
import datetime
import re
from urllib.parse import unquote

from bs4 import BeautifulSoup
from yee.core.torrentmodels import Torrent, Torrents, TorrentType
from yee.pt.nexusprogramsite import NexusProgramSite
from yee.pt.ptsiteparser import PTSiteParser


class PTAtmos(NexusProgramSite):
    def get_site(self):
        """
        返回pt站的网址
        :return:
        """
        return 'https://hdatmos.club'

    def get_site_name(self):
        """
        这是pt网站的名称，确保唯一即可，集成到主程序时用作配置项
        :return:
        """
        return 'ptatmos'

    def parse_torrents(self, text: str) -> Torrents:
        """
        通过返回的网页代码，解析列表页种子的所有信息
        :param text:
        :return:
        """
        soup = BeautifulSoup(text, features="lxml")
        if not soup.find('table', class_="torrents"):
            return []
        search_result = []
        for row in soup.find('table', class_="torrents").findAll('tr', recursive=False)[1:]:
            t = Torrent()
            t.site_name = self.get_site_name()
            t.site = self.get_site()
            for i, item in enumerate(row.findAll('td', recursive=False)[:-1]):
                if i == 0:
                    t.primitive_type = item.select_one('a img')['title']
                    if "电影" in t.primitive_type:
                        t.type = TorrentType.Movie
                        t.cate = TorrentType.Movie.value
                    elif "电视剧" in t.primitive_type:
                        t.type = TorrentType.Series
                        t.cate = TorrentType.Series.value
                    elif "音乐" in t.primitive_type:
                        t.type = TorrentType.Music
                        t.cate = TorrentType.Music.value
                    elif "纪录片" in t.primitive_type:
                        t.type = TorrentType.Other
                        t.cate = '纪录片'
                    elif "动漫" in t.primitive_type:
                        t.type = TorrentType.Other
                        t.cate = '动漫'
                    else:
                        t.type = TorrentType.Other
                        t.cate = TorrentType.Other.value
                elif i == 1:
                    info = item.select('table tr td.embedded')[0]
                    a = info.select_one('a[title]')
                    t.name = a['title']
                    t.id = re.findall('id=(\d+)', a['href'])[0]
                    deadline = info.select_one('b span[title]')
                    if deadline:
                        t.free_deadline = datetime.datetime.strptime(deadline['title'], '%Y-%m-%d %H:%M:%S')
                    else:
                        t.free_deadline = datetime.datetime.max
                    subject = ''
                    if info.select_one('br'):
                        subject = info.select_one('br').next_sibling
                    t.subject = subject
                    t.url = self.get_site() + '/download.php?id=' + t.id
                elif i == 3:
                    t.publish_time = datetime.datetime.strptime(item.select_one('span[title]')['title'], '%Y-%m-%d %H:%M:%S')
                elif i == 4:
                    t.file_size = PTSiteParser.trans_unit_to_mb(float(item.contents[0]), item.contents[2])
                elif i == 5:
                    red = item.select_one('span[class="red"]') or item.select_one('font[color]')
                    if red:
                        t.upload_count = int(red.string)
                        t.red_seed = True
                    else:
                        t.upload_count = int(item.select_one('a').string.replace(',', ''))

                elif i == 7:
                    t.download_count = int(item.select_one('a b').string.replace(',', '') if item.select_one('a b') else 0)
            search_result.append(t)
            # 这里需要去解析种子中的剧集年份，可以留空，集成到主框架时，我可以改这个细节
            # t.movies_release_year = mp.parse_year_by_str_list([t.name, t.subject])
            # 匹配种子发布时间、文件大小、大小单位、做种数量,是否红种、下载数量

        return search_result

    def parse_download_filename(self, response):
        if 'Content-Disposition' not in response.headers:
            print(response.headers)
            return None
        value, params = cgi.parse_header(unquote(response.headers['Content-Disposition']))
        return params['filename']
