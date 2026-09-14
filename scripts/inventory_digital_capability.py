"""Inventory dashboard-derived source columns; candidates are NOT harmonised series."""
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/part-1-digital-capability'
RULES={
 'Basic connectivity':r'internet access|internet connect|broadband|web presence|website|online presence',
 'Digital transactions':r'orders|internet income|commerce|electronic invoice|einvoice',
 'Operational systems':r'enterprise resource|customer relationship|electronic data interchange|automated links|business processes using ict',
 'Data capability':r'data analytics|predictive analys|collected.*data|analysed data|data, analytics|data collection',
 'Advanced technologies':r'cloud|internet of things|\biot\b|artificial intelligence|\bai\b|blockchain|3d print|extended reality|virtual reality',
 'Digital management':r'digital business strategy|digital contribution|contribution of digital|cyber security|cybersecurity|management practices.*ict|digital skill targets|ict specialists|ict consultants',
 'Digital value':r'outcomes.*ict|use of icts was important|use of ict.*important',
 'Constraints':r'barriers|limiting|limited|prevented|hamper|shortages|difficulties',
}
fields=['record_id','publication_year','observation_period','table_id','topic','table_title','header_index','excel_column_number','measure','population','unit','denominator','header_notes','table_notes','breakdowns','row_count','candidate_dimensions','review_status','source_workbook','source_sheet','derived_file']
rows=[]
for p in sorted((ROOT/'data').glob('dashboard*.json')):
 d=json.loads(p.read_text(encoding='utf-8'));year=d.get('year') or '2005-06'
 for t in d['tables']:
  notes=' | '.join(n.get('cell','')+': '+n.get('text','') for n in t['notes'])
  for i,h in enumerate(t['headers']):
   measure=h.get('measure',h['label']);context=t['title']+' '+measure
   dimensions=[name for name,pattern in RULES.items() if re.search(pattern,context,re.I)]
   rows.append(dict(zip(fields,[f"{year}:{t['id']}:{i}",year,t.get('period',d.get('period',year)),t['id'],t['topic'],t['title'],i,h['column']+1,measure,h.get('population','UNREVIEWED: inspect original headers'),h['unit'],h.get('denominator','UNREVIEWED: inspect workbook notes'),' | '.join(h.get('notes',[])),notes,' | '.join(dict.fromkeys(x['group'] for x in t['rows'])),len(t['rows']),' | '.join(dimensions),'UNREVIEWED',t['source'],t['sheet'],p.relative_to(ROOT).as_posix()])))
assert len({x['record_id'] for x in rows})==len(rows)
assert all((ROOT/x['source_workbook']).exists() for x in rows)
OUT.mkdir(parents=True,exist_ok=True)
for name,items in [('indicator_inventory.csv',rows),('candidate_digital_indicators.csv',[x for x in rows if x['candidate_dimensions']])]:
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(items)
with (OUT/'availability_screen.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['publication_year',*RULES])
 for year in sorted({x['publication_year'] for x in rows}):
  w.writerow([year,*[sum(x['publication_year']==year and dim in x['candidate_dimensions'].split(' | ') for x in rows) for dim in RULES]])
print(f"Inventoried {len(rows):,} columns across {len({x['publication_year'] for x in rows})} publications; {sum(bool(x['candidate_dimensions']) for x in rows):,} candidates. IDs and source paths verified.")
