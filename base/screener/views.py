import plotly.graph_objects as go
import plotly.io as pi
import numpy as np
import pandas as pd
from datetime import datetime
from django.shortcuts import render
import yfinance as yf


#helper function that assign color to the cloud
def get_fill_color(label):
    if label >= 1:
        return "rgba(0, 250, 0 , 0.4)"
    else:
        return "rgba(250, 0, 0 , 0.4)"


def plot_bollinger_bands(df):

    # add bollinger band to df
    df['middle_band'] = df['Close'].rolling(window=20).mean()
    df['upper_band'] = df['middle_band'] + 1.96 * df['Close'].rolling(window=20).std()
    df['lower_band'] = df['middle_band'] - 1.96 * df['Close'].rolling(window=20).std()

    fig = go.Figure()
    
    candle = go.Candlestick(x=df.index, open=df["Open"], close=df["Close"], high=df["High"], low=df["Low"], name="Candlestick")
    upper_line = go.Scatter(x=df.index, y=df["upper_band"], line=dict(color="rgba(250, 0, 0, 0.75)", width=1), name='Upper Band')
    middle_line = go.Scatter(x=df.index, y=df["middle_band"], line=dict(color="rgba(0, 0, 250, 0.75)", width=0.7), name='Middle Band')
    lower_line = go.Scatter(x=df.index, y=df["lower_band"], line=dict(color="rgba(0, 250, 0, 0.75)", width=1), name='Lower Band')

    fig.add_trace(candle)
    fig.add_trace(upper_line)
    fig.add_trace(middle_line)
    fig.add_trace(lower_line)

    fig.update_xaxes(title="Date", rangeslider_visible=True)
    fig.update_yaxes(title="Price")

    fig.update_layout(title="Bollinger Bands", height=800, width=1200, showlegend=True)
    return fig


def plot_Ichimoku(df):

    # add ichimoku values to df
    high_value = df['High'].rolling(window=9).max()
    low_value = df['Low'].rolling(window=9).min()
    df['Conversion'] = (high_value + low_value)/2

    #base line = (highest value in period + lowest value in period)/2 (26 periods)
    high_value2 = df['High'].rolling(window=26).max()
    low_value2 = df['Low'].rolling(window=26).min()
    df['Baseline'] = (high_value2 + low_value2)/2

    #leading span A = (Conversion Value + Base Value)/2 (26 periods)
    df['SpanA'] = ((df['Conversion'] + df['Baseline']) / 2 )

    #leading span B = (Conversion Value + Base Value)/2 (52 periods) 
    high_value3 = df['High'].rolling(window=52).max()
    low_value3 = df['Low'].rolling(window=52).min()
    df['SpanB'] = ((high_value3 + low_value3) / 2).shift(26)

    #lagging span = price shifted back 2 periods
    df['Lagging'] = df['Close'].shift(-26)

    candle = go.Candlestick(x=df.index, open=df["Open"], close=df["Close"], high=df["High"], low=df["Low"], name="Candlestick")

    df1 = df.copy()
    fig = go.Figure()
    df["label"] = np.where(df["SpanA"] > df["SpanB"], 1, 0)
    df['group'] = df['label'].ne(df['label'].shift()).cumsum()
    df = df.groupby('group')

    dfs =[]
    for name, data in df:
        dfs.append(data)

    for df in dfs:
        fig.add_traces(go.Scatter(x=df.index, y=df.SpanA, line=dict(color="rgba(0,0,0,0)")))
        fig.add_traces(go.Scatter(x=df.index, y=df.SpanB, line=dict(color="rgba(0,0,0,0)"), fill='tonexty', fillcolor=get_fill_color(df['label'].iloc[0])))

    baseline = go.Scatter(x=df1.index, y=df1['Baseline'], line=dict(color='pink', width=2), name='Baseline')
    conversion = go.Scatter(x=df1.index, y=df1['Conversion'], line=dict(color='black', width=1), name='Conversion')
    lagging = go.Scatter(x=df1.index, y=df1['Lagging'], line=dict(color='purple', width=1), name='Lagging')
    spanA = go.Scatter(x=df1.index, y=df1['SpanA'], line=dict(color='green', width=2, dash='dot'), name='Span A')
    spanB = go.Scatter(x=df1.index, y=df1['SpanB'], line=dict(color='red', width=2, dash='dot'), name='Span B')

    fig.add_trace(candle)
    fig.add_trace(baseline)
    fig.add_trace(conversion)
    fig.add_trace(lagging)
    fig.add_trace(spanA)
    fig.add_trace(spanB)

    fig.update_xaxes(title="Date", rangeslider_visible=True)
    fig.update_yaxes(title="Price")

    fig.update_layout(title="Ichimoku", height=800, width=1200, showlegend=True)
    return fig

#pie chart

# Create your views here.

def index(request):
    context={}
    return render(request, 'screener/landing.html', context)

def ticker(request):
    try:
        # try to get the info about the ticker ### yfinance 
        ticker = yf.Ticker(request.GET['search_query'])
        # use the dates to get the history
        start_date = request.GET['start_date']
        end_date = request.GET['end_date']
        
        # get the balance sheet and the financial statement ### yfinance
        balanceSheet = ticker.balance_sheet
        financials = ticker.financials

        # get tha various voice of the balance sheet and financials
        # to calculate the indices                          ### yfinance 
        total_current_assets = balanceSheet.iloc[18][0]
        total_current_liabilities = balanceSheet.iloc[13][0]
        inventory = balanceSheet.iloc[-2][0]
        total_stockholder_equity = balanceSheet.iloc[2][0]
        net_tangible_assets = balanceSheet.iloc[20][0]
        short_long_term_debt = balanceSheet.iloc[15][0]
        ebit = financials.iloc[7][0]
        interest_expense = financials.iloc[10][0]
        invested_capital = total_stockholder_equity + short_long_term_debt
        total_revenue = financials.iloc[15][0]
        income_before_taxes = financials.iloc[2][0]
        operating_income = financials.iloc[8][0]

        #calculate indices gives str 'Null' if the index cant be calculated
        ## yfinance gives interest expenses as negative
        CR = round(total_current_assets / total_current_liabilities, 3) if total_current_assets is not None and total_current_liabilities is not None else 'Null'
        QR = round((total_current_assets - inventory)/total_current_liabilities, 3) if total_current_assets-inventory is not None and total_current_liabilities is not None else 'Null'
        copertura_immobilizzazioni = round(total_stockholder_equity/net_tangible_assets, 3) if total_stockholder_equity is not None and net_tangible_assets is not None else 'Null'
        RI = round(short_long_term_debt / total_stockholder_equity, 3) if short_long_term_debt is not None and total_stockholder_equity is not None else 'Null'
        copertura_interessi_passivi = round(ebit/interest_expense, 3)  if ebit is not None and interest_expense is not None else 'Null'
        ROD = round(interest_expense/short_long_term_debt, 3) if interest_expense is not None and short_long_term_debt is not None else 'Null'
        ROE = round(income_before_taxes/total_stockholder_equity, 3)  if income_before_taxes is not None and total_stockholder_equity is not None else 'Null'
        #il seguente potrebbe essere errato dato che non rispetta le
        # uguaglianze di modigliani miller
        ROA = round(operating_income/total_current_assets, 3)  if operating_income is not None and total_current_assets is not None else 'Null'
        
        ROS = round(operating_income/total_revenue, 3)  if operating_income is not None and total_revenue is not None else 'Null'
        ROI = round(ebit/invested_capital, 3)  if ebit is not None and invested_capital is not None else 'Null'
        ROT = round(total_revenue/invested_capital, 3)  if total_revenue is not None and invested_capital is not None else 'Null'
        rotazione_attivo_circolante = round(total_revenue/total_current_assets, 3)  if total_revenue is not None and total_current_assets is not None else 'Null'

        # gather info about property
        property_df = pd.concat([ticker.institutional_holders, ticker.mutualfund_holders], ignore_index=True, axis=0)
        distanced_from_center =[0.3]
        for i in range(0, len(property_df)-1):
            distanced_from_center.append(0)

        pie_chart = go.Figure(data=[go.Pie(
            labels=property_df['Holder'], 
            values=property_df['% Out'], 
            #hole=.3,
            textinfo='percent',
            insidetextorientation='horizontal',
            textfont_size=20,
            pull=distanced_from_center,
            )])


        # get the history between dates and put it in db ### yfinance
        df = ticker.history(start=start_date, end=end_date)
        
        # plot the candle plot clean
        candle_plot = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'])]
                    )

       
        
        bollinger_plot = plot_bollinger_bands(df)
        

        ichimoku_plot = plot_Ichimoku(df)



        # get open close max e min of the df and the las 30 days
        # modify df to be displayed in html
        df = df.iloc[:,:5].tail(30).to_html(classes="table table-success table-striped table-hover")

        #create the context
        context = {
            'ticker':ticker.info['shortName'],
            'info':ticker.info,
            'hist':df,
            'CR':CR,
            'QR':QR,
            'copertura_immobilizzazioni':copertura_immobilizzazioni,
            'RI':RI,
            'copertura_interessi_passivi':copertura_interessi_passivi,
            'ROD':ROD,
            'ROE':ROE,
            #il seguente potrebbe essere errato dato che non rispetta le
            # uguaglianze di modigliani miller
            'ROA':ROA,
            
            'ROS':ROS,
            'ROI':ROI,
            'ROT':ROT,
            'rotazione_attivo_circolante':rotazione_attivo_circolante,
            'candlestick':pi.to_html(candle_plot, full_html=False, default_height="1000px"),
            'bollinger': pi.to_html(bollinger_plot, full_html=False),
            'ichimoku': pi.to_html(ichimoku_plot, full_html=False),
            'pie_chart': pi.to_html(pie_chart, full_html=False, default_height="1500px", default_width="100%"),

        }

    except KeyError as e:
        
        context = { 
            'req': request.GET['search_query'],
            'error': e,
         }
        return render(request, 'screener/404.html', context)
    else:
        
        return render(request, 'screener/ticker.html', context)
