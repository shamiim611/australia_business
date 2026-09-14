"""Build source-checked, conservative research outputs. Run from any directory.
A decisions are limited to the recent items ABS itself compares; historical
items stay D (snapshot only), with known breaks C. No composite or imputation.
"""
import csv, json, math, re
from pathlib import Path
import xlrd, openpyxl
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/part-1-digital-capability'
ABS = 'https://www.abs.gov.au/statistics/industry/technology-and-innovation/characteristics-australian-business/2024-25'
METHOD = 'https://www.abs.gov.au/methodologies/characteristics-australian-business-methodology/'
DIMS = ['Basic connectivity','Digital transactions','Operational systems','Data capability','Advanced technologies','Digital management','Digital value','Constraints']
META = {}
def item(key, label, dim): META[key] = {'id':key,'label':label,'dimension':DIMS[dim]}
for args in [('internet','Internet access / any connection',0),('web','Web presence (historical)',0),('website_app','Website or app',0),('social','Social media presence',0),('placed','Orders placed online',1),('received','Orders received online',1),('crm','Customer relationship management (CRM)',2),('erp','Enterprise resource planning (ERP)',2),('edi','Electronic data interchange (EDI)',2),('analytics','Data analytics technology',3),('collected','Collected and/or analysed data',3),('predictive','Predictive analysis',3),('cloud','Cloud technology (broad)',4),('paid_cloud','Paid cloud computing',4),('iot','Internet of Things',4),('ai','Artificial intelligence',4),('printing','3D printing',4),('strategy','Digital business strategy',5),('measure','Measured digital contribution',5),('security','Upgraded cyber security',5),('customer','Improved customer responsiveness',6),('workflow','Improved workflow / inventory / ordering',6),('markets','Opportunities to enter or expand markets',6),('skills','Insufficient skills',7),('funds','Lack of funds',7),('benefits','Uncertainty about costs and benefits',7),('technology','Technology issues',7),('knowledge','Lack of understanding of needs / products',7)]: item(*args)
selection=[]
def select(year,tid,mapping):
 for key,index in mapping.items(): selection.append((year,tid,key,index))
for year,tid,start,count in [('2006-07','4-1',8,4),('2008-09','4-1',8,4),('2009-10','7-1',8,4),('2010-11','4-1',8,4),('2011-12','4-1',10,5),('2012-13','7-1',10,5),('2013-14','4-1',10,5),('2014-15','7-1',10,5),('2015-16','4-1',0,5),('2016-17','4-1',0,5),('2017-18','1-1',1,5),('2018-19','9-1',0,5)]:
 keys=['internet','web','placed','received'] if count==4 else ['internet','web','social','placed','received']
 select(year,tid,dict(zip(keys,range(start,start+count))))
select('2007-08','4-4',{'placed':6,'received':7})
select('2019-20','1-1',{'internet':0,'placed':1,'received':2})
select('2019-20','3-7',{'crm':0,'erp':1,'edi':2,'cloud':4,'analytics':6,'iot':7,'ai':8})
select('2021-22','5-1',{'internet':0})
select('2021-22','6-1',{'website_app':0,'social':2})
select('2021-22','6-2',{'received':4})
select('2021-22','6-5',{'placed':0})
select('2021-22','7-6',{'paid_cloud':0})
select('2021-22','7-1',{'crm':0,'erp':1,'edi':2,'cloud':6,'analytics':9,'iot':10,'ai':11,'printing':12})
select('2021-22','2-3',{'strategy':2,'collected':8,'predictive':9})
select('2021-22','7-2',{'customer':0,'workflow':5,'markets':10})
select('2021-22','7-3',{'skills':0,'funds':1,'benefits':2,'technology':3,'knowledge':5})
select('2024-25','4-1',{'internet':9})
select('2024-25','4-3',{'website_app':0,'social':1})
select('2024-25','4-4',{'received':4})
select('2024-25','4-6',{'placed':0})
select('2024-25','6-2',{'cloud':0,'crm':4,'edi':5,'iot':6,'analytics':7,'erp':8,'printing':9,'ai':10})
select('2024-25','6-1',{'strategy':0,'measure':1,'security':6,'collected':8,'predictive':9})
select('2024-25','6-3',{'customer':0,'workflow':5,'markets':11})
select('2024-25','6-4',{'skills':0,'funds':1,'benefits':2,'technology':3,'knowledge':5})
books={}; datasets={}; observations=[]; reviews=[]; checked=0
def clean(s): return re.sub(r'\s+',' ',str(s).replace('\ufffd','–')).strip()
def sheet_for(t):
 p=ROOT/t['source']
 if str(p) not in books:
  books[str(p)]=xlrd.open_workbook(p) if p.suffix.lower()=='.xls' else openpyxl.load_workbook(p,data_only=True)
 b=books[str(p)]
 return b.sheet_by_name(t['sheet']) if p.suffix.lower()=='.xls' else b[t['sheet']]
def raw(s,r,c): return s.cell_value(r-1,c) if hasattr(s,'cell_value') else s.cell(r,c+1).value
def decision(y,key):
 if y in ['2021-22','2024-25'] and key in ['social','received']:
  return 'A','recent-2021-2024','Matched source items and all-business bases; ABS 2024-25 release explicitly compares these two waves. Descriptive comparison only.'
 if y in ['2021-22','2024-25']:
  return 'C',y,'Survey redevelopment and/or item context changed. Keep this wave separate; no temporal change calculated.'
 return 'D',y,'Original values and headers checked; full historical questionnaire and coverage equivalence is not established. Snapshot only.'
for y,tid,key,index in selection:
 if y not in datasets: datasets[y]=json.loads((ROOT/f'data/dashboard-{y}.json').read_text(encoding='utf-8'))
 d=datasets[y];t=next(t for t in d['tables'] if t['id']==tid);h=t['headers'][index];s=sheet_for(t)
 assert h['unit']=='%',(y,tid,key,h)
 assert h.get('population')=='All businesses',(y,tid,key,h)
 grade,segment,reason=decision(y,key)
 # Preserve exact original header cells, including population anchors in merged bands.
 first=min(r['row'] for r in t['rows']); maxcol=max(x['column'] for x in t['headers'])
 headers=[{'row':r,'values':[clean(raw(s,r,c) or '') for c in range(maxcol+1)]} for r in range(1,first)]
 review={'series_id':key,'dimension':META[key]['dimension'],'record_id':f'{y}:{tid}:{index}','publication_year':y,'reference_period':t.get('period',d.get('period',y)),'exact_source_label':h['label'],'numerator':h.get('measure',h['label']),'denominator':h.get('denominator','See original population header: all businesses in the output category'),'universe':('Employing businesses; ABS exclusions apply. ' if y in ['2019-20','2021-22','2024-25'] else 'Historical scope equivalence not independently established. ')+('Agriculture included in selected table.' if any('Agriculture' in r['label'] for r in t['rows']) else 'Do not assume agriculture coverage from absent rows.'),'industry_classification':'ANZSIC 2006 (Revision 2.0)' if y in ['2019-20','2021-22','2024-25'] else 'Historical classification equivalence not approved','size_bands':'0–4; 5–19; 20–199; 200+ persons; overlapping 0–19 subtotal excluded','decision':grade,'segment':segment,'evidence_source':t['source']+' | '+t['sheet']+' | '+(ABS if grade=='A' else METHOD+y if y in ['2019-20','2021-22','2024-25'] else 'Original workbook only'),'evidence_excerpt':reason,'adjustment':'None','reviewer':'Codex source-cell audit; conservative research gate','review_date':'2026-09-14','source_headers':json.dumps(headers,ensure_ascii=False),'source_notes':json.dumps(t['notes'],ensure_ascii=False),'collection_mode':'Online forms' if y=='2024-25' else 'Not independently verified for this item'}
 reviews.append(review)
 for r in t['rows']:
  if r['group'] not in ['Overall','Employment size','Industry'] or r['label']=='0-19 persons':continue
  c=r['cells'][index];rr=c.get('sourceRow',r['row']);cc=c.get('sourceColumn',h['column']);v=c['value'];rv=raw(s,rr,cc)
  if isinstance(v,(int,float)) and isinstance(rv,(int,float)):
   assert math.isclose(v,rv,abs_tol=1e-8),(y,tid,key,r['label'],v,rv)
   checked+=1
  elif v is not None:
   assert c['status'] in ['rounded-zero','suppressed','missing'],(y,tid,key,v,rv,c['status'])
  observations.append({'series':key,'dimension':META[key]['dimension'],'year':y,'period':review['reference_period'],'group':r['group'],'category':r['label'],'population':'All businesses','value':v,'status':c['status'],'note':c.get('note',''),'unit':'%','decision':grade,'segment':segment,'denominator':review['denominator'],'record_id':review['record_id'],'workbook':t['source'],'sheet':t['sheet'],'cell':c.get('cell',f'row {rr}, column {cc+1}'),'raw_value':rv})
# Within-wave innovation association: 2018-19 only, preserving published strata.
y='2018-19';t=next(t for t in datasets[y]['tables'] if t['id']=='9-1');s=sheet_for(t)
# These columns are separate populations and need their own audit records.
for key,ia,ib in [('internet',5,10),('web',6,11),('social',7,12),('placed',8,13),('received',9,14)]:
 base=next(r for r in reviews if r['publication_year']==y and r['series_id']==key)
 for idx in [ia,ib]:
  h=t['headers'][idx];r=dict(base)
  r.update(record_id=f'{y}:9-1:{idx}',exact_source_label=h['label']+' | '+h['population'],numerator=h['measure'],denominator='Businesses in the named innovation-status population within each output category: '+h['population'],decision='D',segment='2018-19-innovation-snapshot',evidence_excerpt='Original status headers and matching source cells checked. Within-wave comparison only; each status population is its own base. No temporal innovation comparison approved.')
  reviews.append(r)
innovation=[]
for r in t['rows']:
 if r['group'] not in ['Overall','Employment size','Industry'] or r['label']=='0-19 persons':continue
 for key,a,b in [('internet',5,10),('web',6,11),('social',7,12),('placed',8,13),('received',9,14)]:
  cells=[r['cells'][i] for i in (a,b)]
  for i,c in zip((a,b),cells):
   v=raw(s,c.get('sourceRow',r['row']),c.get('sourceColumn',t['headers'][i]['column']))
   if isinstance(c['value'],(int,float)): assert c['value']==v;checked+=1
  usable=all(c['value'] is not None and c['status'] in ['published','caution','rounded-zero'] for c in cells)
  innovation.append({'series':key,'year':y,'group':r['group'],'category':r['label'],'active':cells[0]['value'],'nonactive':cells[1]['value'],'gap':round(cells[0]['value']-cells[1]['value'],1) if usable else None,'status':'caution' if any(c['status']=='caution' for c in cells) else 'published' if usable else 'unavailable','active_status':cells[0]['status'],'nonactive_status':cells[1]['status'],'workbook':t['source'],'sheet':t['sheet'],'active_cell':cells[0]['cell'],'nonactive_cell':cells[1]['cell'],'interpretation':'Within-wave descriptive association; each innovation-status group is its own denominator. No causal or joint size-industry adjustment.'})
def usable(o,strict=False):return o['value'] is not None and o['status'] in (['published','rounded-zero'] if strict else ['published','rounded-zero','caution'])
def national(key,y):return next(o for o in observations if o['series']==key and o['year']==y and o['group']=='Overall')
gaps=[]
for y,tid,key,index in selection:
 rows=[o for o in observations if o['series']==key and o['year']==y and o['group']=='Employment size']
 small=next((o for o in rows if re.match(r'^0[–-]4 ',o['category'])),None);large=next((o for o in rows if o['category'].startswith('200 or more')),None)
 if small and large:
  valid=usable(small) and usable(large)
  gaps.append({'series':key,'year':y,'small':small['value'],'large':large['value'],'gap':round(large['value']-small['value'],1) if valid else None,'status':'caution' if 'caution' in [small['status'],large['status']] else 'published' if valid else 'unavailable','decision':small['decision'],'small_cell':small['cell'],'large_cell':large['cell'],'record_id':small['record_id']})
# Persistence is only counted across A-approved waves, with both waves present.
persistence=[]
for key in ['social','received']:
 categories=sorted({o['category'] for o in observations if o['series']==key and o['group']=='Industry' and o['decision']=='A'})
 for cat in categories:
  rows=[o for o in observations if o['series']==key and o['group']=='Industry' and o['category']==cat and o['decision']=='A']
  if len(rows)!=2 or not all(usable(o) and usable(national(key,o['year'])) for o in rows):continue
  differences={o['year']:round(o['value']-national(key,o['year'])['value'],1) for o in rows}
  persistence.append({'series':key,'industry':cat,'waves':2,'below':sum(v<0 for v in differences.values()),'gap_2021_22':differences['2021-22'],'gap_2024_25':differences['2024-25'],'unflagged_waves':sum(usable(o,True) and usable(national(key,o['year']),True) for o in rows),'interpretation':'Repeated below-national position in two recent waves, not long-run persistence or statistical significance.'})
changes=[]
for key in ['social','received']:
 a,b=[national(key,y) for y in ['2021-22','2024-25']];ga,gb=[next(g for g in gaps if g['series']==key and g['year']==y) for y in ['2021-22','2024-25']]
 changes.append({'series':key,'start':'2021-22','end':'2024-25','start_value':a['value'],'end_value':b['value'],'change_pp':round(b['value']-a['value'],1),'start_size_gap':ga['gap'],'end_size_gap':gb['gap'],'size_gap_change_pp':round(gb['gap']-ga['gap'],1) if ga['gap'] is not None and gb['gap'] is not None else None,'sensitivity_unflagged':all(usable(o,True) for o in [a,b]) and ga['status']=='published' and gb['status']=='published'})
OUT.mkdir(parents=True,exist_ok=True)
def csvout(name,rows):
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,rows in [('comparability_decisions.csv',reviews),('observations.csv',observations),('size_gaps.csv',gaps),('innovation_associations.csv',innovation),('industry_persistence.csv',persistence),('approved_changes.csv',changes)]:csvout(name,rows)
result={'title':'Connected, but unevenly capable','dimensions':DIMS,'indicators':list(META.values()),'observations':observations,'gaps':gaps,'innovation':innovation,'persistence':persistence,'changes':changes,'reviews':[{k:v for k,v in r.items() if k not in ['source_headers','source_notes']} for r in reviews],'verified_numeric_cells':checked,'sources':{'abs_recent':ABS,'methodology_2021':METHOD+'2021-22','methodology_2024':METHOD+'2024-25'},'limitations':['2005-06 has no selected connectivity or transaction measures in the supplied dashboard tables. This is an evidence gap, not zero adoption.','Historical item-level equivalence remains unapproved (D); known recent redevelopment breaks are C. Only social presence and orders received in 2021-22 and 2024-25 are A-approved temporal comparisons.','A applies to the named two-wave comparison, not the entire history. No B adjustments are made.','National rates are unadjusted. Compatible fixed population weights have not been established. Separate size and industry tables do not jointly adjust composition.','No confidence intervals or significance claims: exact uncertainty and covariance for the full comparison set are unavailable. Cautions remain visible; very unreliable values are excluded from charts and differences.','Barriers and digital outcomes allow multiple responses. Reported ICT outcomes are subjective, not causal effects.','Marginal percentages cannot establish how many capabilities each business holds. No maturity index is constructed.']}
(OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/research-digital-capability.js').write_text('window.RESEARCH_DATA = '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
def val(k,y='2024-25'):return national(k,y)['value']
lines=['# Part 1: Connected, but unevenly capable','','Status: source-checked descriptive analysis; historical harmonisation remains open.','','## Findings',f"Internet connectivity reaches {val('internet')}% in 2024-25, while online ordering received is {val('received')}%, CRM {val('crm')}%, analytics technology {val('analytics')}% and AI {val('ai')}%. Connectivity is more widespread than these individual uses; this does not measure joint business-level breadth.",'',f"Historical snapshots show internet access of {val('internet','2006-07')}% in 2006-07 and {val('internet','2018-19')}% in 2018-19. They suggest diffusion, but are not an approved continuous series. Coverage and questionnaire audit remains incomplete; no historical percentage-point change is reported.",'']
for c in changes:
 lines += [f"{META[c['series']]['label']}: {c['start_value']}% (2021-22) to {c['end_value']}% (2024-25), {c['change_pp']:+.1f} percentage points. The 200+ minus 0-4 size gap is {c['start_size_gap']} then {c['end_size_gap']} points (change {c['size_gap_change_pp']:+.1f}). Descriptive only; excluding flagged inputs leaves this result unchanged: {c['sensitivity_unflagged']}.",'']
for key in ['social','received']:
 below=[p['industry'] for p in persistence if p['series']==key and p['below']==2]
 lines += [f"{META[key]['label']}: industries below the national benchmark in both approved recent waves: {', '.join(below)}. Two waves establish recent recurrence, not persistent long-run disadvantage. See industry_persistence.csv for flag sensitivity.",'']
lines += [f"In 2024-25, skills ({val('skills')}%), funds ({val('funds')}%), and cost/benefit uncertainty ({val('benefits')}%) coexist as ICT constraints. The source review does not establish a long-run transition from infrastructure to skills. Recent constraint profiles are separate C snapshots.",'']
for a in innovation:
 if a['series']=='received' and a['group']=='Employment size':lines += [f"2018-19, {a['category']}: innovation-active businesses receiving online orders {a['active']}%, non-active {a['nonactive']}%; difference {a['gap']} points ({a['status']})."]
lines += ['','These within-size associations do not control industry simultaneously and do not identify causality.','','## Evidence and reproduction',f'All {checked:,} selected numeric cells were checked directly against the original workbooks. Exact headers and source notes are retained in comparability_decisions.csv. observations.csv preserves the source workbook, sheet, cell, denominator and flags.','',f'[ABS recent-wave comparisons]({ABS}); [2021-22 methodology]({METHOD}2021-22); [2024-25 methodology]({METHOD}2024-25).','','Run `python scripts/build_digital_research.py` and `python scripts/test_digital_research.py`. Open `research.html` offline.','','## Interpretation limits',*['- '+s for s in result['limitations']]]
(OUT/'findings.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Built {len(observations):,} observations, {len(reviews)} item decisions, {len(gaps)} size gaps; checked {checked:,} source numbers.')
print(json.dumps(changes,indent=2))
