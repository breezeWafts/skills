# -*- coding: utf-8 -*-
"""Extract OCR sampling images + text layers from scanned theory PDFs."""
import os, sys, json, glob, shutil, warnings
warnings.filterwarnings('ignore')
import pymupdf
from PIL import Image
import io

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)                   # build/
SRC = os.path.dirname(WORK)                    # project root
IMG = os.path.join(ROOT, 'img2')
TXT = os.path.join(ROOT, 'text2')
for d in (IMG, TXT):
    os.makedirs(d, exist_ok=True)

files = sorted(glob.glob(os.path.join(SRC, '理论', '*.pdf')))
manifest = []
for bi, f in enumerate(files, 1):
    bid = 'b%02d' % bi
    name = os.path.basename(f)[:-4]
    try:
        doc = pymupdf.open(f)
    except Exception as e:
        print(bid, name, 'OPEN_FAIL', type(e).__name__, flush=True)
        continue
    n = doc.page_count
    # probe text layer on 12 evenly spaced pages
    probe = [i for i in range(0, n, max(1, n // 12))][:12]
    chars = 0
    for i in probe:
        try:
            chars += len(doc[i].get_text('text').strip())
        except Exception:
            pass
    has_text = chars > 600

    # full text export for text-layer books
    if has_text:
        buf = []
        for i in range(n):
            try:
                buf.append(doc[i].get_text('text').strip())
            except Exception:
                buf.append('')
        with open(os.path.join(TXT, bid + '.txt'), 'w', encoding='utf-8') as fh:
            fh.write('\n\n'.join(buf))

    front = [i for i in range(2, min(8, n))][:5]
    step = max(1, (n - 12) // 12)
    mid = [12 + k * step for k in range(12) if 12 + k * step < n]
    pages = sorted(set(front + mid + [n - 1]))

    imgs = 0
    texts = 0
    for pno in pages:
        try:
            page = doc[pno]
            t = page.get_text('text').strip()
            if len(t) > 120:
                with open(os.path.join(TXT, '%s_p%04d.txt' % (bid, pno)), 'w', encoding='utf-8') as fh:
                    fh.write(t)
                texts += 1
                continue
            # render scanned page
            rect = page.rect
            scale = 1700.0 / max(rect.width, rect.height)
            pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
            pic = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
            pic.save(os.path.join(IMG, '%s_p%04d.jpg' % (bid, pno)), quality=85, optimize=True)
            imgs += 1
        except Exception as e:
            print('  ', bid, 'page', pno, 'FAIL', type(e).__name__, flush=True)

    manifest.append(dict(id=bid, name=name, file=os.path.relpath(f, SRC),
                         pages=n, has_text=has_text, probe_chars=chars,
                         sampled=pages, images=imgs, text_pages=texts))
    print('%s %-30s n=%4d text=%-5s(%5d) imgs=%2d txtpg=%2d'
          % (bid, name[:30], n, has_text, chars, imgs, texts), flush=True)
    doc.close()

with open(os.path.join(ROOT, 'manifest.json'), 'w', encoding='utf-8') as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=1)
print('TOTAL images=%d textbooks=%d books=%d'
      % (sum(m['images'] for m in manifest), sum(m['has_text'] for m in manifest), len(manifest)),
      flush=True)
