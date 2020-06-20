#!/usr/bin/env python
# coding: utf-8

# # 爬取股票交易数据

# 导入所需第三方库

# In[1]:


import requests
from  bs4 import BeautifulSoup
import os
import lxml
import json
import threading #线程
import time
import math
import numpy as np
import pandas as pd
import sys

# ## 一、股票信息获取，并计算头寸规模

# In[18]:


class CrawlingStock(object):
    """网络爬取金融数据"""
    def __init__(self):
        #设置递归深度
        sys.setrecursionlimit(6000)  # 例如这里设置为十万
        #1.存放实时数据
        self.all_real_stock_data = []
        #总的股票数
        self.total = 0
        #股票代码
        self.stock_code_data = {}
        #所有股票日K
        # self.all_K_data_dict = {}
    #获取url下的页面内容，返回soup对象
    def get_page(self,url):
        responce = requests.get(url)
        soup = BeautifulSoup(responce.text,'lxml')
        return soup
    
    #1.获取股票实时数据
    #解析实时数据
    def processing_real_stock(self,soup):
        """
        传入一个suop对象，对其进行解析得到股票实时信息数据的字典列表
        """
        #获取P标签下的数据
        a=soup.find_all('p')
        #类型转换
        b = str(a)
        #对字符串进行分割，去掉不需要的数据"<p>jQuery112408123510576841297_1577064081282();</p>"
       
        #处理实时数据
        c=b.split(">")
        #得到json格式的str
        d=c[1].split("<")
        #用json对数据进行解析
        e = json.loads(d[0])
        #得到data下的字典数据
        f=e["data"]
        #得到列表g,存储股票信息的字典
        g = f["diff"]
        #股票总数
        self.total = f['total']
        return g
    #类型转换
    def str_values(self,trips):
        for trip in trips:
            for key, value in trip.items():
                trip[key] = str(value)
        return trips
    #获取某页的实时数据
    def get_one_real_stock(self,page):
        '''获取一页的股票实时数据'''
        #nowTime = lambda:int(round(time.time() * 1000))           #毫秒级时间戳，基于lambda
        url ="""http://39.push2.eastmoney.com/api/qt/clist/get?cb=&pn="""+str(page)+"""
            &pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2
            &fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23&
            fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f23&_="""+str(lambda:int(round(time.time() * 1000)))
        #获取网页信息 
        #获取每页的数据
        #shares_page_data = self.processing_real_stock(self.get_page(url))
        return self.str_values(self.processing_real_stock(self.get_page(url)))
    
    #多线程函数
    def theading_run(self,start,end):
        for page in range(start,end):
            try:
                #获取每页的数据，并合并数据
                self.all_real_stock_data[len(self.all_real_stock_data):len(self.all_real_stock_data)]= self.get_one_real_stock(page)
            except:
                #print("err")
                continue
    #获取沪深所有股票的实时数据
    def get_all_real_stock(self,threading_count=4): 
        """获取所有股票信息
        f2 = '' #最新股价stock_new_price f3 = '' #跌涨幅 CHG f4 = '' #跌涨额 RFP

        f5 = '' #成交量(手) trading f6 = '' #成交额 turnover f7 = '' #振幅 amplitude
    
        f8 = '' #换手率 turnover_rate f9 = '' #市盈率 PE f10 = '' #量比 LMR
    
        f12 = '' #股票代码stock_code f14 = '' #股票名称stock_name f15 = '' #最高 highest
    
        f16 = '' #最低lowest f17 = '' #今开today_open f18 = '' # 昨收 PRE
    
        f23 = '' #市净率 PBV
        """
        self.all_real_stock_data = []
        #获取第一页数据，完成初始化total
        self.all_real_stock_data[len(self.all_real_stock_data):len(self.all_real_stock_data)]= self.get_one_real_stock(1)
        #页面总数,每20条一页
        total_page = math.ceil(self.total/20)
        #从第二页开始遍历
        #多线程获取数据
        avr = math.ceil(total_page/threading_count)
        
        threading.Thread(target=self.theading_run,args=(2,avr)).start()
        for i in range(2,threading_count+1):
            threading.Thread(target=self.theading_run,args=(avr*(i-1),avr*i)).start()
        
        
        #return self.all_real_stock_data
    #2.获取日K数据
    #获取股票代码
    def get_all_code(self):
        """获取股票代码"""
        if not self.all_real_stock_data:
            print("codelist")
            self.all_real_stock_data = self.get_all_real_stock(14)
        #股票代码
        while(len(self.all_real_stock_data)!= self.total):
            time.sleep(2)
        
        self.stock_code_data = {}
        for x in self.all_real_stock_data:
            self.stock_code_data[x["f12"]] = x["f14"]
        return  self.stock_code_data
    
    #获取日k数据集
    def get_K_date(self,code):
        t =time.time()
        nowTime = lambda:int(round(t * 1000))         #毫秒级时间戳，基于lambda
        #股票代码6开头的参数为1.开始；其余为0.开始
        if int(code) > 60000:
            url = '''http://push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery11240059573882596650085_1588346438483&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&ut=7eea3edcaed734bea9cbfc24409ed989&klt=101&fqt=1&secid=1.'''+code+'''&beg=0&end=20500000&_='''+str(nowTime)
        else:
            url = '''http://push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery11240059573882596650085_1588346438483&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&ut=7eea3edcaed734bea9cbfc24409ed989&klt=101&fqt=1&secid=0.'''+code+'''&beg=0&end=20500000&_='''+str(nowTime)
        soup = self.get_page(url)
        #获取P标签下的数据
        a=soup.find_all('p')
        #类型转换
        b = str(a)
        #对字符串进行分割，去掉不需要的数据"<p>jQuery112408123510576841297_1577064081282();</p>"
        c=b.split("(")
        #得到json格式的str
        d = c[1].split(")")
        #用json对数据进行解析
        e = json.loads(d[0])
        f = e['data']

        klines = f['klines']
        K_data = {'date':[],'KP':[],'SP':[],'H':[],'L':[],'CJL':[],'CJE':[],'ZF':[],'HSL':[],'k':[]}
        #'日期','开盘','收盘','最高','最低','成交量','成交额','振幅','换手率','-'
        index = ['date','KP','SP','H','L','CJL','CJE','ZF','HSL','k']
        k_datas = []
        for info in klines:
            info = info.split(',')

            K_data[index[0]].append(info[0])
            K_data[index[1]].append(info[1])
            K_data[index[2]].append(info[2])
            K_data[index[3]].append(info[3])
            K_data[index[4]].append(info[4])
            K_data[index[5]].append(info[5])
            K_data[index[6]].append(info[6])
            K_data[index[7]].append(info[7])
            K_data[index[8]].append(info[8])
            K_data[index[9]].append('-')
        return K_data
    #获取所有股票的日K数据
    def get_all_K_date(self,code_list):
        self.all_K_data_dict = {}
        for code in code_list:
            try:
                K_data = self.get_K_date(code)
                #寻找20日突破点
                self.all_K_data_dict[code] =  K_data
            except:
                continue
        #return self.all_K_data_dict
    
    #3.头寸规模
    def processing_K_data(self,K_data):
        '''处理日K数据得到最高，最低，开盘价数据集'''

        df = pd.DataFrame(K_data)
        df.set_index(["date"], inplace=True)
        #降序排序
        df = df.sort_index(axis = 0,ascending = False)
        #替换缺失值
        df = df.replace({'SP': {'-': np.NaN}})
        df = df.replace({'H': {'-': np.NaN}})
        df = df.replace({'L': {'-': np.NaN}})
        df.fillna(method='pad') #向前填充
        df.fillna(method='backfill') #向后填充
        df.dropna() #丢弃含NaN值的行
        H = df['H'].astype("float")
        L = df['L'].astype("float")
        PDC = df['SP'].astype("float")
        return H,L,PDC
    
    #计算真实波动幅度
    def calculate_TR(self,H,L,PDC):
        '''真实波动幅度 = Max(H - L,H - PDC,PDC - L)
        H = 当日最高价
        L = 当日最低价
        PDC = 前一日收盘价'''

        atr = []
        for i in range(1,len(H)):
            h = float(H[i])
            l = float(L[i])
            pdc = float(PDC[i-1])
            ATR = round(max(h-l,h-pdc,pdc-l),3)
            atr.append(ATR)

        return atr
    
    #递归计算N值
    def calculate_N(self,ATR):
        '''N = (19 * PDN +TR)/20
        PDN = 前一日的N值
        TR = 当日的真实波动幅度
        由于公式中需要前一日的N值，在首次计算的时候不能用这个公式，
        只能计算真实波动幅度的20日的简单平均值。'''
        if len(ATR) <= 20:
            return np.mean(ATR)
        else:
            TR = ATR[0]
            del ATR[0]
            return (19 * self.calculate_N(ATR)+TR)/20
   
    #绝对波动幅度 = N * 每一点数所代表的美元（人民币）
    def buy_decision(self,code,maney=10000):
        """买入决策"""
        K_data = self.get_K_date(code)
        #日k线数据
        # '日期','开盘','收盘','最高','最低','成交量','成交额','振幅','换手率'
        #['date', 'KP', 'SP', 'H', 'L', 'CJL', 'CJE', 'ZF', 'HSL']
        k_data_list = np.c_[K_data['date'],K_data['KP'],K_data['SP'],K_data['ZF'],K_data['HSL'],K_data['L'],K_data['H'],K_data['CJE'],K_data['CJL'],K_data['k']]
        H,L,PDC = self.processing_K_data(K_data)
        #求真实波动幅度
        TR = self.calculate_TR(H,L,PDC)
        N = 0
        if len(TR) > 3000:
            N = self.calculate_N(TR[0:3000])
        else:
            tr = TR.copy()
            N = self.calculate_N(tr)
        #print("波动性指标N:%.3f"%N)
        buy_decision_info = {}
        
#         print("股票代码：%s"%code)
#         print('最新价：%s'%PDC[0])
#         print('当日最高价：%s'%H[0])
#         print('当日最低价：%s'%L[0])
#         print('昨日收盘价：%s'%PDC[1])
        
        buy_decision_info['code'] = code
        buy_decision_info['new_price'] = PDC[0]
        buy_decision_info['H'] = H[0]
        buy_decision_info['L'] = L[0]
        try:
            buy_decision_info['ZSP'] = PDC[1]
        except:
             buy_decision_info['ZSP'] = PDC[0]

        buy_decision_info['JK'] = PDC[0]
        #TR = max(H - L,H - PDC,PDC - L)
#         print("真实波动幅度TR：%s"%TR[0])
        
        buy_decision_info['TR'] = TR[0]
        
        #N = (19 * PDN +TR)/20
#         print('波动性指标N:%.3f'%N)
        buy_decision_info['N'] = round(N,3)
        
        ATR = N * float(PDC[0]) * 100
#         print('市场的绝对波动幅度：%.3f'%ATR)
        buy_decision_info['ATR'] = round(ATR,3)
        
        #maney = 100000
#         print('账户净资产：%.3f'%maney)
        buy_decision_info['maney'] = round(maney,3)
        toucun = int(maney * 0.01 / ATR)
#         print('头寸单位：%d'%toucun)
        
        buy_decision_info['unit'] = toucun
        
        buy1 =  float(PDC[0])
#         print("\n买入各个单位价：")
#         print('第一个单位:%.3f'%buy1)
        buy2 = round(buy1 + 1/2 * N,3)
#         print('第二个单位:%.3f'%buy2)
        buy3 = round(buy2 + 1/2 * N,3)
#         print('第三个单位:%.3f'%buy3)
        buy4 = round(buy3 + 1/2 * N,3)
#         print('第四个单位:%.3f'%buy4)
        zhisun = round(buy1 - 2 * N,3)
#         print('\n止损退出价：%.3f'%zhisun)
        # 350日真实波动幅度均值
        if len(TR)>=350:
            avr_ATR = np.mean(TR[0:350])
            sp_350 = PDC[0:350]
        else:
            avr_ATR = np.mean(TR)
            sp_350 = PDC
        avr_sp_350 = np.mean(sp_350)
        ATR_H = round(avr_sp_350 + 7 * avr_ATR, 3)
        ATR_L = round(avr_sp_350 - 3 * avr_ATR, 3)
        if len(PDC) >= 21:
            max_20 = max(PDC[1:21])
        else:
            max_20 = max(H[1:])
        buy_decision_info['buy1'] = buy1
        buy_decision_info['buy2'] = buy2
        buy_decision_info['buy3'] = buy3
        buy_decision_info['buy4'] = buy4
        buy_decision_info['zhisun'] = zhisun
        buy_decision_info['avr_ATR'] = round(avr_ATR,3)
        buy_decision_info['max_20'] = round(max_20, 3)
        buy_decision_info['ATR_H'] = round(ATR_H, 3)
        buy_decision_info['ATR_L'] = round(ATR_L, 3)

        #收盘价350日线性模拟走势
        sp_data = []
        i = 0
        for j in sp_350[::-1]:
            tam_data = []
            i += 1
            tam_data.append(i)
            tam_data.append(j)
            sp_data.append(tam_data)
        return buy_decision_info,k_data_list.tolist()[::-1],sp_data
