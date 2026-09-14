"""Extract the 2018-19 publication with explicit header spans and population metadata."""
import json
import re
from pathlib import Path
import xlrd
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
    for path in sorted((ROOT/'data_2018-19').glob('**/*')):
        if path.suffix.lower()!='.xls': continue
        book=xlrd.open_workbook(path,formatting_info=True)
        topic=int(re.search(r'DO(\d{3})',path.stem,re.I).group(1))
        if topic in seen_books:
            assert path.read_bytes()==seen_books[topic], f'Different copies of workbook {topic}'
            continue
        seen_books[topic]=path.read_bytes()
        sections=[]
        for sheet in book.sheets()[1:]:
            if topic==11 and sheet.name=='Table_2':
                sections.extend([(sheet,0,33,''),(sheet,31,64,'-development'),(sheet,62,sheet.nrows,'-abandoned')])
            else:sections.append((sheet,0,sheet.nrows,''))
        for s,offset,end,suffix in sections:
            number=int(re.search(r'\d+$',s.name).group());actual_id=f'{topic}-{number}'+suffix
            tid=actual_id
            title_row=4 if tid=='2-5' else offset+3
            u=next(r for r in range(offset+4,offset+12) if '%' in s.row_values(r))
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
                    if tid=='7-3' and r==4:continue
                    if topic==1 and r==4 and c==5:continue
                    if topic==5 and r==4 and c not in [3,4,5]:continue
                    if tid in ['7-3','7-4'] and r==5 and c not in [7,8,9]:continue
                    if tid=='7-5' and r==4 and c>=11:continue
                    if tid=='8-3' and r==4 and c>=8:continue
                    if tid=='10-2' and r==5 and c%5==0:continue
                    if tid=='10-3' and r==5 and (c-1)%5>=3:continue
                    part=clean(s.cell_value(r,k))
                    part=next((p for p in POPULATIONS if p.lower()==popkey(part)),part)
                    if part not in parts:parts.append(part)
                    if note(r,k):inherited.append(note(r,k))
                    left=k
                population=next((p for p in parts if p in POPULATIONS),'All businesses')
                measure=' / '.join(p for p in parts if p not in POPULATIONS) or 'Share of businesses'
                if tid=='9-1':measure=parts[-1]
                denominator='Businesses in the selected category and population.'
                if topic in [6,8] or tid in ['5-3','7-2','7-3','7-4','7-5']:
                    population='Innovation-active businesses';denominator=note(title_row,0)
                if tid=='5-4':population='Non innovation-active businesses';denominator=note(title_row,0)
                if topic in [2,3] and number>=3 and c!=cols[-1]:
                    denominator='Businesses that introduced new or significantly improved '+('goods or services.' if topic==2 else 'processes.')
                if tid=='9-2':denominator='Published types of broadband connection; multiple responses allowed in 2018-19. Not comparable to earlier main-connection tables. See source notes.'
                if tid=='9-3':denominator=note(3,0)
                if tid=='10-5' and c>1:denominator=note(4,2)
                if s.cell_value(u,c)=="'000":denominator='Estimated business count in thousands; contextual information only.'
                if topic==11:denominator+=' These are 2017-18 data recast under Oslo Manual definitions, not 2018-19 observations.'
                denominator+=' Coverage includes Agriculture, Forestry and Fishing.'
                headers.append({'column':c,'parts':parts,'label':' / '.join(parts),'population':population,'measure':measure,'unit':s.cell_value(u,c),'denominator':denominator,'notes':list(dict.fromkeys(inherited))})
            rows=[];section='Industry' if tid=='7-2' else 'Measures';row_population=None;pop_order=[]
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
            tables.append({'id':actual_id,'topic':topic,'unitRow':u,'endRow':end,'period':'2017\u201318' if topic==11 else '2018\u201319','title':(clean(s.cell_value(3,0))+' / '+suffix[1:] if suffix else clean(s.cell_value(title_row,0))),'sheet':s.name,'source':path.relative_to(ROOT).as_posix(),'headers':headers,'rows':rows,'notes':[{'sourceRow':r+1,'sourceColumn':c,'cell':xlrd.formula.colname(c)+str(r+1),'text':clean(n.text)} for (r,c),n in s.cell_note_map.items() if r<=u or c==0]})
    return {'period':'2018\u201319','year':'2018-19','released':'26 June 2020','tables':tables,'ui':{
        'topics':[['Innovation summary',1],['Goods & services',2],['Processes',3],['Development & abandoned',4],['Barriers',5],['Ideas & benefits',6],['Collaboration',7],['Expenditure',8],['Technology',9],['Business characteristics',10],['2017-18 definitions',11]],
        'initialTopic':1,
        'cards':[['Internet access','9-1',0],['Web presence','9-1',1],['Received orders online','9-1',4],['Introduced innovation','1-1',1]],
        'overview':[['2-1',2,'Goods & services'],['3-1',8,'Processes'],['1-1',2,'Still in development'],['1-1',3,'Abandoned']],
        'overviewLabel':'Innovation'}}
if __name__=='__main__':
    data=extract();encoded=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    for ext,content in [('json',encoded),('js','window.BUSINESS_DATA = '+encoded+';\n')]:
        (ROOT/'data'/f'dashboard-2018-19.{ext}').write_text(content,encoding='utf-8')
    print(f"Extracted {len(data['tables'])} tables and {sum(len(r['cells']) for t in data['tables'] for r in t['rows']):,} observations")
