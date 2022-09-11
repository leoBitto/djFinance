
#for defining dates
from calendar import weekday
import datetime as dt
from datetime import timedelta
import time
from os import listdir
from os.path import isfile, join

#styling dates
import matplotlib.dates as mdates
#plotting
import matplotlib.pyplot as plt

#matplotlib finance
import mplfinance as mpf
#provides ways to work with large multidimensional arrays
import numpy as np
#allows for further data manipulation and analysis
import pandas as pd
#read stock data
from pandas_datareader import data as web
import yfinance as yf

import cufflinks as cf
import plotly.express as px
import plotly.graph_objects as go

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)

cf.go_offline()

from plotly.subplots import make_subplots

import warnings
warnings.simplefilter("ignore")

PATH = "/home/leonardo/progetti/Finance/archive/"
PATH_to_stock = "/home/leonardo/progetti/Finance/src/stocks/big_stock_sectors.csv"
#PATH = "/home/leonardo/Documents/projects/Finance/archive/"
#PATH_to_stock = "/home/leonardo/Documents/projects/Finance/src/stocks/big_stock_sectors.csv"




S_YEAR = 2009
S_MONTH = 1
S_DAY = 1
S_DATE_STR = '2009-01-01'
S_DATE_DATETIME = dt.datetime(S_YEAR, S_MONTH, S_DAY)


E_DATE_STR = dt.datetime.today().strftime('%Y' + '-' + '%m' + '-' + '%d')


risk_free_rate = 0.03


stocks_not_downloaded = []
missing_stocks = []
# check archive folder and list all the csv files there
#[:-4] needed to eliminate file extension
# alist of all the tickers in NYSE
tickers = [x[:-4] for x in listdir(PATH) if isfile(join(PATH, x))]

# a df of all the companies + other info of 6000 stocks in NYSE
companies_df = pd.read_csv(PATH_to_stock)

# several sectors that the companies belong to in df
sectors = list(companies_df.Sector.unique())

# several df containing the tickers divided by companies_df
healthcare_df = companies_df.loc[companies_df['Sector']=='Healthcare']
materials_df = companies_df.loc[companies_df['Sector']=='Materials']
spac_df = companies_df.loc[companies_df['Sector']=='SPAC']
discretionary_df = companies_df.loc[companies_df['Sector']=='Discretionary']
real_estate_df = companies_df.loc[companies_df['Sector']=='Real Estate']
industrial_df = companies_df.loc[companies_df['Sector']=='Industrial']
financials_df = companies_df.loc[companies_df['Sector']=='Financials']
information_tech_df = companies_df.loc[companies_df['Sector']=='Information Technology']
staples_df = companies_df.loc[companies_df['Sector']=='Staples']
services_df = companies_df.loc[companies_df['Sector']=='Services']
utilities_df = companies_df.loc[companies_df['Sector']=='Utilities']
communication_df = companies_df.loc[companies_df['Sector']=='Communication']
energy_df = companies_df.loc[companies_df['Sector']=='Energy']
