import os
import re
import requests
import json
from pan_api import PanApi
from pan_save import BaiDuPan
from deal_file import deal_file


class SpiderGteman(object):
    def __init__(self, username: str, password: str, download_name: str):
        """
        构建时模拟登录
        :param username: 用户名
        :param password: 密码
        :param download_name: 下载文件名
        :return:
        """
        bduss = ''
        stoken = ''
        app_id = ""
        app_key = ""
        secret_key = ""
        code = ""
        self.path = '/spider_gteman/{}'.format(download_name)
        login_url = 'https://www.zteman.net/wp-json/jwt-auth/v1/token'
        data = {'username': username, 'password': password}
        res = requests.post(login_url, data)
        self.token = "Bearer " + json.loads(res.text).get("token")
        self.download_name = download_name
        self.decompress_code = "gteman.cn"
        self.baidu_pan = BaiDuPan(bduss, stoken)
        self.pan_api = PanApi(download_name, app_id, app_key, secret_key, code, self.path)
        if not os.path.exists('.' + self.path):
            os.makedirs('.' + self.path)

    def get_id_list(self) -> list:
        """
        根据名字获取不包含合集的对应下载id列表
        :return: id列表(不包含合集)
        """
        id_url = 'https://www.zteman.net/tag/' + self.download_name
        res = requests.get(id_url)
        id_list = re.findall('<li class="post-list-item item-" id="item-(\d+)">', res.text)
        return id_list

    def get_vip_id_list(self) -> list:
        """
        根据名字获取不包含合集的对应下载id列表
        :return: id列表(不包含合集)
        """
        id_url = 'https://www.zteman.net/tag/' + self.download_name
        res = requests.get(id_url)
        id_list = re.findall('<li class="post-list-item item-post-style-\d" id="item-(\d+)">', res.text)
        return id_list

    def get_vip_url_and_code(self, post_id: str) -> tuple:
        """
        VIP获取对应的百度网盘分享链接和提取码
        :param post_id:下载id
        :return:百度网盘分享链接 + 提取码
        """
        data = {'post_id': post_id, 'index': '0', 'i': '1'}
        header = {
            'authorization': self.token}
        get_download_data_res = requests.post("https://www.zteman.net/wp-json/b2/v1/getDownloadPageData", data=data,
                                              headers=header)
        print(get_download_data_res.text.encode('utf-8'))
        redirect_token = json.loads(get_download_data_res.text).get('button').get('url')
        share_code = json.loads(get_download_data_res.text).get('button').get('attr').get('tq')
        self.decompress_code = json.loads(get_download_data_res.text).get('button').get('attr').get('jy')
        # 重定向
        redirect_res = requests.get('https://www.zteman.net/redirect?token=' + redirect_token)
        share_url = redirect_res.url
        print("share_url: " + share_url + "\nshare_code: " + share_code + "\ndecompress_code: " + self.decompress_code)
        return share_url, share_code

    def get_url_and_code(self, post_id: str) -> tuple:
        """
        获取对应的百度网盘分享链接和提取码
        :param post_id:下载id
        :return:百度网盘分享链接 + 提取码
        """
        data = {'id': post_id, 'order_id': 'null'}
        header = {
            'authorization': self.token}
        get_download_data_res = requests.post("https://www.zteman.net/wp-json/b2/v1/getHiddenContent", data=data,
                                              headers=header)
        share_url = re.findall(r'href="(\S+)"', get_download_data_res.text.replace("\\", ""))[0]
        share_code = re.findall(r'<code>(\S+)</code>', get_download_data_res.text.replace("\\", ""))[0]
        self.decompress_code = re.findall(r'<code>(\S+)</code>', get_download_data_res.text.replace("\\", ""))[1]
        print("share_url: " + share_url + "\nshare_code: " + share_code + "\ndecompress_code: " + self.decompress_code)
        return share_url, share_code

    def save_data(self, share_url: str, share_code: str):
        """
        百度网盘分享链接转存到自己的网盘,保存到目录：/spider_gteman/下载人名
        :param share_url: 分享链接
        :param share_code: 提取码
        :return:
        """
        info = self.baidu_pan.saveShare(share_url, share_code, self.path)
        print(info)

    def vip_save(self):
        """
        VIP转存,具体看VIP等级,本月有每日五次
        :return: 依据登录取得token拼接而成
        """
        share_id_list = self.get_vip_id_list()
        if not self.baidu_pan.verify_file("spider_gteman"):
            self.baidu_pan.create_dir('/spider_gteman')
        if not self.baidu_pan.verify_file(self.download_name, '/spider_gteman'):
            self.baidu_pan.create_dir('/spider_gteman/{}'.format(self.download_name))
        else:
            print("已存在同名文件夹")
        if len(share_id_list) == 1:
            share_id = share_id_list[0]
        else:
            print("获取合集id失败，保存失败")
            return None
        share_url, share_code = self.get_vip_url_and_code(share_id)
        self.save_data(share_url, share_code)

    def save(self):
        """
        普通用户转存
        :return:
        """
        share_id_list = self.get_id_list()
        if not self.baidu_pan.verify_file("spider_gteman"):
            self.baidu_pan.create_dir('/spider_gteman')
        if not self.baidu_pan.verify_file(self.download_name, '/spider_gteman'):
            self.baidu_pan.create_dir('/spider_gteman/{}'.format(self.download_name))
        else:
            print("已存在同名文件夹")
        for share_id in share_id_list:
            share_url, share_code = self.get_url_and_code(share_id)
            self.save_data(share_url, share_code)

    def batch_download(self):
        """
        批量下载
        :return:
        """
        self.pan_api.batch_download()

    def deal(self):
        """
        下载文件处理
        :return:
        """
        deal_path = '.' + self.path
        deal_file(self.download_name, deal_path, self.decompress_code)
