# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdjinshuijiItem(scrapy.Item):
    #商品型号
    p_Name = scrapy.Field()
    #店铺名称
    shop_name = scrapy.Field()
    #商品ID
    ProductID = scrapy.Field()
    #正价
    price = scrapy.Field()
    #折扣价
    PreferentialPrice = scrapy.Field()
    #评论总数
    CommentCount = scrapy.Field()
    #好评度
    GoodRateShow = scrapy.Field()
    #好评
    GoodCount = scrapy.Field()
    #中评
    GeneralCount = scrapy.Field()
    #差评
    PoorCount = scrapy.Field()
    #评论关键字
    keyword = scrapy.Field()
    # 核心参数
    type = scrapy.Field()
    #品牌
    brand = scrapy.Field()
    #商品型号
    X_name = scrapy.Field()
    #类别
    X_type=scrapy.Field()
    #安装方式
    install=scrapy.Field()
    # 直饮
    drink=scrapy.Field()
    # 滤芯等级
    level=scrapy.Field()
    # 滤芯种类
    kinds=scrapy.Field()
    #滤芯使用寿命
    life=scrapy.Field()
    #过滤精度
    precision=scrapy.Field()
    #颜色
    color=scrapy.Field()
    product_url=scrapy.Field()
    #来源
    source=scrapy.Field()
    # 爬取时间
    ProgramStarttime=scrapy.Field()


