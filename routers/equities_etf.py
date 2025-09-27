from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import random
from datetime import datetime, timedelta
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import (
    generate_etf_flows,
    generate_short_interest,
    generate_time_series
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config

router = APIRouter(prefix="/equities_etf", tags=["Equities & ETF"])

def generate_settlement_timeline():
    """Generate settlement obligations timeline."""
    dates = []
    t1_obligations = []
    t2_obligations = []
    
    for i in range(14):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        dates.append(date)
        
        # Weekend effect
        is_weekend = (datetime.now() + timedelta(days=i)).weekday() >= 5
        multiplier = 0.3 if is_weekend else 1.0
        
        t1_obligations.append(round(random.uniform(50, 200) * multiplier, 2))
        t2_obligations.append(round(random.uniform(100, 400) * multiplier, 2))
    
    return {
        "dates": dates,
        "t1_obligations": t1_obligations,
        "t2_obligations": t2_obligations
    }

def generate_concentration_risk():
    """Generate concentration risk data."""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD", 
               "NFLX", "CRM", "ADBE", "PYPL", "INTC", "CSCO", "ORCL"]
    
    data = []
    for symbol in symbols:
        data.append({
            "symbol": symbol,
            "net_buy_obligations": round(random.uniform(-1000, 1000), 2),
            "gross_obligations": round(random.uniform(500, 3000), 2),
            "concentration_score": round(random.uniform(0, 100), 1),
            "settlement_risk": round(random.uniform(0, 50), 1),
            "shares_outstanding": round(random.uniform(1, 20) * 1000000000)
        })
    
    return sorted(data, key=lambda x: abs(x["net_buy_obligations"]), reverse=True)

def generate_crowded_trades():
    """Generate crowded trade alerts."""
    symbols = ["TSLA", "AMC", "GME", "PLTR", "SPCE", "RIVN", "LCID", "NKLA"]
    alert_types = ["Borrow Spike", "Delivery Fail", "Unusual Volume", "Concentration Alert"]
    
    alerts = []
    for i in range(10):
        alerts.append({
            "symbol": random.choice(symbols),
            "alert_type": random.choice(alert_types),
            "severity": random.choice(["Medium", "High", "Critical"]),
            "borrow_rate": round(random.uniform(1, 50), 2),
            "utilization": round(random.uniform(60, 98), 1),
            "threshold_breach": round(random.uniform(110, 500), 0),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat()
        })
    
    return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)

# 1. Settlement Obligations Timeline
@register_widget({
    "name": "Settlement Obligations Timeline",
    "description": "T+1/T+2 settlement obligations trends",
    "category": "Equities & ETF",
    "subCategory": "Settlement",
    "type": "chart",
    "endpoint": "equities_etf/settlement_timeline",
    "gridData": {"w": 20, "h": 10},
    "raw": True
})
@router.get("/settlement_timeline")
def get_settlement_timeline(raw: bool = False, theme: str = "dark"):
    """Get settlement obligations timeline."""
    data = generate_settlement_timeline()
    
    if raw:
        return data
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure()
    
    # T+1 obligations
    fig.add_trace(go.Bar(
        x=data["dates"],
        y=data["t1_obligations"],
        name='T+1 Obligations',
        marker_color='#3b82f6',
        opacity=0.8
    ))
    
    # T+2 obligations
    fig.add_trace(go.Bar(
        x=data["dates"],
        y=data["t2_obligations"],
        name='T+2 Obligations',
        marker_color='#8b5cf6',
        opacity=0.8
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': 'Settlement Obligations Timeline',
        'xaxis_title': 'Settlement Date',
        'yaxis_title': 'Obligations ($B)',
        'barmode': 'group',
        'hovermode': 'x unified'
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. ETF Creation/Redemption Flows
@register_widget({
    "name": "ETF Creation/Redemption Flows",
    "description": "ETF flows with basket security drilldowns",
    "category": "Equities & ETF",
    "subCategory": "ETF Analysis",
    "type": "table",
    "endpoint": "equities_etf/etf_flows",
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
                    "field": "etf",
                    "headerName": "ETF",
                    "width": 80,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "date",
                    "headerName": "Date",
                    "width": 100,
                    "cellDataType": "date"
                },
                {
                    "field": "creation",
                    "headerName": "Creation ($M)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "redemption",
                    "headerName": "Redemption ($M)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "net_flow",
                    "headerName": "Net Flow ($M)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                }
            ]
        }
    }
})
@router.get("/etf_flows")
def get_etf_flows():
    """Get ETF creation/redemption flows."""
    return generate_etf_flows()

# 3. Short Interest Tracker
@register_widget({
    "name": "Short Interest Tracker",
    "description": "Monitor borrowed shares outstanding and trends",
    "category": "Equities & ETF",
    "subCategory": "Short Interest",
    "type": "table",
    "endpoint": "equities_etf/short_interest",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": False,
                "chartType": "column"
            },
            "columnsDefs": [
                {
                    "field": "symbol",
                    "headerName": "Symbol",
                    "width": 80,
                    "pinned": "left"
                },
                {
                    "field": "shares_short",
                    "headerName": "Shares Short",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "short_ratio",
                    "headerName": "Short Ratio",
                    "width": 110,
                    "cellDataType": "number",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 7, "color": "#ef4444", "fill": True},
                            {"condition": "gt", "value": 5, "color": "#f59e0b", "fill": False},
                            {"condition": "lte", "value": 3, "color": "#10b981", "fill": False}
                        ]
                    }
                },
                {
                    "field": "days_to_cover",
                    "headerName": "Days to Cover",
                    "width": 120,
                    "cellDataType": "number"
                },
                {
                    "field": "borrow_rate",
                    "headerName": "Borrow Rate (%)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 10, "color": "#ef4444", "fill": True},
                            {"condition": "gt", "value": 5, "color": "#f59e0b", "fill": False},
                            {"condition": "lte", "value": 2, "color": "#10b981", "fill": False}
                        ]
                    }
                },
                {
                    "field": "change_7d",
                    "headerName": "7D Change (%)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                }
            ]
        }
    }
})
@router.get("/short_interest")
def get_short_interest():
    """Get short interest data."""
    return generate_short_interest()

# 4. Concentration Risk Chart
@register_widget({
    "name": "Concentration Risk Monitor",
    "description": "Largest net buy/sell obligations by security",
    "category": "Equities & ETF",
    "subCategory": "Risk Management",
    "type": "table",
    "endpoint": "equities_etf/concentration_risk",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": True,
                "chartType": "scatter"
            },
            "columnsDefs": [
                {
                    "field": "symbol",
                    "headerName": "Symbol",
                    "width": 80,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "net_buy_obligations",
                    "headerName": "Net Buy Obligations ($M)",
                    "width": 180,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed",
                    "chartDataType": "series"
                },
                {
                    "field": "gross_obligations",
                    "headerName": "Gross Obligations ($M)",
                    "width": 160,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                },
                {
                    "field": "concentration_score",
                    "headerName": "Concentration Score",
                    "width": 150,
                    "cellDataType": "number",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 80, "color": "#ef4444", "fill": True},
                            {"condition": "gt", "value": 60, "color": "#f59e0b", "fill": False},
                            {"condition": "lte", "value": 40, "color": "#10b981", "fill": False}
                        ]
                    }
                },
                {
                    "field": "settlement_risk",
                    "headerName": "Settlement Risk",
                    "width": 130,
                    "cellDataType": "number",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 30, "color": "#ef4444", "fill": True},
                            {"condition": "gt", "value": 20, "color": "#f59e0b", "fill": False},
                            {"condition": "lte", "value": 10, "color": "#10b981", "fill": False}
                        ]
                    }
                }
            ]
        }
    }
})
@router.get("/concentration_risk")
def get_concentration_risk():
    """Get concentration risk data."""
    return generate_concentration_risk()

# 5. Crowded Trade Alert System
@register_widget({
    "name": "Crowded Trade Alerts",
    "description": "Spikes in borrow demand or delivery fails",
    "category": "Equities & ETF",
    "subCategory": "Alert System",
    "type": "table",
    "endpoint": "equities_etf/crowded_trades",
    "gridData": {"w": 20, "h": 8},
    "refetchInterval": 60000,
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "timestamp",
                    "headerName": "Time",
                    "width": 150,
                    "cellDataType": "dateString"
                },
                {
                    "field": "symbol",
                    "headerName": "Symbol",
                    "width": 80
                },
                {
                    "field": "alert_type",
                    "headerName": "Alert Type",
                    "width": 120
                },
                {
                    "field": "severity",
                    "headerName": "Severity",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Critical", "color": "#ef4444", "fill": True},
                            {"condition": "eq", "value": "High", "color": "#f59e0b", "fill": True},
                            {"condition": "eq", "value": "Medium", "color": "#3b82f6", "fill": False}
                        ]
                    }
                },
                {
                    "field": "borrow_rate",
                    "headerName": "Borrow Rate (%)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                },
                {
                    "field": "utilization",
                    "headerName": "Utilization (%)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                },
                {
                    "field": "threshold_breach",
                    "headerName": "Threshold Breach (%)",
                    "width": 160,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                }
            ]
        }
    }
})
@router.get("/crowded_trades")
def get_crowded_trades():
    """Get crowded trade alerts."""
    return generate_crowded_trades()

# 6. Equities & ETF Metrics
@register_widget({
    "name": "Equities & ETF Metrics",
    "description": "Key equities and ETF market metrics",
    "category": "Equities & ETF",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "equities_etf/metrics",
    "gridData": {"w": 20, "h": 4}
})
@router.get("/metrics")
def get_equities_etf_metrics():
    """Get equities and ETF metrics."""
    return [
        {
            "label": "Daily Volume",
            "value": "$127B",
            "delta": "4.8"
        },
        {
            "label": "ETF Net Flows",
            "value": "$2.4B",
            "delta": "-12.3"
        },
        {
            "label": "Short Interest",
            "value": "15.2B shares",
            "delta": "8.7"
        },
        {
            "label": "Settlement Rate",
            "value": "99.91%",
            "delta": "0.02"
        },
        {
            "label": "Borrow Cost Avg",
            "value": "3.2%",
            "delta": "0.8"
        }
    ]

# 7. Dashboard Notes
@register_widget({
    "name": "Equities & ETF Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Equities & ETF dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "equities_etf/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Equities & ETF dashboard documentation."""
    markdown_content = """# DTCC Equities & ETF Dashboard

## Overview
The DTCC Equities & ETF Dashboard provides comprehensive equities and ETF market monitoring capabilities, tracking settlement obligations, ETF creation/redemption flows, short interest dynamics, concentration risks, and crowded trade alerts. This dashboard serves as the central monitoring hub for equity market infrastructure and risk management.

## Purpose
• **Settlement Risk Management**: Monitor T+1 and T+2 settlement obligations, track settlement rates, and identify potential settlement disruptions
• **ETF Market Analysis**: Track creation and redemption flows, analyze ETF basket composition impacts, and monitor arbitrage opportunities
• **Short Interest Monitoring**: Track borrowed shares outstanding, borrow rates, and identify securities with high short interest concentrations
• **Concentration Risk Detection**: Identify securities with large net buy/sell obligations and monitor for potential settlement stress

---

## Tab 1: Settlement & Flows
**Purpose**: Monitor settlement obligations and ETF flow dynamics

### Widgets:
• **Equities & ETF Metrics**: Key market indicators including daily volume ($127B), ETF net flows ($2.4B), short interest (15.2B shares), settlement rate (99.91%), and average borrow cost (3.2%)

• **Settlement Obligations Timeline**: Bar chart showing T+1 and T+2 settlement obligations over the next 14 days with weekend adjustments

• **ETF Creation/Redemption Flows**: Detailed table of ETF flows by fund with creation, redemption, and net flow analysis with chart visualization

---

## Tab 2: Risk Monitoring
**Purpose**: Focus on short interest risks and concentration monitoring

### Widgets:
• **Short Interest Tracker**: Comprehensive table of securities with high short interest including shares short, short ratios, days to cover, borrow rates, and 7-day trends

• **Concentration Risk Monitor**: Analysis of largest net buy/sell obligations by security with concentration scores and settlement risk indicators

• **Crowded Trade Alerts**: Real-time alert system for borrow spikes, delivery fails, unusual volume, and concentration breaches with severity levels

---

## Data Sources
• **DTCC Settlement Systems**: Real-time feeds from National Securities Clearing Corporation (NSCC) for settlement obligation tracking

• **ETF Data Providers**: Direct integration with ETF sponsors and authorized participants for creation/redemption flow data

• **Securities Lending Markets**: Real-time borrow availability, rates, and utilization data from major securities lending platforms

• **Exchange Data Feeds**: Trading volume, share outstanding, and corporate action data from major U.S. equity exchanges

• **Regulatory Filings**: Short interest reports, institutional holdings, and other regulatory data for concentration analysis

## Key Metrics Tracked
• **Settlement Analytics**: Settlement rates, fail-to-deliver amounts, aging analysis, and settlement cycle performance metrics

• **ETF Flow Analysis**: Creation/redemption volumes, premium/discount tracking, NAV deviation analysis, and basket composition impacts

• **Short Interest Metrics**: Short interest ratios, days to cover, utilization rates, borrow costs, and short squeeze indicators

• **Concentration Indicators**: Net settlement obligations, market share concentration, single-name exposure limits, and operational risk metrics

• **Liquidity Measures**: Available-for-borrow inventory, borrow demand patterns, and securities lending revenue analytics

• **Risk Alerts**: Threshold breach monitoring, unusual activity detection, and early warning system metrics

• **Operational Efficiency**: Straight-through processing rates, exception handling, and settlement infrastructure performance

## Use Cases
• **Settlement Risk Managers**: Monitor settlement obligations, track settlement performance, and manage operational risk in equity clearing

• **ETF Traders & Market Makers**: Track ETF flows, identify arbitrage opportunities, and monitor creation/redemption efficiency

• **Securities Lending Desks**: Monitor borrow demand, optimize inventory allocation, and manage securities lending revenue

• **Risk Management Teams**: Assess concentration risks, monitor crowded trades, and track potential settlement stress scenarios

• **Compliance Officers**: Ensure adherence to settlement regulations and monitor for market manipulation in heavily shorted securities"""

    return markdown_content