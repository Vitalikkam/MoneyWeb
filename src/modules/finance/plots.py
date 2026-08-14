import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.shared.config import COLORS
from src.shared.currency import convert_pln_to_usd

def create_river_chart(df):
    if df.empty:
        return None
    
    fig = go.Figure()
    
    # Ensure Date is datetime
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
    
    line_color = COLORS['green'] if df['Balance'].iloc[-1] >= 0 else COLORS['red']
    fill_color = COLORS['green_bg'] if df['Balance'].iloc[-1] >= 0 else COLORS['red_bg']
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Balance'],
        mode='lines+markers',
        name='Balance',
        line=dict(color=line_color, width=3),
        fill='tozeroy',
        fillcolor=fill_color,
        marker=dict(size=6, color=line_color)
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_secondary'], size=10),
        height=350,
        margin=dict(l=20, r=10, t=20, b=20),
        xaxis=dict(showgrid=False, title=None, tickformat="%b %d", color=COLORS['text_muted']),
        yaxis=dict(showgrid=True, gridcolor=COLORS['grid'], title=None, tickprefix='$', color=COLORS['text_muted']),
        hovermode='x unified'
    )
    return fig

def create_net_chart(grouped_df):
    if grouped_df.empty:
        return None
    
    grouped_df = grouped_df.copy()
    grouped_df['Net'] = grouped_df['Deposit'] - grouped_df['Withdrawal']
    colors = [COLORS['green'] if val >= 0 else COLORS['red'] for val in grouped_df['Net']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped_df['Date'],
        y=grouped_df['Net'],
        marker_color=colors,
        text=grouped_df['Net'].apply(lambda x: f"${x:,.2f}"),
        textposition='outside',
        textfont=dict(color=COLORS['text_primary'], size=9)
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_secondary'], size=10),
        height=350,
        margin=dict(l=20, r=10, t=20, b=20),
        xaxis=dict(showgrid=False, title=None, color=COLORS['text_muted']),
        yaxis=dict(showgrid=True, gridcolor=COLORS['grid'], title=None, tickprefix='$', color=COLORS['text_muted']),
        hovermode='x unified',
        showlegend=False
    )
    return fig

def prepare_grouped_data(df, freq):
    if df.empty:
        return pd.DataFrame()
    
    df_copy = df.copy()
    
    if not pd.api.types.is_datetime64_any_dtype(df_copy['Date']):
        df_copy['Date'] = pd.to_datetime(df_copy['Date'])
    
    if freq == 'Daily':
        grouped = df_copy.groupby(df_copy['Date'].dt.date).agg({'Deposit': 'sum', 'Withdrawal': 'sum'}).reset_index()
        grouped.rename(columns={'Date': 'Date'}, inplace=True)
    elif freq == 'Weekly':
        df_copy['Week'] = df_copy['Date'] - pd.to_timedelta(df_copy['Date'].dt.weekday, unit='D')
        grouped = df_copy.groupby('Week').agg({'Deposit': 'sum', 'Withdrawal': 'sum'}).reset_index()
        grouped.rename(columns={'Week': 'Date'}, inplace=True)
    elif freq == 'Monthly':
        df_copy['Month'] = df_copy['Date'].dt.to_period('M').dt.start_time
        grouped = df_copy.groupby('Month').agg({'Deposit': 'sum', 'Withdrawal': 'sum'}).reset_index()
        grouped.rename(columns={'Month': 'Date'}, inplace=True)
    else:
        return pd.DataFrame()
    
    if not pd.api.types.is_datetime64_any_dtype(grouped['Date']):
        grouped['Date'] = pd.to_datetime(grouped['Date'])
    
    return grouped


def create_projected_river_chart(df, days_ahead=90, rate=3.766):
    """
    Builds a two-phase balance chart:
      - Solid line: real historical balance (converted to USD)
      - Dashed line + band: projected balance for the next `days_ahead` days

    Projection is based on the mean/std of net monthly change,
    using only fully completed months and excluding the opening month
    (the very first calendar month in the dataset, which usually contains
    large one-off opening deposits that aren't representative).

    Parameters
    ----------
    df : pd.DataFrame
        Must have columns: Date, Deposit, Withdrawal, Balance (PLN)
    days_ahead : int
        How many calendar days to project forward
    rate : float
        PLN → USD exchange rate (PLN per 1 USD)
    """
    if df.empty:
        return None

    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])

    # ── Convert historical balance to USD ──────────────────────────────────
    df['Balance_USD'] = df['Balance'].apply(lambda x: convert_pln_to_usd(x, rate) or x / rate)

    # ── Compute monthly nets for projection ────────────────────────────────
    df['YearMonth'] = df['Date'].dt.to_period('M')
    today = pd.Timestamp.today().normalize()
    current_period = today.to_period('M')

    # The opening month = earliest calendar month in the data (skewed by init deposits)
    opening_period = df['YearMonth'].min()

    monthly = (
        df.groupby('YearMonth')
        .agg(deposits=('Deposit', 'sum'), withdrawals=('Withdrawal', 'sum'))
        .reset_index()
    )
    monthly['net'] = monthly['deposits'] - monthly['withdrawals']

    # Keep only fully completed months, excluding opening month
    completed = monthly[
        (monthly['YearMonth'] < current_period) &
        (monthly['YearMonth'] > opening_period)
    ]

    if completed.empty or len(completed) < 1:
        return None

    monthly_mean = completed['net'].mean()
    monthly_std = completed['net'].std(ddof=1) if len(completed) > 1 else abs(monthly_mean * 0.2)

    # Daily equivalents
    daily_mean = monthly_mean / 30.0
    daily_std = monthly_std / 30.0

    # ── Build projection dates & values ────────────────────────────────────
    last_date = df['Date'].max()
    last_balance_pln = df['Balance'].iloc[-1]

    proj_dates = pd.date_range(start=last_date, periods=days_ahead + 1, freq='D')
    t = np.arange(len(proj_dates))  # 0, 1, 2, … days_ahead

    proj_balance_pln = last_balance_pln + daily_mean * t
    proj_upper_pln   = last_balance_pln + (daily_mean + daily_std) * t
    proj_lower_pln   = last_balance_pln + (daily_mean - daily_std) * t

    # Convert projection to USD
    proj_balance_usd = proj_balance_pln / rate
    proj_upper_usd   = proj_upper_pln   / rate
    proj_lower_usd   = proj_lower_pln   / rate

    # ── Decide colour based on projected end balance ────────────────────────
    end_balance = proj_balance_usd[-1]
    line_color = COLORS['green'] if end_balance >= 0 else COLORS['red']
    fill_color = COLORS['green_bg'] if end_balance >= 0 else COLORS['red_bg']
    band_color = (
        'rgba(74, 222, 128, 0.08)' if end_balance >= 0
        else 'rgba(248, 113, 113, 0.08)'
    )

    fig = go.Figure()

    # ── Historical line ─────────────────────────────────────────────────────
    hist_color = COLORS['green'] if df['Balance_USD'].iloc[-1] >= 0 else COLORS['red']
    hist_fill  = COLORS['green_bg'] if df['Balance_USD'].iloc[-1] >= 0 else COLORS['red_bg']

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Balance_USD'],
        mode='lines+markers',
        name='Balance',
        line=dict(color=hist_color, width=3),
        fill='tozeroy',
        fillcolor=hist_fill,
        marker=dict(size=4, color=hist_color),
        hovertemplate='%{x|%b %d}<br><b>$%{y:,.0f}</b><extra></extra>'
    ))

    # ── Uncertainty band (upper) ────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=proj_dates,
        y=proj_upper_usd,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    # ── Uncertainty band (lower) — fills back to upper ─────────────────────
    fig.add_trace(go.Scatter(
        x=proj_dates,
        y=proj_lower_usd,
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor=band_color,
        showlegend=False,
        hoverinfo='skip'
    ))

    # ── Projected centre line ───────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=proj_dates,
        y=proj_balance_usd,
        mode='lines',
        name='Projected',
        line=dict(color=line_color, width=2, dash='dash'),
        hovertemplate='%{x|%b %d}<br><b>~$%{y:,.0f}</b><extra>projected</extra>'
    ))

    # ── "Today" vertical marker ─────────────────────────────────────────────
    fig.add_vline(
        x=today,
        line_width=1,
        line_dash='dot',
        line_color=COLORS['text_muted'],
        annotation_text='Today',
        annotation_position='top right',
        annotation_font=dict(color=COLORS['text_muted'], size=10)
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_secondary'], size=10),
        height=350,
        margin=dict(l=20, r=10, t=20, b=20),
        xaxis=dict(
            showgrid=False,
            title=None,
            tickformat='%b %d',
            color=COLORS['text_muted']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['grid'],
            title=None,
            tickprefix='$',
            color=COLORS['text_muted']
        ),
        hovermode='x unified',
        legend=dict(
            font=dict(color=COLORS['text_muted'], size=9),
            bgcolor='rgba(0,0,0,0)',
            x=0, y=1
        )
    )

    return fig
