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
    generate_trade_volumes,
    generate_anomalies,
    generate_counterparty_exposures,
    generate_compliance_alerts,
    generate_time_series
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config

router = APIRouter(prefix="/market_surveillance", tags=["Market Surveillance"])

# 1. Trade Volume Heatmap
@register_widget({
    "name": "Trade Volume Heatmap",
    "description": "Monitor trade volumes by asset class across different hours",
    "category": "Market Surveillance",
    "subCategory": "Transparency",
    "type": "chart",
    "endpoint": "market_surveillance/trade_volume_heatmap",
    "gridData": {"w": 20, "h": 12},
    "params": [
        {
            "paramName": "date_range",
            "value": "7d",
            "label": "Date Range",
            "type": "text",
            "options": [
                {"label": "24 Hours", "value": "1d"},
                {"label": "7 Days", "value": "7d"},
                {"label": "30 Days", "value": "30d"}
            ]
        }
    ]
})
@router.get("/trade_volume_heatmap")
def get_trade_volume_heatmap(date_range: str = "7d", theme: str = "dark"):
    """Generate trade volume heatmap by asset class."""
    data = generate_trade_volumes()
    
    # Transform data for heatmap
    df = pd.DataFrame(data)
    pivot = df.pivot_table(values='volume', index='asset_class', columns='hour')
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        text=[[f'{val:.0f}' for val in row] for row in pivot.values],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='Asset: %{y}<br>Hour: %{x}<br>Volume: %{z:.2f}M<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': {
        #     'text': f"Trade Volume Heatmap - {date_range}",
        #     'x': 0.5,
        #     'xanchor': 'center'
        # },
        'xaxis_title': "Hour (UTC)",
        'yaxis_title': "Asset Class",
        'height': 500
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. Anomaly Detector
@register_widget({
    "name": "Anomaly Detector",
    "description": "Track unusual settlement fails and trade cancellation spikes",
    "category": "Market Surveillance",
    "subCategory": "Risk Detection",
    "type": "table",
    "endpoint": "market_surveillance/anomaly_detector",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "id",
                    "headerName": "Anomaly ID",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "timestamp",
                    "headerName": "Time",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "type",
                    "headerName": "Type",
                    "width": 150
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
                            {"condition": "eq", "value": "Medium", "color": "#3b82f6", "fill": False},
                            {"condition": "eq", "value": "Low", "color": "#10b981", "fill": False}
                        ]
                    }
                },
                {
                    "field": "asset",
                    "headerName": "Asset Class",
                    "width": 120
                },
                {
                    "field": "counterparty",
                    "headerName": "Counterparty",
                    "width": 150
                },
                {
                    "field": "value",
                    "headerName": "Value (USD)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "prefix": "$"
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Open", "color": "#ef4444", "fill": False},
                            {"condition": "eq", "value": "Investigating", "color": "#f59e0b", "fill": False},
                            {"condition": "eq", "value": "Resolved", "color": "#10b981", "fill": False}
                        ]
                    }
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "severity_filter",
            "value": "All",
            "label": "Severity",
            "type": "text",
            "options": [
                {"label": "All", "value": "All"},
                {"label": "Critical", "value": "Critical"},
                {"label": "High", "value": "High"},
                {"label": "Medium", "value": "Medium"},
                {"label": "Low", "value": "Low"}
            ]
        }
    ]
})
@router.get("/anomaly_detector")
def get_anomaly_detector(severity_filter: str = "All"):
    """Get anomaly detection data."""
    anomalies = generate_anomalies()
    
    if severity_filter != "All":
        anomalies = [a for a in anomalies if a["severity"] == severity_filter]
    
    return anomalies

# 3. Counterparty Exposure Network
@register_widget({
    "name": "Counterparty Exposure Network",
    "description": "Visualize counterparty exposure relationships and systemic risk",
    "category": "Market Surveillance",
    "subCategory": "Network Analysis",
    "type": "chart",
    "endpoint": "market_surveillance/counterparty_network",
    "gridData": {"w": 20, "h": 15},
    "params": [
        {
            "paramName": "min_exposure",
            "value": 50,
            "label": "Min Exposure ($M)",
            "type": "number"
        }
    ]
})
@router.get("/counterparty_network")
def get_counterparty_network(min_exposure: float = 50, theme: str = "dark"):
    """Generate counterparty exposure network visualization."""
    network_data = generate_counterparty_exposures()
    colors = get_theme_colors(theme)
    
    # Create network graph using plotly
    edge_trace = []
    for link in network_data["links"]:
        if link["value"] >= min_exposure:
            # Find node positions (simplified circular layout)
            source_idx = next(i for i, n in enumerate(network_data["nodes"]) if n["id"] == link["source"])
            target_idx = next(i for i, n in enumerate(network_data["nodes"]) if n["id"] == link["target"])
            
            import math
            n_nodes = len(network_data["nodes"])
            source_x = math.cos(2 * math.pi * source_idx / n_nodes)
            source_y = math.sin(2 * math.pi * source_idx / n_nodes)
            target_x = math.cos(2 * math.pi * target_idx / n_nodes)
            target_y = math.sin(2 * math.pi * target_idx / n_nodes)
            
            edge_trace.append(
                go.Scatter(
                    x=[source_x, target_x, None],
                    y=[source_y, target_y, None],
                    mode='lines',
                    line=dict(width=link["value"]/100, color='rgba(125,125,125,0.5)'),
                    hoverinfo='none'
                )
            )
    
    # Node trace
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    n_nodes = len(network_data["nodes"])
    for i, node in enumerate(network_data["nodes"]):
        x = math.cos(2 * math.pi * i / n_nodes)
        y = math.sin(2 * math.pi * i / n_nodes)
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node['id']}<br>Exposure: ${node['exposure']}M<br>Risk Score: {node['risk_score']}")
        node_color.append(node['risk_score'])
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[n['id'] for n in network_data["nodes"]],
        textposition="top center",
        hovertext=node_text,
        hoverinfo='text',
        marker=dict(
            size=[n['exposure']/50 for n in network_data["nodes"]],
            color=node_color,
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(
                thickness=15,
                title="Risk Score",
                xanchor="left"
            ),
            line=dict(width=2, color=colors["text"])
        )
    )
    
    fig = go.Figure(data=edge_trace + [node_trace])
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Counterparty Exposure Network',
        'showlegend': False,
        'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
        'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
        'height': 600
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 4. Compliance Ticker
@register_widget({
    "name": "Regulatory Compliance Ticker",
    "description": "Real-time regulatory compliance alerts and flags",
    "category": "Market Surveillance",
    "subCategory": "Compliance",
    "type": "table",
    "endpoint": "market_surveillance/compliance_ticker",
    "gridData": {"w": 20, "h": 8},
    "refetchInterval": 30000,
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "timestamp",
                    "headerName": "Time",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "id",
                    "headerName": "Alert ID",
                    "width": 100
                },
                {
                    "field": "type",
                    "headerName": "Type",
                    "width": 150
                },
                {
                    "field": "regulation",
                    "headerName": "Regulation",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Dodd-Frank", "color": "#3b82f6", "fill": False},
                            {"condition": "eq", "value": "MiFID II", "color": "#8b5cf6", "fill": False},
                            {"condition": "eq", "value": "EMIR", "color": "#ec4899", "fill": False},
                            {"condition": "eq", "value": "Basel III", "color": "#f59e0b", "fill": False}
                        ]
                    }
                },
                {
                    "field": "entity",
                    "headerName": "Entity",
                    "width": 150
                },
                {
                    "field": "severity",
                    "headerName": "Severity",
                    "width": 100,
                    "renderFn": "greenRed"
                },
                {
                    "field": "description",
                    "headerName": "Description",
                    "width": 300
                }
            ]
        }
    }
})
@router.get("/compliance_ticker")
def get_compliance_ticker():
    """Get real-time compliance alerts."""
    return generate_compliance_alerts()

# 5. Market Activity Summary Metrics
@register_widget({
    "name": "Market Activity Metrics",
    "description": "Key market surveillance metrics at a glance",
    "category": "Market Surveillance",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "market_surveillance/activity_metrics",
    "gridData": {"w": 20, "h": 4}
})
@router.get("/activity_metrics")
def get_activity_metrics():
    """Get market activity summary metrics."""
    return [
        {
            "label": "Total Trade Volume",
            "value": "$4.7T",
            "delta": "12.5"
        },
        {
            "label": "Active Anomalies",
            "value": "23",
            "delta": "-8.0"
        },
        {
            "label": "Settlement Fails",
            "value": "$892M",
            "delta": "15.3"
        },
        {
            "label": "Compliance Alerts",
            "value": "47",
            "delta": "5.0"
        },
        {
            "label": "System Health",
            "value": "98.7%",
            "delta": "0.2"
        }
    ]

# 7. Dashboard Notes
@register_widget({
    "name": "Market Surveillance Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Market Surveillance dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "market_surveillance/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Market Surveillance dashboard documentation."""
    markdown_content = """# DTCC Market Surveillance Dashboard

## Overview
The DTCC Market Surveillance Dashboard provides comprehensive market transparency and surveillance capabilities, offering real-time monitoring of trade volumes, anomaly detection, counterparty exposure analysis, and regulatory compliance tracking across all asset classes. This dashboard serves as the primary tool for identifying market irregularities and ensuring market integrity.

## Purpose
• **Real-time Market Monitoring**: Track trading activity, volumes, and patterns across all major asset classes with sub-second latency
• **Anomaly Detection**: Identify unusual settlement fails, trade cancellation spikes, and suspicious trading patterns using advanced algorithms
• **Counterparty Risk Assessment**: Analyze exposure relationships and systemic risk through network visualization and concentration metrics
• **Regulatory Compliance Oversight**: Monitor compliance with market regulations and generate alerts for potential violations

---

## Tab 1: Market Overview
**Purpose**: Provide a high-level view of current market activity and key surveillance metrics

### Widgets:
• **Market Activity Metrics**: Key performance indicators including total trade volume ($4.7T), active anomalies (23), settlement fails ($892M), compliance alerts (47), and system health (98.7%)

• **Trade Volume Heatmap**: Interactive visualization showing trade volumes by asset class across different hours, filterable by date range (24 hours, 7 days, 30 days)

• **Counterparty Exposure Network**: Network graph displaying counterparty relationships with exposure amounts, risk scores, and minimum exposure filtering

---

## Tab 2: Anomaly Detection
**Purpose**: Focus on identifying and investigating unusual market behavior and potential risks

### Widgets:
• **Anomaly Detector**: Comprehensive table of detected anomalies with severity levels, asset classes, counterparties, and status tracking

• **Regulatory Compliance Ticker**: Real-time feed of compliance alerts across regulations (Dodd-Frank, MiFID II, EMIR, Basel III) with severity indicators and entity details

---

## Data Sources
• **Real-time Trade Feeds**: Direct connections to major exchanges and trading venues for immediate trade capture

• **Settlement Systems**: Integration with DTCC settlement infrastructure for fails and obligation tracking

• **Regulatory Repositories**: Links to trade repositories for compliance monitoring and reporting validation

• **Counterparty Databases**: Master data for entity identification, LEI validation, and relationship mapping

• **Historical Archives**: Multi-year trading history for trend analysis and anomaly baseline establishment

## Key Metrics Tracked
• **Trade Volume Metrics**: Daily, weekly, and monthly volumes across equities, fixed income, derivatives, and repo markets

• **Settlement Performance**: Fail rates, settlement times, and obligation tracking by asset class and counterparty

• **Anomaly Indicators**: Statistical deviations, unusual volume spikes, and pattern recognition alerts

• **Compliance Scores**: Adherence rates to regulatory requirements with drill-down capabilities

• **Network Risk Metrics**: Counterparty concentration, systemic risk indicators, and exposure clustering

• **System Health**: Platform uptime, data latency, and processing performance metrics

• **Alert Response Times**: Time to detection, investigation duration, and resolution tracking

## Use Cases
• **Market Supervisors**: Monitor overall market health, identify emerging risks, and coordinate regulatory responses

• **Risk Managers**: Track counterparty exposures, assess concentration risks, and monitor settlement obligations

• **Compliance Officers**: Ensure adherence to regulatory requirements and investigate potential violations

• **Operations Teams**: Monitor system performance, track settlement processes, and manage operational risks

• **Regulatory Bodies**: Access aggregated market data for policy development and oversight activities"""

    return markdown_content