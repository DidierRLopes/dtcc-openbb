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
        'title': {
            'text': f"Trade Volume Heatmap - {date_range}",
            'x': 0.5,
            'xanchor': 'center'
        },
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
        'title': 'Counterparty Exposure Network',
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