import json
import os
import time

import pdfkit
import requests


class MpSpider(object):
    def __init__(self):
        self.count = 0
        self.headers = {
            'Host': 'mp.weixin.qq.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 QQBrowser/9.0.2524.400',
            'X-Request-With': 'XMLHttpRequest',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4'
        }
        self.base_url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz={}&uin=MTY0NjU5NzAwMK==&key={}&offset={}&count=10&f=json'
        self.biz = ''  # 公众号id
        self.key = ''  # token
        self.offset = 0
        self.config = pdfkit.configuration(wkhtmltopdf=r'D:/developer/wkhtmltox/bin/wkhtmltopdf.exe')

    def request_data(self):  # 请求数据
        try:
            response = requests.get(self.base_url.format(self.biz, self.key, self.offset), headers=self.headers)
            if 200 == response.status_code:
                self.parse_data(response.text)
        except Exception as e:
            print(e)
            pass

    def parse_data(self, response_data):  # 解析数据
        all_data = json.loads(response_data)

        if 0 == all_data['ret'] and 1 == all_data['can_msg_continue']:
            general_msg_json = all_data['general_msg_list']
            general_data = json.loads(general_msg_json)['list']
            for data in general_data:
                try:
                    title = data['app_msg_ext_info']['title']
                    content_url = data['app_msg_ext_info']['content_url']
                    copy_right = data['app_msg_ext_info']['copyright_stat']
                    copy_right = '原创文章_' if copy_right == 11 else '非原创文章_'
                    self.count = self.count + 1
                    print('第【{}】篇文章'.format(self.count), copy_right, title, content_url)
                    self.create_pdf_file(content_url, '{}{}'.format(copy_right, title))

                except Exception as e:
                    print(e.__cause__)
                    continue

            time.sleep(3)
            self.offset = all_data['next_offset']  # 下一页的偏移量
            self.request_data()

        else:
            if 0 == all_data['can_msg_continue']:
                exit('数据抓取完毕！')
            else:
                exit('数据抓取出错:' + all_data['errmsg'])

    def create_pdf_file(self, url, title):  # 创建pdf
        base_directory = 'D:/wx_file/{}'.format(self.biz)
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
        try:
            file = base_directory + '{}{}.pdf'.format('/', title)
            if not os.path.exists(file):  # 过滤掉重复文件
                pdfkit.from_url(url, file, configuration=self.config)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    ms = MpSpider()
    ms.request_data()
