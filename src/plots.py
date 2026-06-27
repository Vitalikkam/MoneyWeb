import pandas as pd
import plotly.graph_objects as go
from .config import COLORS

def _ensure_datetime(df):
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
    return df

def create_river_chart(df, currency='zł'):
    if df.empty:
        return None
    df = _ensure_datetime(df)
    line_color = COLORS['green'] if df['Balance'].iloc[-1] >= 0 else COLORS['red']
    fill_color = COLORS['green_bg'] if df['Balance'].iloc[-1] >= 0 else COLORS['red_bg']
    prefix = f'{currency} ' if currency == 'zł' else currency
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Balance'],
        mode='lines+markers', name='Balance',
        line=dict(color=line_color, width=3),
        fill='tozeroy', fillcolor=fill_color,
        marker=dict(size=6, color=line_color)
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_secondary'], size=10),
        height=350, margin=dict(l=20, r=10, t=20, b=20),
        xaxis=dict(showgrid=False, title=None, tickformat="%b %d", color=COLORS['text_muted']),
        yaxis=dict(showgrid=True, gridcolor=COLORS['grid'], title=None, tickprefix=prefix, color=COLORS['text_muted']),
        hovermode='x unified'
    )
    return fig

def create_net_chart(grouped_df):
    if grouped_df.empty:
        return None
    grouped_df = grouped_df.copy()
    grouped_df['Net'] = grouped_df['Deposit'] - grouped_df['Withdrawal']
    colors = [COLORS['green'] if v >= 0 else COLORS['red'] for v in grouped_df['Net']]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped_df['Date'], y=grouped_df['Net'],
        marker_color=colors,
        text=grouped_df['Net'].apply(lambda x: f"{x:,.2f} zł"),
        textposition='outside',
        textfont=dict(color=COLORS['text_primary'], size=9)
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_secondary'], size=10),
        height=350, margin=dict(l=20, r=10, t=20, b=20),
        xaxis=dict(showgrid=False, title=None, color=COLORS['text_muted']),
        yaxis=dict(showgrid=True, gridcolor=COLORS['grid'], title=None, tickprefix='zł ', color=COLORS['text_muted']),
        hovermode='x unified', showlegend=False
    )
    return fig

def prepare_grouped_data(df, freq):
    if df.empty:
        return pd.DataFrame()
    df = _ensure_datetime(df)
    if freq == 'Daily':
        grouped = df.groupby(df['Date'].dt.date).agg({'Deposit': 'sum', 'Withdrawal': 'sum'}).reset_index()
    elif freq == 'Weekly':
        df['Week'] = df['Date'] - pd.to_timedelta(df['Date'].dt.weekday, unit='D')
        grouped = df.groupby('Week').agg({'Deposit': 'sum', 'Withdrawal': 'sum'}).reset_index()
        grouped.rename(columns={'Week': 'Date'}, inplace=True)
    elif freq == 'Monthly':
        df['Month'] = df['Date'].dt.to_period('M').dt.start_time
        grouped = df.groupby('Month').agg({'Deposit': 'sum', 'Withdrawal': 'sum'}).reset_index()
        grouped.rename(columns={'Month': 'Date'}, inplace=True)
    else:
        return pd.DataFrame()
    if not pd.api.types.is_datetime64_any_dtype(grouped['Date']):
        grouped['Date'] = pd.to_datetime(grouped['Date'])
    return grouped
