"""Check every exported observation against its original workbook cell."""
import json
from collections import Counter
from pathlib import Path
import xlrd
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/dashboard.json').read_text(encoding='utf-8'))
assert len(data['tables'])==31
books={}
count=0
for t in data['tables']:
    if t['source'] not in books: books[t['source']]=xlrd.open_workbook(ROOT/t['source'],formatting_info=True)
    s=books[t['source']].sheet_by_name(t['sheet'])
    actual_numeric=set()
    for row in t['rows']:
        assert len(row['cells'])==len(t['headers'])
        for h,cell in zip(t['headers'],row['cells']):
            r,c=row['row']-1,h['column']
            raw=s.cell_value(r,c)
            assert cell['cell']==xlrd.formula.colname(c)+str(r+1)
            if isinstance(raw,(int,float)):
                actual_numeric.add((r,c))
                assert cell['value']==raw,(t['id'],cell)
            elif cell['status']=='suppressed':
                assert cell['value'] is None and 'not available for publication' in cell['note']
            elif cell['status']=='rounded-zero':
                assert cell['value']==0 and 'nil or rounded to zero' in cell['note']
            else: assert cell['value'] is None
            if h['unit']=='%' and cell['value'] is not None: assert 0<=cell['value']<=100
            count+=1
    unit_row=next(r for r in range(4,12) if '%' in s.row_values(r))
    source_numeric={(r,h['column']) for r in range(unit_row+1,s.nrows) for h in t['headers'] if s.cell_type(r,h['column'])==xlrd.XL_CELL_NUMBER}
    assert source_numeric==actual_numeric, t['id']
by={t['id']:t for t in data['tables']}
def total(t,c): return next(r for r in by[t]['rows'] if r['group']=='Overall')['cells'][c]['value']
assert total('1-1',0)==716
assert total('2-1',8)==8.4
assert total('6-1',8)==38.1
assert by['3-1']['headers'][5]['label']=='All businesses / Status of finance sought / Obtained / Total obtained'
assert by['6-2']['headers'][9]['label']=='Non-innovating businesses / Total'
for group in ['Industry','Employment size','State/territory']:
    sets=[{r['label'] for r in by[t]['rows'] if r['group']==group} for t in ['4-1','4-3','4-5','4-7']]
    assert all(s==sets[0] for s in sets)
print(f'PASS: {count:,} observations, all source numeric cells, flags, key headers, national totals and overview joins')
print(dict(Counter(c['status'] for t in data['tables'] for r in t['rows'] for c in r['cells'])))
