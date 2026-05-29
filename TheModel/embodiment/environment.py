"""Simple environment loop for grounding internal state in consequences."""

from __future__ import annotations

from TheModel.core.models import EnvironmentState, clamp_01


class SimpleWorldEnvironment:
    def apply_action(self, environment: EnvironmentState, action: str, text: str) -> dict:
        normalized = (action or text or "observe").strip().lower()
        reward_delta = 0.0
        if any(token in normalized for token in ("observe", "look", "notice")):
            environment.novelty = clamp_01(environment.novelty + 0.08)
            environment.coherence = clamp_01(environment.coherence + 0.06)
            environment.last_event = "The environment revealed more detail after observation."
            reward_delta = 0.06
        elif any(token in normalized for token in ("ask", "question", "clarify", "define")):
            environment.coherence = clamp_01(environment.coherence + 0.1)
            environment.last_event = "A clarification channel opened and the environment returned more structure."
            reward_delta = 0.08
        elif any(token in normalized for token in ("approach", "engage", "move", "enter")):
            environment.novelty = clamp_01(environment.novelty + 0.12)
            environment.safety = clamp_01(environment.safety - 0.04)
            environment.scene = "contact"
            environment.last_event = "The system moved closer to uncertainty and gained new input."
            reward_delta = 0.03
        elif any(token in normalized for token in ("rest", "pause", "wait", "breathe")):
            environment.safety = clamp_01(environment.safety + 0.09)
            environment.coherence = clamp_01(environment.coherence + 0.04)
            environment.last_event = "The system paused and recovered stability."
            reward_delta = 0.05
        else:
            environment.last_event = "The environment registered an ambiguous action and produced a weak signal."
            reward_delta = -0.01

        environment.affordances = ["observe", "ask", "rest", "approach", "define"]
        return {
            "scene": environment.scene,
            "last_event": environment.last_event,
            "reward_delta": round(reward_delta, 3),
            "affordances": list(environment.affordances),
            "safety": round(environment.safety, 3),
            "coherence": round(environment.coherence, 3),
            "novelty": round(environment.novelty, 3),
        }