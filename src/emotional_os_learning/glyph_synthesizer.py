"""Glyph Synthesizer - OpenAI Integration for Glyph Synthesis.

Used ONLY by dominant bot to synthesize complex emotional patterns
into new glyphs when local tools can't resolve them.

NOT conversational. NOT used per-message.
Only for structural synthesis of new emotional categories.

Budget: ~1-2 calls per day, ~500 tokens each = ~$5-10/month
"""

from typing import Dict, Optional, List
import json
import os
from datetime import datetime


class GlyphSynthesizer:
    """Uses OpenAI to synthesize new glyphs from proto-glyph clusters."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        """Initialize synthesizer.
        
        Args:
            api_key: OpenAI API key (default: OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.call_count = 0
        self.call_history = []
        self.cost_estimate = 0.0

    def synthesize_from_cluster(
        self,
        cluster_centroid: List[float],
        example_texts: List[str],
        existing_glyphs: Dict,
        glyph_schema: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """Synthesize a new glyph from a proto-glyph cluster.
        
        Args:
            cluster_centroid: Average emotional vector of cluster
            example_texts: Sample texts that triggered this pattern
            existing_glyphs: Reference to existing glyph catalog
            glyph_schema: Template for glyph structure (optional)
            
        Returns:
            Dictionary representing new glyph, or None if synthesis failed
        """
        # Build structured prompt
        prompt = self._build_synthesis_prompt(
            cluster_centroid=cluster_centroid,
            example_texts=example_texts,
            existing_glyphs=existing_glyphs,
            glyph_schema=glyph_schema,
        )
        
        # Call OpenAI
        try:
            response_text = self._call_openai(prompt)
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return None
        
        # Parse response
        try:
            glyph_data = json.loads(response_text)
        except json.JSONDecodeError:
            print(f"Could not parse OpenAI response as JSON: {response_text}")
            return None
        
        # Validate schema
        if not self._validate_glyph_schema(glyph_data, glyph_schema):
            print("Synthesized glyph failed validation")
            return None
        
        return glyph_data

    def _build_synthesis_prompt(
        self,
        cluster_centroid: List[float],
        example_texts: List[str],
        existing_glyphs: Dict,
        glyph_schema: Optional[Dict] = None,
    ) -> str:
        """Build the prompt for OpenAI synthesis."""
        # Build compact representation of emotional vector
        emotion_labels = [
            "anger", "joy", "trust", "fear",
            "surprise", "sadness", "disgust", "anticipation",
        ]
        
        vector_description = ", ".join(
            f"{emotion_labels[i]}: {value:.2f}"
            for i, value in enumerate(cluster_centroid[:8])
            if value > 0.1
        )
        
        # Build prompt
        prompt = f"""You are a symbolic emotional category designer. Analyze this emotional pattern and create a new glyph.

EMOTIONAL SIGNATURE:
{vector_description}

EXAMPLE EXPRESSIONS:
- {example_texts[0] if example_texts else 'No examples'}
- {example_texts[1] if len(example_texts) > 1 else ''}
- {example_texts[2] if len(example_texts) > 2 else ''}

EXISTING GLYPHS (for reference):
{self._format_existing_glyphs(existing_glyphs)}

CREATE A NEW GLYPH with this JSON structure:
{{
  "name": "Evocative name (e.g., 'Echoed Breath', 'Fractured Mirror')",
  "symbol": "Single symbolic character or emoji",
  "emotional_vector": {cluster_centroid},
  "gate_logic": {{
    "trigger_threshold": 0.7,
    "primary_emotions": ["emotion1", "emotion2"],
    "context_sensitive": true
  }},
  "narrative_meaning": "Brief poetic description of what this glyph represents",
  "activation_phrase": "Example phrase that would activate this glyph"
}}

Ensure the new glyph is:
1. Distinct from existing glyphs
2. Coherent with the emotional vector
3. Grounded in the example texts
4. Poetically evocative

Respond ONLY with valid JSON, no other text."""
        
        return prompt

    def _format_existing_glyphs(self, existing_glyphs: Dict) -> str:
        """Format existing glyphs for reference."""
        if not existing_glyphs:
            return "None yet (first glyph!)"
        
        formatted = []
        for name, glyph in list(existing_glyphs.items())[:5]:  # Show first 5
            formatted.append(f'  - "{name}": {glyph.get("narrative_meaning", "(no description)")}')
        
        return "\n".join(formatted)

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with bounded prompt."""
        if not self.api_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            import openai
        except ImportError:
            raise Exception("openai package not installed. Install with: pip install openai")
        
        openai.api_key = self.api_key
        
        # Make API call
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a symbolic emotional category designer. Create new glyphs for FirstPerson based on emotional patterns. Respond with valid JSON only.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
            max_tokens=500,
            timeout=30,
        )
        
        # Extract response
        response_text = response["choices"][0]["message"]["content"].strip()
        
        # Track call
        self.call_count += 1
        self.call_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "prompt_length": len(prompt),
                "response_length": len(response_text),
            }
        )
        
        # Estimate cost (gpt-4-turbo: $0.01/1K input tokens, $0.03/1K output tokens)
        # Rough estimate: 4 chars per token
        input_tokens = len(prompt) / 4
        output_tokens = len(response_text) / 4
        cost = (input_tokens * 0.01 + output_tokens * 0.03) / 1000
        self.cost_estimate += cost
        
        return response_text

    def _validate_glyph_schema(
        self,
        glyph_data: Dict,
        expected_schema: Optional[Dict] = None,
    ) -> bool:
        """Validate that synthesized glyph matches schema."""
        # Minimum required fields
        required = ["name", "symbol", "emotional_vector", "gate_logic"]
        
        for field in required:
            if field not in glyph_data:
                print(f"Missing required field: {field}")
                return False
        
        # Validate emotional_vector is a list of numbers
        if not isinstance(glyph_data["emotional_vector"], (list, tuple)):
            print("emotional_vector must be a list")
            return False
        
        if not all(isinstance(x, (int, float)) for x in glyph_data["emotional_vector"]):
            print("emotional_vector must contain numbers")
            return False
        
        # Validate gate_logic is a dict
        if not isinstance(glyph_data["gate_logic"], dict):
            print("gate_logic must be a dictionary")
            return False
        
        # Validate name and symbol are strings
        if not isinstance(glyph_data["name"], str):
            print("name must be a string")
            return False
        
        if not isinstance(glyph_data["symbol"], str):
            print("symbol must be a string")
            return False
        
        return True

    def get_cost_estimate(self) -> Dict:
        """Get cost estimation."""
        return {
            "total_calls": self.call_count,
            "estimated_cost": f"${self.cost_estimate:.2f}",
            "call_history": self.call_history,
        }