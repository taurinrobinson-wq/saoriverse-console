#!/usr/bin/env python3
from emotional_os.learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2

gen = ArchetypeResponseGeneratorV2()

# Just test Turn 1 and Turn 5
turn1 = "I feel fragile today, like even small things overwhelm me. Work has been relentless lately—this week alone I've felt pummeled by back-to-back client meetings and impossible deadlines."
turn5 = "That's the thing. I lost sight of why it mattered in the first place. The advocacy part used to feel fulfilling, but now I'm just drowning out everything else. I've had this little creative spark lately—I've been thinking about art, about making things—but I feel guilty for even considering that when I'm supposed to be focused on the work."

print('TURN 1 - Overwhelm Opening:')
resp1 = gen.generate_archetype_aware_response(turn1, None)
print(resp1)
print()

# Clear recent to test Turn 5
gen.recent_closings = []
gen.recent_openings = []

print('TURN 5 - Complexity/Creative:')
resp5 = gen.generate_archetype_aware_response(turn5, None)
print(resp5)
print()

# Test if they're different
print(f'Responses different? {resp1 != resp5}')

# Extract closing questions
import re
close1 = re.findall(r'\?[^?]*$', resp1)
close5 = re.findall(r'\?[^?]*$', resp5)

print(f'\nClosing 1: {close1[0] if close1 else "None"}')
print(f'Closing 5: {close5[0] if close5 else "None"}')
print(f'Closings different? {close1 != close5}')
