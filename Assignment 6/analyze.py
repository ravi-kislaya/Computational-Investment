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
import time
import matplotlib.pyplot as plt

portfolio = pd.read_csv(sys.argv[1],index_col=False)
benchmark_symbol = sys.argv[2]
n = len(portfolio.iloc[:,1]) #no.of trading days
start = dt.datetime.strptime(portfolio.ix[0,0],"%Y-%m-%d %H:%M:%S")
end = dt.datetime.strptime(portfolio.ix[n-1,0],"%Y-%m-%d %H:%M:%S")
c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
c_dataobj = da.DataAccess('Yahoo')
timestamps = du.getNYSEdays(start,end, dt.timedelta(hours=16))
key = ['close']
benchmark_data = c_dataobj.get_data(timestamps, [benchmark_symbol], key)[0]
val = copy.deepcopy((portfolio.ix[:,'Total Value']).values)
tsu.returnize0(val)
v = np.cumprod(val + 1)
mean = np.mean(val,axis=0)
std = np.std(val,axis=0)
sharpe_ratio = math.sqrt(252)*mean/std
val_benchmark = copy.deepcopy((benchmark_data.ix[:,benchmark_symbol]).values)
tsu.returnize0(val_benchmark)
v_benchmark = np.cumprod(val_benchmark + 1)
mean_benchmark = np.mean(val_benchmark,axis=0)
std_benchmark = np.std(val_benchmark,axis=0)
sharpe_ratio_benchmark = math.sqrt(252)*mean_benchmark/std_benchmark
norm_benchmark = copy.deepcopy((benchmark_data.ix[:,benchmark_symbol]).values)
norm_benchmark = norm_benchmark[:]/norm_benchmark[0]
print("========================================================================")
print("\nThe final value of the portfolio using the sample file is -- %s , %d" %(portfolio.ix[n-1,0], portfolio.ix[n-1,'Total Value']))
print("\nDetails of the Performance of the portfolio :\n")
print("Data Range :  %s  to  %s" %(portfolio.ix[0,0],portfolio.ix[len(portfolio.iloc[:,1])-1,0]))
print("\nSharpe Ratio of fund : %f" %sharpe_ratio)
print("Sharpe Ratio of %s : %f" %(benchmark_symbol ,sharpe_ratio_benchmark))
print("\nTotal return of fund : %f " %v[len(v)-1])
print("Total return of %s : %f " %(benchmark_symbol ,v_benchmark[len(v_benchmark)-1]))
print("\nStandard Deviation of fund : %f" %std)
print("Standard Deviation of %s: %f" %(benchmark_symbol ,std_benchmark))
print("\nAverage return of fund : %f" %mean)
print("Average return of %s : %f" %(benchmark_symbol, mean_benchmark))
print("========================================================================")
plt.clf()
plt.plot(timestamps, (portfolio.ix[:,'Total Value']).values,c='blue')  # Fund
plt.plot(timestamps, norm_benchmark*portfolio.ix[0,'Total Value'],c='green')  # Benchmark
plt.legend(['Fund', sys.argv[2]])
plt.ylabel('Fund Value')
plt.xlabel('Date')
plt.savefig('MarketSim.pdf', format='pdf')