# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 22:28:35 2017

@author: kislaya
"""

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math as mt

def simulate(dt_start, dt_end, ls_port_syms, lf_port_alloc):   
    #deleting cache object
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
    ls_all_syms = c_dataobj.get_all_symbols()
    # Bad symbols are symbols present in portfolio but not in all syms
    ls_bad_syms = list(set(ls_port_syms) - set(ls_all_syms))
    if len(ls_bad_syms) != 0:
        print "Portfolio contains bad symbols : ", ls_bad_syms

    for s_sym in ls_bad_syms:
        i_index = ls_port_syms.index(s_sym)
        ls_port_syms.pop(i_index)
        lf_port_alloc.pop(i_index)

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_port_syms, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    # Copying close price into separate dataframe to find rets
    df_rets = d_data['close'].copy()
    
    # Filling the data.
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    df_rets = df_rets.fillna(1.0)    
    
    # Numpy matrix of filled data values
    na_rets = df_rets.values
    na_rets = na_rets/na_rets[0,:]
    
    # Estimate portfolio returns
    lf_port_alloc1 = np.asarray(lf_port_alloc)
    na_portrets = np.sum(na_rets * lf_port_alloc1, axis=1) 

    # returnize0 calculates the daily return
    tsu.returnize0(na_portrets) 
    na_port_total = np.cumprod(na_portrets + 1)
    
    #Calculating mean
    mean =  np.mean(na_portrets,axis=0)
    
    #Calculating standard deviation
    std = np.std(na_portrets,axis=0)
    
    #Calculating Sharpe Ratio
    sharpe_ratio = mt.sqrt(252)*mean/std
    
    #returning values
    return (std,mean,sharpe_ratio,na_port_total[250])

def optimize(dt_start, dt_end, ls_port_syms):
    max_alloc = [1,0,0,0]
    vol, daily_ret, sharpe, cum_ret = simulate(dt_start, dt_end, ls_port_syms,max_alloc)
    for i in range(0,11,1):
        for j in range(0,11,1):
            for k in range(0,11,1):
                for l in range(0,11,1):
                    if(i+j+k+l == 10):
                        tvol, tdaily_ret, tsharpe, tcum_ret = simulate(dt_start, dt_end, ls_port_syms,[i/10.0,j/10.0,k/10.0,l/10.0])
                        if(tsharpe>sharpe):
                            vol = tvol
                            daily_ret = tdaily_ret
                            sharpe = tsharpe
                            cum_ret = tcum_ret
                            max_alloc = [i/10.0,j/10.0,k/10.0,l/10.0]
    return (vol, daily_ret, sharpe, cum_ret, max_alloc)
    
def main():
    startdate = dt.datetime(2010,1,1)
    enddate = dt.datetime(2010,12,31)
    symbols = ['C', 'GS', 'IBM', 'HNZ']
    vol, daily_ret, sharpe, cum_ret, port_alloc = optimize(startdate, enddate,symbols)
    print("Start Date %s" %startdate)
    print("End Date %s" %enddate)
    print("Symbols %s" %symbols)
    print("Portfolio %s" %port_alloc)
    print("Sharpe Ratio: %f" %sharpe)
    print("Volatility (stdev of daily returns): %f" %vol)
    print("Average Daily Return: %f" %daily_ret)
    print("Cumulative Return: %f" %cum_ret)
    
if __name__ == '__main__':
    main()