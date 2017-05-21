"""
Created on Tue Apr 13 21:05:09 2017

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

def main():
    #start and end date
    startdate = dt.datetime(2008,1,1)
    enddate = dt.datetime(2009,12,31)
    #creating dataframe
    order = pd.DataFrame(columns=['Date','Symbol','Category','Quantity'])
    #Retrieving Data
    timestamps = du.getNYSEdays(startdate,enddate,dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    dataobj = da.DataAccess('Yahoo')
    all_syms = dataobj.get_symbols_from_list("sp5002012")
    keys = ['actual_close']
    market_data = dataobj.get_data(timestamps,all_syms,keys)[0]
    market_data = market_data.fillna(method='ffill')
    count = 0
    for sym in all_syms:
        for i in range(1,len(timestamps)-5):
            price_today = market_data.ix[i,sym]
            price_yesterday = market_data.ix[i-1,sym]
            if(price_today<10 and price_yesterday>=10):
                order.loc[count] = [timestamps[i],sym,'BUY',100]
                order.loc[count+1] = [timestamps[i+5],sym,'SELL',100]
                count = count+2
        for i in range(len(timestamps)-5,len(timestamps)):
            price_today = market_data.ix[i,sym]
            price_yesterday = market_data.ix[i-1,sym]
            if(price_today<5 and price_yesterday>=5):
                order.loc[count] = [timestamps[i],sym,'BUY',100]
                order.loc[count+1] = [timestamps[len(timestamps)-1],sym,'SELL',100]
                count = count+2  
    order.to_csv('order.csv')
    
if __name__ == '__main__':
    main()