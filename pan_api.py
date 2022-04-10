import os
import time
import webbrowser
import requests


# 1、配置开放平台应用
# 2、获取授权code
# 3、获取授权auth_code与refresh_code
def access_code(func):
    """
    获取授权更新装饰器
    :param func:
    :return:
    """
    def wrapper(self):
        if os.path.exists("refresh"):
            with open("refresh", "r") as refresh:
                self.refresh_token = refresh.read()
        url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=refresh_token&refresh_token={}&client_id={}&client_secret={}".format(
            self.refresh_token, self.app_key, self.secret_key
        )
        res: dict = requests.get(url).json()
        self.access_token = res.get("access_token")
        self.refresh_token = res.get("refresh_token")
        with open("refresh", 'w') as refresh:
            refresh.write(res.get("refresh_token"))
        time.sleep(0.5)
        result = func(self)
        return result
    return wrapper


class PanApi(object):
    """
    百度网盘api接口实现
    """
    def __init__(self, name: str, app_id: str, app_key: str, secret_key: str, code: str, path: str):
        self.path: str = path
        self.download_path: str = '.' + path + '/'
        self.download_link: str = ""
        self.file_name: str = ""
        self.app_id: str = app_id
        self.app_key: str = app_key
        self.secret_key: str = secret_key
        # 复制获取到的授权码填入下列code
        self.code: str = code
        self.refresh_token: str = ""
        self.access_token: str = ""
        url: str = "http://openapi.baidu.com/oauth/2.0/authorize?response_type=code&scope=basic,netdisk&redirect_uri=oob&client_id={}&device_id={}".format(
            self.app_key, self.app_id
        )
        if len(self.code) == 0:
            webbrowser.open(url)
        if os.path.exists("refresh"):
            with open("refresh", "r") as refresh:
                self.refresh_token = refresh.read()
        if len(self.refresh_token) == 0 and len(self.code) != 0:
            self.get_auth_by_code()

    def get_auth_by_code(self):
        """
        依据code获取对应的auth_token
        :return:
        """
        url: str = "https://openapi.baidu.com/oauth/2.0/token?grant_type=authorization_code&redirect_uri=oob&code={}&client_id={}&client_secret={}".format(
            self.code, self.app_key, self.secret_key
        )
        res: dict = requests.get(url).json()
        self.refresh_token: str = res.get("refresh_token")
        self.access_token: str = res.get("access_token")
        with open("refresh", 'w') as refresh:
            refresh.write(res.get("refresh_token"))
        time.sleep(0.5)
        # print("refresh_token:" + res.get("refresh_token"))

    @access_code
    def get_user_info(self):
        """
        获取登录用户信息
        :return: 用户dict
        """
        url: str = "https://pan.baidu.com/rest/2.0/xpan/nas?method=uinfo&access_token={}".format(self.access_token)
        return requests.get(url).json()

    @access_code
    def get_file_list(self):
        """
        递归获取文件列表
        :return:
        """
        url: str = "http://pan.baidu.com/rest/2.0/xpan/multimedia?method=listall&path={}&access_token={}&web=1&recursion=1&start=0".format(self.path, self.access_token)
        headers: dict = {
            'User-Agent': 'pan.baidu.com'
        }
        # print(requests.get(url, headers=headers).json())
        return requests.get(url, headers=headers).json().get("list")

    def get_fs_id(self):
        fs_id_list: list = []
        file_list: list = self.get_file_list()
        for item in file_list:
            if self.path in item["path"]:
                fs_id_list.append(item["fs_id"])
        return fs_id_list

    @access_code
    def get_download_link(self):
        fs_id_list: list = self.get_fs_id()
        download_link_list: list = []
        url: str = "http://pan.baidu.com/rest/2.0/xpan/multimedia?method=filemetas&access_token={}&fsids={}&thumb=1&dlink=1&extra=1".format(
            self.access_token, fs_id_list
        )
        headers = {
            'User-Agent': 'pan.baidu.com'
        }
        res_list = requests.get(url, headers=headers).json().get("list")
        for item in res_list:
            download_link_list.append(item["dlink"])
        return download_link_list

    @access_code
    def download(self):
        headers: dict = {
            'User-Agent': 'pan.baidu.com'
        }
        url: str = self.download_link + '&access_token={}'.format(self.access_token)
        res = requests.get(url, headers=headers)
        print("开始下载" + self.download_path + self.file_name + ".7z")
        path = self.download_path + self.file_name + '.7z'
        with open(path, "wb") as file:
            file.write(res.content)
            file.close()
        print(self.download_path + self.file_name + '.7z' + "下载结束")

    def batch_download(self):
        download_link_list: list = self.get_download_link()
        for item in download_link_list:
            self.download_link = item
            self.file_name = "{:03}".format(download_link_list.index(item) + 1)
            self.download()
