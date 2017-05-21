"""
Created on Tue Apr 11 15:07:35 2017

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

initial_cash = int(sys.argv[1])
order = pd.read_csv(sys.argv[2],header=None,names=['Year','Month','Day','Symbol','Type','Quantity','Date'],index_col=False)
for i in range(0,len(order.iloc[:,1])):
    order.loc[i,'Date'] = dt.datetime(year=order.loc[i,'Year'],month=order.loc[i,'Month'],day=order.loc[i,'Day'],hour=16)
order = order.sort('Date')
order = order.reset_index(drop=True)
s = np.asarray(order.loc[:,'Symbol'])
Symbol = []
Symbol = np.unique(s)
#Accessing Data
c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
c_dataobj = da.DataAccess('Yahoo')
all_syms = c_dataobj.get_all_symbols()
start = order.ix[0,'Date']
end = order.ix[len(order.iloc[:,1])-1,'Date']
timestamps = du.getNYSEdays(start,end, dt.timedelta(hours=16))
key = ['close']
market_data = c_dataobj.get_data(timestamps, Symbol, key)[0]
portfolio = copy.deepcopy(market_data)
portfolio = portfolio*0
portfolio.ix[0,:]=0
portfolio['Cash'] = 0
portfolio['Stock Value'] = 0
portfolio['Total Value'] = 0
for i,d in enumerate(order['Date']):
    sym = order.ix[i,'Symbol']
    category = order.ix[i,'Type']
    quantity = order.ix[i,'Quantity']
    money = market_data.loc[d,sym]*quantity
    if(category=='Buy'):
        portfolio.loc[d,sym] = portfolio.loc[d,sym]+quantity
        portfolio.loc[d,'Cash'] = portfolio.loc[d,'Cash']-money
    else:
        portfolio.loc[d,sym] = portfolio.loc[d,sym]-quantity
        portfolio.loc[d,'Cash'] = portfolio.loc[d,'Cash']+money
for s in Symbol:
    #portfolio[s] = portfolio[s].fillna(0)
    portfolio.ix[:,s] = portfolio[s].cumsum(axis=0)
portfolio.ix[0,'Cash'] = initial_cash + portfolio.ix[0,'Cash']
portfolio.ix[:,'Cash'] = portfolio['Cash'].cumsum(axis=0)
portfolio.ix[:,'Stock Value'] = (portfolio.ix[:,Symbol]*market_data.ix[:,Symbol]).sum(axis=1)
portfolio.ix[:,'Total Value'] = portfolio.ix[:,'Cash'] + portfolio.ix[:,'Stock Value']
portfolio.to_csv(sys.argv[3])
