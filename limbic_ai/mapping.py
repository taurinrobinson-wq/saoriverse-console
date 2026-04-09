"""
Mapping functions to convert emotional features to limbic activations.

This module implements the neuroscience-based mapping from high-level emotional
features to specific brain region activations.
"""

from limbic_ai.models import EmotionalFeatures, LimbicState, clamp_01


def map_features_to_limbic(features: EmotionalFeatures) -> LimbicState:
    """Map emotional features to limbic brain region activations.
    
    This implements a simplified but neuroscientifically grounded mapping:
    - Amygdala activates on threat, social rejection, and identity threat
    - Hippocampus on contextual/memory factors 
    - ACC on emotional conflict and self-blame
    - Insula on empathy deficits and interoception gaps
    - vmPFC on valuation and emotional significance
    - dlPFC on rationalization/cognitive control
    - Nucleus accumbens on loss reactions
    
    Args:
        features: EmotionalFeatures instance
        
    Returns:
        LimbicState with activation levels (0-1)
    """
    return LimbicState(
        # Amygdala: threat and rejection detection
        amygdala=clamp_01(
            features.social_rejection * 0.7 + features.threat_to_identity * 0.5
        ),
        
        # Hippocampus: context and memory
        hippocampus=clamp_01(
            features.threat_to_identity * 0.3
        ),
        
        # ACC: emotional conflict and pain
        acc=clamp_01(
            features.social_rejection * 0.5 + features.self_blame * 0.4
        ),
        
        # Insula: empathy and bodily awareness
        insula=clamp_01(
            features.empathy_for_other * 0.8
        ),
        
        # vmPFC: value and emotional significance assessment
        vmPFC=clamp_01(
            features.loss_of_reward * 0.5 + features.self_blame * 0.3
        ),
        
        # dlPFC: cognitive control and rationalization (downregulation)
        dlPFC=clamp_01(
            features.rationalization
        ),
        
        # Nucleus accumbens: reward loss and motivation
        nucleus_accumbens=clamp_01(
            features.loss_of_reward * 0.7
        ),
    )


# Descriptions for each brain region to explain activations
LIMBIC_DESCRIPTIONS = {
    "amygdala": """
**Amygdala** | Threat & Danger Detection
The amygdala detects social threats and triggers defensive responses. It's responsible for 
the immediate "social alarm" system. High activation suggests the situation is being 
experienced as a threat to belonging or status.
""",
    
    "hippocampus": """
**Hippocampus** | Memory & Context
The hippocampus binds emotional experiences to context and memory. It helps you remember 
where you were and what happened. Activation here suggests the situation is being encoded 
as a significant memory with emotional weight.
""",
    
    "acc": """
**Anterior Cingulate Cortex (ACC)** | Emotional Pain & Conflict
The ACC monitors emotional distress and detects conflict between what you think/feel and 
reality. High activation indicates emotional suffering or awareness of contradictions 
in the situation.
""",
    
    "insula": """
**Insula** | Empathy & Body Awareness (Interoception)
The insula creates awareness of your own and others' emotional/physical states. High 
activation means strong felt resonance with someone's distress. Low activation suggests 
reduced empathic connection or dismissal of emotional significance.
""",
    
    "vmPFC": """
**Ventromedial PFC** | Valuation & Significance
The vmPFC assigns emotional value and significance to events. It's the "how big a deal is 
this?" brain region. High activation means the situation carries substantial emotional weight.
""",
    
    "dlPFC": """
**Dorsolateral PFC** | Cognitive Control & Rationalization
The dlPFC is your rational "lawyer" that can talk you down from strong emotions. High 
activation suggests active cognitive strategies to minimize or reframe emotional impact—
sometimes adaptive, sometimes defensive.
""",
    
    "nucleus_accumbens": """
**Nucleus Accumbens** | Reward Loss & Motivation
This region tracks reward and loss. Activation here is about the gap between what you 
expected or wanted and what actually happened. High levels suggest significant loss aversion.
""",
}


def get_region_explanation(region_name: str, activation: float) -> str:
    """Generate explanation for a brain region's activation level.
    
    Args:
        region_name: Name of limbic region (e.g., "amygdala")
        activation: Current activation level (0-1)
        
    Returns:
        Explanation string tailored to activation level
    """
    base = LIMBIC_DESCRIPTIONS.get(region_name, "Unknown region")
    
    if activation < 0.3:
        intensity = "**Low activation**: This mechanism is not strongly engaged."
    elif activation < 0.6:
        intensity = "**Moderate activation**: This mechanism is moderately engaged."
    else:
        intensity = "**High activation**: This mechanism is strongly engaged."
    
    return f"{base}\n\n{intensity}"
