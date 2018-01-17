import scrapy
from bs4 import BeautifulSoup
import requests
import re
import json
from jdjinshuiji.items import JdjinshuijiItem
import time,random
import pandas as pd
import csv

class jdspider(scrapy.Spider):
    name="jd_jinshuiji"                 #京东净水机
    allowed_domains=["jd.com"]
    start_urls=[
        "https://list.jd.com/list.html?cat=737,738,898"   #京东净水机
    ]
    num=0
    pagenum=0
    ProgramStarttime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    with open("price.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ProductID", "PreferentialPrice", "price"])

    def parse(self, response):
        sel=scrapy.Selector(response)

        '''''''''
        方法二
        '''''''''
        productid_list1=sel.xpath(".//div[@id='plist']/ul/li/div[contains(@class,'gl-i-wrap')]/@data-sku").extract()
        #单件，套餐……
        productid_list2 = sel.xpath( ".//div[@class='gl-i-tab-content']/div[@class='tab-content-item tab-cnt-i-selected j-sku-item']/@data-sku").extract()
        productid_list=productid_list1+productid_list2
        print(productid_list)
        print(len(productid_list))
        productid_str='%2CJ_'.join(productid_list)
        # time.sleep(random.randint(60,120))
        price_web="https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(productid_str)
        price_webs = requests.get(price_web, timeout=1000).text
        price_jsons = json.loads(price_webs)
        if len(price_jsons)>50:
            self.pagenum=self.pagenum+1
            print("第"+str(self.pagenum)+"页")
        for price_json in price_jsons:
            try:
                id = price_json['id']
                ProductID = id[2:]
                PreferentialPrice = price_json['p']
                price = price_json['m']
            except:
                ProductID=None
                PreferentialPrice = None
                price = None  # 商品价格
            if ProductID:
                item=JdjinshuijiItem()
                with open("price.csv", "a") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([ProductID,PreferentialPrice,price])
                item['ProductID']=ProductID
                item['PreferentialPrice'] = PreferentialPrice
                item['price'] = price
                goods_web = "https://item.jd.com/" + str(ProductID) + ".html"
                request = scrapy.Request(url=goods_web, callback=self.goods, meta={'item': item}, dont_filter=True)
                yield request
            else:
                print("ProductID未获取到")
                self.num=self.num+1
            if (self.num)>60:
                print("ProductID多次未获取到")
                exit()

        ''''''''''
        方法一
        '''''''''''
        # # url="https://item.jd.hk/18739277759.html"    #京东全球购与普通网址不同，不同的地方为“https://item.jd.com/4251335.html”
        # goods_info=sel.xpath(".//div[@id='plist']/ul/li")
        # for goods in goods_info:
        #     ProductID_info=goods.xpath(".//div[@class='gl-i-wrap j-sku-item']/@data-sku").extract()       #商品编号
        #     if len(ProductID_info)==0:
        #         ProductID_info=goods.xpath(".//div[@class='gl-i-tab-content']/div[@class='tab-content-item tab-cnt-i-selected j-sku-item']/@data-sku").extract()
        #         ProductID=ProductID_info[0]
        #     else:
        #         ProductID=ProductID_info[0]
        #     # print(ProductID)
        #     if len(ProductID)!=0:
        #         goods_web="https://item.jd.com/"+str(ProductID)+".html"         #商品链接   包含商品型号,店铺名称,类别,品牌,型号等
        #         item=JdItem(ProductID=ProductID)
        #         request=scrapy.Request(url=goods_web,callback=self.goods,meta={'item':item},dont_filter=True)
        #         yield request
        #     else:
        #         print("parse中ProductID为空  没有读到")

        # #测试用
        # ProductID='11699508209'
        # item = JdItem(ProductID=ProductID)
        # # url="https://item.jd.hk/1971910764.html"
        # url="https://item.jd.com/11699508209.html"
        # request = scrapy.Request(url=url, callback=self.goods,meta={'item':item}, dont_filter=True)
        # yield request

        #翻页功能
        time.sleep(random.randint(60, 120))
        next_page=sel.xpath(".//div[@class='p-wrap']/span[@class='p-num']/a[@class='pn-next']/@href").extract()
        if next_page:
            next="https://list.jd.com/"+next_page[0]
            yield scrapy.Request(next,callback=self.parse)

    def goods(self,response):
        item=response.meta['item']
        sel=scrapy.Selector(response)
        url=response.url
        body=response.body
        ProductID=item['ProductID']
        PreferentialPrice = item['PreferentialPrice']
        price = item['price']

        if "error" in url or "2017?t" in url:        #302重定向页面,写回原页面处理
            url="https://item.jd.com/"+str(ProductID)+".html"
            item = JdjinshuijiItem(ProductID=ProductID,PreferentialPrice=PreferentialPrice,price=price)
            yield scrapy.Request(url,callback=self.goods,meta={'item':item})
            return None

        # --------------------全球购网页---------------------------------------------
        elif "hk" in url:
            print("全球购：", url)

            #京东商品介绍部分
            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/text()").extract()
            if detail[0]=='品牌： ':
                detail_brand=detail_info.xpath(".//li[1]/@title").extract()[0]
                detail[0]=detail[0]+detail_brand
            product_detail = '\"'+' '.join(detail).replace('\t', '').replace('\n', '').replace('  ','')+'\"'
            detail_1 = detail_info.extract()          #缩小范围，从商品介绍部分获取想要的内容

            #商品名称
            try:
                p_Name = sel.xpath(".//div[@class='sku-name']/text()").extract()[-1].strip('\"').strip('\n').strip().replace('\t', '')
                print(p_Name)
            except:
                p_Name = None

            # detail_info=sel.xpath(".//div[@class='p-parameter']/text()").extract()

            #店铺名称
            try:
                shop_name = sel.xpath(".//div[@class='shopName']/strong/span/a/text()").extract()[0]  # 店铺名称
            except:
                try:
                    shop = sel.xpath(".//div[@class='p-parameter']/ul[@class='parameter2']/li[3]/@title").extract()[0]
                    if '店' in shop:
                        shop_name = shop
                    else:
                        shop_name=None
                except:
                    shop_name = None

            #京东规格与包装部分（将这部分的内容读为字典形式，x为字典）
            try:
                s = BeautifulSoup(body, 'lxml')
                guige = s.find('div', id_='specifications')
                x = {}
                guige2 = guige.find_all('td', class_='tdTitle')
                guige3 = guige.find_all('td', class_=None)
                for i in range(len(guige2)):
                    dt = re.findall(">(.*?)<", str(guige2[i]))
                    dd = re.findall(">(.*?)<", str(guige3[i]))
                    x.setdefault(dt[0], dd[0])
            except:
                x = None

            #商品品牌
            try:
                brand = x['品牌']
            except:
                brand = p_Name

            if brand!=p_Name:
                if ("（" and "）") in brand:
                    dd = re.findall("（.*?）", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if ("(" and ")") in brand:
                    dd = re.findall("\(.*?\)", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if brand == "TOSOT":
                    brand = "大松"
                if brand == "Panasonic":
                    brand = "松下"

            #商品名称（型号）
            try:
                try:
                    X_name = re.findall(">货号：(.*?)<", detail_1[0])[0].strip()
                    if p_Name == None:
                        p_Name = X_name
                except:
                    try:
                        X_name = x['型号']
                        if p_Name == None:
                            p_Name = X_name
                    except:
                        X_name = re.findall(">商品名称：(.*?)<", detail_1[0])[0].strip().replace('\t', '')  # 商品名称
                        if len(X_name) == 0:
                            X_name = p_Name
                        if p_Name == None:
                            p_Name = X_name
            except:
                X_name = p_Name

            try:
                X_type = x['类型']
            except:
                try:
                    X_type = re.findall(">类别：(.*?)<", detail_1[0])[0].strip()
                except:
                    X_type = None

            try:
                install = re.findall(">安装方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    install = x['安装方式']
                except:
                    install = None

            try:
                drink = re.findall(">饮用方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    drink = x['用途(用水范围）']
                except:
                    drink = None
            if drink:
                if '不可直饮' in drink:
                    drink="非直饮"
                elif '可直饮' in drink:
                        drink='直饮'

            try:
                level = re.findall(">过滤层级：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    level = x['滤芯级数']
                except:
                    level = None

            try:
                kinds=re.findall(">过滤材质：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    kinds = x['过滤材质']
                except:
                    kinds = None

            try:
                life = x['是否有滤芯寿命提示']
            except:
                try:
                    life = re.findall(">是否有滤芯寿命提示：(.*?)<", detail_1[0])[0].strip()
                except:
                    life = None
            if life=="是":
                life='有滤芯寿命提示'
            elif life=="否":
                life = '无滤芯寿命提示'

            try:
                color = x['颜色']
            except:
                try:
                    color = re.findall(">颜色：(.*?)<", detail_1[0])[0].strip()
                except:
                    color = None

            # price_web="https://p.3.cn/prices/mgets?pduid=15107253217849152442&skuIds=J_"+str(ProductID)
            comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
        # ---------------------普通网页-----------------------------------
        else:

            #商品名称（1.从名称处读；2.从表头的名称处读）
            try:
                p_Name = sel.xpath(".//div[@class='sku-name']/text()").extract()[0].strip('\"').strip('\n').strip().replace('\t', '')  # 商品名称
                if len(p_Name) == 0:     # 如发生商品名称读取结果为空的情况
                    p_Name = sel.xpath(".//div[@class='item ellipsis']/@title").extract()[0].replace('\t', '')
            except:
                try:
                    p_Name = sel.xpath(".//div[@class='item ellipsis']/@title").extract()[0].replace('\t', '')
                except:
                    p_Name = None

            #京东商品介绍部分
            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/text()").extract()
            if detail[0]=='品牌： ':
                detail_brand=detail_info.xpath(".//li[1]/@title").extract()[0]
                detail[0]=detail[0]+detail_brand
            product_detail = '\"'+' '.join(detail).replace('\t', '').replace('\n', '').replace('  ','')+'\"'
            detail_1 = detail_info.extract()

            #京东规格与包装部分（读取为字典格式）
            try:
                s = BeautifulSoup(body, 'lxml')
                # print(s)
                guige = s.find('div', class_='Ptable')
                # print (guige)
                guige1 = guige.find_all('div', class_='Ptable-item')
                # print (guige1)
                x = {}
                for gg in guige1:
                    guige2 = gg.find_all('dt', class_=None)
                    guige3 = gg.find_all('dd', class_=None)
                    for i in range(len(guige2)):
                        dt = re.findall(">(.*?)<", str(guige2[i]))
                        dd = re.findall(">(.*?)<", str(guige3[i]))
                        x.setdefault(dt[0], dd[0])
            except:
                x = None

            #店铺名称
            try:
                try:
                    shop_name = sel.xpath(".//div[@class='name']/a/text()").extract()[0]  # 店铺名称
                except:
                    shop_name=re.findall(">店铺：(.*?)<", detail_1[0])[0].strip()
            except:
                shop_name = "京东自营"

            #不是品牌：**的形式，不用find
            try:
                brand = detail_info.xpath(".//ul[@id='parameter-brand']/li/a/text()").extract()[0].strip()  # 商品品牌
            except:
                try:
                    brand = x['品牌']
                except:
                    brand = None

            if brand:
                if ("（" and "）") in brand:
                    dd = re.findall("（.*?）", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if ("(" and ")") in brand:
                    dd = re.findall("\(.*?\)", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if brand == "TOSOT":
                    brand = "大松"
                if brand == "Panasonic":
                    brand = "松下"
                if brand == "GUOER":
                    brand = "果儿"
                if brand == "TATUNG":
                    brand = "大同"

            #商品名称（型号）
            try:
                try:
                    X_name = re.findall(">货号：(.*?)<", detail_1[0])[0].strip()
                except:
                    try:
                        X_name = x['型号']
                    except:
                        X_name = re.findall(">商品名称：(.*?)<", detail_1[0])[0].strip().replace('\t', '')  # 商品名称
                        if len(X_name) == 0:
                            X_name = p_Name
                        if p_Name == None:
                            p_Name = X_name
            except:
                X_name = p_Name

            try:
                X_type = x['类型']
            except:
                try:
                    X_type = re.findall(">类别：(.*?)<", detail_1[0])[0].strip()
                except:
                    X_type = None

            try:
                install = re.findall(">安装方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    install = x['安装方式']
                except:
                    install = None

            try:
                drink = re.findall(">饮用方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    drink = x['用途(用水范围）']
                except:
                    drink = None
            if drink:
                if '不可直饮' in drink:
                    drink="非直饮"
                elif '可直饮' in drink:
                        drink='直饮'

            try:
                level = re.findall(">过滤层级：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    level = x['滤芯级数']
                except:
                    level = None

            try:
                kinds=re.findall(">过滤材质：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    kinds = x['过滤材质']
                except:
                    kinds = None

            try:
                life = x['是否有滤芯寿命提示']
            except:
                try:
                    life = re.findall(">是否有滤芯寿命提示：(.*?)<", detail_1[0])[0].strip()
                except:
                    life = None
            if life=="是":
                life='有滤芯寿命提示'
            elif life=="否":
                life = '无滤芯寿命提示'

            try:
                color = x['颜色']
            except:
                try:
                    color = re.findall(">颜色：(.*?)<", detail_1[0])[0].strip()
                except:
                    color = None

            # price_web = "https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
            comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
            # price_web = "https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
            # price_web="https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(ProductID)+"&pdbp=0&pdtk=vJSo%2BcN%2B1Ot1ULpZg6kb4jfma6jcULJ1G2ulutvvlxgL3fj5JLFWweQbLYhUVX2E&pdpin=&pduid=1508741337887922929012&source=list_pc_front&_=1510210566056"


        # 商品评价   json格式

        # comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
        # comment_web="https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds="+str(ProductID)

        # comment_webs = requests.get(comment_web,timeout=1000).text
        # urls = json.loads(comment_webs)
        urls = requests.get(comment_web, timeout=1000).json()
        try:
            comment = urls['hotCommentTagStatistics']
            keyword_list = []
            for i in range(len(comment)):
                keyword_list.append(comment[i]['name'])
            if len(keyword_list)==0:
                keyword=None
            else:
                keyword = ' '.join(keyword_list)                 #关键词
        except:
            keyword=None

        rate = urls['productCommentSummary']
        try:
            CommentCount = rate['commentCount']  # 评论总数
        except:
            CommentCount=None
            print("评价总数",CommentCount)
        try:
            GoodRateShow = rate['goodRateShow']  # 好评率
        except:
            GoodRateShow=None
        try:
            GoodCount = rate['goodCount']  # 好评数
        except:
            GoodCount=None
        try:
            GeneralCount = rate['generalCount']  # 中评数
        except:
            GeneralCount =None
        try:
            PoorCount = rate['poorCount']  # 差评数
        except:
            PoorCount=None

        ''''''''''
        方法一
        '''''''''''
        # search_web = "https://search.jd.com/Search?keyword=" + str(p_Name) + "&enc=utf-8&wq=" + str(p_Name)
        # # print ("search页面：",search_web)
        # search_webs = requests.get(search_web, timeout=1000).text
        # soup = BeautifulSoup(search_webs, 'lxml')
        # skuid = "J_" + str(ProductID)
        # try:
        #     price_info = soup('strong', class_=skuid)
        #     PreferentialPrice = re.findall("<em>ï¿¥</em><i>(.*?)</i>", str(price_info[0]))[0]
        #     # 会有<strong class="J_10108922808" data-done="1" data-price="639.00"><em>ï¿¥</em><i></i></strong>出现
        #     #如id=10108922808  p_Name=柏翠（petrus） 38L电烤箱家用多功能 精准控温 PE7338 升级版
        #     if len(PreferentialPrice) == 0:
        #         PreferentialPrice = re.findall('data-price=\"(.*?)\"', str(price_info[0]))[0]
        #     price = PreferentialPrice
        # except:
        #     try:
        #         print("价格：",price_web)
        #         price_webs = requests.get(price_web, timeout=1000).text
        #         price_json = json.loads(price_webs)[0]
        #         PreferentialPrice = price_json['p']
        #         price = price_json['m']
        #     except:
        #         price=None
        #         PreferentialPrice=None
        # print(price,PreferentialPrice)
        if float(PreferentialPrice)>0.00:
            item = JdjinshuijiItem()
            item['ProductID']=ProductID
            item['p_Name']=p_Name
            item['shop_name']=shop_name
            item['price']=price
            item['PreferentialPrice']=PreferentialPrice
            item['CommentCount']=CommentCount
            item['GoodRateShow']=GoodRateShow
            item['GoodCount']=GoodCount
            item['GeneralCount']=GeneralCount
            item['PoorCount']=PoorCount
            item['keyword']=keyword
            item['type']=product_detail
            item['brand']=brand
            item['X_name']=X_name
            item['X_type']=X_type
            item['install'] = install
            item['drink']=drink
            item['level']=level
            item['kinds']=kinds
            item['life']=life
            item['precision']=None
            item['color'] = color
            item['product_url']=url
            item['source']="京东"
            item['ProgramStarttime']=self.ProgramStarttime
            yield item
        else:
            print('广告及无效页面:',url)


