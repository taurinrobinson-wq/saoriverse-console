"""Integration Orchestrator for FirstPerson Phase 1.

Coordinates all Phase 1 modules (story-start detection, frequency reflection,
memory rehydration, template selection, Supabase persistence) into a cohesive
end-to-end pipeline for realistic conversation flows.

Architecture:
1. Input enters via handle_conversation_turn()
2. StoryStartDetector checks for ambiguity
3. FrequencyReflector tracks emotional themes
4. MemoryManager provides context
5. ResponseTemplates generate non-repetitive output
6. SupabaseManager persists everything
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass

from .story_start_detector import StoryStartDetector
from .frequency_reflector import FrequencyReflector
from .memory_manager import MemoryManager
from .response_templates import ResponseTemplates
from .supabase_manager import SupabaseManager
from .agent_state_manager import AgentStateManager
from .affect_parser import AffectParser


@dataclass
class ConversationTurn:
    """Single turn in a conversation."""

    user_id: str
    conversation_id: str
    user_input: str
    turn_number: int
    timestamp: str = None

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class IntegrationResponse:
    """Response from integration orchestrator."""

    response_text: str
    detected_pronoun_ambiguity: bool
    clarifying_prompt: Optional[str] = None
    detected_theme: Optional[str] = None
    theme_frequency: Optional[int] = None
    memory_context_injected: bool = False
    template_used: str = "default"
    supabase_recorded: bool = False
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


class FirstPersonOrchestrator:
    """Orchestrates all FirstPerson Phase 1 modules."""

    def __init__(self, user_id: str, conversation_id: str = None):
        """Initialize orchestrator with user context.

        Args:
            user_id: User identifier for data isolation
            conversation_id: Current conversation ID (generated if not provided)
        """
        self.user_id = user_id
        self.conversation_id = conversation_id or f"conv_{datetime.now(timezone.utc).timestamp()}"

        # Initialize all Phase 1 modules
        self.story_start_detector = StoryStartDetector()
        self.frequency_reflector = FrequencyReflector()
        self.memory_manager = MemoryManager(user_id=user_id)
        self.response_templates = ResponseTemplates()
        self.supabase_manager = SupabaseManager(user_id=user_id)
        self.affect_parser = AffectParser()
        
        # Initialize agent state manager (NEW: Phase 1 of emotional continuity)
        self.agent_state_manager = AgentStateManager(
            user_id=user_id,
            conversation_id=self.conversation_id
        )

        # Track conversation state
        self.turn_count = 0
        self.turn_history: List[ConversationTurn] = []
        self.response_history: List[IntegrationResponse] = []
        self.memory_rehydrated = False

    def initialize_session(self) -> Dict[str, Any]:
        """Initialize a new session with memory rehydration.

        Returns:
            Dictionary with session initialization data
        """
        # Rehydrate memory from Supabase
        memory_context = self.memory_manager.rehydrate_memory(limit=20)
        self.memory_rehydrated = memory_context.get("anchor_count", 0) > 0

        return {
            "session_id": self.conversation_id,
            "user_id": self.user_id,
            "memory_rehydrated": self.memory_rehydrated,
            "anchors_loaded": memory_context.get("anchor_count", 0),
            "top_themes": self.memory_manager.get_top_themes(limit=5),
            "memory_salience": memory_context.get("memory_salience", 0.0),
        }

    def handle_conversation_turn(self, user_input: str) -> IntegrationResponse:
        """Process a single conversation turn through all Phase 1 modules.

        Args:
            user_input: User's input message

        Returns:
            IntegrationResponse with orchestrated output
        """
        self.turn_count += 1

        # Create turn record
        turn = ConversationTurn(
            user_id=self.user_id,
            conversation_id=self.conversation_id,
            user_input=user_input,
            turn_number=self.turn_count,
        )
        self.turn_history.append(turn)

        # Step 0: Emotional Analysis (NEW: Agent State Update)
        # Parse user's affect and update agent's emotional response
        user_affect = self.affect_parser.analyze_affect(user_input)
        self.agent_state_manager.on_input(user_input, user_affect)

        # Step 1: Story-Start Detection
        story_analysis = self.story_start_detector.analyze_story_start(
            user_input)
        has_ambiguity = (
            story_analysis.get("detected_pronouns", []) != []
            or story_analysis.get("detected_temporal_markers", []) != []
        )

        clarifying_prompt = None
        if has_ambiguity:
            clarifying_prompt = story_analysis.get("clarifying_prompt")

        # Step 2: Frequency Reflection
        freq_analysis = self.frequency_reflector.analyze_frequency(user_input)
        detected_theme = freq_analysis.get("detected_theme")
        theme_frequency = freq_analysis.get("frequency", 0)
        should_reflect = freq_analysis.get("should_reflect", False)

        # Step 3: Generate Response
        response_text = self._compose_response(
            user_input=user_input,
            has_ambiguity=has_ambiguity,
            clarifying_prompt=clarifying_prompt,
            detected_theme=detected_theme,
            should_reflect=should_reflect,
            freq_analysis=freq_analysis,
            agent_state=self.agent_state_manager,  # NEW: Pass agent state
            user_affect=user_affect,  # NEW: Pass affect analysis
        )

        # Step 4: Persist to Supabase
        supabase_recorded = self._persist_turn(
            user_input=user_input,
            response_text=response_text,
            theme=detected_theme,
            turn=turn,
            agent_state=self.agent_state_manager,  # NEW: Include agent state in persistence
        )

        # Step 5: Integrate response back into agent state (NEW)
        self.agent_state_manager.integrate_after_response(response_text)

        # Step 6: Create response object
        integration_response = IntegrationResponse(
            response_text=response_text,
            detected_pronoun_ambiguity=has_ambiguity,
            clarifying_prompt=clarifying_prompt,
            detected_theme=detected_theme,
            theme_frequency=theme_frequency,
            memory_context_injected=self.memory_rehydrated,
            supabase_recorded=supabase_recorded,
            metadata={
                "turn_number": self.turn_count,
                "story_analysis": story_analysis,
                "frequency_analysis": freq_analysis,
                "memory_anchors": self.memory_manager.get_top_themes(),
                "agent_mood": self.agent_state_manager.get_mood_string(),  # NEW
                "agent_state": self.agent_state_manager.get_state_summary(),  # NEW
            },
        )

        self.response_history.append(integration_response)
        return integration_response

    def _compose_response(
        self,
        user_input: str,
        has_ambiguity: bool,
        clarifying_prompt: Optional[str],
        detected_theme: Optional[str],
        should_reflect: bool,
        freq_analysis: Dict[str, Any],
        agent_state: AgentStateManager,  # NEW
        user_affect: Any,  # NEW
    ) -> str:
        """Compose response by orchestrating templates and context.

        Args:
            user_input: User's input
            has_ambiguity: Whether pronoun/temporal ambiguity detected
            clarifying_prompt: Recommended clarifying prompt if needed
            detected_theme: Detected emotional theme
            should_reflect: Whether frequency threshold met for reflection
            freq_analysis: Full frequency analysis result
            agent_state: Current agent emotional state (NEW)
            user_affect: User's affect analysis (NEW)

        Returns:
            Composed response text
        """
        response_parts = []

        # Part 1: Clarifying prompt if ambiguity detected
        if has_ambiguity and clarifying_prompt:
            response_parts.append(clarifying_prompt)

        # Part 2: Frequency reflection if threshold met
        if should_reflect and detected_theme:
            reflection = freq_analysis.get("reflection")
            if reflection:
                response_parts.append(reflection)
            else:
                frequency = freq_analysis.get("frequency", 2)
                reflection = self.response_templates.get_frequency_reflection(
                    frequency, detected_theme, use_rotation=True
                )
                response_parts.append(reflection)

        # Part 3: Empathetic acknowledgment if no ambiguity/reflection
        if not response_parts:
            if detected_theme:
                acknowledgment = f"I'm hearing that {detected_theme} is affecting you."
                response_parts.append(acknowledgment)
            else:
                acknowledgment = (
                    self.response_templates.get_clarifying_prompt(
                        "combined", use_rotation=True
                    )
                )
                response_parts.append(acknowledgment)

        response_text = " ".join(response_parts)
        
        # NEW: Validate response against agent state
        is_valid, error_msg = agent_state.validate_response(response_text)
        if not is_valid:
            # If response violates commitments, regenerate with disclaimer
            response_text = f"I need to be honest with you: {response_text}"
        
        return response_text

    def _persist_turn(
        self,
        user_input: str,
        response_text: str,
        theme: Optional[str],
        turn: ConversationTurn,
        agent_state: AgentStateManager = None,  # NEW
    ) -> bool:
        """Persist conversation turn to Supabase.

        Args:
            user_input: User's input
            response_text: System response
            theme: Detected theme
            turn: Turn record
            agent_state: Agent state for persistence (NEW)

        Returns:
            True if successful
        """
        if not self.supabase_manager.is_available():
            return False

        try:
            # Record theme history
            if theme:
                self.supabase_manager.record_theme_history(
                    theme=theme,
                    conversation_id=self.conversation_id,
                    frequency_at_time=1,
                    context={
                        "user_input": user_input[:100], "turn": turn.turn_number},
                )

                # Record anchor if significant
                anchor = self._extract_anchor(user_input, theme)
                if anchor:
                    self.supabase_manager.record_theme_anchor(
                        theme=theme,
                        anchor=anchor,
                        confidence=0.7,
                        context={
                            "turn": turn.turn_number,
                            "response": response_text[:100],
                        },
                    )
            
            # NEW: Store agent state snapshot if provided
            if agent_state:
                try:
                    # Save emotional pivot if mood changed
                    if agent_state.state.recent_mood_shifts:
                        # Store last mood shift as an emotional pivot
                        # This could be persisted to a separate table
                        pass
                except Exception as e:
                    print(f"Error storing agent state: {e}")

            return True
        except Exception as e:
            print(f"Error persisting to Supabase: {e}")
            return False

    def _extract_anchor(self, user_input: str, theme: str) -> Optional[str]:
        """Extract memorable anchor phrase from user input.

        Args:
            user_input: User's input
            theme: Detected theme

        Returns:
            Anchor phrase or None
        """
        # Simple heuristic: first 10-20 words as anchor
        words = user_input.split()
        if len(words) > 5:
            anchor = " ".join(words[:min(10, len(words))])
            return anchor if len(anchor) > 10 else None

        return None

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation state.

        Returns:
            Summary statistics and context
        """
        themes_detected = [
            r.detected_theme for r in self.response_history if r.detected_theme
        ]
        unique_themes = list(set(themes_detected))

        ambiguities_detected = sum(
            1
            for r in self.response_history
            if r.detected_pronoun_ambiguity
        )

        reflections_triggered = sum(
            1
            for r in self.response_history
            if r.metadata and "frequency_analysis" in r.metadata
            and r.metadata["frequency_analysis"].get("should_reflect", False)
        )

        return {
            "conversation_id": self.conversation_id,
            "turn_count": self.turn_count,
            "unique_themes": unique_themes,
            "themes_detected": themes_detected,
            "ambiguities_detected": ambiguities_detected,
            "reflections_triggered": reflections_triggered,
            "memory_rehydrated": self.memory_rehydrated,
            "supabase_integrated": self.supabase_manager.is_available(),
        }

    def get_response_variety_metrics(self) -> Dict[str, Any]:
        """Check response template variety across conversation.

        Returns:
            Metrics about template variation
        """
        responses = [r.response_text for r in self.response_history]
        unique_responses = len(set(responses))

        # Check for repeated consecutive responses
        repeated_consecutive = 0
        for i in range(len(responses) - 1):
            if responses[i] == responses[i + 1]:
                repeated_consecutive += 1

        return {
            "total_responses": len(responses),
            "unique_responses": unique_responses,
            "variety_ratio": unique_responses / max(1, len(responses)),
            "repeated_consecutive": repeated_consecutive,
            "variation_healthy": repeated_consecutive == 0,
        }


    def generate_response_with_glyph(self, user_input: str, best_glyph: dict) -> str:
        """Generate response using glyph as emotional constraint.

        This method integrates with the StructuralGlyphComposer to ensure
        the glyph drives the response structure.

        Args:
            user_input: User's input message
            best_glyph: Selected glyph dict with glyph_name, description, etc.

        Returns:
            Response text using glyph as meaning anchor
        """
        try:
            from .structural_glyph_composer import StructuralGlyphComposer
            
            composer = StructuralGlyphComposer()
            glyph_name = best_glyph.get("glyph_name", "unknown")
            
            # Parse affect first
            user_affect = self.affect_parser.analyze_affect(user_input)
            
            # Update agent state
            self.agent_state_manager.on_input(user_input, user_affect)
            
            # Compose response with structural glyph
            response = composer.compose_with_structural_glyph(
                user_input=user_input,
                user_affect=user_affect,
                agent_state=self.agent_state_manager,
                glyph=best_glyph,
                hypothesis=self.agent_state_manager.state.emotional_hypothesis
            )
            
            # Integrate after response
            self.agent_state_manager.integrate_after_response(response)
            
            return response
        except Exception as e:
            import logging
            logging.debug(f"generate_response_with_glyph failed: {e}")
            # Fallback to simple response
            glyph_name = best_glyph.get("glyph_name", "something") if isinstance(best_glyph, dict) else "something"
            return f"I'm sensing {glyph_name.lower()} in what you're saying. Tell me more."


def create_orchestrator(
    user_id: str, conversation_id: str = None
) -> FirstPersonOrchestrator:
    """Factory function to create orchestrator instance.

    Args:
        user_id: User identifier
        conversation_id: Optional conversation ID

    Returns:
        FirstPersonOrchestrator instance
    """
    return FirstPersonOrchestrator(user_id=user_id, conversation_id=conversation_id)


def create_affect_parser() -> AffectParser:
    """Factory function to create affect parser instance.

    Returns:
        AffectParser instance
    """
    return AffectParser()
