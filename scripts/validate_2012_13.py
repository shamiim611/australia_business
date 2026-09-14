"""Check every new observation, source coverage, header spans and denominators."""
import json
from pathlib import Path
from collections import Counter
import xlrd
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/dashboard-2012-13.json').read_text(encoding='utf-8'))
assert len(data['tables'])==38
books={};count=0
for t in data['tables']:
    if t['source'] not in books:books[t['source']]=xlrd.open_workbook(ROOT/t['source'],formatting_info=True)
    s=books[t['source']].sheet_by_name(t['sheet']);seen=set()
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
            elif 'relative standard error' in n:assert c['status']=='caution'
            assert h['denominator'] and h['measure'] and h['population']
            count+=1
    u=next(r for r in range(4,12) if '%' in s.row_values(r))
    source={(r,h['column']) for r in range(u+1,s.nrows) for h in t['headers'] if s.cell_type(r,h['column'])==xlrd.XL_CELL_NUMBER}
    assert seen==source,t['id']
by={t['id']:t for t in data['tables']}
assert 'Purchase' in by['3-2']['headers'][9]['measure']
assert 'Purchase' not in by['3-2']['headers'][10]['measure']
assert 'Australian suppliers' not in by['2-8']['headers'][3]['label']
assert by['7-1']['headers'][12]['measure']=='social media presence'
assert by['7-3']['headers'][8]['unit']=='$b'
assert len(by['6-3']['rows'])==22
assert any('Any level of government' in h['measure'] for h in by['2-6']['headers'])
assert all('relying on a small number' in h['denominator'] for h in by['2-9']['headers'][1:])
flags=Counter(c['status'] for t in data['tables'] for r in t['rows'] for c in r['cells'])
print(f'PASS: {count:,} observations match Excel; source coverage, population pivots, flags, units, procurement and header spans verified')
print(dict(flags))
