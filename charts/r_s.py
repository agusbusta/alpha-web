import requests
import pandas as pd
import plotly.graph_objs as go

def get_kline_data(symbol, interval):
    base_url = f"https://api3.binance.com/api/v3/klines"
    params = {"symbol": str(symbol.upper()), "limit": 50, "interval": interval}
    response = requests.get(base_url, params=params)
    data = response.json()
    return data

def generate_chart_with_support_resistance(symbol_asset, interval, resistance_level, support_level):
    binance_data = get_kline_data(symbol_asset, interval)
    df = pd.DataFrame(binance_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTimestamp', 'QuoteAssetVolume', 'NumberofTrades', 'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume', 'Ignore'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df['Close'] = pd.to_numeric(df['Close'])

    # Crea un gráfico con líneas de resistencia y soporte
    fig = go.Figure()

    # Agrega el gráfico de velas (candlestick)
    fig.add_trace(go.Candlestick(
        x=df['Timestamp'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'))

    # Agrega una línea de resistencia al gráfico
    fig.add_shape(
        go.layout.Shape(
            type='line',
            x0=df['Timestamp'].iloc[0],
            y0=resistance_level,
            x1=df['Timestamp'].iloc[-1],
            y1=resistance_level,
            line=dict(color='red', width=2),
        )
    )

    # Agrega una etiqueta a la línea de resistencia
    fig.add_annotation(
        go.layout.Annotation(
            x=df['Timestamp'].iloc[-1],
            y=resistance_level,
            text=f'Resistance 1',
            showarrow=True,
            arrowhead=4,
        )
    )

    # Agrega una línea de soporte al gráfico
    fig.add_shape(
        go.layout.Shape(
            type='line',
            x0=df['Timestamp'].iloc[0],
            y0=support_level,
            x1=df['Timestamp'].iloc[-1],
            y1=support_level,
            line=dict(color='green', width=2),
        )
    )

    # Agrega una etiqueta a la línea de soporte
    fig.add_annotation(
        go.layout.Annotation(
            x=df['Timestamp'].iloc[-1],
            y=support_level,
            text=f'Support 1',
            showarrow=True,
            arrowhead=4,
        )
    )

    # Configura el diseño del gráfico
    fig.update_layout(
        title=dict(text=f'Candlestick Chart of {symbol_asset.upper()} with Support and Resistance'),
        yaxis_title='Price (USD)',
        xaxis_title=f'Time Frames ({interval})',
        xaxis_rangeslider_visible=False,
        font=dict(family='Arial', size=15, color='#fff'),
        autosize=True,
        paper_bgcolor='#0E1E25',
        plot_bgcolor='#0E1E25'
    )

    # Muestra el gráfico
    fig.show()

# Ejemplo de uso: ETHBTC 1W Resistencia en 2, Soporte en 1
generate_chart_with_support_resistance('ETHUSDT', '1d', 1753, 1763)
