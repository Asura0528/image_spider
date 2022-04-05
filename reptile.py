import re

import requests
import json
from pan_save import BaiDuPan


# 执行步骤
# 1、获取宅特曼 authorization https://www.zteman.net
# 2、登录百度网盘获取 BDUSS和STOKEN https://pan.baidu.com/
def get_id_list(download_name):
    """
    根据名字获取不包含合集的对应下载id列表
    :param download_name: 需要下载的人名
    :return: id列表(不包含合集)
    """
    id_url = 'https://www.zteman.net/tag/' + download_name
    res = requests.get(id_url)
    id_list = re.findall('<li class="post-list-item item-" id="item-(\d+)">', res.text)
    return id_list


def get_vip_id_list(download_name):
    """
    根据名字获取不包含合集的对应下载id列表
    :param download_name: 需要下载的人名
    :return: id列表(不包含合集)
    """
    id_url = 'https://www.zteman.net/tag/' + download_name
    res = requests.get(id_url)
    id_list = re.findall('<li class="post-list-item item-post-style-\d" id="item-(\d+)">', res.text)
    return id_list


def get_vip_url_and_code(post_id, authorization):
    """
    VIP获取对应的百度网盘分享链接和提取码
    :param post_id:下载id
    :return:百度网盘分享链接 + 提取码
    """
    data = {'post_id': post_id, 'index': '0', 'i': '1'}
    header = {
        'authorization': authorization}
    get_download_data_res = requests.post("https://www.zteman.net/wp-json/b2/v1/getDownloadPageData", data=data,
                                          headers=header)
    print(get_download_data_res.text.encode('utf-8'))
    token = json.loads(get_download_data_res.text).get('button').get('url')
    share_code = json.loads(get_download_data_res.text).get('button').get('attr').get('tq')
    decompress_code = json.loads(get_download_data_res.text).get('button').get('attr').get('jy')
    # 重定向
    redirect_res = requests.get('https://www.zteman.net/redirect?token=' + token)
    share_url = redirect_res.url
    print("share_url: " + share_url + "\nshare_code: " + share_code + "\ndecompress_code: " + decompress_code)
    return share_url, share_code


def get_url_and_code(post_id, authorization):
    """
    获取对应的百度网盘分享链接和提取码
    :param post_id:下载id
    :return:
    """
    data = {'id': post_id, 'order_id': 'null'}
    header = {
        'authorization': authorization}
    get_download_data_res = requests.post("https://www.zteman.net/wp-json/b2/v1/getHiddenContent", data=data,
                                          headers=header)
    share_url = re.findall(r'href="(\S+)"', get_download_data_res.text.replace("\\", ""))[0]
    share_code = re.findall(r'<code>(\S+)</code>', get_download_data_res.text.replace("\\", ""))[0]
    decompress_code = re.findall(r'<code>(\S+)</code>', get_download_data_res.text.replace("\\", ""))[1]
    print("share_url: " + share_url + "\nshare_code: " + share_code + "\ndecompress_code: " + decompress_code)
    return share_url, share_code


def save_data(share_url, share_code, download_name):
    """
    百度网盘分享链接转存到自己的网盘,保存到目录：/需要下载/下载人名
    :param share_url: 分享链接
    :param share_code: 提取码
    :param download_name: 下载人名
    :return:
    """
    baidu_pan = BaiDuPan()
    info = baidu_pan.saveShare(share_url, share_code, '/需要下载/{}'.format(download_name))
    print(info)


def vip_download(download_name, authorization):
    share_id_list = get_vip_id_list(download_name)
    share_id = ''
    baidu_pan = BaiDuPan()
    baidu_pan.create_dir('/需要下载/{}'.format(download_name))
    if len(share_id_list) == 1:
        share_id = share_id_list[0]
    else:
        print("获取合集id失败，保存失败")
        return None
    share_url, share_code = get_vip_url_and_code(share_id, authorization)
    save_data(share_url, share_code, download_name)


def download(download_name, authorization):
    share_id_list = get_id_list(download_name)
    baidu_pan = BaiDuPan()
    baidu_pan.create_dir('/需要下载/{}'.format(download_name))
    for share_id in share_id_list:
        share_url, share_code = get_url_and_code(share_id, authorization)
        save_data(share_url, share_code, download_name)


if __name__ == '__main__':
    token = ''
    name = 'rioko凉凉子'
    # vip 一天只有五次
    vip_download(name, token)
    # download(name, token)
