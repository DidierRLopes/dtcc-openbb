from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import random
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import (
    generate_counterparties,
    generate_time_series,
    generate_asset_classes
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config

router = APIRouter(prefix="/risk_management", tags=["Risk Management"])

def generate_exposure_treemap():
    """Generate counterparty exposure treemap data."""
    sectors = ["Banks", "Asset Managers", "Hedge Funds", "Insurance", "Pension Funds"]
    firms = generate_counterparties()
    
    data = []
    for sector in sectors:
        for i in range(3):
            firm = random.choice(firms)
            exposure = random.uniform(100, 5000)
            data.append({
                "firm": firm,
                "sector": sector,
                "exposure": round(exposure, 2),
                "collateral": round(exposure * random.uniform(0.7, 1.3), 2),
                "net_exposure": round(exposure * random.uniform(0.3, 0.8), 2)
            })
    
    return data

def generate_collateral_forecast():
    """Generate collateral requirement forecast data."""
    dates = []
    baseline = []
    stressed = []
    extreme = []
    
    for i in range(90):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        dates.append(date)
        base_value = 1000 + i * 5
        baseline.append(round(base_value + random.uniform(-50, 50), 2))
        stressed.append(round(base_value * 1.3 + random.uniform(-100, 100), 2))
        extreme.append(round(base_value * 1.8 + random.uniform(-150, 150), 2))
    
    return {
        "dates": dates,
        "baseline": baseline,
        "stressed": stressed,
        "extreme": extreme
    }

def generate_settlement_fails():
    """Generate settlement fails tracking data."""
    data = []
    dates, _ = generate_time_series(30)
    
    for date in dates:
        data.append({
            "date": date,
            "treasury_fails": round(random.uniform(100, 1000), 2),
            "equity_fails": round(random.uniform(50, 500), 2),
            "mbs_fails": round(random.uniform(200, 800), 2),
            "corporate_fails": round(random.uniform(30, 300), 2)
        })
    
    return data

def generate_liquidity_heatmap():
    """Generate liquidity heatmap data."""
    maturities = ["O/N", "1W", "1M", "3M", "6M", "1Y", "2Y", "5Y"]
    collateral_types = ["Treasury", "Agency", "MBS", "Corporate IG", "Corporate HY", "Equity"]
    
    data = []
    for collateral in collateral_types:
        for maturity in maturities:
            availability = random.uniform(0, 100)
            if "Treasury" in collateral and maturity in ["O/N", "1W"]:
                availability *= 1.5
            data.append({
                "collateral": collateral,
                "maturity": maturity,
                "availability": round(min(availability, 100), 2),
                "demand": round(random.uniform(20, 80), 2)
            })
    
    return data

# 1. Counterparty Exposure Treemap
@register_widget({
    "name": "Counterparty Exposure Treemap",
    "description": "Hierarchical view of counterparty exposures by firm and sector",
    "category": "Risk Management",
    "subCategory": "Exposure Analysis",
    "type": "chart",
    "endpoint": "risk_management/exposure_treemap",
    "gridData": {"w": 20, "h": 12},
    "params": [
        {
            "paramName": "exposure_type",
            "value": "gross",
            "label": "Exposure Type",
            "type": "text",
            "options": [
                {"label": "Gross Exposure", "value": "gross"},
                {"label": "Net Exposure", "value": "net"},
                {"label": "Collateralized", "value": "collateral"}
            ]
        }
    ]
})
@router.get("/exposure_treemap")
def get_exposure_treemap(exposure_type: str = "gross", theme: str = "dark"):
    """Generate counterparty exposure treemap."""
    data = generate_exposure_treemap()
    colors = get_theme_colors(theme)
    
    # Prepare data for treemap
    labels = []
    parents = []
    values = []
    text = []
    
    # Add root
    labels.append("Total")
    parents.append("")
    values.append(0)
    text.append("Total Exposure")
    
    # Add sectors
    sectors = list(set(d["sector"] for d in data))
    for sector in sectors:
        labels.append(sector)
        parents.append("Total")
        sector_exposure = sum(d["exposure"] if exposure_type == "gross" 
                             else d["net_exposure"] if exposure_type == "net"
                             else d["collateral"] 
                             for d in data if d["sector"] == sector)
        values.append(sector_exposure)
        text.append(f"${sector_exposure:,.0f}M")
    
    # Add firms
    for d in data:
        labels.append(d["firm"])
        parents.append(d["sector"])
        value = d["exposure"] if exposure_type == "gross" else d["net_exposure"] if exposure_type == "net" else d["collateral"]
        values.append(value)
        text.append(f"${value:,.0f}M")
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        text=text,
        textposition="middle center",
        marker=dict(
            colorscale='RdYlGn_r',
            cmid=50
        ),
        hovertemplate='<b>%{label}</b><br>Exposure: %{text}<br>%{percentRoot}<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': f'Counterparty {exposure_type.title()} Exposure by Sector',
        'height': 500
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. Collateral Requirement Forecast
@register_widget({
    "name": "Collateral Requirement Forecast",
    "description": "Projected collateral requirements under different stress scenarios",
    "category": "Risk Management",
    "subCategory": "Collateral Management",
    "type": "chart",
    "endpoint": "risk_management/collateral_forecast",
    "gridData": {"w": 20, "h": 10},
    "params": [
        {
            "paramName": "forecast_days",
            "value": 30,
            "label": "Forecast Period (Days)",
            "type": "number"
        }
    ]
})
@router.get("/collateral_forecast")
def get_collateral_forecast(forecast_days: int = 30, theme: str = "dark"):
    """Generate collateral requirement forecast."""
    forecast_data = generate_collateral_forecast()
    colors = get_theme_colors(theme)
    
    # Limit to requested days
    dates = forecast_data["dates"][:forecast_days]
    baseline = forecast_data["baseline"][:forecast_days]
    stressed = forecast_data["stressed"][:forecast_days]
    extreme = forecast_data["extreme"][:forecast_days]
    
    fig = go.Figure()
    
    # Add baseline scenario
    fig.add_trace(go.Scatter(
        x=dates,
        y=baseline,
        name='Baseline',
        mode='lines',
        line=dict(color='#10b981', width=2)
    ))
    
    # Add stressed scenario
    fig.add_trace(go.Scatter(
        x=dates,
        y=stressed,
        name='Stressed (2008-like)',
        mode='lines',
        line=dict(color='#f59e0b', width=2, dash='dash')
    ))
    
    # Add extreme scenario
    fig.add_trace(go.Scatter(
        x=dates,
        y=extreme,
        name='Extreme Stress',
        mode='lines',
        line=dict(color='#ef4444', width=2, dash='dot')
    ))
    
    # Add fill between baseline and extreme
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1],
        y=baseline + extreme[::-1],
        fill='toself',
        fillcolor='rgba(239, 68, 68, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': 'Collateral Requirement Forecast',
        'xaxis_title': 'Date',
        'yaxis_title': 'Collateral Required ($B)',
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

# 3. Settlement Fails Tracker
@register_widget({
    "name": "Settlement Fails Tracker",
    "description": "Track settlement failures with stress scenario overlays",
    "category": "Risk Management",
    "subCategory": "Settlement Risk",
    "type": "chart",
    "endpoint": "risk_management/settlement_fails",
    "gridData": {"w": 20, "h": 10},
    "raw": True
})
@router.get("/settlement_fails")
def get_settlement_fails(raw: bool = False, theme: str = "dark"):
    """Track settlement fails across asset classes."""
    data = generate_settlement_fails()
    
    if raw:
        return data
    
    df = pd.DataFrame(data)
    colors = get_theme_colors(theme)
    
    fig = go.Figure()
    
    # Create stacked area chart
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['treasury_fails'],
        name='Treasury',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(59, 130, 246, 0.5)',
        line=dict(color='#3b82f6', width=0)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['equity_fails'],
        name='Equity',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(139, 92, 246, 0.5)',
        line=dict(color='#8b5cf6', width=0)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['mbs_fails'],
        name='MBS',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(236, 72, 153, 0.5)',
        line=dict(color='#ec4899', width=0)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['corporate_fails'],
        name='Corporate',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(245, 158, 11, 0.5)',
        line=dict(color='#f59e0b', width=0)
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': 'Settlement Fails by Asset Class',
        'xaxis_title': 'Date',
        'yaxis_title': 'Fails Amount ($M)',
        'hovermode': 'x unified'
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 4. Liquidity Heatmap
@register_widget({
    "name": "Liquidity Heatmap",
    "description": "Repo availability vs collateral type across maturity buckets",
    "category": "Risk Management",
    "subCategory": "Liquidity Risk",
    "type": "chart",
    "endpoint": "risk_management/liquidity_heatmap",
    "gridData": {"w": 20, "h": 10}
})
@router.get("/liquidity_heatmap")
def get_liquidity_heatmap(theme: str = "dark"):
    """Generate liquidity heatmap."""
    data = generate_liquidity_heatmap()
    df = pd.DataFrame(data)
    
    # Create pivot table
    pivot = df.pivot_table(values='availability', index='collateral', columns='maturity')
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=50,
        text=[[f'{val:.0f}%' for val in row] for row in pivot.values],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='Collateral: %{y}<br>Maturity: %{x}<br>Availability: %{z:.1f}%<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': 'Liquidity Availability Heatmap',
        'xaxis_title': 'Maturity',
        'yaxis_title': 'Collateral Type',
        'height': 400
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 5. Risk Metrics Summary
@register_widget({
    "name": "Risk Metrics Summary",
    "description": "Key risk management metrics",
    "category": "Risk Management",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "risk_management/risk_metrics",
    "gridData": {"w": 20, "h": 4},
    "refetchInterval": 60000
})
@router.get("/risk_metrics")
def get_risk_metrics():
    """Get risk management summary metrics."""
    return [
        {
            "label": "Total Exposure",
            "value": "$28.4B",
            "delta": "5.2"
        },
        {
            "label": "Collateral Coverage",
            "value": "87.3%",
            "delta": "-2.1"
        },
        {
            "label": "Settlement Fail Rate",
            "value": "0.42%",
            "delta": "0.08"
        },
        {
            "label": "Liquidity Score",
            "value": "78/100",
            "delta": "-3.0"
        },
        {
            "label": "VaR (99%)",
            "value": "$142M",
            "delta": "12.5"
        }
    ]

# 6. Stress Test Results Table
@register_widget({
    "name": "Stress Test Results",
    "description": "Detailed stress test results by scenario",
    "category": "Risk Management",
    "subCategory": "Stress Testing",
    "type": "table",
    "endpoint": "risk_management/stress_test_results",
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
                    "field": "scenario",
                    "headerName": "Scenario",
                    "width": 200,
                    "pinned": "left"
                },
                {
                    "field": "probability",
                    "headerName": "Probability",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "percent"
                },
                {
                    "field": "impact",
                    "headerName": "P&L Impact ($M)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "renderFn": "greenRed"
                },
                {
                    "field": "collateral_call",
                    "headerName": "Collateral Call ($M)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "liquidity_need",
                    "headerName": "Liquidity Need ($M)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "risk_score",
                    "headerName": "Risk Score",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 80, "color": "#ef4444", "fill": True},
                            {"condition": "gt", "value": 60, "color": "#f59e0b", "fill": True},
                            {"condition": "gt", "value": 40, "color": "#3b82f6", "fill": False},
                            {"condition": "lte", "value": 40, "color": "#10b981", "fill": False}
                        ]
                    }
                }
            ]
        }
    }
})
@router.get("/stress_test_results")
def get_stress_test_results():
    """Get stress test scenario results."""
    scenarios = [
        {"name": "Market Crash (2008-like)", "prob": 5, "impact": -2500},
        {"name": "Flash Crash", "prob": 10, "impact": -800},
        {"name": "Interest Rate Shock (+300bp)", "prob": 15, "impact": -1200},
        {"name": "Credit Spread Widening", "prob": 20, "impact": -600},
        {"name": "Liquidity Crisis", "prob": 8, "impact": -1800},
        {"name": "Counterparty Default", "prob": 3, "impact": -3000},
        {"name": "Operational Failure", "prob": 12, "impact": -400},
        {"name": "Cyber Attack", "prob": 7, "impact": -1000}
    ]
    
    results = []
    for scenario in scenarios:
        results.append({
            "scenario": scenario["name"],
            "probability": scenario["prob"],
            "impact": scenario["impact"],
            "collateral_call": abs(scenario["impact"]) * random.uniform(0.3, 0.6),
            "liquidity_need": abs(scenario["impact"]) * random.uniform(0.4, 0.8),
            "risk_score": min(100, abs(scenario["impact"]) / 30)
        })
    
    return results

# 7. Dashboard Notes
@register_widget({
    "name": "Risk Management Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Risk Management dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "risk_management/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Risk Management dashboard documentation."""
    markdown_content = """# DTCC Risk Management Dashboard

## Overview
The DTCC Risk Management Dashboard provides advanced risk management and stress testing capabilities featuring counterparty exposure analysis, collateral requirement forecasting, settlement risk monitoring, and comprehensive stress scenario modeling. This dashboard enables proactive risk assessment and mitigation across all trading activities.

## Purpose
• **Counterparty Risk Monitoring**: Track and analyze exposures across all counterparties with real-time risk scoring and concentration analysis
• **Collateral Management**: Forecast collateral requirements under various scenarios including baseline, stressed, and extreme market conditions
• **Settlement Risk Assessment**: Monitor settlement failures, track obligations, and identify potential disruptions across asset classes
• **Stress Testing**: Run comprehensive stress tests using historical and hypothetical scenarios to assess portfolio resilience

---

## Tab 1: Exposure Analysis
**Purpose**: Comprehensive view of counterparty exposures and concentration risks

### Widgets:
• **Risk Metrics Summary**: Key risk indicators including total exposure ($28.4B), collateral coverage (87.3%), settlement fail rate (0.42%), liquidity score (78/100), and VaR 99% ($142M)

• **Counterparty Exposure Treemap**: Hierarchical visualization of exposures by firm and sector, switchable between gross exposure, net exposure, and collateralized views

• **Liquidity Heatmap**: Repo availability matrix across collateral types (Treasury, Agency, MBS, Corporate IG/HY, Equity) and maturity buckets

---

## Tab 2: Stress Testing
**Purpose**: Scenario analysis and stress testing for risk assessment and planning

### Widgets:
• **Collateral Requirement Forecast**: 90-day projection of collateral needs under baseline, stressed (2008-like), and extreme stress scenarios

• **Settlement Fails Tracker**: Stacked area chart showing fails by asset class (Treasury, Equity, MBS, Corporate) with trend analysis

• **Stress Test Results**: Comprehensive scenario analysis table showing probability, P&L impact, collateral calls, liquidity needs, and risk scores for various stress events

---

## Data Sources
• **Exposure Management Systems**: Real-time feeds from counterparty exposure databases and netting systems
• **Collateral Management Platforms**: Integration with collateral optimization and forecasting systems
• **Settlement Infrastructure**: Direct connections to DTCC settlement platforms for real-time fail tracking
• **Market Data Providers**: Historical and real-time market data for stress testing and scenario modeling
• **Risk Management Systems**: Portfolio risk metrics, VaR calculations, and concentration monitoring tools

## Key Metrics Tracked
• **Exposure Metrics**: Gross exposure, net exposure, collateral coverage ratios, and concentration indices by counterparty and sector
• **Liquidity Indicators**: Available collateral, funding costs, repo availability, and liquidity transformation ratios
• **Settlement Performance**: Fail rates, settlement times, obligation aging, and counterparty-specific settlement statistics
• **Stress Test Results**: Scenario-based P&L impacts, capital adequacy, liquidity survival periods, and recovery metrics
• **Risk Appetite Metrics**: Limit utilization, risk budget consumption, and early warning indicator thresholds
• **Collateral Optimization**: Cheapest-to-deliver analysis, substitution costs, and inventory management metrics
• **Operational Risk**: Processing errors, system availability, and exception rates across risk management processes

## Use Cases
• **Chief Risk Officers**: Oversee enterprise-wide risk management, set risk appetite, and ensure regulatory compliance
• **Portfolio Managers**: Monitor position-level risks, optimize collateral usage, and assess concentration limits
• **Collateral Managers**: Forecast funding needs, optimize collateral allocation, and manage margin requirements
• **Stress Testing Teams**: Design and execute stress scenarios, validate model assumptions, and report regulatory stress tests
• **Treasury Teams**: Manage liquidity risks, optimize funding strategies, and coordinate with collateral management"""

    return markdown_content