#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced data generator capabilities.
This shows how the mock data generators now support all the enhanced parameters
that were added to the widgets.
"""

import data_generator as dg
import json
from pprint import pprint

def demonstrate_parameter_support():
    """Demonstrate all the enhanced parameter support."""
    
    print("=" * 60)
    print("ENHANCED DATA GENERATOR DEMONSTRATION")
    print("=" * 60)
    
    # 1. Show available parameters
    print("\n1. AVAILABLE PARAMETERS")
    print("-" * 30)
    params = dg.get_available_parameters()
    for param_type, values in params.items():
        print(f"{param_type}: {values}")
    
    # 2. Demonstrate time period filtering
    print("\n2. TIME PERIOD FILTERING")
    print("-" * 30)
    for period in ["1D", "1W", "1M", "1Y"]:
        trade_data = dg.generate_trade_volumes(time_period=period, asset_classes=["Equities"])
        period_key = "hour" if period == "1D" else ("day" if period == "1W" else "week")
        print(f"{period}: {len(trade_data)} records with '{period_key}' time dimension")
    
    # 3. Demonstrate asset class filtering
    print("\n3. ASSET CLASS FILTERING")
    print("-" * 30)
    for asset_class in ["Equities", "Fixed Income", "Derivatives"]:
        anomalies = dg.generate_anomalies(asset_classes=[asset_class], time_period="1D")
        print(f"{asset_class}: {len(anomalies)} anomalies generated")
    
    # 4. Demonstrate regional variations
    print("\n4. REGIONAL VARIATIONS")
    print("-" * 30)
    for region in ["US", "Europe", "APAC"]:
        treasury_data = dg.generate_treasury_volumes(region=region, time_period="1W")
        print(f"{region} Treasury Types: {[t['tenor'] for t in treasury_data]}")
    
    # 5. Demonstrate risk level filtering
    print("\n5. RISK LEVEL FILTERING")
    print("-" * 30)
    for risk_level in ["Low", "High", "Critical"]:
        cds_data = dg.generate_cds_spreads(risk_levels=[risk_level], time_period="1M")
        if cds_data["single_names"]:
            avg_spread = sum(s for spreads in [sn["spreads"] for sn in cds_data["single_names"]] for s in spreads) / \
                        sum(len(sn["spreads"]) for sn in cds_data["single_names"])
            print(f"{risk_level} Risk - Avg CDS Spread: {avg_spread:.1f} bps")
    
    # 6. Demonstrate minimum threshold filtering
    print("\n6. MINIMUM THRESHOLD FILTERING")
    print("-" * 30)
    for min_vol in [0, 1000, 5000]:
        volumes = dg.generate_trade_volumes(min_volume=min_vol, time_period="1D")
        if volumes:
            avg_vol = sum(v["volume"] for v in volumes) / len(volumes)
            print(f"Min volume {min_vol}: {len(volumes)} records, avg volume: {avg_vol:.2f}")
        else:
            print(f"Min volume {min_vol}: No records meet threshold")
    
    # 7. Demonstrate currency filtering
    print("\n7. CURRENCY FILTERING")
    print("-" * 30)
    for currencies in [["USD"], ["EUR", "GBP"], ["JPY", "CHF"]]:
        swap_data = dg.generate_swap_notionals(currencies=currencies, time_period="1M")
        unique_currencies = list(set(s["currency"] for s in swap_data))
        print(f"Requested {currencies} -> Generated: {unique_currencies}")
    
    # 8. Demonstrate counterparty type filtering
    print("\n8. COUNTERPARTY TYPE FILTERING")
    print("-" * 30)
    for cp_type in [["Banks"], ["Asset Managers"], ["Hedge Funds"]]:
        exposure_data = dg.generate_counterparty_exposures(
            counterparty_types=cp_type, region="Global"
        )
        cp_types = list(set(node["type"] for node in exposure_data["nodes"]))
        print(f"Requested {cp_type} -> Generated types: {cp_types}")
    
    # 9. Demonstrate regulatory framework filtering
    print("\n9. REGULATORY FRAMEWORK FILTERING")
    print("-" * 30)
    for frameworks in [["Dodd-Frank"], ["MiFID II", "EMIR"], ["Basel III"]]:
        compliance_data = dg.generate_compliance_alerts(
            regulatory_scope=frameworks, time_period="1W"
        )
        used_frameworks = list(set(alert["regulation"] for alert in compliance_data))
        print(f"Requested {frameworks} -> Generated: {used_frameworks}")
    
    # 10. Demonstrate new data types
    print("\n10. NEW DATA TYPES")
    print("-" * 30)
    
    # Derivatives data
    deriv_data = dg.generate_derivatives_data(currencies=["USD", "EUR"], time_period="1M")
    print(f"Derivatives: {len(deriv_data['swaps'])} swaps, {len(deriv_data['options'])} options, {len(deriv_data['volatility_surface'])} vol points")
    
    # Equity data
    equity_data = dg.generate_equity_data(settlement_types=["T+2"], time_period="1W")
    print(f"Equities: {len(equity_data['settlement_timeline'])} settlements, {len(equity_data['etf_flows'])} ETF flows")
    
    # Compliance data
    compliance_data = dg.generate_compliance_data(regulatory_frameworks=["MiFID II"], time_period="1M")
    print(f"Compliance: {len(compliance_data['regulatory_heatmap'])} heatmap points, {len(compliance_data['audit_trail'])} audit entries")
    
    # Strategy data
    strategy_data = dg.generate_strategy_data(asset_classes=["Equities"], time_period="1M")
    print(f"Strategy: {len(strategy_data['arbitrage'])} arbitrage ops, {len(strategy_data['sentiment'])} sentiment points")
    
    # Risk metrics
    risk_data = dg.generate_risk_metrics(counterparty_types=["Banks"], time_period="1M")
    print(f"Risk: {len(risk_data['var_metrics'])} VaR metrics, {len(risk_data['stress_tests'])} stress tests")
    
    # 11. Show realistic parameter combinations
    print("\n11. REALISTIC PARAMETER COMBINATIONS")
    print("-" * 30)
    
    # High-frequency equity trading scenario
    hf_data = dg.generate_trade_volumes(
        time_period="1D",
        asset_classes=["Equities"],
        min_volume=2000,
        region="US"
    )
    print(f"High-frequency US equity trading: {len(hf_data)} qualifying volume periods")
    
    # European compliance monitoring
    eu_compliance = dg.generate_compliance_alerts(
        regulatory_scope=["MiFID II", "EMIR"],
        severity=["High", "Critical"],
        entity_type=["Banks"],
        time_period="1W"
    )
    print(f"EU bank compliance issues: {len(eu_compliance)} high-severity alerts")
    
    # Asian derivatives risk assessment
    asia_risk = dg.generate_counterparty_exposures(
        counterparty_types=["Banks", "Asset Managers"],
        risk_levels=["Medium", "High", "Critical"],
        min_exposure=1000,
        region="APAC"
    )
    print(f"APAC derivatives risk network: {len(asia_risk['nodes'])} counterparties, {len(asia_risk['links'])} relationships")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nThe enhanced data generator now supports:")
    print("✓ Time period filtering (1D, 1W, 1M, 3M, 6M, 1Y, YTD)")
    print("✓ Asset class filtering (Equities, Fixed Income, Derivatives, etc.)")
    print("✓ Counterparty type filtering (Banks, Asset Managers, Hedge Funds, etc.)")
    print("✓ Geographic region filtering (US, Europe, APAC, Americas, Global)")
    print("✓ Risk level filtering (Low, Medium, High, Critical)")
    print("✓ Currency filtering (USD, EUR, JPY, GBP, etc.)")
    print("✓ Settlement type filtering (T+0, T+1, T+2, T+3+)")
    print("✓ Regulatory framework filtering (Dodd-Frank, MiFID II, EMIR, etc.)")
    print("✓ Minimum threshold filtering (volumes, exposures, amounts)")
    print("✓ New data types (derivatives, equity, compliance, strategy, risk)")
    print("✓ Realistic parameter-driven data variation")
    print("✓ Performance optimization for quick execution")

if __name__ == "__main__":
    demonstrate_parameter_support()