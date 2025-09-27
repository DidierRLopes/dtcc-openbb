from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import (
    generate_swap_notionals,
    generate_cds_spreads,
    generate_counterparties
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config

router = APIRouter(prefix="/derivatives", tags=["Derivatives"])

def generate_volatility_surface():
    """Generate mock volatility surface data."""
    import numpy as np
    
    strikes = np.arange(80, 121, 5)
    maturities = [7, 14, 30, 60, 90, 120, 180, 365]
    
    surface = []
    for maturity in maturities:
        row = []
        for strike in strikes:
            # Generate implied vol with smile
            moneyness = strike / 100
            base_vol = 0.15 + 0.005 * maturity / 30
            smile = 0.05 * (moneyness - 1) ** 2
            vol = base_vol + smile + np.random.normal(0, 0.01)
            row.append(max(0.05, min(0.5, vol)) * 100)
        surface.append(row)
    
    return {
        "strikes": strikes.tolist(),
        "maturities": maturities,
        "surface": surface
    }

def generate_net_positions():
    """Generate net open positions by asset class."""
    asset_classes = ["Interest Rate", "FX", "Equity", "Credit", "Commodity"]
    
    data = []
    for asset in asset_classes:
        data.append({
            "asset_class": asset,
            "long_notional": np.random.uniform(1000, 5000),
            "short_notional": np.random.uniform(1000, 5000),
            "net_notional": np.random.uniform(-2000, 2000),
            "contracts": np.random.randint(10000, 100000),
            "delta": np.random.uniform(-1000, 1000)
        })
    
    return data

# 1. Swap Notional Traded
@register_widget({
    "name": "Swap Notional by Tenor",
    "description": "Swap notional traded by tenor and currency",
    "category": "Derivatives",
    "subCategory": "Interest Rate Swaps",
    "type": "table",
    "endpoint": "derivatives/swap_notionals",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": True,
                "chartType": "heatmap"
            },
            "columnsDefs": [
                {
                    "field": "currency",
                    "headerName": "Currency",
                    "width": 100,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "tenor",
                    "headerName": "Tenor",
                    "width": 80,
                    "chartDataType": "category"
                },
                {
                    "field": "notional",
                    "headerName": "Notional ($B)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "trades",
                    "headerName": "# Trades",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "avg_size",
                    "headerName": "Avg Size ($M)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                }
            ]
        }
    }
})
@router.get("/swap_notionals")
def get_swap_notionals():
    """Get swap notional data."""
    return generate_swap_notionals()

# 2. CDS Spread Monitor
@register_widget({
    "name": "CDS Spread Monitor",
    "description": "Monitor CDS spreads for indices and single names",
    "category": "Derivatives",
    "subCategory": "Credit Derivatives",
    "type": "chart",
    "endpoint": "derivatives/cds_spreads",
    "gridData": {"w": 20, "h": 12},
    "raw": True,
    "params": [
        {
            "paramName": "view",
            "value": "indices",
            "label": "View",
            "type": "text",
            "options": [
                {"label": "Indices", "value": "indices"},
                {"label": "Single Names", "value": "single_names"},
                {"label": "Both", "value": "both"}
            ]
        }
    ]
})
@router.get("/cds_spreads")
def get_cds_spreads(view: str = "indices", raw: bool = False, theme: str = "dark"):
    """Get CDS spread data."""
    data = generate_cds_spreads()
    
    if raw:
        return data
    
    colors = get_theme_colors(theme)
    fig = go.Figure()
    
    if view in ["indices", "both"]:
        for idx, index_data in enumerate(data["indices"]):
            fig.add_trace(go.Scatter(
                x=index_data["dates"],
                y=index_data["spreads"],
                name=index_data["name"],
                mode='lines',
                line=dict(width=2),
                visible=True if view != "both" else None
            ))
    
    if view in ["single_names", "both"]:
        for name_data in data["single_names"]:
            fig.add_trace(go.Scatter(
                x=name_data["dates"],
                y=name_data["spreads"],
                name=name_data["name"],
                mode='lines',
                line=dict(width=2, dash='dash' if view == "both" else None),
                visible=True if view != "both" else None
            ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': 'CDS Spread Monitor',
        'xaxis_title': 'Date',
        'yaxis_title': 'Spread (bps)',
        'hovermode': 'x unified',
        'legend': dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 3. Volatility Surface
@register_widget({
    "name": "Volatility Surface",
    "description": "3D volatility surface from OTC trade activity",
    "category": "Derivatives",
    "subCategory": "Options",
    "type": "chart",
    "endpoint": "derivatives/volatility_surface",
    "gridData": {"w": 20, "h": 15}
})
@router.get("/volatility_surface")
def get_volatility_surface(theme: str = "dark"):
    """Generate volatility surface visualization."""
    vol_data = generate_volatility_surface()
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=[go.Surface(
        x=vol_data["strikes"],
        y=vol_data["maturities"],
        z=vol_data["surface"],
        colorscale='Viridis',
        hovertemplate='Strike: %{x}<br>Maturity: %{y} days<br>IV: %{z:.1f}%<extra></extra>'
    )])
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': 'Implied Volatility Surface',
        'scene': dict(
            xaxis_title='Strike',
            yaxis_title='Maturity (Days)',
            zaxis_title='Implied Vol (%)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        'height': 600
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 4. Net Open Positions
@register_widget({
    "name": "Net Open Positions",
    "description": "Net open positions by asset class",
    "category": "Derivatives",
    "subCategory": "Positions",
    "type": "table",
    "endpoint": "derivatives/net_positions",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": False,
                "chartType": "groupedColumn"
            },
            "columnsDefs": [
                {
                    "field": "asset_class",
                    "headerName": "Asset Class",
                    "width": 150,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "long_notional",
                    "headerName": "Long ($B)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "short_notional",
                    "headerName": "Short ($B)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "net_notional",
                    "headerName": "Net ($B)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                },
                {
                    "field": "contracts",
                    "headerName": "Contracts",
                    "width": 110,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "delta",
                    "headerName": "Delta ($M)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                }
            ]
        }
    }
})
@router.get("/net_positions")
def get_net_positions():
    """Get net open positions data."""
    return generate_net_positions()

# 5. Counterparty Network - Derivatives
@register_widget({
    "name": "Derivatives Counterparty Network",
    "description": "Network of derivatives exposures between counterparties",
    "category": "Derivatives",
    "subCategory": "Network Analysis",
    "type": "chart",
    "endpoint": "derivatives/counterparty_network",
    "gridData": {"w": 20, "h": 15}
})
@router.get("/counterparty_network")
def get_derivatives_counterparty_network(theme: str = "dark"):
    """Generate derivatives counterparty network."""
    import math
    import random
    
    firms = generate_counterparties()[:12]
    colors = get_theme_colors(theme)
    
    # Generate network data
    nodes = []
    links = []
    
    for i, firm in enumerate(firms):
        nodes.append({
            "id": firm,
            "derivatives_exposure": random.uniform(100, 3000),
            "collateral_posted": random.uniform(50, 1500)
        })
    
    # Create links
    for i in range(len(firms)):
        for j in range(i+1, len(firms)):
            if random.random() > 0.6:
                links.append({
                    "source": i,
                    "target": j,
                    "value": random.uniform(10, 500)
                })
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[f"{firm}<br>${nodes[i]['derivatives_exposure']:.0f}M" 
                   for i, firm in enumerate(firms)],
            color=[f"rgba(59, 130, 246, {min(1, n['derivatives_exposure']/3000)})" 
                   for n in nodes]
        ),
        link=dict(
            source=[link["source"] for link in links],
            target=[link["target"] for link in links],
            value=[link["value"] for link in links],
            color="rgba(0, 0, 0, 0.2)"
        )
    )])
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': 'Derivatives Exposure Flow Network',
        'height': 600
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 6. Derivatives Metrics
@register_widget({
    "name": "Derivatives Metrics",
    "description": "Key derivatives market metrics",
    "category": "Derivatives",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "derivatives/metrics",
    "gridData": {"w": 20, "h": 4}
})
@router.get("/metrics")
def get_derivatives_metrics():
    """Get derivatives market metrics."""
    return [
        {
            "label": "Total Notional",
            "value": "$487T",
            "delta": "6.8"
        },
        {
            "label": "Daily Volume",
            "value": "$2.3T",
            "delta": "-3.2"
        },
        {
            "label": "Compression Rate",
            "value": "42%",
            "delta": "2.1"
        },
        {
            "label": "CDS Spread (IG)",
            "value": "68bps",
            "delta": "5.0"
        },
        {
            "label": "Active Contracts",
            "value": "1.2M",
            "delta": "8.5"
        }
    ]