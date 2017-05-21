# -*- coding: utf-8 -*-
"""
Created on Tue Apr 07 22:28:35 2017

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

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

def find_events(ls_symbols,d_data):
    #retrieving actual close data
    d_actclose = d_data['actual_close']
    #retieving market benchmark data(SPY in this assignment)
    ts_market = d_actclose['SPY']
    
    print("Finding Event")
    
    #Time stamps of the data
    ldt_timestamp = d_actclose.index
    
    #creating event matrix
    df_events = copy.deepcopy(d_actclose)
    df_events = df_events*np.NAN
    
    for sym in ls_symbols:
        for i in range(1,len(ldt_timestamp)):
            price_today = d_actclose[sym].ix[i]
            price_yesterday = d_actclose[sym].ix[i-1]
            if(price_today<6 and price_yesterday>=6):
                df_events[sym].ix[i] = 1
    
    return df_events

def main():
    #setting the start and end dates
    dt_startdate = dt.datetime(2008,1,1)
    dt_enddate = dt.datetime(2009,12,31)
    
    #working days in NYSE
    ldt_timestamps = du.getNYSEdays(dt_startdate,dt_enddate,dt.timedelta(hours=16))
    
    #deleting cache object
    dataobj = da.DataAccess('Yahoo', cachestalltime=0)   
    
    #retrieving symbols of S&P500 in 2008
    dataobj = da.DataAccess('Yahoo')
    symbols = dataobj.get_symbols_from_list("sp5002012")
    symbols.append('SPY')    
    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps,symbols,ls_keys)
    d_data = dict(zip(ls_keys,ldf_data))
    
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    df_events = find_events(symbols, d_data)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                    s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                    s_market_sym='SPY') 
    
if __name__ == '__main__':
    main()