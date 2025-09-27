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
from mockup_data.data_generator import generate_counterparties
from plotly_config import get_theme_colors, base_layout, get_toolbar_config

router = APIRouter(prefix="/regulatory_compliance", tags=["Regulatory & Compliance"])

def generate_regulation_heatmap():
    """Generate regulation compliance heatmap."""
    regulations = ["Dodd-Frank", "MiFID II", "EMIR", "Basel III", "CFTC Rules", "ESMA Guidelines"]
    obligation_types = ["Reporting", "Clearing", "Margining", "Capital", "Liquidity", "Risk Mgmt"]
    
    data = []
    for regulation in regulations:
        for obligation in obligation_types:
            compliance_rate = random.uniform(85, 99.5)
            open_issues = random.randint(0, 25)
            
            data.append({
                "regulation": regulation,
                "obligation_type": obligation,
                "compliance_rate": round(compliance_rate, 1),
                "open_issues": open_issues,
                "status": "Good" if compliance_rate > 95 and open_issues < 5 
                         else "Warning" if compliance_rate > 90 
                         else "Critical"
            })
    
    return data

def generate_trade_lifecycle_audit():
    """Generate trade lifecycle audit trail data."""
    trade_ids = [f"TRD-{i:06d}" for i in range(100001, 100021)]
    stages = ["Execution", "Confirmation", "Clearing", "Settlement", "Reporting"]
    
    audit_trail = []
    for trade_id in trade_ids:
        execution_time = datetime.now() - timedelta(hours=random.randint(1, 72))
        
        for i, stage in enumerate(stages):
            stage_time = execution_time + timedelta(minutes=random.randint(5, 120) * (i + 1))
            
            audit_trail.append({
                "trade_id": trade_id,
                "stage": stage,
                "timestamp": stage_time.isoformat(),
                "status": random.choice(["Completed", "Pending", "Failed"] if i < len(stages)-1 else ["Completed"]),
                "counterparty": random.choice(generate_counterparties()),
                "venue": random.choice(["NYSE", "NASDAQ", "DTCC", "LCH", "CME"]),
                "sla_met": random.choice([True, False]),
                "processing_time": random.randint(1, 300)
            })
    
    return sorted(audit_trail, key=lambda x: x["timestamp"], reverse=True)[:50]

def generate_exception_reports():
    """Generate exception report data."""
    exception_types = [
        "Missing LEI", "Invalid ISIN", "Incomplete Trade Details", 
        "Late Reporting", "Counterparty Mismatch", "Settlement Fail"
    ]
    
    exceptions = []
    for i in range(25):
        exceptions.append({
            "exception_id": f"EXC-{i+1:05d}",
            "trade_id": f"TRD-{random.randint(100001, 999999)}",
            "exception_type": random.choice(exception_types),
            "severity": random.choice(["Low", "Medium", "High", "Critical"]),
            "created_date": (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
            "assigned_to": random.choice(["Compliance Team", "Operations", "Risk Team", "Legal"]),
            "status": random.choice(["Open", "In Progress", "Pending Review", "Resolved"]),
            "description": f"Exception in {random.choice(exception_types)} validation",
            "regulatory_impact": random.choice(["None", "Low", "Medium", "High"])
        })
    
    return sorted(exceptions, key=lambda x: x["created_date"], reverse=True)

def generate_kyc_aml_flags():
    """Generate KYC/AML risk flag data."""
    risk_types = ["High Risk Country", "PEP Status", "Sanctions List", "Unusual Activity", "Documentation Gap"]
    
    flags = []
    entities = generate_counterparties()[:15]
    
    for entity in entities:
        if random.random() > 0.7:  # 30% chance of having flags
            flags.append({
                "entity": entity,
                "risk_type": random.choice(risk_types),
                "risk_score": random.randint(60, 95),
                "flag_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "status": random.choice(["Active", "Under Review", "Cleared", "Escalated"]),
                "trade_volume": round(random.uniform(10, 500), 2),
                "jurisdiction": random.choice(["US", "EU", "UK", "APAC", "LATAM"]),
                "review_required": random.choice([True, False])
            })
    
    return sorted(flags, key=lambda x: x["risk_score"], reverse=True)

def generate_compliance_alerts():
    """Generate real-time compliance alerts."""
    alert_types = [
        "Late Trade Report", "Missing Regulatory Field", "Threshold Breach", 
        "Unusual Volume", "Cross-Border Issue", "Margin Call"
    ]
    
    alerts = []
    for i in range(15):
        alerts.append({
            "alert_id": f"ALERT-{i+1:04d}",
            "timestamp": datetime.now().isoformat(),
            "alert_type": random.choice(alert_types),
            "regulation": random.choice(["Dodd-Frank", "MiFID II", "EMIR", "CFTC"]),
            "entity": random.choice(generate_counterparties()),
            "severity": random.choice(["Info", "Warning", "Critical"]),
            "auto_resolved": random.choice([True, False]),
            "description": f"Automated alert for {random.choice(alert_types)}",
            "action_required": random.choice(["None", "Review", "Report", "Escalate"])
        })
    
    return alerts

# 1. Regulation Compliance Heatmap
@register_widget({
    "name": "Regulation Compliance Heatmap",
    "description": "Open obligations tagged by regulation type",
    "category": "Regulatory & Compliance",
    "subCategory": "Overview",
    "type": "chart",
    "endpoint": "regulatory_compliance/regulation_heatmap",
    "gridData": {"w": 20, "h": 10}
})
@router.get("/regulation_heatmap")
def get_regulation_heatmap(theme: str = "dark"):
    """Generate regulation compliance heatmap."""
    data = generate_regulation_heatmap()
    df = pd.DataFrame(data)
    
    # Create pivot table
    pivot = df.pivot_table(values='compliance_rate', index='regulation', columns='obligation_type')
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=95,
        zmin=85,
        zmax=100,
        text=[[f'{val:.1f}%' for val in row] for row in pivot.values],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='Regulation: %{y}<br>Obligation: %{x}<br>Compliance: %{z:.1f}%<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        'title': 'Regulatory Compliance Heatmap',
        'xaxis_title': 'Obligation Type',
        'yaxis_title': 'Regulation',
        'height': 400
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. Trade Lifecycle Audit Trail
@register_widget({
    "name": "Trade Lifecycle Audit Trail",
    "description": "Interactive drilldown from execution to settlement",
    "category": "Regulatory & Compliance",
    "subCategory": "Audit Trail",
    "type": "table",
    "endpoint": "regulatory_compliance/audit_trail",
    "gridData": {"w": 20, "h": 12},
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "trade_id",
                    "headerName": "Trade ID",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "stage",
                    "headerName": "Stage",
                    "width": 120
                },
                {
                    "field": "timestamp",
                    "headerName": "Timestamp",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Completed", "color": "#10b981", "fill": False},
                            {"condition": "eq", "value": "Pending", "color": "#f59e0b", "fill": False},
                            {"condition": "eq", "value": "Failed", "color": "#ef4444", "fill": True}
                        ]
                    }
                },
                {
                    "field": "counterparty",
                    "headerName": "Counterparty",
                    "width": 150
                },
                {
                    "field": "venue",
                    "headerName": "Venue",
                    "width": 100
                },
                {
                    "field": "sla_met",
                    "headerName": "SLA Met",
                    "width": 90,
                    "cellDataType": "boolean",
                    "renderFn": "greenRed"
                },
                {
                    "field": "processing_time",
                    "headerName": "Processing Time (min)",
                    "width": 160,
                    "cellDataType": "number"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "trade_filter",
            "value": "All",
            "label": "Filter by Status",
            "type": "text",
            "options": [
                {"label": "All", "value": "All"},
                {"label": "Failed", "value": "Failed"},
                {"label": "Pending", "value": "Pending"}
            ]
        }
    ]
})
@router.get("/audit_trail")
def get_audit_trail(trade_filter: str = "All"):
    """Get trade lifecycle audit trail."""
    data = generate_trade_lifecycle_audit()
    
    if trade_filter != "All":
        data = [d for d in data if d["status"] == trade_filter]
    
    return data

# 3. Exception Report Table
@register_widget({
    "name": "Exception Reports",
    "description": "Trades missing key fields or failing validation",
    "category": "Regulatory & Compliance",
    "subCategory": "Exceptions",
    "type": "table",
    "endpoint": "regulatory_compliance/exceptions",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "exception_id",
                    "headerName": "Exception ID",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "trade_id",
                    "headerName": "Trade ID",
                    "width": 120
                },
                {
                    "field": "exception_type",
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
                    "field": "created_date",
                    "headerName": "Created",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "assigned_to",
                    "headerName": "Assigned To",
                    "width": 120
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Resolved", "color": "#10b981", "fill": False},
                            {"condition": "eq", "value": "Open", "color": "#ef4444", "fill": False},
                            {"condition": "eq", "value": "In Progress", "color": "#f59e0b", "fill": False}
                        ]
                    }
                },
                {
                    "field": "regulatory_impact",
                    "headerName": "Reg Impact",
                    "width": 120
                }
            ]
        }
    }
})
@router.get("/exceptions")
def get_exceptions():
    """Get exception reports."""
    return generate_exception_reports()

# 4. KYC/AML Risk Flag List
@register_widget({
    "name": "KYC/AML Risk Flags",
    "description": "Suspicious counterparties linked to trade flows",
    "category": "Regulatory & Compliance",
    "subCategory": "Risk Management",
    "type": "table",
    "endpoint": "regulatory_compliance/kyc_aml_flags",
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
                    "field": "entity",
                    "headerName": "Entity",
                    "width": 150,
                    "pinned": "left"
                },
                {
                    "field": "risk_type",
                    "headerName": "Risk Type",
                    "width": 150
                },
                {
                    "field": "risk_score",
                    "headerName": "Risk Score",
                    "width": 110,
                    "cellDataType": "number",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 85, "color": "#ef4444", "fill": True},
                            {"condition": "gt", "value": 70, "color": "#f59e0b", "fill": False},
                            {"condition": "lte", "value": 70, "color": "#10b981", "fill": False}
                        ]
                    }
                },
                {
                    "field": "flag_date",
                    "headerName": "Flag Date",
                    "width": 120,
                    "cellDataType": "date"
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Active", "color": "#ef4444", "fill": False},
                            {"condition": "eq", "value": "Cleared", "color": "#10b981", "fill": False},
                            {"condition": "eq", "value": "Under Review", "color": "#f59e0b", "fill": False}
                        ]
                    }
                },
                {
                    "field": "trade_volume",
                    "headerName": "Trade Volume ($M)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                },
                {
                    "field": "jurisdiction",
                    "headerName": "Jurisdiction",
                    "width": 110
                },
                {
                    "field": "review_required",
                    "headerName": "Review Req.",
                    "width": 110,
                    "cellDataType": "boolean",
                    "renderFn": "greenRed"
                }
            ]
        }
    }
})
@router.get("/kyc_aml_flags")
def get_kyc_aml_flags():
    """Get KYC/AML risk flags."""
    return generate_kyc_aml_flags()

# 5. Compliance Alerts Ticker
@register_widget({
    "name": "Compliance Alerts Ticker",
    "description": "Real-time summary of compliance issues needing review",
    "category": "Regulatory & Compliance",
    "subCategory": "Alerts",
    "type": "table",
    "endpoint": "regulatory_compliance/alerts_ticker",
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
                    "field": "alert_id",
                    "headerName": "Alert ID",
                    "width": 100
                },
                {
                    "field": "alert_type",
                    "headerName": "Type",
                    "width": 150
                },
                {
                    "field": "regulation",
                    "headerName": "Regulation",
                    "width": 120
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
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Critical", "color": "#ef4444", "fill": True},
                            {"condition": "eq", "value": "Warning", "color": "#f59e0b", "fill": False},
                            {"condition": "eq", "value": "Info", "color": "#3b82f6", "fill": False}
                        ]
                    }
                },
                {
                    "field": "action_required",
                    "headerName": "Action",
                    "width": 100
                }
            ]
        }
    }
})
@router.get("/alerts_ticker")
def get_alerts_ticker():
    """Get compliance alerts ticker."""
    return generate_compliance_alerts()

# 6. Compliance Metrics
@register_widget({
    "name": "Compliance Metrics",
    "description": "Key regulatory compliance metrics",
    "category": "Regulatory & Compliance",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "regulatory_compliance/metrics",
    "gridData": {"w": 20, "h": 4}
})
@router.get("/metrics")
def get_compliance_metrics():
    """Get compliance metrics."""
    return [
        {
            "label": "Overall Compliance",
            "value": "94.2%",
            "delta": "1.8"
        },
        {
            "label": "Open Exceptions",
            "value": "127",
            "delta": "-15.0"
        },
        {
            "label": "KYC Flags",
            "value": "8",
            "delta": "2.0"
        },
        {
            "label": "SLA Compliance",
            "value": "96.8%",
            "delta": "0.5"
        },
        {
            "label": "Audit Score",
            "value": "A-",
            "delta": "0.0"
        }
    ]