import pandas as pd
import plotly.graph_objs as go

def get_indicator(indicator: str, strategy_name: str) -> str:

    formatted_startegy_name = strategy_name.casefold().strip()

    if indicator in formatted_startegy_name:
        return True
    else:
        return False
    

def create_alert_chart(data):
    


# Replace with your data source for BTC and the benchmark asset
# For this example, we'll assume you have two pandas DataFrames, btc_data and benchmark_data.

# Calculate relative strength
relative_strength = btc_data['Close'] / benchmark_data['Close']

# Create a Plotly figure
fig = go.Figure()

# Add a line chart for BTC's price
fig.add_trace(go.Scatter(x=btc_data['Date'], y=btc_data['Close'], mode='lines', name='BTC'))

# Add a line chart for the benchmark asset's price
fig.add_trace(go.Scatter(x=benchmark_data['Date'], y=benchmark_data['Close'], mode='lines', name='Benchmark'))

# Add a line chart for the relative strength
fig.add_trace(go.Scatter(x=btc_data['Date'], y=relative_strength, mode='lines', name='Relative Strength', yaxis='y2'))

# Create a secondary y-axis for the relative strength
fig.update_layout(yaxis2=dict(title='Relative Strength', overlaying='y', side='right'))

# Customize the layout and labels
fig.update_layout(title='BTC Relative Strength Analysis', xaxis_title='Date', yaxis_title='Price', legend=dict(x=0, y=1))

# Show the chart
fig.show()
