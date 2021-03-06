import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import pytz
import sys
import math

if sys.version_info > (3,0): 
    import bitmex
    from datetime import datetime, timedelta, timezone

def comparison_chart(first,second,first_label=None,second_label=None):
    '''Draw two different time series on the same chart. Each series gets its own x and y scales.
    This allows time series from different periods to be compared to see if the same patterns exist.
    Params
    ------
    first: dataframe with first set of values and a datetime index
    second: dataframe with the second set of values and a datetime index
    first_label: label for the first series, default None
    second_label: label for the second series, default none
    
    Returns
    -------
    Draws the chart and returns a fig object
    '''

    sns.set_style('dark')
    fig=plt.figure(figsize=(14,10))
    ax=fig.add_subplot(111, label=first_label)
    ax2=fig.add_subplot(111, label=second_label, frame_on=False)

    ax.plot(first, color="C0")
    ax.set_xlabel(first_label, color="C0")
    ax.set_ylabel(first_label, color="C0")
    ax.tick_params(axis='x', colors="C0")
    ax.tick_params(axis='y', colors="C0")

    ax2.plot(second, color="white")
    ax2.xaxis.tick_top()
    ax2.yaxis.tick_right()
    ax2.set_xlabel(second_label, color="gray") 
    ax2.set_ylabel(second_label, color="gray")       
    ax2.xaxis.set_label_position('top') 
    ax2.yaxis.set_label_position('right') 
    ax2.tick_params(axis='x', colors="gray")
    ax2.tick_params(axis='y', colors="gray")
    plt.show()
    return fig


class bitmex_utils():
    ''' Utility class for loading data from bitmex
    api_key and api_secret need to be stored in environment variables as BITMEX_API_KEY and BITMEX_API_SECRET
    '''
    def __init__(self):
        api_key, api_secret = os.environ['BITMEX_API_KEY_TEST'], os.environ['BITMEX_API_SECRET_TEST']
        self.client = bitmex.bitmex(test=True, api_key=api_key, api_secret=api_secret)

    def get_last(self,symbol='XBTUSD',n=1,freq='1d'):
        ''' Get most recent n periods of data'''
        try:
            ohlc = pd.DataFrame(self.client.Trade.Trade_getBucketed(
                        binSize=freq,
                        symbol=symbol,
                        count=n,
                        reverse=True
                    ).result()[0])
            ohlc.set_index(['timestamp'], inplace=True)
            ohlc.sort_index(inplace=True)
            return ohlc
        except:
            return None

    def get_page(self,symbol='XBTUSD',n=1,freq='1d'):
        PAGE_SIZE = 100
        try:
            ohlcv_candles = pd.DataFrame(self.client.Trade.Trade_getBucketed(
                        binSize=freq,
                        symbol=symbol,
                        count=PAGE_SIZE,
                        start=PAGE_SIZE*(n-1)
                        #reverse=True
                    ).result()[0])
            ohlcv_candles.set_index(['timestamp'], inplace=True)
            return ohlcv_candles
        except:
            return None

    def get_all(self,symbol='XBTUSD',freq='1d'):
        '''Return the latest data. If any data is missing then get it first and save it.'''
        
        name = symbol.replace('.','')

        if freq !='1d':
            name += '_' + freq
        
        ohlc = pd.read_hdf('bitmex',name)

        last_date = ohlc.iloc[-1].name
        today = datetime.now(tz=pytz.utc) # timezone for bitmex is UTC
        days = (today - last_date).days
        hours = int((today - last_date).seconds / (60*60))

        if freq=='1h':
            n = (days * 24) + hours
        elif freq=='1d':
            n = days
        else:
            raise ValueError('Freq of %s is not supported' % freq)

        if n > 0:
            try:
                ohlc = pd.concat([ohlc,self.get_last(n=n,symbol=symbol,freq=freq)],verify_integrity=True)
            except:
                pass
            finally:
                ohlc.to_hdf('bitmex',name,format='table')

        return ohlc

def client(self):

    return self.client

