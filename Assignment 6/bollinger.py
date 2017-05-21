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

def bollinger(date,sym,time_band):
    delta = dt.timedelta(days=2*time_band)
    startdate = date - delta
    enddate = date + delta
    timestamps = du.getNYSEdays(startdate,enddate,dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    dataobj = da.DataAccess('Yahoo')
    market_data = dataobj.get_data(timestamps,[sym],['close'])[0]
    market_data = market_data.fillna(method='ffill')
    index = 0
    while (timestamps[index]<=date):
        index = index+1    
    market_data['Rolling Mean'] = pd.rolling_mean(market_data[sym],window=20,center=False)
    market_data['STD'] = pd.rolling_std(market_data[sym],window=20,center=False)
    market_data['Upper Limit'] = market_data['Rolling Mean'] + market_data['STD']
    market_data['Lower Limit'] = market_data['Rolling Mean'] - market_data['STD'] 
    market_data['Value'] = (market_data[sym]-market_data['Rolling Mean'])/market_data['STD']   
    return market_data.ix[index,'Value']

def main():
    s = dt.datetime(2010,5,1,16,0,0)
    v = bollinger(s,'$SPX',20)
    print("Bollinger Value is %f" %v)
    
if __name__ == '__main__':
    main()