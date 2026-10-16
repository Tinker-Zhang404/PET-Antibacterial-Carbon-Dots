import json,re
from pathlib import Path
import pdfplumber
root=Path.cwd(); manifest=json.loads((root/'tmp/extracted/manifest.json').read_text(encoding='utf8'))
queries={'F05':['PLQY values','1.60 nm','82.61%','With the optimized','3.4.','3.5.','The PL spectra'],'F04':['2.6','3.6.','3.9','75 μ'],'F07':['3.87','35.23','3.5. Biological'],'F10':['3.7. Disk','3.8. Cytotoxicity'],'F15':['20.6','10.7','61.9']}
for fid,qs in queries.items():
    t=(root/f'tmp/extracted/{fid}.txt').read_text(encoding='utf8'); pages=re.split(r'=== PDF PAGE [0-9]+ ===',t)
    for q in qs: print(fid,q,[i for i,p in enumerate(pages) if q in p])
src=root/'文献-木质素基抗菌碳点'/'文献-木质素基抗菌碳点'
p=src/next(x['file'].replace('\\','/') for x in manifest if x['file_id']=='F05')
with pdfplumber.open(p) as doc:
    pg=doc.pages[4]
    pg.crop((40,45,pg.width-40,155)).to_image(resolution=250).save(root/'tmp/source_previews/F05_sizes.png')
