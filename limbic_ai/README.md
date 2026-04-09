# LimbicAI - Interactive Emotional Analysis System

An interactive web application for analyzing emotional responses through the lens of affective neuroscience. Users enter scenarios that trigger emotions, and the system maps the likely limbic system activation patterns, providing science-grounded guidance.

## What is LimbicAI?

LimbicAI is a teaching/translation tool that:

1. **Parses** your emotional scenario using NLP
2. **Maps** extracted emotional features to limbic brain region activations
3. **Visualizes** the limbic system state with activation levels
4. **Explains** what's happening neurobiologically and psychologically

## Core Concept

### Brain Model

LimbicAI models seven key limbic/emotion-related brain regions:

- **Amygdala**: Threat & fear detection, social rejection response
- **Hippocampus**: Memory formation, contextual binding  
- **Anterior Cingulate Cortex (ACC)**: Emotional pain, conflict monitoring
- **Insula**: Interoception, empathy, bodily awareness
- **Ventromedial PFC**: Valuation ("how big a deal is this?"), moral weighing
- **Dorsolateral PFC**: Cognitive control, rationalization
- **Nucleus Accumbens**: Reward/loss tracking, motivation

### Emotional Feature Space

Input scenarios are parsed to extract emotional features:

- **Social Rejection**: Feeling excluded or not belonging
- **Self Blame**: Attribution of responsibility to oneself
- **Other Blame**: Attribution of responsibility to others
- **Empathy for Other**: Perspective-taking and understanding
- **Rationalization**: Cognitive downregulation strategies
- **Threat to Identity**: Challenge to sense of self
- **Loss of Reward**: Gap between expected and actual outcomes

These features are then mathematically mapped to limbic activations.

## Installation

### Requirements

- Python 3.8+
- pip

### Setup

1. **Clone/navigate to the project**:
```bash
cd limbic_ai
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python app.py
```

4. **Access the web interface**:
Open browser to `http://localhost:5000`

## Usage

### Web Interface

1. Navigate to the main page
2. Enter your emotional scenario in the text area
3. Click "Analyze"
4. View:
   - Visual limbic map showing brain region activations
   - Summary of emotional patterns
   - Detailed explanations for each brain region
   - Feature extraction results

### Example Scenario

```
Input: "My girlfriend broke up with me. She said I couldn't hear her 
and didn't know how to support her emotionally, but I always felt like 
she was too dramatic and overblown. I mean she got fired from her job, 
it happens, I don't get why that's such a big deal."
```

### Expected Output

- **Amygdala (0.7)**: High social threat/rejection activation
- **ACC (0.6)**: Emotional conflict between perspectives  
- **Insula (0.2)**: Low empathy/emotional resonance
- **dlPFC (0.8)**: High rationalization/cognitive control
- Plus analysis and guidance based on activation patterns

## Project Structure

```
limbic_ai/
├── __init__.py              # Package initialization
├── models.py                # Data models (EmotionalFeatures, LimbicState)
├── mapping.py               # Feature → limbic activation mapping
├── nlp_parser.py            # NLP for feature extraction
├── analyzer.py              # Main analysis orchestration
├── visualization.py         # SVG/HTML visualization generation
├── app.py                   # Flask web application
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Reference

### Analyze Endpoint

**POST** `/api/analyze`

**Request**:
```json
{
  "scenario": "User's emotional scenario text..."
}
```

**Response**:
```json
{
  "scenario": "...",
  "features": {
    "social_rejection": 0.5,
    "self_blame": 0.3,
    ...
  },
  "limbic_state": {
    "amygdala": 0.7,
    "hippocampus": 0.4,
    ...
  },
  "visualization": "<svg>...</svg>",
  "summary": "Narrative summary...",
  "explanations": {
    "amygdala": "Explanation text...",
    ...
  }
}
```

### Health Check

**GET** `/api/health`

Returns system status.

## Core Algorithm

### Feature Extraction

Keywords and patterns are identified in the scenario text, normalized by text length, and converted to 0-1 activation scores.

Example keyword groups:
- Social rejection: "broke up", "rejected", "excluded", "abandoned"
- Self blame: "my fault", "I failed", "I should have"
- Rationalization: "not a big deal", "too dramatic", "common"

### Feature → Limbic Mapping

Linear combination function:

```
amygdala = clamp(social_rejection * 0.7 + threat_to_identity * 0.5)
insula = clamp(empathy_for_other * 0.8)
dlPFC = clamp(rationalization)
... (7 regions total)
```

Weights are based on neuroscientific literature on emotional responding.

### Visualization

- Brain regions displayed as colored circles
- Color intensity represents activation level (blue=low, red=high)
- Size represents activation magnitude
- SVG-based for compatibility

## Scientific Grounding

LimbicAI is inspired by:

- **Affective Neuroscience** (Panksepp, Solms, Damasio)
- **Emotion Theory** (Barrett, Schachter & Singer)
- **Neurobiology of Attachment** (Bowlby, Lipton)
- **Cognitive Control** (Ochsner & Gross)

**Important**: This is a *modeling* and *teaching* tool, not clinical diagnosis. It represents simplified but evidence-based mappings.

## Future Enhancements

- [ ] LLM-based feature extraction (more sophisticated NLP)
- [ ] Machine learning model trained on emotional datasets
- [ ] Three-state visualization (before/during/after emotion)
- [ ] Guidance recommendations based on activation patterns
- [ ] Session history and progress tracking
- [ ] Mobile app version
- [ ] Multimodal input (voice, images)

## Contributing

Contributions welcome! Areas for improvement:

- Better NLP models for feature extraction
- Enhanced visualizations
- Additional brain regions or emotional dimensions
- Clinical validation studies
- Performance optimization

## License

MIT License - See LICENSE file

## Citation

If using this in research or publications:

```
Robinson, T. (2026). LimbicAI: Interactive emotional response analyzer. 
Saoriverse Console Project.
```

## Support

For issues or questions:
1. Check the examples in this README
2. Review the inline code documentation
3. Open an issue with detailed problem description

---

**Note**: LimbicAI is a teaching tool designed to help people understand 
the neurobiology of emotions. It should not replace professional mental 
health support or clinical assessment.
