import random
from datetime import datetime, timedelta
import json

def generate_time_series(days=30, base_value=100, volatility=0.05):
    """Generate time series data with random walk."""
    dates = []
    values = []
    current_value = base_value
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        dates.append(date)
        
        change = random.gauss(0, volatility) * current_value
        current_value += change
        current_value = max(current_value, base_value * 0.5)
        values.append(round(current_value, 2))
    
    return dates, values

def generate_asset_classes():
    """Generate mock asset class data."""
    return [
        "Equities", "Fixed Income", "Derivatives", 
        "Commodities", "FX", "Crypto", "ETFs", "Options"
    ]

def generate_counterparties():
    """Generate mock counterparty data."""
    firms = [
        "JP Morgan", "Goldman Sachs", "Morgan Stanley", "Bank of America",
        "Citi", "Wells Fargo", "Deutsche Bank", "Barclays", "HSBC", "UBS",
        "Credit Suisse", "BNP Paribas", "Societe Generale", "RBC",
        "TD Bank", "Scotiabank", "State Street", "BNY Mellon"
    ]
    return firms

def generate_trade_volumes():
    """Generate mock trade volume heatmap data."""
    asset_classes = generate_asset_classes()
    hours = [f"{i:02d}:00" for i in range(24)]
    
    data = []
    for asset in asset_classes:
        for hour in hours:
            volume = random.uniform(100, 5000) * (1.5 if 9 <= int(hour[:2]) <= 16 else 0.5)
            data.append({
                "asset_class": asset,
                "hour": hour,
                "volume": round(volume, 2),
                "trades": random.randint(50, 500)
            })
    
    return data

def generate_anomalies():
    """Generate mock anomaly data."""
    anomaly_types = ["Settlement Fail", "Cancel Spike", "Price Deviation", "Volume Anomaly", "Latency Issue"]
    severities = ["Low", "Medium", "High", "Critical"]
    
    anomalies = []
    for i in range(20):
        timestamp = (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat()
        anomalies.append({
            "id": f"ANO-{i+1:04d}",
            "timestamp": timestamp,
            "type": random.choice(anomaly_types),
            "severity": random.choice(severities),
            "asset": random.choice(generate_asset_classes()),
            "counterparty": random.choice(generate_counterparties()),
            "value": round(random.uniform(100000, 10000000), 2),
            "status": random.choice(["Open", "Investigating", "Resolved"])
        })
    
    return sorted(anomalies, key=lambda x: x["timestamp"], reverse=True)

def generate_counterparty_exposures():
    """Generate counterparty exposure network data."""
    firms = generate_counterparties()[:10]
    
    nodes = []
    links = []
    
    for i, firm in enumerate(firms):
        exposure = random.uniform(100, 5000)
        nodes.append({
            "id": firm,
            "group": i % 3,
            "exposure": round(exposure, 2),
            "risk_score": round(random.uniform(0, 100), 1)
        })
    
    for i in range(len(firms)):
        for j in range(i+1, len(firms)):
            if random.random() > 0.7:
                links.append({
                    "source": firms[i],
                    "target": firms[j],
                    "value": round(random.uniform(10, 500), 2)
                })
    
    return {"nodes": nodes, "links": links}

def generate_compliance_alerts():
    """Generate mock compliance alerts."""
    alert_types = ["Under-reported", "Mismatched Trade", "Missing Field", "Late Settlement", "KYC Issue"]
    
    alerts = []
    for i in range(10):
        alerts.append({
            "id": f"COMP-{i+1:04d}",
            "timestamp": datetime.now().isoformat(),
            "type": random.choice(alert_types),
            "regulation": random.choice(["Dodd-Frank", "MiFID II", "EMIR", "Basel III"]),
            "entity": random.choice(generate_counterparties()),
            "severity": random.choice(["Low", "Medium", "High"]),
            "description": f"Alert description for {alert_types[i % len(alert_types)]}"
        })
    
    return alerts

def generate_treasury_volumes():
    """Generate treasury trade volume data by tenor."""
    tenors = ["Bills (1-12M)", "Notes (2-10Y)", "Bonds (20-30Y)", "TIPS", "FRNs"]
    dates, _ = generate_time_series(30)
    
    data = []
    for tenor in tenors:
        volumes = []
        for date in dates:
            volume = random.uniform(50, 500) * (1.2 if "Bills" in tenor else 0.8)
            volumes.append(round(volume, 2))
        
        data.append({
            "tenor": tenor,
            "dates": dates,
            "volumes": volumes
        })
    
    return data

def generate_repo_rates():
    """Generate repo rate data."""
    dates, gcf_rates = generate_time_series(30, base_value=2.5, volatility=0.01)
    _, sofr_rates = generate_time_series(30, base_value=2.45, volatility=0.01)
    _, on_rrp_rates = generate_time_series(30, base_value=2.4, volatility=0.008)
    
    return {
        "dates": dates,
        "GCF_Repo": gcf_rates,
        "SOFR": sofr_rates,
        "ON_RRP": on_rrp_rates
    }

def generate_settlement_fails():
    """Generate settlement fails data."""
    cusips = [f"CUSIP{i:04d}" for i in range(1, 21)]
    
    data = []
    for cusip in cusips:
        data.append({
            "cusip": cusip,
            "tenor": random.choice(["2Y", "5Y", "10Y", "30Y"]),
            "fails_amount": round(random.uniform(0, 100) * 1000000, 2),
            "fail_rate": round(random.uniform(0, 5), 2),
            "days_failed": random.randint(0, 10)
        })
    
    return sorted(data, key=lambda x: x["fails_amount"], reverse=True)

def generate_dealer_activity():
    """Generate dealer activity leaderboard."""
    dealers = generate_counterparties()[:15]
    
    data = []
    for dealer in dealers:
        data.append({
            "dealer": dealer,
            "lending_volume": round(random.uniform(100, 2000), 2),
            "borrowing_volume": round(random.uniform(100, 2000), 2),
            "net_position": round(random.uniform(-500, 500), 2),
            "market_share": round(random.uniform(1, 15), 1)
        })
    
    return sorted(data, key=lambda x: x["lending_volume"] + x["borrowing_volume"], reverse=True)

def generate_swap_notionals():
    """Generate swap notional data."""
    currencies = ["USD", "EUR", "GBP", "JPY", "CHF"]
    tenors = ["1Y", "2Y", "5Y", "10Y", "30Y"]
    
    data = []
    for currency in currencies:
        for tenor in tenors:
            data.append({
                "currency": currency,
                "tenor": tenor,
                "notional": round(random.uniform(100, 5000), 2),
                "trades": random.randint(10, 500),
                "avg_size": round(random.uniform(1, 50), 2)
            })
    
    return data

def generate_cds_spreads():
    """Generate CDS spread data."""
    indices = ["CDX.IG", "CDX.HY", "iTraxx Europe", "iTraxx XOver"]
    single_names = ["AAPL", "MSFT", "JPM", "BAC", "GS"]
    
    data = {
        "indices": [],
        "single_names": []
    }
    
    dates, _ = generate_time_series(30)
    
    for index in indices:
        spreads = [round(random.uniform(50, 200), 2) for _ in dates]
        data["indices"].append({
            "name": index,
            "dates": dates,
            "spreads": spreads
        })
    
    for name in single_names:
        spreads = [round(random.uniform(20, 150), 2) for _ in dates]
        data["single_names"].append({
            "name": name,
            "dates": dates,
            "spreads": spreads
        })
    
    return data

def generate_etf_flows():
    """Generate ETF creation/redemption flow data."""
    etfs = ["SPY", "QQQ", "IWM", "EEM", "GLD", "TLT", "HYG", "LQD"]
    
    data = []
    dates, _ = generate_time_series(7)
    
    for etf in etfs:
        for date in dates:
            creation = round(random.uniform(0, 500), 2)
            redemption = round(random.uniform(0, 500), 2)
            data.append({
                "etf": etf,
                "date": date,
                "creation": creation,
                "redemption": redemption,
                "net_flow": round(creation - redemption, 2)
            })
    
    return data

def generate_short_interest():
    """Generate short interest data."""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD"]
    
    data = []
    for symbol in symbols:
        data.append({
            "symbol": symbol,
            "shares_short": round(random.uniform(1, 50) * 1000000),
            "short_ratio": round(random.uniform(1, 10), 2),
            "days_to_cover": round(random.uniform(1, 5), 1),
            "borrow_rate": round(random.uniform(0.5, 15), 2),
            "change_7d": round(random.uniform(-20, 20), 2)
        })
    
    return sorted(data, key=lambda x: x["shares_short"], reverse=True)