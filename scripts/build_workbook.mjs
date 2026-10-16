import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root=process.cwd();
const data=JSON.parse(await fs.readFile(path.join(root,'tmp/database.json'),'utf8'));
const output=path.join(root,'output/木质素碳点训练数据库');
const preview=path.join(root,'tmp/workbook_previews');
const selectedRenders=process.argv[2]?.split(',');
await fs.mkdir(preview,{recursive:true});
const wb=Workbook.create();
function col(n){let s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;}
const longHeaders=new Set(['notes','source_locator','source_file_id','processing','evidence_text','missing_fields','conditions_raw','description','issue','handling','definition_zh','activity_evidence','required_condition','reported_method','transfer_limit','precursor','operation','candidate','data_to_extract','available_conditions']);
const colors={'路线筛选':'#234D43','抗菌训练长表':'#1F4E78','碳点合成':'#3C6587','建库说明':'#73767B','PET实验录入':'#9A6B24'};
let tableNo=0;
for(const [name,rows] of Object.entries(data.tables)){
  const sh=wb.worksheets.add(name); sh.showGridLines=false;
  if(colors[name]) sh.tabColor=colors[name];
  const headers=data.headers[name];
  const matrix=[headers,...rows.map(r=>headers.map(h=>{const v=r[h]??null; return typeof v==='string'&&v.startsWith('=')?"'"+v:v;}))];
  const last=col(headers.length), end=Math.max(matrix.length,2);
  sh.getRange(`A1:${last}${matrix.length}`).values=matrix;
  const all=sh.getRange(`A1:${last}${end}`);
  all.format.font={name:'Microsoft YaHei',size:10,color:'#243746'};
  all.format.verticalAlignment='center';
  all.format.rowHeight=38;
  const head=sh.getRange(`A1:${last}1`);
  head.format.fill=colors[name]??'#3C5363';
  head.format.font={name:'Microsoft YaHei',size:10,bold:true,color:'#FFFFFF'};
  head.format.wrapText=true;
  head.format.horizontalAlignment='center';
  head.format.rowHeight=52;
  for(let j=0;j<headers.length;j++){
    const h=headers[j], letter=col(j+1);
    const rng=sh.getRange(`${letter}1:${letter}${end}`);
    const numeric=rows.some(r=>typeof r[h]==='number');
    const width=longHeaders.has(h)?400:h==='missing_policy'?300:h==='file_name'||h==='title'?460:h==='doi'?300:h==='endpoint'||h==='chemical_name'||h==='material_context'||h==='default_training_use'?270:h==='organism'?240:h.includes('id')||h==='sample_label'||h==='formulation_label'?145:180;
    rng.format.columnWidthPx=width;
    if(matrix.length>1){
      const body=sh.getRange(`${letter}2:${letter}${matrix.length}`);
      body.format.horizontalAlignment=numeric?'right':'left';
      body.format.wrapText=!numeric;
      if(numeric)body.setNumberFormat(h.endsWith('year')||h==='year'||h.endsWith('_id')||h==='step_order'||h==='n'||h==='pet_present'||h.includes('eligible')||h==='include_primary_training'?'0':'General');
    }
  }
  if(rows.length){
    const table=sh.tables.add(`A1:${last}${matrix.length}`,true,`Data${++tableNo}`);
    table.showFilterButton=true;
    const body=sh.getRange(`A2:${last}${matrix.length}`);
    body.format.autofitRows();
    // Separate rows have deliberately different heights when required for wrapped source notes.
    for(let i=2;i<=matrix.length;i++){
      const rr=sh.getRange(`A${i}:${last}${i}`);
      if(rr.format.rowHeight<30) rr.format.rowHeight=30;
    }
  }
  sh.freezePanes.freezeRows(1);
  if(headers.length>10)sh.freezePanes.freezeColumns(2);
  if(name==='待核查'&&rows.length)sh.getRange(`D2:F${end}`).format.fill='#FFF4D6';
  if(name==='建库说明'){
    sh.getRange(`A2:A${end}`).format.font={name:'Microsoft YaHei',size:10,bold:true,color:'#243746'};
    sh.getRange(`B1:B${end}`).format.columnWidthPx=900;
    sh.getRange(`A2:B${end}`).format.autofitRows();
  }
  console.log(`populated ${name}: ${rows.length} rows, ${headers.length} columns`);
}
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'碳点合成!A1:J5',include:'values',tableMaxRows:5,tableMaxCols:10,maxChars:1800})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'formula error scan',maxChars:1200})).ndjson);
const file=await SpreadsheetFile.exportXlsx(wb);
await file.save(path.join(output,'PET搭配材料筛选_木质素碳点文献数据库.xlsx'));
console.log('xlsx exported');
for(const [name,rows] of Object.entries(data.tables)){
  if(selectedRenders&&!selectedRenders.includes(name))continue;
  const ncol=Math.min(name==='路线筛选'?7:6,data.headers[name].length);
  const nrow=Math.min(rows.length+1,7);
  try{
    const img=await wb.render({sheetName:name,range:`A1:${col(ncol)}${Math.max(nrow,2)}`,scale:1.1,format:'png'});
    await fs.writeFile(path.join(preview,`${name}.png`),new Uint8Array(await img.arrayBuffer()));
    console.log(`rendered ${name}`);
  }catch(e){console.log(`RENDER_ERROR ${name}: ${e.message}`);}
}
await fs.writeFile(path.join(root,'tmp/workbook_inspection.json'),JSON.stringify({summary:data.summary,exported:true},null,2));
