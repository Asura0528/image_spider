import os

from spider_gteman import SpiderGteman
from deal_file import deal_file

name = 'rioko凉凉子'
# 爬取宅特曼
spider_gteman = SpiderGteman("875778210@qq.com", "axlxmlt", name)
# vip 一天只有五次
# spider_gteman.vip_download()
spider_gteman.download()
# 百度网盘数据下载

path = r'\\192.168.0.101\39008675\我的图片\{}'.format(name)
deal_file(os.listdir(path), name)
