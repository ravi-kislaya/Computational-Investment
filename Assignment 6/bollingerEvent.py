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

def bollingerData(symbols,startdate,enddate,data_zip,time_band):
    bollinger_data = copy.deepcopy(data_zip['close'])*0
    market_data = copy.deepcopy(data_zip['close'])
    for sym in symbols:
        bollinger_data[sym] = (market_data[sym]-pd.rolling_mean(market_data[sym],window=20,center=False))/pd.rolling_std(market_data[sym],window=20,center=False)       
    return bollinger_data

def eventCapture():
    time_band = 20
    dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    dataobj = da.DataAccess('Yahoo')    
    symbols = dataobj.get_symbols_from_list("sp5002012")
    symbols.append('SPY') 
    startdate = dt.datetime(2008,1,1)
    enddate = dt.datetime(2009,12,31)
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    delta = dt.timedelta(days=2*time_band)
    timestamps = du.getNYSEdays(startdate,enddate,dt.timedelta(hours=16))
    market_data = dataobj.get_data(timestamps,symbols,keys)
    data_zip = dict(zip(keys,market_data))
    for s_key in keys:
            data_zip[s_key] = data_zip[s_key].fillna(method='ffill')
            data_zip[s_key] = data_zip[s_key].fillna(method='bfill')
            data_zip[s_key] = data_zip[s_key].fillna(1.0)           
    bollinger_data = bollingerData(symbols,startdate,enddate,data_zip,time_band)
    indx = 0
    while (timestamps[indx]<=startdate):
        indx = indx+1    
    events = data_zip['close']*np.NAN
    benchmark_data = bollinger_data['SPY']
    #bollinger_data = bollinger_data.drop(bollinger_data.index[0:indx-1],inplace='True')
    #a_timestamps = du.getNYSEdays(startdate,enddate,dt.timedelta(hours=16))
    count = 0
    order = pd.DataFrame(columns=['Date','Symbol','Category','Quantity'])
    for sym in symbols:
        for index in range(1,len(timestamps)-5):
            today = bollinger_data.ix[index,sym]
            yesterday = bollinger_data.ix[index-1,sym]
            benchmark = benchmark_data.ix[index,sym]
            if(today<=-2 and yesterday>=-2 and benchmark>=1.4):
                events[sym].ix[index] = 1  
                count = count+2
                order.loc[count] = [timestamps[index],sym,'BUY',100]
                order.loc[count+1] = [timestamps[index+5],sym,'SELL',100]                
        for index in range(len(timestamps)-5,len(timestamps)):
            today = bollinger_data.ix[index,sym]
            yesterday = bollinger_data.ix[index-1,sym]
            benchmark = benchmark_data.ix[index,sym]
            if(today<=-2 and yesterday>=-2 and benchmark>=1.4):
                events[sym].ix[index] = 1  
                count = count+2  
                order.loc[count] = [timestamps[index],sym,'BUY',100]
                order.loc[count+1] = [timestamps[len(timestamps)-1],sym,'SELL',100]                
    print "Creating Study"
    order.to_csv('order.csv')
    events.to_csv('events.csv')
    ep.eventprofiler(events, data_zip, i_lookback=20, i_lookforward=20,
                    s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                    s_market_sym='SPY') 

def main():
    eventCapture()

if __name__ == '__main__':
    main()