import requests
from lxml import etree

import re


class THSSpider(object):
    def __init__(self):

        self.all_nums = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}

    def send_request(self, url):
        # 发送一级页面请求，返回响应
        response = requests.get(url=url, headers=self.headers)
        return response

    def parse_request(self, response):

        # 获取一级页面
        html = response.content

        html_obj = etree.HTML(html)
        #  返回列表
        # 标题
        node_list = html_obj.xpath('//div[@class="list-con"]/ul/li/span[@class="arc-title"]/a/text()')

        # 日期
        time_list = html_obj.xpath('//div[@class="list-con"]/ul/li/span[@class="arc-title"]/span/text()')

        # 详情页链接
        href_list = html_obj.xpath('//div[@class="list-con"]/ul/li/span[@class="arc-title"]/a/@href')
        # 把需要的内容都拼接在一起
        for node, time, herf in zip(node_list, time_list, href_list):
            all_message = node + ":\r\n" + time + "\r\n" + herf + "\r\n"
            # 发送二级页面链接，返回响应
            response = self.send_request(herf)

            data = self.detail_data(response)
            # 返回有内容进行拼接
            if data:
                each_cap = all_message + data + "\r\n\r\n"

                self.save_data(each_cap)

    def detail_data(self, response):

        html2 = response.content

        # 返回的html2中有下面的形式，  不能用xpath解析，解决重定向问题
        weixin_url = re.findall(r'http-equiv="Refresh" content="1;URL=(.*?)"></head', html2.decode("gbk"), re.S)
        # 二级微信界面会有重定向问题
        if weixin_url != []:
            new_url = weixin_url[0]
            response_2 = self.send_request(new_url)
            html2 = response_2.content

        # 逆推

        html2_obj = etree.HTML(html2)
        # # 详情页内容
        # 同花顺财经新闻
        substance1 = html2_obj.xpath('//div[@class="main-text atc-content"]/p/text()')
        # 微信链接新闻
        substance2 = html2_obj.xpath('//div[@id="js_content"]//text()')
        # 界面股市快讯
        substance3 = html2_obj.xpath('//div[@class="article-content"]/p/text()')  # 小红
        # 倍特期货
        substance4 = html2_obj.xpath('//div[@class="t-con"]//text()')  # 球
        # 上海证券报
        substance5 = html2_obj.xpath('//div[@class="f-left"]//text()')

        sub_list = []

        # 判断二级页面内容类型
        if substance1 == [] and substance2 == [] and substance3 == [] and substance4 == [] and substance5 == []:

            with open("2.html", "wb") as f:
                f.write(html2)


        elif substance1 == [] and substance2 == [] and substance4 == [] and substance5 == []:
            for sub in substance3:
                # 对正文内容进行正则解析，获取需要有用的内容
                sub3 = re.compile(r'\s|<.*?>|\u3000|&.*?;')
                data = sub3.sub("", sub)

                sub_list.append(data)
            sublist = ''.join(sub_list)
            return sublist.strip()

        elif substance1 == [] and substance3 == [] and substance4 == [] and substance5 == []:
            for sub in substance2:
                sub2 = re.compile(r'\s|<.*?>|\u3000|&.*?;')
                data = sub2.sub("", sub)

                sub_list.append(data)
            sublist = ''.join(sub_list)
            return sublist.strip()

        elif substance2 == [] and substance3 == [] and substance4 == [] and substance5 == []:
            for sub in substance1:
                sub1 = re.compile(r'\s|<.*?>|\u3000|&.*?;')
                data = sub1.sub("", sub)

                sub_list.append(data)
            sublist = ''.join(sub_list)
            return sublist.strip()
        elif substance1 == [] and substance2 == [] and substance3 == [] and substance5 == []:
            for sub in substance4:
                sub4 = re.compile(r'\s|<.*?>|\u3000|&.*?;')
                data = sub4.sub("", sub)

                sub_list.append(data)
            sublist = ''.join(sub_list)
            return sublist.strip()
        elif substance1 == [] and substance2 == [] and substance3 == [] and substance4 == []:
            for sub in substance5:
                sub5 = re.compile(r'\s|<.*?>|\u3000|&.*?;')
                data = sub5.sub("", sub)

                sub_list.append(data)
            sublist = ''.join(sub_list)
            return sublist.strip()

        else:
            with open("1.html", "wb") as f:
                f.write(html2)

    def save_data(self, each):
        # 保存txt格式
        with open("ths.txt", "a") as f:
            f.write(each)

    def main(self):
        # url分页，每页20条，取4页内容
        for page in range(4):
            url = "http://goodsfu.10jqka.com.cn/futuresnews_list/index_" + str(page) + ".shtml"
            response = self.send_request(url=url)
            self.parse_request(response=response)


if __name__ == '__main__':
    ths_spider = THSSpider()
    ths_spider.main()
