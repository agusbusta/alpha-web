import requests
import pandas as pd
import plotly.graph_objs as go

def generate_chart(symbol, interval, direction, ma_type, ma_period):
    # Obtiene los datos históricos del símbolo y el intervalo proporcionados
    data = get_kline_data(symbol, interval)

    # Crea un DataFrame a partir de los datos
    df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTimestamp', 'QuoteAssetVolume', 'NumberofTrades', 'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume', 'Ignore'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df['Close'] = pd.to_numeric(df['Close'])

    # Calcula la media móvil (MA) según el tipo y período proporcionados
    ma_window = int(ma_period)
    if ma_type.lower() == 'ema':
        df['MA'] = df['Close'].ewm(span=ma_window, adjust=False).mean()
    elif ma_type.lower() == 'sma':
        df['MA'] = df['Close'].rolling(window=ma_window).mean()
    else:
        raise ValueError("Tipo de MA inválido. Use 'ema' o 'sma'.")

    # Crea el gráfico utilizando Plotly
    ma_label = f'{ma_type.upper()} {ma_window} MA'
    fig = go.Figure(data=[go.Candlestick(
        x=df['Timestamp'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'),
        go.Scatter(
            x=df['Timestamp'],
            y=df['MA'],
            mode='lines',
            name=ma_label,
            line=dict(width=2, color='orange')
        )])

    # Configura el diseño del graficos. 
    fig.update_layout(
        title=f'Candle Stick for {symbol} - {interval} with {ma_label} - {direction}',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=True
    )

    fig.show()

def get_kline_data(symbol, interval):
    base_url = f"https://api3.binance.com/api/v3/klines"
    params = {"symbol": str(symbol.upper()), "limit": 50, "interval": interval}
    response = requests.get(base_url, params=params)
    data = response.json()
    return data

# Ejemplo de uso: BTC 1W CROSS DOWN EMA 20
generate_chart('BTCUSDT', '1w', 'CROSS DOWN', 'EMA', '20')
