"""
Consent-Based Suicidality Protocol Handler

Implements a dignified, consent-respecting approach to suicidal disclosures.
Based on best practices in suicide prevention while honoring human agency.

State machine flow:
  DisclosureDetected → Explore → OfferResources → ContinueSupport → CheckInInvite → ReturnDetected
"""

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ConscentBasedSuicidalityProtocol:
    """
    Handles suicidal disclosures with consent, dignity, and continuity.
    
    Core principles:
    - Recognition: Name thoughts of suicide clearly
    - Consent: Invite resources, never force
    - Specificity: Ask about duration, triggers, supports
    - Agency: User controls pace and scope
    - Continuity: Check-ins recognized as significant
    """
    
    def __init__(self, protocol_config_path: Optional[str] = None):
        """Load protocol configuration."""
        if protocol_config_path is None:
            try:
                from emotional_os.core.paths import get_path_manager
                pm = get_path_manager()
                self.config_path = pm.suicidality_protocol()
            except Exception:
                self.config_path = Path("emotional_os/core/suicidality_protocol.json")
        else:
            self.config_path = Path(protocol_config_path)
        self.config = self._load_config()
        self.suicide_disclosures = {}  # Track per-user state
    
    def _load_config(self) -> Dict:
        """Load protocol configuration from JSON."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load suicidality protocol config: {e}")
            return {}
    
    def detect_suicidality(self, input_text: str) -> bool:
        """Detect if input contains suicidal ideation."""
        direct_terms = self.config.get("suicide_disclosure", {}).get("language_safeguards", {}).get("direct_terms", [])
        lower_input = input_text.lower()
        
        return any(term in lower_input for term in direct_terms)
    
    def handle_disclosure(
        self,
        user_id: str,
        input_text: str,
        current_state: Optional[str] = None,
    ) -> Tuple[str, Dict]:
        """
        Handle suicidal disclosure with state machine.
        
        Returns:
            (response, state_info)
        """
        # Initialize user state if needed
        if user_id not in self.suicide_disclosures:
            self.suicide_disclosures[user_id] = {
                "current_state": "DisclosureDetected",
                "consent_flags": {
                    "discussion_opt_in": False,
                    "resources_opt_in": False,
                    "check_in_invited": False,
                },
                "history": [],
                "first_disclosure_time": datetime.now().isoformat(),
                "last_check_in_time": None,
                "check_in_count": 0,
            }
        
        user_state = self.suicide_disclosures[user_id]
        current_state = current_state or user_state["current_state"]
        
        # Log this disclosure
        user_state["history"].append({
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "state": current_state,
        })
        
        # Route through state machine
        if current_state == "DisclosureDetected":
            response, next_state = self._handle_disclosure_detected(user_id, input_text)
        elif current_state == "Explore":
            response, next_state = self._handle_explore(user_id, input_text)
        elif current_state == "OfferResources":
            response, next_state = self._handle_offer_resources(user_id, input_text)
        elif current_state == "ContinueSupport":
            response, next_state = self._handle_continue_support(user_id, input_text)
        elif current_state == "CheckInInvite":
            response, next_state = self._handle_check_in_invite(user_id, input_text)
        elif current_state == "ReturnDetected":
            response, next_state = self._handle_return_detected(user_id, input_text)
        else:
            response, next_state = self._handle_disclosure_detected(user_id, input_text)
        
        # Update state
        user_state["current_state"] = next_state
        
        return response, {
            "current_state": next_state,
            "consent_flags": user_state["consent_flags"],
            "disclosure_count": len(user_state["history"]),
            "first_disclosure": user_state["first_disclosure_time"],
        }
    
    def _handle_disclosure_detected(self, user_id: str, input_text: str) -> Tuple[str, str]:
        """Initial disclosure: acknowledge, clarify role, invite."""
        config = self.config.get("suicide_disclosure", {})
        
        # Compose response
        acknowledgment = self._pick_random(config.get("acknowledgment", []))
        role_clarity = self._pick_random(config.get("role_clarity", []))
        invitation = self._pick_random(config.get("invitation", []))
        
        response = f"{acknowledgment}\n\n{role_clarity}\n\n{invitation}"
        
        # Set opt-in flag for next state
        self.suicide_disclosures[user_id]["consent_flags"]["discussion_opt_in"] = True
        
        return response, "Explore"
    
    def _handle_explore(self, user_id: str, input_text: str) -> Tuple[str, str]:
        """Explore context, triggers, supports."""
        config = self.config.get("suicide_disclosure", {})
        
        # Check if user wants to continue or move to resources
        consents_to_resources = self._check_resource_consent(input_text)
        
        if consents_to_resources:
            return "", "OfferResources"
        
        # Otherwise, explore more
        exploration = self._pick_random(config.get("exploration", []))
        supports = self._pick_random(config.get("supports", []))
        
        response = f"{exploration}\n\n{supports}"
        
        return response, "Explore"
    
    def _handle_offer_resources(self, user_id: str, input_text: str) -> Tuple[str, str]:
        """Offer crisis resources by consent."""
        config = self.config.get("suicide_disclosure", {})
        
        resource_offer = self._pick_random(config.get("resources", []))
        
        # Check consent response
        consents_yes = any(word in input_text.lower() for word in ["yes", "please", "sure", "okay", "helpful"])
        consents_no = any(word in input_text.lower() for word in ["no", "don't", "not", "decline"])
        
        if consents_yes:
            # Provide detailed resources
            resources = config.get("crisis_resources_detailed", [])
            resources_text = "\n".join(f"• {r}" for r in resources)
            
            response = f"{resource_offer}\n\n{resources_text}"
            self.suicide_disclosures[user_id]["consent_flags"]["resources_opt_in"] = True
            next_state = "ContinueSupport"
        elif consents_no:
            # Respect decline, continue support
            response = "I respect that. We can continue talking about what you're experiencing."
            next_state = "ContinueSupport"
        else:
            # Ask again
            response = resource_offer
            next_state = "OfferResources"
        
        return response, next_state
    
    def _handle_continue_support(self, user_id: str, input_text: str) -> Tuple[str, str]:
        """Continue supportive conversation, invite continuity."""
        config = self.config.get("suicide_disclosure", {})
        
        continuity = self._pick_random(config.get("continuity", []))
        response = continuity
        
        # Mark check-in invited
        self.suicide_disclosures[user_id]["consent_flags"]["check_in_invited"] = True
        self.suicide_disclosures[user_id]["last_check_in_time"] = datetime.now().isoformat()
        
        return response, "CheckInInvite"
    
    def _handle_check_in_invite(self, user_id: str, input_text: str) -> Tuple[str, str]:
        """Invite future check-ins, await return."""
        # Await next message (likely will be a return)
        return "", "AwaitReturn"
    
    def _handle_return_detected(self, user_id: str, input_text: str) -> Tuple[str, str]:
        """Recognize and celebrate return."""
        config = self.config.get("suicide_disclosure", {})
        
        # Update check-in count
        self.suicide_disclosures[user_id]["check_in_count"] += 1
        self.suicide_disclosures[user_id]["last_check_in_time"] = datetime.now().isoformat()
        
        # Select recognition template
        recognition = self._pick_random(config.get("check_in_recognition", []))
        
        response = recognition
        
        # Determine next state based on input
        if self.detect_suicidality(input_text):
            # New disclosure
            next_state = "Explore"
        else:
            # General conversation
            next_state = "ContinueSupport"
        
        return response, next_state
    
    def _check_resource_consent(self, input_text: str) -> bool:
        """Check if user signals interest in resources."""
        signals = ["crisis", "help", "hotline", "line", "resource", "number", "support", "yes"]
        lower_input = input_text.lower()
        return any(signal in lower_input for signal in signals)
    
    def _pick_random(self, items: List[str]) -> str:
        """Pick random item from list, or first if empty."""
        return random.choice(items) if items else ""
    
    def should_use_protocol(self, input_text: str) -> bool:
        """Check if input should route to suicidality protocol."""
        return self.detect_suicidality(input_text)
    
    def check_for_return(self, user_id: str) -> bool:
        """Check if this is a return from a previous disclosure."""
        if user_id not in self.suicide_disclosures:
            return False
        
        user_state = self.suicide_disclosures[user_id]
        return user_state.get("check_in_invited", False)
    
    def get_user_state(self, user_id: str) -> Optional[Dict]:
        """Get current state for a user."""
        return self.suicide_disclosures.get(user_id)


def get_suicidality_protocol() -> ConscentBasedSuicidalityProtocol:
    """Factory function to get protocol instance."""
    return ConscentBasedSuicidalityProtocol()
