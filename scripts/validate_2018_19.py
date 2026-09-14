"""Check every new observation, source coverage, header spans and denominators."""
import json
from pathlib import Path
from collections import Counter
import xlrd
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/dashboard-2018-19.json').read_text(encoding='utf-8'))
assert len(data['tables'])==47
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
    u=t['unitRow']
    source={(r,h['column']) for r in range(u+1,t['endRow']) for h in t['headers'] if s.cell_type(r,h['column'])==xlrd.XL_CELL_NUMBER}
    assert seen==source,t['id']
by={t['id']:t for t in data['tables']}
assert len(by)==47
assert by['2-5']['title'].startswith('Table 5')
assert by['5-3']['headers'][0]['population']=='Innovation-active businesses'
assert by['5-4']['headers'][0]['population']=='Non innovation-active businesses'
assert 'Australian sources' not in by['10-2']['headers'][4]['measure']
assert by['8-3']['headers'][7]['measure'].startswith('Design, planning')
assert all(t['period']=='2017\u201318' for t in data['tables'] if t['topic']==11)
print(f'PASS: {count:,} observations match Excel; source coverage, flags, populations and periods verified')
