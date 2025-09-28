# DTCC OpenBB Dashboard System

A comprehensive market monitoring and analytics dashboard system built for OpenBB Workspace, providing real-time insights across major financial asset classes and risk dimensions.

## 🎯 Overview

This system provides 7 specialized dashboards with 41+ interactive widgets covering:
- Market transparency and surveillance
- Risk management and stress testing
- Fixed income and repo markets
- Derivatives analytics
- Equities and ETF monitoring
- Regulatory compliance
- Trading strategy insights

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
```bash
git clone <repository-url>
cd dtcc-openbb
```

2. **Run the setup script**
```bash
./setup.sh
```

3. **Or install manually**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System

1. **Activate virtual environment** (if not already active)
```bash
source venv/bin/activate
```

2. **Start the server**
```bash
uvicorn main:app --reload --port 8000
```

3. **Access the system**
- API Root: http://localhost:8000
- Widgets Configuration: http://localhost:8000/widgets.json
- Apps Configuration: http://localhost:8000/apps.json

## 📊 Dashboards & Widgets

### 1. Market Transparency & Surveillance
- **Trade Volume Heatmap** - Monitor volumes by asset class/hour
- **Anomaly Detector** - Track settlement fails and cancel spikes
- **Counterparty Exposure Network** - Interactive network visualization
- **Regulatory Compliance Ticker** - Real-time compliance alerts
- **Activity Metrics** - Key surveillance metrics

### 2. Risk Management & Stress Testing
- **Counterparty Exposure Treemap** - Hierarchical exposure view
- **Collateral Requirement Forecast** - Multi-scenario projections
- **Settlement Fails Tracker** - Time series with stress overlays
- **Liquidity Heatmap** - Repo availability matrix
- **Stress Test Results** - Scenario impact analysis
- **Risk Metrics** - Key risk indicators

### 3. Fixed Income Market
- **Treasury Trade Volumes** - Volumes by tenor over time
- **Repo Rate Spread Tracker** - GCF vs SOFR/ON RRP
- **Fails-to-Deliver Monitor** - CUSIP-level fail tracking
- **Dealer Activity Leaderboard** - Top lenders/borrowers
- **Liquidity Curve Heatmap** - Availability by collateral type
- **Fixed Income Metrics** - Market summary

### 4. Derivatives Analytics
- **Swap Notional by Tenor** - Cross-currency analysis
- **CDS Spread Monitor** - Index vs single-name tracking
- **Volatility Surface** - 3D implied vol visualization
- **Net Open Positions** - Asset class breakdown
- **Derivatives Network** - Counterparty flow analysis
- **Derivatives Metrics** - Market statistics

### 5. Equities & ETF
- **Settlement Timeline** - T+1/T+2 obligations forecast
- **ETF Flows** - Creation/redemption with basket drilldown
- **Short Interest Tracker** - Borrow rates and utilization
- **Concentration Risk** - Largest net obligations by security
- **Crowded Trade Alerts** - Real-time borrow/fail spikes
- **Equities Metrics** - Market summary

### 6. Regulatory & Compliance
- **Regulation Heatmap** - Compliance rates by regulation
- **Trade Lifecycle Audit** - Execution to settlement tracking
- **Exception Reports** - Missing fields and validations
- **KYC/AML Flags** - Suspicious entity monitoring
- **Compliance Alerts** - Real-time regulatory issues
- **Compliance Metrics** - Regulatory KPIs

### 7. Trading & Investment Strategy
- **Repo Squeeze Detector** - Collateral demand spikes
- **Sentiment Gauge** - Short interest as bearishness proxy
- **Liquidity Fragmentation** - Cross-venue analysis
- **Arbitrage Monitor** - CDS/bond spreads, ETF/NAV gaps
- **Flow Momentum** - Net flows mapped to performance
- **Strategy Metrics** - Trading insights

## 🛠️ Technical Architecture

### Backend Stack
- **FastAPI** - Modern async web framework
- **Plotly** - Interactive charts and visualizations
- **Pandas/NumPy** - Data manipulation and analysis
- **Uvicorn** - ASGI server

### Widget Types
- **Interactive Charts** - Plotly-based with theme support
- **Advanced Tables** - AgGrid with sorting, filtering, charting
- **Metrics** - KPI displays with delta indicators
- **Heatmaps** - Multi-dimensional data visualization
- **Network Graphs** - Relationship and flow analysis
- **3D Surfaces** - Complex data representations

### Features
- ✅ OpenBB Workspace compatible
- ✅ Dark/Light theme support
- ✅ Real-time data refresh
- ✅ Interactive parameters
- ✅ Raw data mode for AI copilot
- ✅ Responsive design
- ✅ Comprehensive mock data

## 🔧 Configuration

### Apps Configuration Structure
Each dashboard has its own app configuration file in the `apps/` directory:
- `apps/market_surveillance.json` - Market surveillance app
- `apps/risk_management.json` - Risk management app  
- `apps/fixed_income.json` - Fixed income app
- `apps/derivatives.json` - Derivatives app
- `apps/equities_etf.json` - Equities & ETF app
- `apps/regulatory_compliance.json` - Compliance app
- `apps/trading_strategy.json` - Trading strategy app

The `/apps.json` endpoint dynamically loads and aggregates these individual files.

### Updating Apps Configuration
1. Edit individual app files in `apps/` directory
2. Changes are automatically available via the `/apps.json` endpoint
3. No manual regeneration needed (dynamic loading)

### Adding New Widgets
1. Create endpoint function in appropriate router
2. Use `@register_widget()` decorator with configuration
3. Widget will be automatically registered
4. Add widget to appropriate app configuration in `apps/` directory

### Widget Configuration Example
```python
@register_widget({
    "name": "My Widget",
    "description": "Widget description",
    "category": "Dashboard Category", 
    "type": "chart",  # or "table", "metric"
    "endpoint": "dashboard/my_widget",
    "gridData": {"w": 20, "h": 10}
})
@router.get("/my_widget")
def my_widget():
    return {"data": "example"}
```

## 📡 API Endpoints

### Core Endpoints
- `GET /` - API root information
- `GET /widgets.json` - Widget configurations for OpenBB (41 widgets)
- `GET /apps.json` - Dashboard app configurations (7 apps with 14 tabs)

### Dashboard Endpoints
- `/market_surveillance/*` - Market surveillance widgets
- `/risk_management/*` - Risk management widgets
- `/fixed_income/*` - Fixed income widgets
- `/derivatives/*` - Derivatives widgets
- `/equities_etf/*` - Equities & ETF widgets
- `/regulatory_compliance/*` - Compliance widgets
- `/trading_strategy/*` - Trading strategy widgets

## 🧪 Testing

Test individual widgets:
```bash
curl http://localhost:8000/market_surveillance/activity_metrics
curl http://localhost:8000/widgets.json
```

## 🚢 OpenBB Workspace Integration

1. Start the DTCC dashboard system
2. In OpenBB Workspace, add custom backend: `http://localhost:8000`
3. Widgets will appear in the widget library
4. Apps will be available in the apps section

## 📝 Mock Data

The system includes comprehensive mock data generators that simulate realistic DTCC scenarios:
- Trade volumes and patterns
- Counterparty relationships
- Settlement fails and anomalies
- Regulatory compliance data
- Risk metrics and stress scenarios

## 🔒 Security

- CORS properly configured for OpenBB Workspace
- No sensitive data in mock generators
- Secure defaults for all configurations

## 📄 License

This project is provided as-is for demonstration and development purposes.

## Branding

Logo: https://d2pasa6bkzkrjd.cloudfront.net/_resize/consensus2025/partner/500/site/consensus2025/images/userfiles/partners/15d6a0492f47a15733c125af54845766.png

Palette:
- #0E5447
- #ED6D3C
- #f6c544

---

**Built for OpenBB Workspace** | **Comprehensive DTCC Market Analytics**
