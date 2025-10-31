"""
Test Messages for FirstPerson Emotional OS Glyph Processing
Comprehensive test suite covering various emotional states, contexts, and scenarios
"""

TEST_MESSAGES = {
    # ===== POSITIVE EMOTIONS =====
    "joy": [
        "I just got the job offer I've been dreaming about! This is incredible!",
        "The sunrise this morning was absolutely breathtaking. Pure magic.",
        "My child said their first word today. I'm crying happy tears.",
        "We won the championship! The whole team is celebrating together.",
        "Just finished a project I'm really proud of. It turned out perfect!",
    ],
    
    "love": [
        "Being with you makes everything feel right in the world.",
        "I love how you always know exactly what to say when I need it.",
        "My family means everything to me. I'm so grateful for them.",
        "This place feels like home because of the people I share it with.",
        "The way you look at me... I feel completely seen and accepted.",
    ],
    
    "gratitude": [
        "I can't thank you enough for helping me through this.",
        "Grateful for the small moments - coffee, sunshine, good conversations.",
        "Thank you for believing in me when I didn't believe in myself.",
        "I appreciate every single person who showed up for me.",
        "Life is full of blessings when you take time to notice them.",
    ],
    
    "peace": [
        "Finally took time to just breathe. Everything feels calm now.",
        "Meditation helped me find clarity in the chaos.",
        "The forest is so quiet. This is exactly what my soul needed.",
        "I've made peace with what happened. I can move forward now.",
        "There's a stillness inside me that wasn't there before.",
    ],
    
    # ===== NEGATIVE EMOTIONS =====
    "sadness": [
        "I miss them every single day. Some days it hits harder than others.",
        "Everything feels empty since they left. I don't know how to fill the void.",
        "I keep waiting for my phone to ring. It never does.",
        "The weight of everything is too much right now.",
        "I feel so alone even when I'm surrounded by people.",
    ],
    
    "anger": [
        "I can't believe they would do this to me! How could they betray me like that?",
        "This is absolutely unacceptable! I'm furious!",
        "They lied to my face and I'm done being understanding about it.",
        "The injustice of this situation makes my blood boil.",
        "I'm angry at the world right now and I don't care who knows it.",
    ],
    
    "fear": [
        "What if I mess this up? What if I'm not good enough?",
        "I keep having panic attacks about the future. Everything feels uncertain.",
        "I'm terrified of failing. What if I disappoint everyone?",
        "Something bad is going to happen, I can feel it.",
        "I'm scared to try because I'm afraid of rejection.",
    ],
    
    "anxiety": [
        "My heart won't stop racing. I can't focus on anything.",
        "I keep checking my phone. What if something's wrong?",
        "The constant worry is exhausting. I can't turn my brain off.",
        "I feel like something is about to go wrong, but I don't know what.",
        "My thoughts are spiraling and I can't stop them.",
    ],
    
    "shame": [
        "I did something I'm not proud of. I don't think I can forgive myself.",
        "Everyone knows what I did. I'm so embarrassed I can't face them.",
        "I feel so small and worthless right now.",
        "I made a huge mistake and now everything is ruined.",
        "I keep replaying it in my head. How could I be so stupid?",
    ],
    
    # ===== COMPLEX/MIXED EMOTIONS =====
    "bittersweet": [
        "I'm happy for them, but it hurts knowing I can't be there.",
        "This is a good change, but I'm sad to leave this chapter behind.",
        "I'm proud of what I've accomplished, but it cost me more than I expected.",
        "This success feels empty without the people I wanted to share it with.",
        "I'm grateful for what was, even though I'm grieving what's gone.",
    ],
    
    "overwhelmed": [
        "There's too much happening at once. I don't know where to start.",
        "Everything is falling apart and I'm trying to hold it all together.",
        "I have so many responsibilities and not enough time or energy.",
        "Everyone needs something from me and I have nothing left to give.",
        "The pressure is crushing me. I can't breathe.",
    ],
    
    "hopeful": [
        "Things are hard right now, but I believe tomorrow will be better.",
        "Despite everything, I still believe in happy endings.",
        "I can see the light at the end of the tunnel.",
        "Something inside me keeps saying things will work out.",
        "I'm not there yet, but I can see where I want to be.",
    ],
    
    "ambivalent": [
        "I don't know how I feel about this. Part of me wants to, part of me doesn't.",
        "I'm not sure if this is the right decision or the wrong one.",
        "I care about them, but I'm also frustrated with them.",
        "This opportunity excites me and terrifies me at the same time.",
        "I want to move forward, but I'm also scared of letting go.",
    ],
    
    # ===== CONTEXTUAL/SITUATIONAL =====
    "work": [
        "My boss completely dismissed my ideas in the meeting. I feel unheard.",
        "I got praised for my work and it feels amazing to be recognized.",
        "I'm drowning in deadlines and nobody seems to care that I'm struggling.",
        "My team and I just launched something incredible together.",
        "I'm worried about job security. What if there are layoffs?",
    ],
    
    "relationships": [
        "We had a huge argument and I don't know if we can fix this.",
        "They said exactly what I needed to hear when I needed it most.",
        "I feel like they don't really know me anymore.",
        "We're growing together and it's beautiful to witness.",
        "I'm lonely even in this relationship. We're not connecting.",
    ],
    
    "health": [
        "The diagnosis was worse than I expected. I'm terrified.",
        "I'm finally feeling better after weeks of being sick.",
        "My mental health is spiraling and I don't know how to stop it.",
        "The physical pain is affecting everything in my life.",
        "I made progress in therapy today. There's hope.",
    ],
    
    "identity": [
        "I finally feel like I'm being my true self. This is who I really am.",
        "I don't recognize the person I've become.",
        "People keep trying to put me in a box, but I'm so much more.",
        "I'm learning to accept all the different parts of myself.",
        "I'm lost. I don't know who I am anymore.",
    ],
    
    # ===== INTENSITY VARIATIONS =====
    "subtle": [
        "I'm a bit tired today.",
        "There's something on my mind, but I can't quite put my finger on it.",
        "I'm slightly off, not sure why.",
        "Today feels a little different, in a way I can't explain.",
        "I've been thinking about things more than usual.",
    ],
    
    "intense": [
        "I CAN'T TAKE THIS ANYMORE!!! I'M AT MY BREAKING POINT!!!",
        "THIS IS THE BEST DAY OF MY ENTIRE LIFE!!!",
        "I FEEL LIKE I'M DYING INSIDE! EVERYTHING HURTS!",
        "I NEVER WANT TO FEEL THIS WAY AGAIN! NEVER!",
        "THIS IS THE MOST BEAUTIFUL MOMENT I'VE EVER EXPERIENCED!!!",
    ],
    
    # ===== NEUTRAL/REFLECTIVE =====
    "neutral": [
        "It is what it is.",
        "I don't have strong feelings about this either way.",
        "Things are just normal right now.",
        "I'm observing everything without judgment.",
        "This is just another day.",
    ],
    
    "reflective": [
        "Looking back, I realize how much I've grown.",
        "I'm processing what just happened and what it means.",
        "This situation taught me something important about myself.",
        "I'm starting to understand why I react the way I do.",
        "The more time passes, the more I see the bigger picture.",
    ],
}

def get_test_message(emotion: str = None, index: int = 0) -> str:
    """Get a test message by emotion category and index"""
    if emotion is None:
        # Return first message from each category
        return {cat: messages[0] for cat, messages in TEST_MESSAGES.items()}
    
    if emotion in TEST_MESSAGES:
        messages = TEST_MESSAGES[emotion]
        return messages[index % len(messages)]
    else:
        raise ValueError(f"Unknown emotion category: {emotion}. Available: {list(TEST_MESSAGES.keys())}")

def get_all_messages() -> list:
    """Get all test messages as a flat list"""
    all_messages = []
    for emotion, messages in TEST_MESSAGES.items():
        for msg in messages:
            all_messages.append({"emotion": emotion, "message": msg})
    return all_messages

def print_test_suite():
    """Print all test messages organized by category"""
    for emotion, messages in TEST_MESSAGES.items():
        print(f"\n{'='*60}")
        print(f"EMOTION: {emotion.upper()}")
        print(f"{'='*60}")
        for i, msg in enumerate(messages, 1):
            print(f"{i}. {msg}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        emotion = sys.argv[1].lower()
        try:
            msg = get_test_message(emotion)
            print(f"Emotion: {emotion}")
            print(f"Message: {msg}")
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("FirstPerson Emotional OS - Glyph Processing Test Suite")
        print(f"Total test messages: {sum(len(msgs) for msgs in TEST_MESSAGES.values())}")
        print(f"Total categories: {len(TEST_MESSAGES)}")
        print("\nUsage:")
        print("  python test_glyph_messages.py <emotion>  - Get a message from category")
        print("  python test_glyph_messages.py --all       - Print all messages")
        print("  python test_glyph_messages.py --categories - List all categories")
        print("\nAvailable categories:")
        for emotion in sorted(TEST_MESSAGES.keys()):
            count = len(TEST_MESSAGES[emotion])
            print(f"  - {emotion} ({count} messages)")
        
        if len(sys.argv) > 1 and sys.argv[1] == "--all":
            print_test_suite()
        elif len(sys.argv) > 1 and sys.argv[1] == "--categories":
            for emotion in sorted(TEST_MESSAGES.keys()):
                print(f"  - {emotion}")
