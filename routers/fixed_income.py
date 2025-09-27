from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import (
    generate_treasury_volumes,
    generate_repo_rates,
    generate_settlement_fails,
    generate_dealer_activity
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config

router = APIRouter(prefix="/fixed_income", tags=["Fixed Income"])

# 1. Treasury Trade Volumes
@register_widget({
    "name": "Treasury Trade Volumes",
    "description": "Trade volumes over time by tenor (bills, notes, bonds)",
    "category": "Fixed Income",
    "subCategory": "Treasury Market",
    "type": "chart",
    "endpoint": "fixed_income/treasury_volumes",
    "gridData": {"w": 20, "h": 10},
    "raw": True,
    "params": [
        {
            "paramName": "period",
            "value": "30d",
            "label": "Time Period",
            "type": "text",
            "options": [
                {"label": "7 Days", "value": "7d"},
                {"label": "30 Days", "value": "30d"},
                {"label": "90 Days", "value": "90d"}
            ]
        }
    ]
})
@router.get("/treasury_volumes")
def get_treasury_volumes(period: str = "30d", raw: bool = False, theme: str = "dark"):
    """Get treasury trade volumes by tenor."""
    data = generate_treasury_volumes()
    
    if raw:
        return data
    
    colors = get_theme_colors(theme)
    fig = go.Figure()
    
    color_map = {
        "Bills (1-12M)": "#3b82f6",
        "Notes (2-10Y)": "#8b5cf6",
        "Bonds (20-30Y)": "#ec4899",
        "TIPS": "#f59e0b",
        "FRNs": "#10b981"
    }
    
    for tenor_data in data:
        fig.add_trace(go.Scatter(
            x=tenor_data["dates"],
            y=tenor_data["volumes"],
            name=tenor_data["tenor"],
            mode='lines',
            line=dict(width=2, color=color_map.get(tenor_data["tenor"], "#6b7280"))
        ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Treasury Trade Volumes by Tenor',
        'xaxis_title': 'Date',
        'yaxis_title': 'Volume ($B)',
        'hovermode': 'x unified',
        'legend': dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. Repo Rate Spread Tracker
@register_widget({
    "name": "Repo Rate Spread Tracker",
    "description": "DTCC GCF Repo vs SOFR/ON RRP spreads",
    "category": "Fixed Income",
    "subCategory": "Repo Market",
    "type": "chart",
    "endpoint": "fixed_income/repo_spreads",
    "gridData": {"w": 20, "h": 10},
    "refetchInterval": 300000
})
@router.get("/repo_spreads")
def get_repo_spreads(theme: str = "dark"):
    """Track repo rate spreads."""
    data = generate_repo_rates()
    colors = get_theme_colors(theme)
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=('Repo Rates', 'GCF-SOFR Spread')
    )
    
    # Plot rates
    fig.add_trace(
        go.Scatter(x=data["dates"], y=data["GCF_Repo"], 
                  name="GCF Repo", line=dict(color="#3b82f6", width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data["dates"], y=data["SOFR"], 
                  name="SOFR", line=dict(color="#8b5cf6", width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data["dates"], y=data["ON_RRP"], 
                  name="ON RRP", line=dict(color="#ec4899", width=2)),
        row=1, col=1
    )
    
    # Calculate and plot spread
    spread = [gcf - sofr for gcf, sofr in zip(data["GCF_Repo"], data["SOFR"])]
    fig.add_trace(
        go.Scatter(x=data["dates"], y=spread, 
                  name="GCF-SOFR Spread", 
                  fill='tozeroy',
                  line=dict(color="#f59e0b", width=2)),
        row=2, col=1
    )
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Repo Rate Monitor',
        'xaxis2_title': 'Date',
        'yaxis_title': 'Rate (%)',
        'yaxis2_title': 'Spread (bps)',
        'hovermode': 'x unified',
        'showlegend': True,
        'height': 500
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 3. Fails-to-Deliver Chart
@register_widget({
    "name": "Fails-to-Deliver Monitor",
    "description": "Track fails by CUSIP and tenor",
    "category": "Fixed Income",
    "subCategory": "Settlement",
    "type": "table",
    "endpoint": "fixed_income/fails_to_deliver",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": False,
                "chartType": "bar"
            },
            "columnsDefs": [
                {
                    "field": "cusip",
                    "headerName": "CUSIP",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "tenor",
                    "headerName": "Tenor",
                    "width": 80
                },
                {
                    "field": "fails_amount",
                    "headerName": "Fails Amount ($)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "chartDataType": "series"
                },
                {
                    "field": "fail_rate",
                    "headerName": "Fail Rate (%)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 3, "color": "#ef4444", "fill": True},
                            {"condition": "gt", "value": 2, "color": "#f59e0b", "fill": False},
                            {"condition": "lte", "value": 2, "color": "#10b981", "fill": False}
                        ]
                    }
                },
                {
                    "field": "days_failed",
                    "headerName": "Days Failed",
                    "width": 110,
                    "cellDataType": "number",
                    "renderFn": "greenRed"
                }
            ]
        }
    }
})
@router.get("/fails_to_deliver")
def get_fails_to_deliver():
    """Get fails-to-deliver data."""
    return generate_settlement_fails()

# 4. Dealer Activity Leaderboard
@register_widget({
    "name": "Dealer Activity Leaderboard",
    "description": "Top repo lenders and borrowers",
    "category": "Fixed Income",
    "subCategory": "Dealer Activity",
    "type": "table",
    "endpoint": "fixed_income/dealer_activity",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": True,
                "chartType": "groupedColumn"
            },
            "columnsDefs": [
                {
                    "field": "dealer",
                    "headerName": "Dealer",
                    "width": 180,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "lending_volume",
                    "headerName": "Lending ($B)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "borrowing_volume",
                    "headerName": "Borrowing ($B)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "net_position",
                    "headerName": "Net Position ($B)",
                    "width": 140,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                },
                {
                    "field": "market_share",
                    "headerName": "Market Share (%)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                }
            ]
        }
    }
})
@router.get("/dealer_activity")
def get_dealer_activity():
    """Get dealer activity leaderboard."""
    return generate_dealer_activity()

# 5. Liquidity Curve Heatmap
@register_widget({
    "name": "Liquidity Curve Heatmap",
    "description": "Repo availability vs collateral type",
    "category": "Fixed Income",
    "subCategory": "Liquidity",
    "type": "chart",
    "endpoint": "fixed_income/liquidity_curve",
    "gridData": {"w": 20, "h": 10}
})
@router.get("/liquidity_curve")
def get_liquidity_curve(theme: str = "dark"):
    """Generate liquidity curve heatmap."""
    import random
    
    # Generate mock data
    collateral_types = ["Treasury", "Agency", "MBS", "Corp IG", "Corp HY"]
    terms = ["O/N", "1W", "2W", "1M", "3M", "6M", "9M", "1Y"]
    
    z_data = []
    for collateral in collateral_types:
        row = []
        for term in terms:
            # Treasury has highest availability, Corp HY lowest
            base = 80 if collateral == "Treasury" else 60 if collateral == "Agency" else 40
            availability = base + random.uniform(-20, 20)
            row.append(max(0, min(100, availability)))
        z_data.append(row)
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=terms,
        y=collateral_types,
        colorscale='RdYlGn',
        zmid=50,
        text=[[f'{val:.0f}%' for val in row] for row in z_data],
        texttemplate='%{text}',
        hovertemplate='Collateral: %{y}<br>Term: %{x}<br>Availability: %{z:.1f}%<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Repo Liquidity Availability',
        'xaxis_title': 'Term',
        'yaxis_title': 'Collateral Type',
        'height': 400
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 6. Fixed Income Metrics
@register_widget({
    "name": "Fixed Income Metrics",
    "description": "Key fixed income market metrics",
    "category": "Fixed Income",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "fixed_income/metrics",
    "gridData": {"w": 20, "h": 4}
})
@router.get("/metrics")
def get_fixed_income_metrics():
    """Get fixed income market metrics."""
    return [
        {
            "label": "Treasury Volume",
            "value": "$892B",
            "delta": "8.3"
        },
        {
            "label": "GCF Repo Rate",
            "value": "2.48%",
            "delta": "0.05"
        },
        {
            "label": "Fails Rate",
            "value": "1.2%",
            "delta": "-0.3"
        },
        {
            "label": "Top Dealer Share",
            "value": "14.7%",
            "delta": "1.2"
        },
        {
            "label": "Liquidity Score",
            "value": "82/100",
            "delta": "-2.0"
        }
    ]

# 7. Dashboard Notes
@register_widget({
    "name": "Fixed Income Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Fixed Income Markets dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "fixed_income/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Fixed Income dashboard documentation."""
    markdown_content = """# DTCC Fixed Income Markets Dashboard

## Overview
The DTCC Fixed Income Markets Dashboard provides comprehensive treasury and repo market monitoring capabilities, tracking trade volumes by tenor, repo rate spreads, settlement failures, dealer activity, and liquidity conditions across fixed income securities. This dashboard serves as the central hub for monitoring the health and efficiency of fixed income markets.

## Purpose
• **Treasury Market Analysis**: Monitor trading volumes, price trends, and liquidity conditions across bills, notes, bonds, TIPS, and FRNs
• **Repo Market Surveillance**: Track repo rates, spreads vs benchmarks, and monitor GCF repo activity and pricing dynamics
• **Settlement Monitoring**: Identify and track fails-to-deliver events, aging analysis, and settlement efficiency metrics
• **Dealer Activity Analysis**: Monitor primary dealer participation, market share analysis, and competitive dynamics in fixed income markets

---

## Tab 1: Treasury Market
**Purpose**: Comprehensive monitoring of U.S. Treasury market activity and performance

### Widgets:
• **Fixed Income Metrics**: Key market indicators including treasury volume ($892B), GCF repo rate (2.48%), fails rate (1.2%), top dealer share (14.7%), and liquidity score (82/100)

• **Treasury Trade Volumes**: Time series visualization of trading volumes by tenor (Bills 1-12M, Notes 2-10Y, Bonds 20-30Y, TIPS, FRNs) with selectable time periods

• **Repo Rate Spread Tracker**: Dual-panel chart showing repo rates vs SOFR/ON RRP with spread analysis and real-time updates every 5 minutes

---

## Tab 2: Repo Market
**Purpose**: In-depth analysis of repo market dynamics and participant activity

### Widgets:
• **Dealer Activity Leaderboard**: Ranking of primary dealers by lending/borrowing volume, net positions, and market share with chart visualization capabilities

• **Liquidity Curve Heatmap**: Matrix showing repo availability by collateral type (Treasury, Agency, MBS, Corp IG/HY) across term structure

• **Fails-to-Deliver Monitor**: Detailed table of settlement fails by CUSIP and tenor with fail rates, aging analysis, and severity indicators

---

## Data Sources
• **DTCC Trade Repositories**: Real-time feeds from DTCC's Fixed Income Clearing Corporation (FICC) for comprehensive trade capture

• **Federal Reserve Systems**: Integration with SOFR, ON RRP, and other Federal Reserve benchmark rates and operations data

• **Primary Dealer Reports**: Direct feeds from primary dealer reporting systems for accurate market share and activity analysis

• **Settlement Systems**: Real-time connection to DTCC settlement infrastructure for immediate fail detection and tracking

• **Market Data Vendors**: Bloomberg, Refinitiv, and other providers for benchmark rates, yield curves, and market reference data

## Key Metrics Tracked
• **Volume Analytics**: Daily, weekly, and monthly trading volumes across all treasury tenors with historical trend analysis

• **Rate Monitoring**: GCF repo rates, general collateral rates, SOFR spreads, and ON RRP facility usage

• **Settlement Performance**: Fail-to-deliver rates, aging analysis, resolution times, and counterparty-specific settlement statistics

• **Liquidity Indicators**: Bid-ask spreads, market depth, dealer inventory levels, and collateral availability metrics

• **Market Structure**: Dealer market share, client flow analysis, electronic vs voice trading ratios, and trading venue analysis

• **Risk Metrics**: Duration risk, yield curve positioning, basis risks, and interest rate exposure across the fixed income complex

• **Operational Efficiency**: Settlement rates, exception handling, STP rates, and processing time analytics

## Use Cases
• **Fixed Income Traders**: Monitor market conditions, identify trading opportunities, and track competitor activity and market share

• **Risk Managers**: Assess interest rate risk, monitor settlement exposure, and track counterparty concentration in repo markets

• **Compliance Teams**: Ensure adherence to repo market regulations and monitor for suspicious trading patterns or market manipulation

• **Treasury Operations**: Optimize repo funding strategies, monitor collateral availability, and manage settlement risk exposure

• **Market Regulators**: Oversee market integrity, monitor systemic risk in repo markets, and assess market structure evolution"""

    return markdown_content