from pathlib import Path
import json, hashlib
import zipfile, xml.etree.ElementTree as ET
from pypdf import PdfReader
from openpyxl import load_workbook

root=Path.cwd()
src=root/'文献-木质素基抗菌碳点'/'文献-木质素基抗菌碳点'
out=root/'tmp'/'extracted'
out.mkdir(parents=True,exist_ok=True)
manifest=[]
for n,p in enumerate(sorted(src.rglob('*'), key=lambda p:p.relative_to(src).as_posix().casefold())):
    if not p.is_file(): continue
    fid=f'F{len(manifest)+1:02}'
    rec={'file_id':fid,'file':p.relative_to(src).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'suffix':p.suffix.lower()}
    text=''
    if p.suffix.lower()=='.pdf':
        r=PdfReader(p)
        rec['pages']=len(r.pages)
        text='\n\n'.join(f'=== PDF PAGE {i+1} ===\n'+(page.extract_text() or '') for i,page in enumerate(r.pages))
    elif p.suffix.lower()=='.docx':
        with zipfile.ZipFile(p) as z:
            tree=ET.fromstring(z.read('word/document.xml'))
            ns={'w':tree.tag.split('}')[0][1:]}
            text='\n'.join(f'P{i+1}: '+''.join(t.text or '' for t in v.findall('.//w:t',ns)) for i,v in enumerate(tree.findall('.//w:p',ns)))
    elif p.suffix.lower()=='.xlsx':
        wb=load_workbook(p,data_only=True)
        text='\n\n'.join('SHEET '+s.title+'\n'+'\n'.join(json.dumps(row,ensure_ascii=False,default=str) for row in s.values) for s in wb)
    rec['text_chars']=len(text)
    (out/f'{fid}.txt').write_text(text,encoding='utf-8')
    manifest.append(rec)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for rec in manifest:
    print(json.dumps(rec,ensure_ascii=False))
