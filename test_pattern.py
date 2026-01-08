import re

text = 'Open abdonimal surgery'
pattern = r'open\s+abdom[ia]nal\s+surgery'

print(f'Text: {text}')
print(f'Pattern: {pattern}')
print(f'Lowercase text: {text.lower()}')

if re.search(pattern, text.lower()):
    m = re.search(pattern, text.lower())
    print(f'✓ MATCHES: {repr(m.group())}')
else:
    print('✗ Does NOT match')

# Test just the character class
print(f'\nTesting just "abdom[ia]nal":')
if re.search(r'abdom[ia]nal', 'abdonimal'):
    print('✓ abdom[ia]nal matches abdonimal')
else:
    print('✗ abdom[ia]nal does NOT match abdonimal')
    
# What is abdonimal?
word = 'abdonimal'
print(f'\nWord: {word}')
print(f'Characters: {list(word)}')
