# -*- coding: utf-8 -*-
"""Convert frame-img fixed heights to full 16:9 display."""
import re

p = r'C:\Users\hp\Dsh\ppt_tasks\ai-video-local-business\webdeck\index.html'
src = open(p, encoding='utf-8').read()
pat = r'(class="frame-img[^"]*" style=")(?:height:[0-9.]+vh)(?:;max-height:[0-9.]+vh)?(")'
# careful: the style attr may contain other tokens; replace only height/max-height occurrences
src2 = re.sub(pat, lambda m: m.group(1) + 'aspect-ratio:16/9;width:100%;max-height:36vh' + m.group(2), src)
open(p, 'w', encoding='utf-8').write(src2)
print('frame-img aspect-ratio count:', src2.count('aspect-ratio:16/9'))
print('remaining height:vh in frame-img:', len(re.findall(r'frame-img[^>]*height:[0-9.]+vh', src2)))
