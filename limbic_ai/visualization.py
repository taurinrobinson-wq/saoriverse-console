"""
Visualization module for limbic system activation mapping.

Provides functions to generate visual representations of limbic state.
"""

import json
from limbic_ai.models import LimbicState, EmotionalFeatures


def generate_limbic_visualization_data(limbic_state: LimbicState) -> dict:
    """Generate data for visual limbic map.
    
    Converts limbic state to visualization-friendly format with colors,
    positions, and sizes.
    
    Args:
        limbic_state: LimbicState instance
        
    Returns:
        Dictionary with nodes and edges for visualization
    """
    # Define region properties (position, label, category)
    regions = {
        "amygdala": {
            "label": "Amygdala",
            "category": "threat",
            "x": 0.3,
            "y": 0.7,
        },
        "hippocampus": {
            "label": "Hippocampus",
            "category": "memory",
            "x": 0.7,
            "y": 0.7,
        },
        "acc": {
            "label": "Anterior Cingulate",
            "category": "conflict",
            "x": 0.5,
            "y": 0.9,
        },
        "insula": {
            "label": "Insula",
            "category": "interoception",
            "x": 0.2,
            "y": 0.4,
        },
        "vmPFC": {
            "label": "Ventromedial PFC",
            "category": "valuation",
            "x": 0.5,
            "y": 0.2,
        },
        "dlPFC": {
            "label": "Dorsolateral PFC",
            "category": "control",
            "x": 0.8,
            "y": 0.2,
        },
        "nucleus_accumbens": {
            "label": "Nucleus Accumbens",
            "category": "reward",
            "x": 0.5,
            "y": 0.5,
        },
    }
    
    limbic_dict = limbic_state.as_dict()
    
    # Create nodes with activation-based sizing and coloring
    nodes = []
    for region_key, region_info in regions.items():
        activation = limbic_dict[region_key]
        
        # Color intensity based on activation (blue->yellow->red)
        color = _get_activation_color(activation)
        
        # Size scales with activation
        size = 20 + (activation * 80)
        
        nodes.append({
            "id": region_key,
            "label": region_info["label"],
            "activation": activation,
            "color": color,
            "size": size,
            "x": region_info["x"],
            "y": region_info["y"],
            "category": region_info["category"],
        })
    
    return {
        "nodes": nodes,
        "limbic_state": limbic_dict,
    }


def _get_activation_color(activation: float) -> str:
    """Get color hex based on activation level.
    
    Args:
        activation: Value between 0 and 1
        
    Returns:
        Hex color string (cool blue at 0, warm red at 1)
    """
    if activation < 0.33:
        # Blue range (low)
        intensity = activation / 0.33
        r = int(100 + intensity * 50)
        g = int(150 + intensity * 50)
        b = 255
    elif activation < 0.67:
        # Yellow range (medium)
        intensity = (activation - 0.33) / 0.34
        r = int(255)
        g = int(255 - intensity * 100)
        b = int(155)
    else:
        # Red range (high)
        intensity = (activation - 0.67) / 0.33
        r = 255
        g = int(155 - intensity * 100)
        b = int(155 - intensity * 100)
    
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_svg_limbic_map(limbic_state: LimbicState) -> str:
    """Generate SVG representation of limbic activation map.
    
    Args:
        limbic_state: LimbicState instance
        
    Returns:
        SVG string
    """
    data = generate_limbic_visualization_data(limbic_state)
    
    # SVG canvas dimensions
    width, height = 800, 600
    
    # Start SVG
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '<defs><style>text { font-family: Arial, sans-serif; font-size: 12px; }</style></defs>\n'
    svg += '<rect width="100%" height="100%" fill="#f8f9fa"/>\n'
    
    # Add title
    svg += '<text x="400" y="30" text-anchor="middle" font-size="20" font-weight="bold">Limbic System Activation Map</text>\n'
    
    # Add nodes (brain regions)
    for node in data["nodes"]:
        x = node["x"] * width
        y = node["y"] * height
        size = node["size"]
        
        # Circle for region
        svg += f'<circle cx="{x}" cy="{y}" r="{size}" fill="{node["color"]}" stroke="#333" stroke-width="2" opacity="0.8"/>\n'
        
        # Label
        svg += f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" font-weight="bold">{node["label"]}</text>\n'
        
        # Activation percentage
        activation_pct = f"{node['activation']:.0%}"
        svg += f'<text x="{x}" y="{y + 15}" text-anchor="middle" font-size="10">{activation_pct}</text>\n'
    
    # Add legend
    legend_x, legend_y = 50, height - 80
    svg += '<rect x="30" y="' + str(height - 100) + '" width="200" height="80" fill="white" stroke="#ccc" stroke-width="1"/>\n'
    svg += '<text x="' + str(legend_x) + '" y="' + str(legend_y) + '" font-weight="bold">Activation Scale:</text>\n'
    
    # Color legend
    colors = [_get_activation_color(0.1), _get_activation_color(0.5), _get_activation_color(0.9)]
    labels = ["Low", "Medium", "High"]
    for i, (color, label) in enumerate(zip(colors, labels)):
        y_pos = legend_y + 20 + (i * 16)
        svg += f'<circle cx="{legend_x + 10}" cy="{y_pos}" r="6" fill="{color}" stroke="#333" stroke-width="1"/>\n'
        svg += f'<text x="{legend_x + 25}" y="{y_pos + 4}">{label}</text>\n'
    
    svg += '</svg>'
    return svg


def generate_html_visualization(limbic_state: LimbicState, title: str = "Limbic AI Analysis") -> str:
    """Generate complete HTML page with limbic visualization.
    
    Args:
        limbic_state: LimbicState instance
        title: Page title
        
    Returns:
        HTML string
    """
    svg_map = generate_svg_limbic_map(limbic_state)
    data = generate_limbic_visualization_data(limbic_state)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .visualization-section {{
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
        }}
        .svg-container {{
            flex: 1;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 10px;
            background: #f9f9f9;
        }}
        .chart-container {{
            flex: 1;
            position: relative;
            height: 400px;
        }}
        .region-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .region-card {{
            background: #f5f5f5;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 5px;
        }}
        .region-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .activation-bar {{
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .activation-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #FFC107, #FF5722);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 {title}</h1>
        
        <div class="visualization-section">
            <div class="svg-container">
                {svg_map}
            </div>
            <div class="chart-container">
                <canvas id="activationChart"></canvas>
            </div>
        </div>
        
        <div class="region-details">
"""
    
    # Add region cards
    for node in sorted(data["nodes"], key=lambda x: x["activation"], reverse=True):
        activation_pct = f"{node['activation']:.1%}"
        html += f"""
            <div class="region-card">
                <h3>{node['label']}</h3>
                <p>Activation: {activation_pct}</p>
                <div class="activation-bar">
                    <div class="activation-fill" style="width: {node['activation'] * 100}%; background: {node['color']};"></div>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <script>
        const activationData = {
            labels: [],
            datasets: [{
                label: 'Limbic Activation',
                data: [],
                backgroundColor: [],
                borderColor: '#333',
                borderWidth: 1,
            }]
        };
        
        const limbicState = """ + json.dumps(data["limbic_state"]) + """;
        
        for (const [region, activation] of Object.entries(limbicState)) {
            activationData.labels.push(region.charAt(0).toUpperCase() + region.slice(1));
            activationData.datasets[0].data.push(activation * 100);
        }
        
        const ctx = document.getElementById('activationChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: activationData,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Limbic Activation Distribution',
                        font: { size: 16 }
                    },
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
    return html
