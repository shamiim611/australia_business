"""Extract the 2024-25 publication with explicit header spans and population metadata."""
import json
import re
from pathlib import Path
import xlrd
import openpyxl
from types import SimpleNamespace

class XlsxSheet:
    def __init__(self,s):
        self.s=s;self.name=s.title
        bounds=re.search(r'to ([A-Z]+)(\d+)',str(s['A1'].value))
        if bounds:
            self.nrows=int(bounds[2]);self.ncols=openpyxl.utils.column_index_from_string(bounds[1])
        else:self.nrows=s.max_row;self.ncols=s.max_column
        self.cell_note_map={(c.row-1,c.column-1):c.comment for c in s._cells.values() if c.comment and c.row<=self.nrows and c.column<=self.ncols}
        foot=next((i for i in range(1,self.nrows+1) if s.cell(i,1).value=='Footnotes'),self.nrows+1)
        self.data_end=foot-1
        self.footnotes=[(i-1,str(s.cell(i,1).value)) for i in range(foot+1,self.nrows+1) if s.cell(i,1).value]
        zero=any('including null cells' in text for _,text in self.footnotes)
        for row in s.iter_rows(min_row=4,max_row=self.data_end,max_col=self.ncols):
            for c in row[1:]:
                text=c.comment.text if c.comment else ''
                if str(c.value).lower()=='np':text+=' not available for publication'
                elif c.value in ['\u2014','\u2013'] or (c.value is None and zero):text+=' nil or rounded to zero'
                if isinstance(c.value,(int,float)):
                    if '**' in c.number_format:text+=' too unreliable for general use'
                    elif '^' in c.number_format or '*' in c.number_format:text+=' estimate has a relative standard error and should be used with caution'
                if text:self.cell_note_map[(c.row-1,c.column-1)]=SimpleNamespace(text=text)
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
    for path in sorted((ROOT/'data_2024-25').glob('**/*')):
        if path.suffix.lower()!='.xlsx': continue
        book=open_book(path)
        topic=int(re.search(r'BCSDC(\d{2})',path.stem,re.I).group(1))
        if topic in seen_books:
            assert path.read_bytes()==seen_books[topic], f'Different copies of workbook {topic}'
            continue
        seen_books[topic]=path.read_bytes()
        for s in book.sheets()[1:]:
            number=int(re.search(r'\d+$',s.name).group());actual_id=f'{topic}-{number}'
            tid=actual_id;title_row=1;end=s.data_end;offset=0;suffix=''
            u=next(r for r in range(3,12) if any(v in ['%',"'000"] for v in s.row_values(r)))
            cols=[c for c in range(1,s.ncols) if s.cell_value(u,c) in ['%',"'000",'$b'] or (s.cell_value(u,c)=='' and s.cell_value(u-1,c)!='' and any(isinstance(s.cell_value(rr,c),(int,float)) for rr in range(u+1,end)))]
            def note(r,c):
                n=s.cell_note_map.get((r,c));return clean(n.text) if n else ''
            headers=[]
            for c in cols:
                parts=[]; inherited=[];left=1
                for r in range(3,u):
                    starts=[k for k in range(left,c+1) if s.cell_value(r,k)!='']
                    if not starts: continue
                    k=starts[-1]
                    spans={'1-6':(3,7,9),'1-8':(3,3,5),'2-4':(3,1,11),'3-1':(3,2,6),'3-2':(3,2,6),'4-1':(3,4,6),'6-2':(3,2,4),'6-5':(3,3,5),'7-2':(3,6,8),'8-13':(3,4,7),'9-5':(3,8,12),'10-2':(3,1,3),'11-2':(3,3,5)}
                    if tid in spans:
                        rr,lo,hi=spans[tid]
                        if r==rr and not lo<=c<=hi:continue
                    if tid=='8-2' and r==3 and c in [4,5,8]:continue
                    if tid=='12-3' and r==3 and c==6:continue
                    part=clean(s.cell_value(r,k))
                    part=next((p for p in POPULATIONS if p.lower()==popkey(part)),part)
                    if part not in parts:parts.append(part)
                    if note(r,k):inherited.append(note(r,k))
                    left=k
                population=next((p for p in parts if p in POPULATIONS),'All businesses')
                measure=' / '.join(p for p in parts if p not in POPULATIONS) or 'Share of businesses'
                denominator=note(1,0) or 'All businesses in the selected category.'
                if topic==8 and number in [4,5,6,8,9,10] and c!=cols[-1]:denominator=note(3,1)
                if topic in [9,10] or tid in ['8-13','8-14']:population='Innovation-active businesses'
                if tid=='11-1':population='Innovating businesses'
                if s.cell_value(u,c)=="'000":denominator='Estimated business count in thousands; contextual information only.'
                denominator+=' Coverage includes Agriculture, Forestry and Fishing.'
                headers.append({'column':c,'parts':parts,'label':' / '.join(parts),'population':population,'measure':measure,'unit':s.cell_value(u,c) or '%','denominator':denominator,'notes':list(dict.fromkeys(inherited))})
            rows=[];section='Measures';row_population=None;pop_order=[]
            location='Australia'
            for r in range(u+1,end):
                if tid=='7-3':
                    if 'From Overseas' in str(s.cell_value(r,1)):location='Overseas'
                    if 'From Any location' in str(s.cell_value(r,1)):location='Any location'
                label=clean(s.cell_value(r,0))
                if not label or 'Commonwealth' in label:continue
                if not any(isinstance(s.cell_value(r,c),(int,float)) or str(s.cell_value(r,c)).lower()=='np' for c in cols) and label not in POPULATIONS and not any(s.cell_value(r,c) in ['\u2014','\u2013'] for c in cols):
                    section=label;continue
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
            tables.append({'id':actual_id,'topic':topic,'unitRow':u,'endRow':end,'period':'2017\u201318' if topic==11 else '2024\u201325','title':(clean(s.cell_value(3,0))+' / '+suffix[1:] if suffix else clean(s.cell_value(title_row,0))),'sheet':s.name,'source':path.relative_to(ROOT).as_posix(),'headers':headers,'rows':rows,'notes':[{'sourceRow':rr+1,'sourceColumn':0,'cell':'A'+str(rr+1),'text':text} for rr,text in s.footnotes]+[{'sourceRow':r+1,'sourceColumn':c,'cell':xlrd.formula.colname(c)+str(r+1),'text':clean(n.text)} for (r,c),n in s.cell_note_map.items() if r<=u or c==0]})
    return {'period':'2024\u201325','year':'2024-25','released':'25 June 2026','tables':tables,'ui':{
        'topics':[['Internet & commerce',4],['Digital practices',6],['Cybersecurity',5],['Clean technology',7],['Innovation',8],['Collaboration',9],['Innovation funding',10],['Benefits & barriers',11],['Business characteristics',1],['Finance',2],['Skills',3],['Principal managers',12]],
        'initialTopic':4,
        'cards':[['Internet connection','4-1',9],['Own website or app','4-3',0],['Received orders online','4-4',4],['Cloud technology','6-2',0]],
        'overview':[['4-1',9,'Internet connection'],['4-3',0,'Own website or app'],['4-3',1,'Social media'],['4-6',0,'Placed orders online'],['4-4',4,'Received orders online']],
        'overviewLabel':'Technology adoption'}}
if __name__=='__main__':
    data=extract();encoded=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    for ext,content in [('json',encoded),('js','window.BUSINESS_DATA = '+encoded+';\n')]:
        (ROOT/'data'/f'dashboard-2024-25.{ext}').write_text(content,encoding='utf-8')
    print(f"Extracted {len(data['tables'])} tables and {sum(len(r['cells']) for t in data['tables'] for r in t['rows']):,} observations")
