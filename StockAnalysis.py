from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
#from flask_sqlalchemy import SQLAlchemy
import os
import numpy as np
import threading #线程
import time
#自定义库

from craw import CrawStockTD as cs

app = Flask(__name__)


#初始化数据
craw = cs.CrawlingStock()
craw.get_all_real_stock()
craw.get_all_code()

def str_values(trips):
    for trip in trips:
        for key, value in trip.items():
            trip[key] = str(value)

    return trips

#子线程刷新数据
def get_data():
    while 1:
        week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        week = time.strftime("%A", time.localtime())
        Hour = int(time.strftime("%H", time.localtime()))
        Mo = int(time.strftime("%M", time.localtime()))
        Se = int(time.strftime("%S", time.localtime()))
        jiange = 0
        if (week in week_list) and ((Hour >= 9 and Hour < 12) or (Hour > 13 and Hour <= 15)):
            if (Hour == 9 and Mo < 30):
                print('非交易时间')
                jiange = (30 - Mo) * 60  - (60 - Se)
            elif(Hour == 11 and Mo > 30):
                print('非交易时间')
                jiange = (Mo - 30) * 60 - (60 - Se)
            else:
                jiange = 30
                print('交易时间')
                craw.get_all_real_stock()

        else:
            if Hour > 15:
                jiange = (24 - Hour + 9) * 60 * 60 - (60 - Mo)*60 - (60 - Se)
            elif Hour < 9:
                jiange = (9 - Hour) * 60 * 60  - (60 - Mo)*60 - (60 - Se)
            else:
                pass
        time.sleep(jiange)

craw.all_real_stock_data = str_values(craw.all_real_stock_data)

threading.Thread(target=get_data,args=()).start()
#threading.Thread(target=update_xuangu,args=()).start()

@app.route('/real_stock',methods=['GET','POST'])
def real_stock():
    if request.method == "GET":
        while(len(craw.all_real_stock_data) != craw.total):
            time.sleep(1)

        real_stock_list = craw.all_real_stock_data

        return render_template("real_stock.html",pagename="数据中心",real_stock_list=real_stock_list)

@app.route('/')
@app.route('/buy_decision',methods=['GET','POST'])
def Buy_decision():
    if request.method == "GET":
        try:
            code = request.args["code"]
            code_en = code.strip("'")
        except:
            code_en = list(craw.stock_code_data.keys())[5]
        try:
            infos,k_data_list,sp_data  = craw.buy_decision(code_en)
            infos['name'] = craw.stock_code_data[code_en]
            return render_template('buy_decision.html', pagename='数据分析', infos=infos,k_data_list=k_data_list,sp_data = sp_data,state='True')
        except:
            return render_template('buy_decision.html', pagename='数据分析', infos={},k_data_list=[],sp_data = [],state='False')
    else:
        try:
            maney = request.form["maney"]
        except:
            maney = 10000.000
        # try:
        code = request.form["code"]
        infos,k_data_list,sp_data = craw.buy_decision(code, float(maney))
        infos['name'] = craw.stock_code_data[code]
        return render_template('buy_decision.html', pagename='数据分析', infos=infos,k_data_list=k_data_list,sp_data =sp_data,state='True')
        # except:
        #     return render_template('buy_decision.html', pagename='数据分析', infos={},k_data_list =[],sp_data =[],state='False     ')

if __name__ == '__main__':
    app.run(debug=True)
