# Enhanced Data Generator Summary

## Overview

The `data_generator.py` file has been comprehensively updated to support all the enhanced parameters that were added to the DTCC OpenBB widgets. The mock data generators are now sophisticated, parameter-driven functions that produce realistic, varied data based on user selections.

## Key Enhancements

### 1. Parameter Support
All generator functions now accept flexible parameters using **kwargs pattern:

- **Time Periods**: 1D, 1W, 1M, 3M, 6M, 1Y, YTD
- **Asset Classes**: Equities, Fixed Income, Derivatives, Repo, FX, Commodities
- **Counterparty Types**: Banks, Asset Managers, Hedge Funds, Insurance, Pension Funds
- **Geographic Regions**: US, Europe, APAC, Americas, Global
- **Risk Levels**: Low, Medium, High, Critical
- **Currencies**: USD, EUR, JPY, GBP, CHF, CAD, AUD
- **Settlement Types**: T+0, T+1, T+2, T+3+
- **Regulatory Frameworks**: Dodd-Frank, MiFID II, EMIR, Basel III, CFTC, SEC, ESMA
- **Minimum Thresholds**: min_volume, min_exposure, min_amount, min_notional, etc.

### 2. Enhanced Existing Functions

#### `generate_trade_volumes()`
- **New Parameters**: time_period, asset_classes, min_volume, region
- **Behavior**: Time granularity adjusts based on period (hours/days/weeks), regional volume multipliers, asset-specific patterns, trading hours effects

#### `generate_anomalies()`
- **New Parameters**: severity, asset_classes, counterparty_types, time_period
- **Behavior**: Severity-weighted distribution, asset-specific anomaly types, time-scaled quantity

#### `generate_counterparty_exposures()`
- **New Parameters**: counterparty_types, risk_levels, min_exposure, region
- **Behavior**: Type-specific exposure multipliers, risk-correlated exposure levels, regional counterparty pools

#### `generate_compliance_alerts()`
- **New Parameters**: regulatory_scope, severity, entity_type, time_period
- **Behavior**: Framework-specific alert types, realistic severity distribution, entity-aware alerts

#### All other existing functions similarly enhanced with relevant parameters

### 3. New Generator Functions

#### `generate_derivatives_data()`
- **Returns**: Swaps, options, and volatility surface data
- **Parameters**: asset_classes, currencies, time_period, min_notional
- **Features**: Currency-specific patterns, tenor-based volume scaling, realistic vol surfaces

#### `generate_equity_data()`
- **Returns**: Settlement timelines, ETF flows, short interest by sector
- **Parameters**: settlement_types, currencies, time_period, region
- **Features**: Settlement timing effects, category-based ETF flows, sector-grouped short interest

#### `generate_compliance_data()`
- **Returns**: Regulatory heatmaps, audit trails, exception reports
- **Parameters**: regulatory_frameworks, entity_types, time_period, region
- **Features**: Framework-specific compliance areas, automated audit trails, categorized exceptions

#### `generate_strategy_data()`
- **Returns**: Arbitrage opportunities, market sentiment, liquidity fragmentation
- **Parameters**: asset_classes, time_period, currencies, min_volume
- **Features**: Strategy-specific opportunities, multi-source sentiment, venue fragmentation

#### `generate_risk_metrics()`
- **Returns**: VaR metrics, stress tests, risk concentration
- **Parameters**: counterparty_types, risk_levels, time_period, region
- **Features**: Realistic VaR scaling, scenario-based stress tests, factor concentration

### 4. Realistic Data Patterns

#### Regional Variations
- **US**: Full range of counterparties, USD-focused, comprehensive regulations
- **Europe**: EU-specific banks/frameworks, EUR focus, MiFID II/EMIR emphasis
- **APAC**: Regional banks, JPY focus, local regulatory frameworks
- **Global**: Aggregated view with higher volumes

#### Risk-Based Scaling
- **Low Risk**: Conservative spreads, lower volatility, established counterparties
- **High Risk**: Wider spreads, higher volatility, stressed scenarios
- **Critical Risk**: Extreme values, crisis scenarios, distressed situations

#### Time Period Effects
- **1D**: Hourly granularity, intraday patterns, trading hours effects
- **1W-1M**: Daily/weekly aggregation, business cycle patterns
- **3M+**: Longer-term trends, seasonal effects, regulatory cycles

#### Asset Class Specifics
- **Equities**: High volumes during market hours, sector-based patterns
- **Fixed Income**: Tenor-based scaling, duration effects, credit quality
- **Derivatives**: Notional-based sizing, volatility correlation, risk metrics
- **FX**: 24/7 patterns, currency pair effects, volatility clustering

### 5. Performance Optimizations

- **Efficient Parameter Handling**: Default values minimize computation
- **Realistic Data Limits**: Capped record counts prevent performance issues
- **Smart Filtering**: Minimum thresholds applied during generation, not post-processing
- **Cached Calculations**: Common values computed once per function call

### 6. Utility Functions

#### `get_available_parameters()`
Returns all possible parameter values for discovery

#### `get_function_parameters(function_name)`
Returns specific parameters supported by each generator function

#### Helper Functions
- `get_days_from_period()`: Convert time periods to day counts
- `get_all_*()`: Retrieve complete lists of parameter options

## Usage Examples

### Basic Usage with Defaults
```python
# Use default parameters
trade_data = generate_trade_volumes()
anomalies = generate_anomalies()
```

### Filtered Usage
```python
# European bank compliance for high-severity MiFID II issues
alerts = generate_compliance_alerts(
    regulatory_scope=['MiFID II'],
    severity=['High', 'Critical'],
    entity_type=['Banks'],
    time_period='1W',
    region='Europe'
)

# US equity high-frequency trading with volume filter
volumes = generate_trade_volumes(
    time_period='1D',
    asset_classes=['Equities'],
    min_volume=2000,
    region='US'
)
```

### New Data Types
```python
# Comprehensive derivatives analysis
deriv_data = generate_derivatives_data(
    asset_classes=['Derivatives'],
    currencies=['USD', 'EUR'],
    time_period='1M',
    min_notional=1000
)

# Risk assessment for APAC banks
risk_data = generate_risk_metrics(
    counterparty_types=['Banks'],
    risk_levels=['Medium', 'High'],
    time_period='3M',
    region='APAC'
)
```

## Benefits

1. **Widget Compatibility**: All enhanced widget parameters are now supported
2. **Realistic Variation**: Data responds meaningfully to parameter changes
3. **Performance**: Functions execute quickly even with complex filtering
4. **Extensibility**: Easy to add new parameters or data types
5. **Flexibility**: **kwargs pattern allows for future parameter additions
6. **Discoverability**: Utility functions help users understand available options

## Testing

The `test_enhanced_generator.py` file provides comprehensive testing and demonstrations of all enhanced functionality. Run it to see the enhanced data generator in action across all parameter combinations and new data types.

## Backward Compatibility

All existing function signatures remain compatible. New parameters are optional with sensible defaults, ensuring existing widget code continues to work unchanged while gaining access to enhanced functionality when parameters are provided.