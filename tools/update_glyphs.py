import io
import sys
from pathlib import Path
p = Path('velinor/markdowngameinstructions/glyphs/Glyph_Organizer.csv')
text = p.read_text(encoding='utf-8')
text = text.replace('Desert Trial Grounds (Archive Chamber)', 'Archive Interior (Reclaimed Chambers)')
text = text.replace('Shifting Sands (Desert Archive)', 'The Shared Archive Building (Entrance)')
old1 = "Malrik leads the player through a gauntlet of desert ruins???each step destabilizing stone. He teaches measured pace: not fast (panic), not slow (paralysis), but a tempo that matches the ground beneath. The glyph manifests when the player successfully traverses the ruins, understanding that sovereignty isn't freedom from consequence, but the discipline to move through consequence with intention. This is endurance as art."
new1 = "Malrik navigates the archive building's interior with the player, each step deliberate and measured. The glyph now integrates archive collapse context: when the building fails this motif signals the tension between preservation and ritual—choices here influence Malrik/Elenya reconciliation and rebuild potential. The glyph manifests when the player moves through the chambers and recognizes discipline as both protection and a barrier to intimacy."
text = text.replace(old1, new1)
old2 = "Malrik teaches the player to carve boundary markers in the desert sand???stones or glyphs that define safe space amid chaos. These markers are temporary; the wind will erase them. But while they stand, they hold. The glyph manifests when the player carves their first boundary marker and watches it hold against the wind for a time. This is clarity through definition: the act of saying 'this far, no further,' knowing full well the boundary will eventually dissolve. Sovereignty isn't permanence???it's the repeated choice to mark and hold and redefine."
new2 = "Malrik stands at the archive building's entrance, inscribing preservation boundaries. He argues that records must be sealed and organized—that structure is the only way to honor memory. After collapse, this boundary becomes contentious: will the rebuilt archive be a sealed repository or a shared ritual space? The glyph manifests when the player helps mark preservation zones and recognizes the cost of rigid boundaries."
text = text.replace(old2, new2)
old3 = "Malrik shows the player chambers where the Corelink system stored emotional data???now corrupted, glitching, displaying fragments of millions of private moments. Names blur into meaninglessness. Relationships dissolve into noise. The glyph manifests when the player realizes that this fracture isn't accidental???it's what happens when a system designed to hold consciousness collapses mid-transmission. Data doesn't just vanish; it becomes distorted, haunting. This is the ache of information without context, memory without meaning."
new3 = "Malrik shows the player chambers where the Corelink system stored emotional data — now corrupted, glitching, displaying fragments of millions of private moments. After the archive collapse the glyph becomes central to salvage options: choices to rescue, reconstruct, or abandon records influence rebuild potential and Malrik/Elenya's relationship. The glyph manifests when the player recognizes the human cost of institutional failure and the possibility of rebuilding meaning from fragments."
text = text.replace(old3, new3)
Path('velinor/markdowngameinstructions/glyphs/Glyph_Organizer.csv').write_text(text, encoding='utf-8')
print('updated')
