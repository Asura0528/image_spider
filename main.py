from spider_gteman import SpiderGteman

# 需要下载的名字
name = '可可老师'
# 爬取宅特曼
spider_gteman = SpiderGteman("875778210@qq.com", "axlxmlt", name)
# 百度网盘转存
# vip 一天只有五次
# spider_gteman.vip_save()
# spider_gteman.save()
# 百度网盘数据下载
# spider_gteman.batch_download()
# 下载后数据处理
spider_gteman.deal()
