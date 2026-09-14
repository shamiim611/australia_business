"""Check every new observation, source coverage, header spans and denominators."""
import json
from pathlib import Path
from collections import Counter
import xlrd
from extract_2024_25 import open_book
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/dashboard-2024-25.json').read_text(encoding='utf-8'))
assert len(data['tables'])==61
books={};count=0
for t in data['tables']:
    if t['source'] not in books:books[t['source']]=open_book(ROOT/t['source'])
    s=next(s for s in books[t['source']].sheets() if s.name==t['sheet']);seen=set()
    assert len({(r['group'],r['label']) for r in t['rows']})==len(t['rows']),t['id']
    for row in t['rows']:
        assert len(row['cells'])==len(t['headers'])
        for h,c in zip(t['headers'],row['cells']):
            r,col=c['sourceRow']-1,c['sourceColumn'];raw=s.cell_value(r,col)
            assert c['cell']==xlrd.formula.colname(col)+str(r+1)
            original=s.cell_note_map.get((r,col));n=original.text if original else ''
            if isinstance(raw,(int,float)):
                seen.add((r,col));assert raw==c['value'],(t['id'],c)
            elif 'not available for publication' in n:assert c['value'] is None and c['status']=='suppressed'
            elif 'nil or rounded to zero' in n:assert c['value']==0 and c['status']=='rounded-zero'
            else:assert c['value'] is None
            if 'too unreliable' in n:assert c['status']=='unreliable'
            elif 'relative standard error' in n:assert c['status']==('caution' if c['value'] is not None else 'missing')
            assert h['denominator'] and h['measure'] and h['population']
            count+=1
    u=t['unitRow']
    source={(r,c) for r in range(u+1,t['endRow']) for c in range(1,s.ncols) if s.cell_type(r,c)==xlrd.XL_CELL_NUMBER}
    assert seen==source,t['id']
by={t['id']:t for t in data['tables']}
assert len(by)==61
assert len(by['4-1']['headers'])==10
assert 'sought debt or equity' in by['2-3']['headers'][0]['denominator']
assert by['11-1']['headers'][0]['population']=='Innovating businesses'
assert by['6-2']['headers'][4]['measure'].startswith('Customer')
assert all(len(t['headers'])<250 for t in data['tables'])
print(f'PASS: {count:,} observations match XLSX; table bounds, populations, flags and coordinates verified')
