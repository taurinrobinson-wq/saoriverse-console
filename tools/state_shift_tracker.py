import random


class StateShiftTracker:
    """
    Tracks the user's internal conversational state using simple
    linguistic cues. No NLP or model calls required.
    """

    def __init__(self):
        self.state = "opening"
        self.last_state = None

    def update(self, user_text: str) -> str:
        text = (user_text or "").lower()
        self.last_state = self.state

        # Regression checks: quick panic indicators
        if any(p in text for p in [
            "i'm overwhelmed", "i feel overwhelmed", "i'm panicking",
            "i'm starting to panic", "i can't handle this",
        ]):
            # fall back to hesitation/opening depending on last state
            self.state = "hesitation" if self.last_state in ["integration", "stabilization"] else "opening"
            return self.state

        # --- HESITATION ---
        if any(p in text for p in [
            "don't know where to start", "not sure where to start",
            "not sure who to talk to", "i don't know who", "i don't know",
        ]):
            self.state = "hesitation"
            return self.state

        # --- DISCLOSURE ---
        if any(p in text for p in [
            "my company is out of money", "my family depends on me",
            "i'm struggling", "i just found out", "i thought things were",
            "i'm in debt", "i'm overwhelmed by",
        ]):
            self.state = "disclosure"
            return self.state

        # --- STABILIZATION ---
        if any(p in text for p in [
            "i just need to not", "i'm trying not to panic",
            "i'm trying to stay calm", "i'm trying to keep steady",
            "i just need to keep steady", "i'm trying to hold it together",
        ]):
            self.state = "stabilization"
            return self.state

        # --- INTEGRATION ---
        if any(p in text for p in [
            "part of the problem is", "i think more than anything",
            "i guess it's hard to", "i'm realizing that",
            "i just need to remember", "i think what's happening is",
        ]):
            self.state = "integration"
            return self.state

        return self.state


class Templates:
    def __init__(self):
        self._rng = random.Random()

    def opening(self):
        return self._rng.choice([
            "Yeah, I get that.",
            "Oof, that's rough.",
            "I hear you.",
            "I'm sorry — that's a lot.",
        ])

    def hesitation(self):
        return self._rng.choice([
            "That's okay. Take your time.",
            "No rush — start wherever feels easiest.",
            "It's alright. You don't have to have it all sorted.",
            "We can go slow. Whenever you're ready.",
            "That's fine — just start with whatever's on top.",
        ])

    def disclosure(self):
        return self._rng.choice([
            "Yeah, that's a lot to carry.",
            "Oof — that's a heavy mix.",
            "That sounds like a lot hitting at once.",
            "I hear you — that's a tough stack.",
            "Yeah, that makes sense. That's a lot on one person.",
        ])

    def stabilization(self):
        return self._rng.choice([
            "Yeah, that makes sense — you're doing what you can to stay steady.",
            "I get that. You're trying to keep your footing.",
            "That tracks — you're working to stay grounded.",
            "Makes sense. You're holding yourself together the best you can.",
        ])

    def integration(self):
        return self._rng.choice([
            "Yeah, that's a clear read on what's going on.",
            "Makes sense — you're seeing the pattern.",
            "I hear you — you're sorting through it.",
            "Yeah, that's you getting a handle on things.",
        ])

    def get(self, state: str) -> str:
        return getattr(self, state, self.opening)()
