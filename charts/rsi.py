import re
import numpy as np
import requests
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def get_kline_data(symbol, interval):
    base_url = f"https://api3.binance.com/api/v3/klines"
    params = {"symbol": str(symbol.upper()), "limit": 100, "interval": interval}
    response = requests.get(base_url, params=params)
    data = response.json()
    return data

def calculate_rsi(df, period=14):
    close_prices = df['Close']
    delta = close_prices.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    avg_loss = np.where(avg_loss == 0, 0.0001, avg_loss)

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def generate_chart_with_rsi_from_params(symbol, interval, rsi_condition):
    symbol_asset = symbol
    interval = interval
    period = int(re.search(r'\d+', rsi_condition).group())

    if 'RSI>' in rsi_condition:
        rsi_operator = '>'
        rsi_value = int(rsi_condition.split('RSI>')[1])
    elif 'RSI<' in rsi_condition:
        rsi_operator = '<'
        rsi_value = int(rsi_condition.split('RSI<')[1])
    else:
        rsi_operator = None
        rsi_value = None

    binance_data = get_kline_data(symbol_asset, interval)
    df = pd.DataFrame(binance_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTimestamp', 'QuoteAssetVolume', 'NumberofTrades', 'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume', 'Ignore'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df['Close'] = pd.to_numeric(df['Close'])

    rsi = calculate_rsi(df, period)

    # Crear un gráfico de velas
    candlestick_fig = go.Figure()

    candlestick_fig.add_trace(go.Candlestick(
        x=df['Timestamp'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'
    ))

    # Personalizar el diseño del gráfico de velas
    candlestick_fig.update_layout(
        yaxis_title='Price (USD)',
        xaxis_title=f'Time Frames ({interval})',
        xaxis_rangeslider_visible=False,
        font=dict(family='Arial', size=15, color='#fff'),
        autosize=True,
        paper_bgcolor='#0E1E25',
        plot_bgcolor='#0E1E25'
    )

    # Crear el gráfico del indicador RSI
    rsi_fig = go.Figure()

    rsi_fig.add_trace(go.Scatter(
        x=df['Timestamp'],
        y=rsi,
        mode='lines',
        name=f'RSI ({period}-period)',
        line=dict(width=2, color='blue')
    ))

    if len(df) >= 2:
        rsi_fig.add_shape(
            dict(
                type="line",
                x0=df['Timestamp'].iloc[0],
                x1=df['Timestamp'].iloc[-1],
                y0=70,
                y1=70,
                line=dict(color="red", width=2),
                name="Overbought (70)"
            )
        )

        rsi_fig.add_shape(
            dict(
                type="line",
                x0=df['Timestamp'].iloc[0],
                x1=df['Timestamp'].iloc[-1],
                y0=30,
                y1=30,
                line=dict(color="green", width=2),
                name="Oversold (30)"
            )
        )
    else:
        print("No hay suficientes datos disponibles para generar el gráfico del RSI.")

    # Personalizar el diseño del gráfico del indicador RSI
    rsi_fig.update_layout(
        yaxis_title='RSI Value',
        xaxis_title=f'Time Frames ({interval})',
        xaxis_rangeslider_visible=False,
        font=dict(family='Arial', size=15, color='#fff'),
        autosize=True,
        paper_bgcolor='#0E1E25',
        plot_bgcolor='#0E1E25'
    )

    # Crear subplots
    subplots = make_subplots(rows=2, cols=1, shared_xaxes=True)

    # Agregar los gráficos a los subplots
    subplots.add_trace(candlestick_fig.data[0], row=1, col=1)
    subplots.add_trace(rsi_fig.data[0], row=2, col=1)

    # Actualizar diseño de los subplots
    subplots.update_layout(
        title=dict(text=f'Candlestick Chart of {symbol_asset.upper()} with RSI ({period}-period)'),
        paper_bgcolor='#0E1E25',
        plot_bgcolor='#0E1E25',
        showlegend=False
    )

    # Mostrar los subplots
    subplots.show()

generate_chart_with_rsi_from_params("ETHUSDT", "1d", "RSI>70")
