"""Extract the 2021-22 publication with explicit header spans and population metadata."""
import json
import re
from pathlib import Path
import xlrd
import openpyxl
from types import SimpleNamespace

class XlsxSheet:
    def __init__(self,s):
        self.s=s;self.name=s.title;self.nrows=s.max_row;self.ncols=s.max_column
        self.cell_note_map={(c.row-1,c.column-1):c.comment for row in s for c in row if c.comment}
    def cell_value(self,r,c):
        v=self.s.cell(r+1,c+1).value
        return v if v is not None else ""
    def row_values(self,r):return [self.cell_value(r,c) for c in range(self.ncols)]
    def cell_type(self,r,c):return xlrd.XL_CELL_NUMBER if isinstance(self.cell_value(r,c),(int,float)) else 1

def open_book(path):
    b=openpyxl.load_workbook(path,data_only=True)
    sheets=[XlsxSheet(s) for s in b]
    return SimpleNamespace(sheets=lambda:sheets)
from extract_data import clean
ROOT=Path(__file__).resolve().parents[1]
POPULATIONS=['Innovation-active businesses','Non innovation-active businesses','All businesses']
def popkey(value):
    value=value.lower().replace('–','-').replace('businessses','businesses')
    if value in ['innovation-active','non innovation-active']:value+=' businesses'
    if value.endswith(' business'):value+='es'
    return value

def extract():
    tables=[];seen_books={}
    for path in sorted((ROOT/'data_2021-22').glob('**/*')):
        if path.suffix.lower()!='.xlsx': continue
        book=open_book(path)
        topic=int(re.search(r'DO(\d{3})',path.stem,re.I).group(1))
        if topic in seen_books:
            assert path.read_bytes()==seen_books[topic], f'Different copies of workbook {topic}'
            continue
        seen_books[topic]=path.read_bytes()
        for s in book.sheets()[1:]:
            number=int(re.search(r'\d+$',s.name).group());actual_id=f'{topic}-{number}'
            tid=actual_id;title_row=3;end=s.nrows;offset=0;suffix=''
            u=next(r for r in range(4,12) if any(v in ['%',"'000"] for v in s.row_values(r)))
            cols=[c for c in range(1,s.ncols) if s.cell_value(u,c) in ['%',"'000",'$b']]
            def note(r,c):
                n=s.cell_note_map.get((r,c));return clean(n.text) if n else ''
            headers=[]
            for c in cols:
                parts=[]; inherited=[];left=1
                for r in range(title_row+1,u):
                    starts=[k for k in range(left,c+1) if s.cell_value(r,k)!='']
                    if not starts: continue
                    k=starts[-1]
                    if tid=='1-7' and r==5 and c>=8:continue
                    if tid=='2-2' and r==4 and c not in [7,8]:continue
                    if tid=='4-1' and r==4 and not 3<=c<=12:continue
                    if tid=='5-2' and r==4 and c not in [4,5]:continue
                    if tid=='7-1' and r==4 and c not in [4,5,6]:continue
                    if tid=='7-6' and r==5 and c in [8,12]:continue
                    part=clean(s.cell_value(r,k))
                    part=next((p for p in POPULATIONS if p.lower()==popkey(part)),part)
                    if part not in parts:parts.append(part)
                    if note(r,k):inherited.append(note(r,k))
                    left=k
                population=next((p for p in parts if p in POPULATIONS),'All businesses')
                measure=' / '.join(p for p in parts if p not in POPULATIONS) or 'Share of businesses'
                denominator=note(3,0) or 'All businesses in the selected category.'
                if tid=='7-6':denominator=note(4,3) if c>=3 else note(5,1)
                if s.cell_value(u,c)=="'000":denominator='Estimated business count in thousands; contextual information only.'
                denominator+=' Coverage includes Agriculture, Forestry and Fishing.'
                headers.append({'column':c,'parts':parts,'label':' / '.join(parts),'population':population,'measure':measure,'unit':s.cell_value(u,c),'denominator':denominator,'notes':list(dict.fromkeys(inherited))})
            rows=[];section='Measures';row_population=None;pop_order=[]
            location='Australia'
            for r in range(u+1,end):
                if tid=='7-3':
                    if 'From Overseas' in str(s.cell_value(r,1)):location='Overseas'
                    if 'From Any location' in str(s.cell_value(r,1)):location='Any location'
                label=clean(s.cell_value(r,0))
                if not label or 'Commonwealth' in label:continue
                matched=next((p for p in POPULATIONS if p.lower()==popkey(label)),None)
                if matched:
                    row_population=matched;section='Employment size'
                    if matched not in pop_order:pop_order.append(matched)
                    continue
                if not any(s.cell_type(r,c)==xlrd.XL_CELL_NUMBER or note(r,c) for c in cols):section='Employment size' if label=='Total All Industries' else label;continue
                group='Overall' if label in ['Total','Total All Industries'] and section in ['Measures','Employment size','Industry','Region','State/territory'] else section
                if tid=='7-3':label=location+' / '+label
                cells=[]
                for c in cols:
                    raw=s.cell_value(r,c);n=note(r,c);value=raw if isinstance(raw,(int,float)) else None;status='published'
                    if 'not available for publication' in n:value,status=None,'suppressed'
                    elif 'nil or rounded to zero' in n:value,status=0,'rounded-zero'
                    elif value is None:status='missing'
                    elif 'too unreliable' in n:status='unreliable'
                    elif 'relative standard error' in n:status='caution'
                    cells.append({'value':value,'status':status,'note':n,'sourceRow':r+1,'sourceColumn':c,'cell':xlrd.formula.colname(c)+str(r+1)})
                rows.append({'label':label,'group':group,'population':row_population,'row':r+1,'note':note(r,0),'cells':cells})
            if pop_order:
                base=headers
                headers=[dict(h,population=p,label=p+' / '+h['measure']) for p in pop_order for h in base]
                keyed={}
                for row in rows:
                    key=(row['group'],row['label'])
                    if key not in keyed:keyed[key]={}
                    assert row['population'] not in keyed[key],(tid,key)
                    keyed[key][row['population']]=row
                merged=[]
                for key,pops in keyed.items():
                    assert set(pops)==set(pop_order),(tid,key,'Incomplete population blocks')
                    row=dict(pops[pop_order[0]])
                    row['cells']=[dict(c,note=' '.join(x for x in [pops[p]['note'],c['note']] if x)) for p in pop_order for c in pops[p]['cells']]
                    row['note']='';merged.append(row)
                rows=merged
            tables.append({'id':actual_id,'topic':topic,'unitRow':u,'endRow':end,'period':'2017\u201318' if topic==11 else '2021\u201322','title':(clean(s.cell_value(3,0))+' / '+suffix[1:] if suffix else clean(s.cell_value(title_row,0))),'sheet':s.name,'source':path.relative_to(ROOT).as_posix(),'headers':headers,'rows':rows,'notes':[{'sourceRow':r+1,'sourceColumn':c,'cell':xlrd.formula.colname(c)+str(r+1),'text':clean(n.text)} for (r,c),n in s.cell_note_map.items() if r<=u or c==0]})
    return {'period':'2021\u201322','year':'2021-22','released':'22 June 2023','tables':tables,'ui':{
        'topics':[['Connectivity',5],['Online commerce',6],['Digital practices',7],['Cybersecurity',8],['Skills',4],['Business characteristics',1],['Performance & work',2],['Government',3]],
        'initialTopic':5,
        'cards':[['Internet access','5-1',0],['Own website or app','6-1',0],['Received orders online','6-2',4],['Paid cloud computing','7-6',0]],
        'overview':[['5-1',0,'Internet access'],['6-1',0,'Own website or app'],['6-1',2,'Social media'],['6-5',0,'Placed orders online'],['6-2',4,'Received orders online']],
        'overviewLabel':'Technology adoption'}}
if __name__=='__main__':
    data=extract();encoded=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    for ext,content in [('json',encoded),('js','window.BUSINESS_DATA = '+encoded+';\n')]:
        (ROOT/'data'/f'dashboard-2021-22.{ext}').write_text(content,encoding='utf-8')
    print(f"Extracted {len(data['tables'])} tables and {sum(len(r['cells']) for t in data['tables'] for r in t['rows']):,} observations")
