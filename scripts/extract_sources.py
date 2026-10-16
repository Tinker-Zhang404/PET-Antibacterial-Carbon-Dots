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
original_paths=sorted(src.rglob('*'), key=lambda p:p.relative_to(src).as_posix().casefold())
additional_paths=sorted((root/'抗菌文献').rglob('*.pdf'),key=lambda p:p.relative_to(root).as_posix().casefold())
registry_path=root/'data/source_registry.json'
registry=json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else []
by_path={r['project_path']:r for r in registry}
paths=[p for p in original_paths+additional_paths if p.is_file()]
for entry in registry:
    if not (root/entry['project_path']).is_file():
        raise FileNotFoundError(f'Registered source missing: {entry["project_path"]}')
for p in paths:
    key=p.relative_to(root).as_posix()
    if key not in by_path:
        entry=dict(file_id=f'F{max([int(r["file_id"][1:]) for r in registry],default=0)+1:02}',project_path=key,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        registry.append(entry); by_path[key]=entry
paths.sort(key=lambda p:int(by_path[p.relative_to(root).as_posix()]['file_id'][1:]))
for n,p in enumerate(paths):
    if not p.is_file(): continue
    entry=by_path[p.relative_to(root).as_posix()]
    fid=entry['file_id']
    rec={'file_id':fid,'file':p.relative_to(src).as_posix() if p.is_relative_to(src) else p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'suffix':p.suffix.lower()}
    rec['project_path']=p.relative_to(root).as_posix()
    if rec['sha256'] != entry['sha256']:
        raise ValueError(f'Original source changed: {fid} {rec["project_path"]}')
    text=''
    if p.suffix.lower()=='.pdf':
        r=PdfReader(p)
        rec['pages']=len(r.pages)
        pages=[page.extract_text() or '' for page in r.pages]
        text='\n\n'.join(f'=== PDF PAGE {i+1} ===\n'+page for i,page in enumerate(pages))
        (out/f'{fid}.pages.json').write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
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
registry_path.parent.mkdir(exist_ok=True)
registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for rec in manifest:
    print(json.dumps(rec,ensure_ascii=False))
