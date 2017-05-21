"""
Created on Tue Apr 15 21:25:49 2017

@author: kislaya
"""

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import sys

startdate = dt.datetime(2010,5,1,16,0,0)
enddate = dt.datetime(2010,6,30)
bufferdate = dt.datetime(2009,11,1)
timestamps = du.getNYSEdays(bufferdate,enddate,dt.timedelta(hours=16))
dataobj = da.DataAccess('Yahoo', cachestalltime=0)
dataobj = da.DataAccess('Yahoo')
sym = 'MSFT'
market_data = dataobj.get_data(timestamps,[sym],['close'])[0]
market_data = market_data.fillna(method='ffill')
index = 0
while (timestamps[index]<=startdate):
    index = index+1
market_data['Rolling Mean'] = pd.rolling_mean(market_data[sym],window=20,center=False)
market_data['STD'] = pd.rolling_std(market_data[sym],window=20,center=False)
market_data['Upper Limit'] = market_data['Rolling Mean'] + market_data['STD']
market_data['Lower Limit'] = market_data['Rolling Mean'] - market_data['STD'] 
market_data['Value'] = (market_data[sym]-market_data['Rolling Mean'])/market_data['STD']
"""for i in range(index,len(timestamps)):
    sub_data = (market_data.iloc[i-20:i,:]).values
    print i
    mean = np.mean(sub_data,axis=0)
    print mean
    std = np.std(sub_data,axis=0)
    bollinger.loc[timestamps[i],'Rolling Mean'] = mean
    bollinger.loc[timestamps[i],'Upper Limit'] = mean+std
    bollinger.loc[timestamps[i],'Lower Limit'] = mean-std
    bollinger.loc[timestamps[i],'Value'] = (bollinger.loc[timestamps[i],sym]-mean)/std"""
bollinger = copy.deepcopy(market_data.iloc[index-1:len(timestamps),:])
bollinger.to_csv('Bollinger.csv')