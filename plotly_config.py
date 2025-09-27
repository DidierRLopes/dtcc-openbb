"""
Plotly configuration for DTCC OpenBB Dashboard with official DTCC branding colors.
"""

import plotly.graph_objects as go

# DTCC Official Brand Colors
DTCC_COLORS = {
    'jaffa': '#ED6D3C',        # Primary brand color (RGB: 237, 109, 60)
    'eden': '#0E5447',         # Secondary/complementary color  
    'gallery': '#EBEBEB',      # Neutral off-white/light tone
    'cream': '#F8F6F3',        # Cream/off-white neutral background
    'dark_grey': '#2E2E2E',    # Dark tone for text/contrast
    'light_grey': '#8E8E8E',   # Medium grey for secondary text
}

def get_dtcc_palette():
    """Get DTCC color palette for charts."""
    return [
        DTCC_COLORS['jaffa'],      # Primary
        DTCC_COLORS['eden'],       # Secondary
        '#B85D47',                 # Jaffa variant
        '#1A6B5A',                 # Eden variant
        '#F4946B',                 # Light Jaffa
        '#236B5C',                 # Medium Eden
        '#D96343',                 # Medium Jaffa
        '#0F4A3F',                 # Dark Eden
    ]

def get_theme_colors(theme='dark'):
    """Get DTCC color configuration for light and dark themes."""
    if theme == 'dark':
        return {
            'text': '#FFFFFF',
            'bg_color': '#151518',        # OpenBB dark background
            'paper_bg': '#151518',       # OpenBB dark background
            'grid_color': 'rgba(255, 255, 255, 0.1)',
            'zeroline_color': 'rgba(255, 255, 255, 0.2)',
            'line_color': DTCC_COLORS['jaffa'],
            'main_line': DTCC_COLORS['jaffa'],
            'positive_color': DTCC_COLORS['eden'],
            'negative_color': '#E74C3C',
            'neutral': DTCC_COLORS['jaffa'],
            'neutral_color': DTCC_COLORS['eden'],
            'hover_bg': 'rgba(0, 0, 0, 0.8)',
            'legend_bg': 'rgba(0, 0, 0, 0.7)',
            'legend_border': f"rgba(237, 109, 60, 0.3)",
            'grid': 'rgba(255, 255, 255, 0.1)',
            'heatmap': {
                'zmid': 0,
                'text_color': '#FFFFFF'
            },
            'palette': get_dtcc_palette()
        }
    else:  # light theme
        return {
            'text': DTCC_COLORS['dark_grey'],
            'bg_color': '#FFFFFF',       # OpenBB light background (white)
            'paper_bg': '#FFFFFF',      # OpenBB light background (white)
            'grid_color': 'rgba(0, 0, 0, 0.15)',
            'zeroline_color': 'rgba(0, 0, 0, 0.25)',
            'line_color': DTCC_COLORS['jaffa'],
            'main_line': DTCC_COLORS['jaffa'],
            'positive_color': DTCC_COLORS['eden'],
            'negative_color': '#C0392B',
            'neutral': DTCC_COLORS['eden'],
            'neutral_color': DTCC_COLORS['jaffa'],
            'hover_bg': 'rgba(255, 255, 255, 0.95)',
            'legend_bg': 'rgba(255, 255, 255, 0.9)',
            'legend_border': f"rgba(237, 109, 60, 0.2)",
            'grid': 'rgba(0, 0, 0, 0.1)',
            'heatmap': {
                'zmid': 0,
                'text_color': DTCC_COLORS['dark_grey']
            },
            'palette': get_dtcc_palette()
        }


def base_layout(x_title=None, y_title=None, theme='dark', margin=None, height=None, show_title=False):
    """Create base layout configuration for DTCC branded charts."""
    colors = get_theme_colors(theme)
    
    # Optimized margins for dashboard widgets (no title space needed)
    default_margin = {'l': 50, 'r': 50, 't': 20, 'b': 50, 'pad': 0}
    if margin:
        default_margin.update(margin)
    
    layout = {
        'plot_bgcolor': colors['bg_color'],
        'paper_bgcolor': colors['paper_bg'],
        'font': {
            'color': colors['text'], 
            'family': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            'size': 12
        },
        'showlegend': True,
        'hovermode': 'closest',
        'margin': default_margin,
        'colorway': colors['palette'],  # Use DTCC color palette
        'xaxis': {
            'title': {'text': x_title, 'font': {'color': colors['text'], 'size': 11}} if x_title else None,
            'gridcolor': colors['grid_color'],
            'zeroline': True,
            'zerolinecolor': colors['zeroline_color'],
            'tickfont': {'color': colors['text'], 'size': 10},
            'linecolor': colors['grid_color'],
            'linewidth': 1
        },
        'yaxis': {
            'title': {'text': y_title, 'font': {'color': colors['text'], 'size': 11}} if y_title else None,
            'gridcolor': colors['grid_color'],
            'tickfont': {'color': colors['text'], 'size': 10},
            'linecolor': colors['grid_color'],
            'linewidth': 1
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
            'font': {'color': colors['text'], 'size': 10}
        }
    }
    
    # Never show main title on charts (handled by OpenBB widget system)
    layout['title'] = None
    
    if height:
        layout['height'] = height
        
    return layout


def create_line_trace(x_data, y_data, name, theme='dark', color=None, dash=None, width=2):
    """Create a line trace with DTCC branded styling."""
    colors = get_theme_colors(theme)
    
    if not color:
        color = colors['line_color']  # Uses DTCC Jaffa by default
    
    line_config = {'color': color, 'width': width}
    if dash:
        line_config['dash'] = dash
    
    return go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines',
        name=name,
        line=line_config,
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'X: %{x}<br>' +
                     'Y: %{y}<br>' +
                     '<extra></extra>'
    )


def create_vertical_line_trace(x_value, y_range, name, theme='dark', color=None):
    """Create a vertical line trace with DTCC branded markers."""
    colors = get_theme_colors(theme)
    
    if not color:
        if 'current' in name.lower() or 'actual' in name.lower():
            color = DTCC_COLORS['jaffa']  # Primary color for current/actual
        elif 'target' in name.lower() or 'consensus' in name.lower():
            color = DTCC_COLORS['eden']   # Secondary color for targets
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


def create_dtcc_heatmap(z_data, x_labels, y_labels, theme='dark', colorscale=None):
    """Create a heatmap with DTCC branded colors."""
    if not colorscale:
        # DTCC branded colorscale from cream to jaffa to eden
        colorscale = [
            [0.0, DTCC_COLORS['cream']],
            [0.3, DTCC_COLORS['gallery']],
            [0.6, DTCC_COLORS['jaffa']],
            [1.0, DTCC_COLORS['eden']]
        ]
    
    colors = get_theme_colors(theme)
    
    return go.Heatmap(
        z=z_data,
        x=x_labels,
        y=y_labels,
        colorscale=colorscale,
        showscale=True,
        hovertemplate='<b>%{y}</b><br>' +
                     '%{x}<br>' +
                     'Value: %{z}<br>' +
                     '<extra></extra>',
        colorbar={
            'title': {'side': 'right', 'font': {'color': colors['text'], 'size': 10}},
            'tickfont': {'color': colors['text'], 'size': 9}
        }
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