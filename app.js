"use strict";
const data=window.BUSINESS_DATA;
const modern=Boolean(data.year);
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const tableBy=id=>data.tables.find(t=>t.id===id);
const unique=xs=>[...new Set(xs)];
const fmt=(cell,unit='%')=>cell.value===null?(cell.status==='suppressed'?'NP':'\u2014'):cell.value.toFixed(1)+(unit==='%'?'%':unit==='$b'?' billion AUD':" thousand")+(cell.status==='unreliable'?' !!':cell.status==='caution'?' \u2020':cell.status==='rounded-zero'?' \u2248':'');
const hint=cell=>cell.note||(cell.status==='missing'?'Blank in source; no value inferred.':'Published estimate.');
const options=(id,items,selected)=>{$(id).innerHTML=items.map(([v,l])=>`<option value="${esc(v)}">${esc(l)}</option>`).join('');if(selected!==undefined&&items.some(x=>String(x[0])===String(selected)))$(id).value=selected;};
const topics=data.ui?.topics || (modern? [['Technology',4],['Innovation',5],['Markets & customers',2],['Finance',3],['Ownership & collaboration',1],['Performance',6],['Barriers',7]] : [['Innovation',4],['Barriers',6],['Markets & competition',2],['Finance',3],['Ownership & cooperation',1],['Performance',5]]);
let active=4, csvRows=[];
function national(id,c){return tableBy(id).rows.find(r=>r.group==='Overall').cells[c];}
const cards=data.ui?data.ui.cards.map(([label,id,c])=>[label,national(id,c),'%',`${data.year==='2024-25'?'BCSDC'+id.split('-')[0].padStart(2,'0'):'DO00'+id.split('-')[0]} / Table ${id.split('-')[1]}`]):modern? [['Internet access',national('4-1',8),'%','DO004 / Table 1'],['Web presence',national('4-1',9),'%','DO004 / Table 1'],['Received orders online',national('4-1',11),'%','DO004 / Table 1'],['Introduced goods or services innovation',national('5-1',2),'%','DO005 / Table 1']] : [['Businesses in survey scope',national('1-1',0),"'000",'DO001 \u00b7 Table 1'],['Introduced goods or services innovation',national('4-1',2),'%','DO004 \u00b7 Table 1'],['Operated in overseas markets',national('2-1',8),'%','DO002 \u00b7 Table 1'],['Reported barriers to innovation',national('6-1',8),'%','DO006 \u00b7 Table 1']];
$('kpis').innerHTML=cards.map(([label,c,u,src])=>`<article class="kpi" title="${esc(hint(c))}"><p>${esc(label)}</p><strong>${u==="'000"?`${c.value.toLocaleString()}k`:fmt(c,u)}</strong><small>National total \u00b7 ${src}</small></article>`).join('');
function heatCell(c,unit='%'){
 const p=c.value===null?0:Math.max(0,Math.min(100,c.value))/100;
 const rgb=[240,246,237].map((v,i)=>Math.round(v+([19,121,105][i]-v)*p));
 return `<td tabindex="0" style="background:rgb(${rgb});color:${p>.65?'white':'#163b35'}" title="${esc(hint(c))}">${fmt(c,unit)}</td>`;
}
function overview(){
 const specs=data.ui?.overview || (modern? [['4-1',8,'Internet access'],['4-1',9,'Web presence'],['4-1',10,'Placed orders online'],['4-1',11,'Received orders online']] : [['4-1',2,'Goods & services'],['4-3',4,'Operational processes'],['4-5',4,'Organisation & management'],['4-7',3,'Marketing methods']]);
 const rows=tableBy(specs[0][0]).rows.filter(r=>r.group===$('overviewGroup').value);
 $('heatmap').innerHTML=`<table class="heat"><caption class="source">${data.ui?.overviewLabel||(modern?'Technology adoption':'Innovation')} by ${esc($('overviewGroup').value.toLowerCase())} \u00b7 percentage of all businesses</caption><thead><tr><th scope="col">${esc($('overviewGroup').value)}</th>${specs.map(s=>`<th scope="col">${s[2]}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr><th scope="row">${esc(r.label)}</th>${specs.map(([id,c])=>heatCell(tableBy(id).rows.find(x=>x.group===r.group&&x.label===r.label).cells[c])).join('')}</tr>`).join('')}</tbody></table>`;
}
function setTopic(n){
 active=n;
 $('topics').innerHTML=topics.map(([name,id])=>`<button type="button" aria-pressed="${id===active}" data-topic="${id}">${name}</button>`).join('');
 const tables=data.tables.filter(t=>t.topic===active&&(!$('coverage')||t.scope===$('coverage').value));
 options('table',tables.map(t=>[t.id,t.title]));
 if(!modern&&n===6)$('table').value='6-2';
 setupTable();
}
function current(){return tableBy($('table').value);}
function setupTable(){
 if(modern)return setupModern();
 const t=current();
 options('group',unique(t.rows.map(r=>r.group)).map(g=>[g,g]),t.rows.some(r=>r.group==='Industry')?'Industry':undefined);
 options('metric',t.headers.map((h,i)=>[i,h.label]),t.headers.findIndex(h=>h.label.includes('All businesses')&&h.parts.at(-1).startsWith('Any new')));
 if(t.id==='6-2')$('metric').value='14';
 $('mode').value='groups';
 setupRows();render();
}
function setupRows(){const t=current();options('row',t.rows.map((r,i)=>[i,`${r.group} / ${r.label}`]),t.rows.findIndex(r=>r.group==='Overall'));}
function render(){
 if(modern)return renderModern();
 const t=current(),mode=$('mode').value,mi=Number($('metric').value),head=t.headers[mi];
 $('groupWrap').hidden=mode==='measures';$('metricWrap').hidden=mode!=='groups';$('rowWrap').hidden=mode!=='measures';$('sortWrap').hidden=mode==='heat';
 let entries=[];
 if(mode==='measures'){
  const r=t.rows[Number($('row').value)];
  const unitSet=unique(t.headers.map(h=>h.unit));
  // A count and a percentage must never share a numerical axis.
  entries=t.headers.map((h,i)=>({label:h.label,cell:r.cells[i],unit:h.unit,row:r})).filter(e=>unitSet.length===1||e.unit==='%');
  $('chartTitle').textContent=r.label;
  $('chartContext').textContent=`${r.group} \u00b7 Published measures${unitSet.length>1?' \u00b7 Business count excluded from percentage chart':''}`;
 }else{
  entries=t.rows.filter(r=>r.group===$('group').value).map(r=>({label:r.label,cell:r.cells[mi],unit:head.unit,row:r}));
  $('chartTitle').textContent=mode==='heat'?t.title.replace(/^Table \d+ /,''):head.label;
  $('chartContext').textContent=`${$('group').value} \u00b7 ${mode==='heat'?'All published columns':head.unit==='%'?'Percentage':'Number of businesses (thousands)'}`;
 }
 if($('sort').value!=='source'&&mode!=='heat')entries.sort((a,b)=>a.cell.value===null?1:b.cell.value===null?-1:($('sort').value==='desc'?-1:1)*(a.cell.value-b.cell.value));
 const valid=entries.filter(e=>e.cell.value!==null);
 if(mode==='groups'&&valid.length){const max=valid.reduce((a,b)=>a.cell.value>b.cell.value?a:b);$('insight').textContent=`${max.label} has the highest displayed estimate: ${fmt(max.cell,max.unit)}. Differences are descriptive; sampling uncertainty may affect comparisons.`;}
 else $('insight').textContent=mode==='heat'?'Compare shading within percentage columns. Hover or focus a cell for its source note.':'Measures may overlap or use different populations. Read the source notes before comparing or adding percentages.';
 if(mode==='heat'){
  $('chart').innerHTML=`<div class="overflow"><table class="heat"><thead><tr><th scope="col">Category</th>${t.headers.map(h=>`<th scope="col">${esc(h.label)} (${esc(h.unit)})</th>`).join('')}</tr></thead><tbody>${entries.map(e=>`<tr><th scope="row">${esc(e.label)}</th>${e.row.cells.map((c,i)=>t.headers[i].unit==='%'?heatCell(c):`<td title="${esc(hint(c))}">${fmt(c,t.headers[i].unit)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
 }else{
  const limit=entries[0]?.unit==='%'?100:Math.max(1,...valid.map(e=>e.cell.value))*1.05;
  $('chart').innerHTML=`<div class="bars" role="list" aria-label="${esc($('chartTitle').textContent)}">${entries.map(e=>`<div class="bar-row" role="listitem" tabindex="0" title="${esc(e.label+' \u00b7 '+fmt(e.cell,e.unit)+' \u00b7 '+hint(e.cell))}"><span>${esc(e.label)}</span><div class="track" aria-hidden="true"><div class="fill" style="width:${e.cell.value===null?0:e.cell.value/limit*100}%"></div></div><strong>${fmt(e.cell,e.unit)}</strong></div>`).join('')}<div class="axis">${[0,.25,.5,.75,1].map(x=>`<span>${Math.round(x*limit)}${entries[0]?.unit==='%'?'%':''}</span>`).join('')}</div></div>`;
 }
 $('source').innerHTML=`Source: <a href="${esc(t.source)}">${esc(t.source.split('/').at(-1))}</a> &middot; ${esc(t.sheet)} &middot; Survey period ${esc(t.period||data.period)}. &dagger; Caution &middot; &asymp; Nil or rounded to zero &middot; NP Not published &middot; &mdash; Missing.`;
 csvRows=mode==='heat'?entries.flatMap(e=>t.headers.map((h,i)=>({label:e.label,measure:h.label,cell:e.row.cells[i],unit:h.unit,row:e.row}))):entries.map(e=>({...e,measure:mode==='groups'?head.label:e.label}));
 $('values').innerHTML=`<table class="values"><thead><tr><th>Category</th><th>Measure</th><th>Value</th><th>Source cell</th><th>Notes</th></tr></thead><tbody>${csvRows.map(e=>`<tr><td>${esc(mode==='measures'?e.row.label:e.label)}</td><td>${esc(e.measure)}</td><td>${fmt(e.cell,e.unit)}</td><td>${esc(e.cell.cell)}</td><td>${esc([e.row.note,hint(e.cell)].filter(Boolean).join(' '))}</td></tr>`).join('')}</tbody></table>`;
 $('notes').innerHTML='<h4>Original table and header notes</h4>'+(t.notes.length?t.notes.map(n=>`<p><strong>${esc(n.cell)}</strong> \u00b7 ${esc(n.text)}</p>`).join(''):'<p>No table or header comments recorded in this sheet.</p>');
}
$('topics').addEventListener('click',e=>{const b=e.target.closest('[data-topic]');if(b)setTopic(Number(b.dataset.topic));});
$('table').addEventListener('change',setupTable);
for(const id of ['mode','group','metric','row','sort'])$(id).addEventListener('change',render);
$('overviewGroup').addEventListener('change',overview);
$('download').addEventListener('click',()=>{
 const t=current();const quote=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
 const rows=[['Category','Measure','Value','Unit','Status','Cell','Notes','Workbook','Sheet','Period','Table notes'],...csvRows.map(e=>[$('mode').value==='measures'?e.row.label:e.label,e.measure,e.cell.value,e.unit,e.cell.status,e.cell.cell,[e.row.note,e.cell.note,e.headerNote].filter(Boolean).join(' '),t.source,t.sheet,t.period||data.period,t.notes.map(n=>n.cell+': '+n.text).join(' | ')])];
 const blob=new Blob(['\ufeff'+rows.map(r=>r.map(quote).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`australian-business-${t.id}-${data.year||'2005-06'}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});

function setupModern(){
 const t=current();
 options('group',unique(t.rows.map(r=>r.group)).map(g=>[g,g]),t.rows.some(r=>r.group==='Industry')?'Industry':undefined);
 const pops=unique(t.headers.map(h=>h.population));
 options('population',pops.map(p=>[p,p]),'All businesses');
 modernMetrics();setupRows();$('mode').value='groups';renderModern();
}
function modernMetrics(){
 const t=current(),old=t.headers[Number($('metric').value)]?.measure;
 const hs=t.headers.map((h,i)=>({...h,i})).filter(h=>h.population===$('population').value);
 options('metric',hs.map(h=>[h.i,h.measure]),hs.find(h=>h.measure===old)?.i);
}
function renderModern(){
 const t=current(),mode=$('mode').value,pop=$('population').value,mi=Number($('metric').value),h=t.headers[mi];
 const hs=t.headers.map((h,i)=>({...h,i})).filter(h=>h.population===pop);
 $('populationWrap').hidden=mode==='populations';$('groupWrap').hidden=mode==='measures';$('metricWrap').hidden=!['groups','populations'].includes(mode);$('rowWrap').hidden=mode!=='measures';$('sortWrap').hidden=mode==='heat';
 let entries=[];
 const add=(r,i,label)=>({label,measure:t.headers[i].label,cell:r.cells[i],unit:t.headers[i].unit,row:r,header:t.headers[i],headerNote:[t.headers[i].denominator,...t.headers[i].notes].join(' ')});
 if(mode==='measures'){
  const r=t.rows[Number($('row').value)];
  entries=hs.filter(h=>h.unit==='%'||hs.every(x=>x.unit===h.unit)).map(h=>add(r,h.i,h.measure));
  $('chartTitle').textContent=r.label;
  $('chartContext').textContent=`${r.group} / ${pop}. ${hs.some(h=>h.unit==='%')?'Percentage measures; counts are available in category and heatmap views.':'Business counts in thousands.'}`;
 }else{
  const rows=t.rows.filter(r=>r.group===$('group').value);
  if(mode==='heat')entries=rows.flatMap(r=>hs.map(h=>add(r,h.i,r.label)));
  else if(mode==='populations')entries=rows.flatMap(r=>t.headers.map((hh,i)=>({hh,i})).filter(x=>x.hh.measure===h.measure&&x.hh.unit===h.unit).map(x=>add(r,x.i,`${r.label} / ${x.hh.population}`)));
  else entries=rows.map(r=>add(r,mi,r.label));
  $('chartTitle').textContent=mode==='heat'?t.title.replace(/^Table \d+ /,''):h.measure+(h.unit==='$b'?' (AUD billions)':h.unit==="'000"?' (thousands)':'');
  $('chartContext').textContent=`${$('group').value} / ${mode==='populations'?'Published business populations':pop}`;
 }
 if(mode!=='heat'&&$('sort').value!=='source')entries.sort((a,b)=>{
  const av=a.cell.value!==null&&a.cell.status!=='unreliable',bv=b.cell.value!==null&&b.cell.status!=='unreliable';
  return av!==bv?(av?-1:1):av?($('sort').value==='desc'?-1:1)*(a.cell.value-b.cell.value):0;
 });
 const valid=entries.filter(e=>e.cell.value!==null&&e.cell.status!=='unreliable');
 $('insight').textContent=mode==='groups'&&valid.length?(()=>{const max=valid.reduce((a,b)=>a.cell.value>b.cell.value?a:b);return `${max.label} has the highest displayed usable estimate: ${fmt(max.cell,max.unit)}. Differences are descriptive, not tests of statistical significance.`;})():'Published categories can overlap or omit responses. Percentages are not rescaled to total 100%. Estimates marked !! are excluded from bars and rankings.';
 const denominatorNotes=unique(entries.map(e=>e.header.denominator));
 const extra=unique(entries.flatMap(e=>e.header.notes));
 $('denominator').textContent='Population / denominator: '+denominatorNotes.join('\n')+(extra.length?'\n'+extra.join('\n'):'');
 if(mode==='heat'){
  const rows=t.rows.filter(r=>r.group===$('group').value);
  $('chart').innerHTML=`<div class="overflow"><table class="heat"><caption>${esc(pop)}</caption><thead><tr><th scope="col">Category</th>${hs.map(h=>`<th scope="col">${esc(h.measure)} (${esc(h.unit)})</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr><th scope="row">${esc(r.label)}</th>${hs.map(h=>r.cells[h.i].status==='unreliable'?`<td class="unreliable" tabindex="0" title="${esc(hint(r.cells[h.i]))}">${fmt(r.cells[h.i],h.unit)}</td>`:h.unit==='%'?heatCell(r.cells[h.i]):`<td>${fmt(r.cells[h.i],h.unit)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
 }else{
  const limit=entries[0]?.unit==='%'?100:Math.max(1,...valid.map(e=>e.cell.value))*1.05;
  $('chart').innerHTML=`<div class="bars" role="list" aria-label="${esc($('chartTitle').textContent)}">${entries.map(e=>`<div class="bar-row ${e.cell.status==='unreliable'?'unreliable':''}" role="listitem" tabindex="0" title="${esc(e.label+' / '+fmt(e.cell,e.unit)+' / '+hint(e.cell))}"><span>${esc(e.label)}</span><div class="track" aria-hidden="true"><div class="fill" style="width:${e.cell.value===null||e.cell.status==='unreliable'?0:e.cell.value/limit*100}%"></div></div><strong>${fmt(e.cell,e.unit)}</strong></div>`).join('')}<div class="axis">${[0,.25,.5,.75,1].map(x=>`<span>${Math.round(x*limit)}${entries[0]?.unit==='%'?'%':''}</span>`).join('')}</div></div>`;
 }
 $('source').innerHTML=`Source: <a href="${esc(t.source)}">${esc(t.source.split('/').at(-1))}</a> / ${esc(t.sheet)} / ${esc(t.period||data.period)}. &dagger; Caution / !! Too unreliable for general use / &asymp; Rounded zero / NP Not published / &mdash; Missing.`;
 csvRows=entries;
 $('values').innerHTML=`<table class="values"><thead><tr><th>Category</th><th>Measure / population</th><th>Value</th><th>Source cell</th><th>Notes</th></tr></thead><tbody>${entries.map(e=>`<tr><td>${esc(e.row.label)}</td><td>${esc(e.measure)}</td><td>${fmt(e.cell,e.unit)}</td><td>${esc(e.cell.cell)}</td><td>${esc([e.row.note,hint(e.cell),e.headerNote].filter(Boolean).join(' '))}</td></tr>`).join('')}</tbody></table>`;
 $('notes').innerHTML='<h4>Original table and header notes</h4>'+t.notes.map(n=>`<p><strong>${esc(n.cell)}</strong> / ${esc(n.text)}</p>`).join('');
}

if($('coverage'))$('coverage').addEventListener('change',()=>setTopic(active));
$('yearNav').addEventListener('change',()=>{location.href=$('yearNav').value;});
if(modern)$('population').addEventListener('change',()=>{modernMetrics();renderModern();});
overview();setTopic(data.ui?.initialTopic||4);
