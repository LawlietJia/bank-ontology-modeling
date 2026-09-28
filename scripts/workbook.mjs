import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const [input, output, modules] = process.argv.slice(2);
const require = createRequire(path.join(path.dirname(modules),'ontology-resolver.cjs'));
const {Workbook,SpreadsheetFile} = await import(pathToFileURL(require.resolve('@oai/artifact-tool')));
const specs = JSON.parse(await fs.readFile(input,'utf8'));
const wb = Workbook.create();
for (const spec of specs) {
  const sheet = wb.worksheets.add(spec.name);
  const rows = spec.rows.map(row=>row.map(v=>v.startsWith('=')?"'"+v:v));
  const range=sheet.getRangeByIndexes(0,0,rows.length,rows[0].length);
  range.setNumberFormat('@'); range.values=rows;
  if(spec.name==='_baseline') continue;
  range.format.font={name:'Arial',size:11};range.format.wrapText=true;
  range.format.verticalAlignment='top';range.format.columnWidth=32;range.format.rowHeight=88;
  sheet.getRangeByIndexes(0,0,rows.length,1).format.columnWidth=20;
  sheet.getRangeByIndexes(0,0,1,rows[0].length).format={fill:'#153B50',font:{bold:true,color:'#FFFFFF'},rowHeight:30};
  sheet.freezePanes.freezeRows(1);
  if(rows[0].length>=3) sheet.getRangeByIndexes(0,2,rows.length,1).format.columnWidth=48;
  if(spec.name==='使用说明') sheet.getRangeByIndexes(0,1,rows.length,1).format.columnWidth=80;
  if(rows.length>1 && spec.name!=='使用说明') sheet.tables.add(sheet.getUsedRange().address,true,'T'+specs.indexOf(spec));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
