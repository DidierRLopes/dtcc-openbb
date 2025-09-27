"""
Plotly configuration for Causeway backend with light and dark theme support.
"""

import plotly.graph_objects as go


def get_theme_colors(theme='dark'):
    """Get color configuration for light and dark themes."""
    if theme == 'dark':
        return {
            'text': '#FFFFFF',
            'bg_color': '#151518',
            'paper_bg': '#151518',
            'grid_color': 'rgba(128, 128, 128, 0.2)',
            'zeroline_color': 'rgba(128, 128, 128, 0.4)',
            'line_color': '#4169E1',
            'main_line': '#FF8000',  # Orange for dark theme
            'positive_color': '#00C851',
            'negative_color': '#FF4444',
            'neutral': '#2D9BF0',  # Blue
            'neutral_color': '#33B5E5',
            'hover_bg': 'rgba(0, 0, 0, 0.8)',
            'legend_bg': 'rgba(0, 0, 0, 0.5)',
            'legend_border': 'rgba(255, 255, 255, 0.2)',
            'grid': 'rgba(51, 51, 51, 0.3)',
            'heatmap': {
                'zmid': 0,
                'text_color': '#FFFFFF'
            }
        }
    else:  # light theme
        return {
            'text': '#2E2E2E',
            'bg_color': '#FFFFFF',
            'paper_bg': '#FFFFFF',
            'grid_color': 'rgba(128, 128, 128, 0.3)',
            'zeroline_color': 'rgba(128, 128, 128, 0.5)',
            'line_color': '#2E5090',
            'main_line': '#2E5090',  # Navy blue for light theme
            'positive_color': '#008F11',
            'negative_color': '#CC0000',
            'neutral': '#00AA44',  # Forest green
            'neutral_color': '#1976D2',
            'hover_bg': 'rgba(255, 255, 255, 0.9)',
            'legend_bg': 'rgba(255, 255, 255, 0.8)',
            'legend_border': 'rgba(0, 0, 0, 0.2)',
            'grid': 'rgba(221, 221, 221, 0.3)',
            'heatmap': {
                'zmid': 0,
                'text_color': '#333333'
            }
        }


def base_layout(x_title=None, y_title=None, theme='dark', margin=None, height=None):
    """Create base layout configuration for charts."""
    colors = get_theme_colors(theme)
    
    default_margin = {'l': 50, 'r': 50, 't': 10, 'b': 50, 'pad': 0}
    if margin:
        default_margin.update(margin)
    
    layout = {
        'plot_bgcolor': colors['bg_color'],
        'paper_bgcolor': colors['paper_bg'],
        'font': {'color': colors['text'], 'family': 'Arial, sans-serif'},
        'showlegend': True,
        'hovermode': 'closest',
        'margin': default_margin,
        'xaxis': {
            'title': {'text': x_title, 'font': {'color': colors['text']}} if x_title else None,
            'gridcolor': colors['grid_color'],
            'zeroline': True,
            'zerolinecolor': colors['zeroline_color'],
            'tickfont': {'color': colors['text']}
        },
        'yaxis': {
            'title': {'text': y_title, 'font': {'color': colors['text']}} if y_title else None,
            'gridcolor': colors['grid_color'],
            'tickfont': {'color': colors['text']}
        },
        'legend': {
            'orientation': 'v',
            'yanchor': 'top',
            'y': 0.98,
            'xanchor': 'right',
            'x': 0.98,
            'bgcolor': colors['legend_bg'],
            'bordercolor': colors['legend_border'],
            'borderwidth': 1,
            'font': {'color': colors['text']}
        }
    }
    
    if height:
        layout['height'] = height
        
    return layout


def create_line_trace(x_data, y_data, name, theme='dark', color=None, dash=None, width=2):
    """Create a line trace with theme-appropriate styling."""
    colors = get_theme_colors(theme)
    
    if not color:
        color = colors['line_color']
    
    line_config = {'color': color, 'width': width}
    if dash:
        line_config['dash'] = dash
    
    return go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines',
        name=name,
        line=line_config
    )


def create_vertical_line_trace(x_value, y_range, name, theme='dark', color=None):
    """Create a vertical line trace for markers."""
    colors = get_theme_colors(theme)
    
    if not color:
        if 'current' in name.lower():
            color = colors['negative_color']
        elif 'target' in name.lower() or 'consensus' in name.lower():
            color = colors['positive_color']
        else:
            color = colors['neutral_color']
    
    return go.Scatter(
        x=[x_value, x_value],
        y=y_range,
        mode='lines',
        name=name,
        line={'color': color, 'dash': 'dash', 'width': 2},
        showlegend=True,
        hoverinfo='skip'
    )


def get_toolbar_config():
    """Get standard toolbar configuration for Plotly charts."""
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'pan2d',
            'lasso2d',
            'select2d',
            'autoScale2d',
            'hoverClosestCartesian',
            'hoverCompareCartesian',
            'toggleSpikelines'
        ],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'chart',
            'height': 500,
            'width': 800,
            'scale': 1
        }
    }


def format_hover_text(price, rank, change, fy2_pe, fy3_pe, consensus_prob, mc_prob):
    """Format hover text consistently across charts."""
    return (
        f"<b>Price: ${price:.2f}</b><br>"
        f"Rank: {rank:.0f}<br>"
        f"Change: {change:.2f}%<br>"
        f"Implied FY2 PE: {fy2_pe:.2f}<br>"
        f"Implied FY3 PE: {fy3_pe:.2f}<br>"
        f"Probability at or above (consensus cdf): {consensus_prob:.2f}%<br>"
        f"Probability at or above (Monte Carlo): {mc_prob:.1f}%"
    )