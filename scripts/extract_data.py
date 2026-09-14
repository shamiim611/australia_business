"""Rebuild the offline dashboard dataset from the six original ABS XLS files."""
import json
import re
from pathlib import Path
import xlrd

ROOT = Path(__file__).resolve().parents[1]

def clean(value):
    return re.sub(r'\s+', ' ', str(value).replace('\ufffd', '\u2013')).strip()

def extract():
    tables = []
    for path in sorted((ROOT / 'data_2005-06/extracted').rglob('*.XLS')):
        book = xlrd.open_workbook(path, formatting_info=True)
        topic = int(path.stem[7:10])
        for sheet in book.sheets()[1:]:
            unit_row = next(r for r in range(4, 12) if '%' in sheet.row_values(r))
            cols = [c for c in range(1, sheet.ncols) if sheet.cell_value(unit_row,c) in ['%', "'000"]]
            notes = {f'{r}:{c}': clean(n.text) for (r,c),n in sheet.cell_note_map.items()}
            def note(r,c):
                return notes.get(f'{r}:{c}', '')
            headers = []
            for c in cols:
                parts = []
                # Fill each header level only inside the enclosing header span.
                left = 1
                for r in range(4, unit_row):
                    starts = [k for k in range(left,c+1) if sheet.cell_value(r,k) != '']
                    if starts:
                        k = starts[-1]
                        part = clean(sheet.cell_value(r,k))
                        if part not in parts: parts.append(part)
                        left = k
                headers.append({'column':c, 'label':' / '.join(parts), 'parts':parts,
                                'unit':sheet.cell_value(unit_row,c)})
            rows = []
            section = 'Measures'
            for r in range(unit_row+1, sheet.nrows):
                raw = sheet.cell_value(r,0)
                label = clean(raw)
                if not label or 'Commonwealth' in label: continue
                has_data = any(sheet.cell_type(r,c)==xlrd.XL_CELL_NUMBER or note(r,c) for c in cols)
                if not has_data:
                    section = label
                    continue
                group = section
                if label == 'Total' and not str(raw).startswith(' '): group = 'Overall'
                # Unindented barrier names are standalone measures, not children of the preceding heading.
                if topic == 6 and sheet.name in ['Table 2','Table 4']:
                    group = 'Measures'
                    if str(raw).startswith(' ') and section.endswith(':'):
                        label = section.rstrip(':') + ' ' + label
                cells = []
                for c in cols:
                    v = sheet.cell_value(r,c)
                    n = note(r,c)
                    status = 'published'
                    value = v if isinstance(v,(int,float)) else None
                    if 'not available for publication' in n: value,status = None,'suppressed'
                    elif 'nil or rounded to zero' in n: value,status = 0,'rounded-zero'
                    elif value is None: status = 'missing'
                    elif 'relative standard error' in n: status = 'caution'
                    cells.append({'value':value,'status':status,'note':n,'cell':xlrd.formula.colname(c)+str(r+1)})
                rows.append({'label':label,'group':group,'row':r+1,'note':note(r,0),'cells':cells})
            tables.append({'id':f'{topic}-{sheet.name.split()[-1]}','topic':topic,
                'title':clean(sheet.cell_value(3,0)), 'sheet':sheet.name,
                'source':path.relative_to(ROOT).as_posix(), 'headers':headers, 'rows':rows,
                'notes':[{'cell':xlrd.formula.colname(c)+str(r+1),'text':clean(n.text)}
                         for (r,c),n in sheet.cell_note_map.items() if r<=unit_row or c==0]})
    return {'period':'2005\u201306','released':'1 April 2008','tables':tables}

if __name__ == '__main__':
    data = extract()
    output = ROOT / 'data'
    output.mkdir(exist_ok=True)
    encoded = json.dumps(data, ensure_ascii=False, separators=(',',':'))
    (output / 'dashboard.json').write_text(encoded,encoding='utf-8')
    (output / 'dashboard.js').write_text('window.BUSINESS_DATA = '+encoded+';\n',encoding='utf-8')
    print(f"Extracted {len(data['tables'])} tables, {sum(len(t['rows']) for t in data['tables'])} rows")
