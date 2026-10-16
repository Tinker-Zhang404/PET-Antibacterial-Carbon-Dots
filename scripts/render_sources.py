from pathlib import Path
import json, zipfile
import pdfplumber
root=Path.cwd(); out=root/'tmp'/'source_previews'; out.mkdir(exist_ok=True)
manifest=json.loads((root/'tmp/extracted/manifest.json').read_text(encoding='utf-8'))
src=root/'文献-木质素基抗菌碳点'/'文献-木质素基抗菌碳点'
for fid,pages in {'F01':[6,7],'F05':[4,5,8],'F06':[10],'F14':[8],'F18':[6,9,14,16,21],'F19':[8]}.items():
    p=src/next(r['file'].replace('\\','/') for r in manifest if r['file_id']==fid)
    with pdfplumber.open(p) as doc:
        for page in pages:
            doc.pages[page-1].to_image(resolution=110).save(out/f'{fid}_p{page}.png')
    print(fid)
