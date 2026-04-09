"""
Flask web application for LimbicAI interactive system.

Provides web interface for emotion analysis and guidance.
"""

from flask import Flask, render_template_string, request, jsonify
from limbic_ai.analyzer import LimbicAnalyzer
import os

app = Flask(__name__)

# Initialize analyzer
analyzer = LimbicAnalyzer()


# HTML Template for main page
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LimbicAI - Emotional Analysis & Guidance</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .input-section h2,
        .results-section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        textarea {
            width: 100%;
            min-height: 250px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 1em;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results-content {
            display: none;
        }
        
        .limbic-map {
            margin: 20px 0;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px;
            background: #f9f9f9;
        }
        
        .limbic-map svg {
            max-width: 100%;
            height: auto;
        }
        
        .explanation {
            background: #f5f5f5;
            padding: 15px;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            margin: 15px 0;
        }
        
        .explanation h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .explanation p {
            color: #666;
            line-height: 1.6;
        }
        
        .feature-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 3px;
        }
        
        .summary-box {
            background: #f0f4ff;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .error-message {
            background: #ff6b6b;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            display: none;
        }
        
        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 LimbicAI</h1>
            <p class="subtitle">Understanding your emotional responses through neuroscience</p>
        </header>
        
        <div class="main-content">
            <div class="card input-section">
                <h2>Your Scenario</h2>
                <p style="color: #666; margin-bottom: 15px;">
                    Describe a scenario that triggers an emotional response. The more detail, the better we can understand what's happening emotionally.
                </p>
                <textarea id="scenarioInput" placeholder="Share what happened..."></textarea>
                <button onclick="analyzeScenario()">Analyze</button>
                <div class="error-message" id="errorMessage"></div>
            </div>
            
            <div class="card results-section">
                <h2>📊 Analysis Results</h2>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p style="margin-top: 10px; color: #666;">Analyzing your scenario...</p>
                </div>
                <div class="results-content" id="resultsContent">
                    <!-- Results will be inserted here -->
                </div>
            </div>
        </div>
        
        <div class="card" id="detailedSection" style="display: none;">
            <h2>🔬 Detailed Insights</h2>
            <div id="detailedContent"></div>
        </div>
    </div>
    
    <script>
        async function analyzeScenario() {
            const scenario = document.getElementById('scenarioInput').value.trim();
            const errorMsg = document.getElementById('errorMessage');
            
            // Clear previous error
            errorMsg.style.display = 'none';
            errorMsg.textContent = '';
            
            if (!scenario) {
                errorMsg.textContent = 'Please enter a scenario to analyze.';
                errorMsg.style.display = 'block';
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultsContent').style.display = 'none';
            document.getElementById('detailedSection').style.display = 'none';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ scenario: scenario })
                });
                
                if (!response.ok) {
                    throw new Error(`Error: ${response.statusText}`);
                }
                
                const data = await response.json();
                displayResults(data);
                
            } catch (error) {
                errorMsg.textContent = 'Error analyzing scenario: ' + error.message;
                errorMsg.style.display = 'block';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('resultsContent');
            const detailedDiv = document.getElementById('detailedContent');
            
            // Build main results
            let html = `
                <div class="summary-box">
                    <strong>Quick Summary:</strong> ${data.summary}
                </div>
                <div class="limbic-map">${data.visualization}</div>
                <h3 style="margin-top: 20px; color: #333;">Key Emotional Features:</h3>
                <div>
            `;
            
            // Add feature badges
            for (const [feature, value] of Object.entries(data.features)) {
                if (value > 0.1) {
                    html += `<span class="feature-badge">${feature.replace(/_/g, ' ')}: ${(value * 100).toFixed(0)}%</span>`;
                }
            }
            html += '</div>';
            
            resultsDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
            
            // Build detailed explanations
            let detailedHtml = '';
            for (const [region, explanation] of Object.entries(data.explanations)) {
                const activation = (data.limbic_state[region] * 100).toFixed(0);
                detailedHtml += `
                    <div class="explanation">
                        <h3>${region} (Activation: ${activation}%)</h3>
                        <p>${explanation}</p>
                    </div>
                `;
            }
            
            detailedDiv.innerHTML = detailedHtml;
            document.getElementById('detailedSection').style.display = 'block';
            
            // Scroll to results
            document.getElementById('detailedSection').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main page."""
    return render_template_string(MAIN_TEMPLATE)


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze a scenario and return results."""
    try:
        data = request.json
        scenario = data.get('scenario', '').strip()
        
        if not scenario:
            return jsonify({'error': 'Scenario is required'}), 400
        
        # Analyze
        analysis = analyzer.analyze(scenario)
        
        # Generate visualization
        from limbic_ai.visualization import generate_svg_limbic_map
        svg = generate_svg_limbic_map(analysis.limbic_state)
        
        # Generate summary
        summary = analyzer.get_summary(analysis)
        
        return jsonify({
            'scenario': scenario,
            'features': {
                'social_rejection': analysis.emotional_features.social_rejection,
                'self_blame': analysis.emotional_features.self_blame,
                'other_blame': analysis.emotional_features.other_blame,
                'empathy_for_other': analysis.emotional_features.empathy_for_other,
                'rationalization': analysis.emotional_features.rationalization,
                'threat_to_identity': analysis.emotional_features.threat_to_identity,
                'loss_of_reward': analysis.emotional_features.loss_of_reward,
            },
            'limbic_state': analysis.limbic_state.as_dict(),
            'visualization': svg,
            'summary': summary,
            'explanations': analysis.explanations,
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'version': '0.1.0'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
