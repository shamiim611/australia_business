"""Extract the 2013-14 publication with explicit header spans and population metadata."""
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
    tables=[]
    for path in sorted((ROOT/'data_2013-14/extracted').glob('**/*')):
        if path.suffix.lower()!='.xls': continue
        book=xlrd.open_workbook(path,formatting_info=True)
        topic=int(path.stem[7:10])
        for s in book.sheets()[1:]:
            number=int(re.search(r'\d+$',s.name).group());actual_id=f'{topic}-{number}'
            canonical=number-2 if topic==2 and number>=7 else number
            tid=f'{topic}-{canonical}'
            if topic==2 and number in [5,6]:tid=f'procurement-{number}'
            u=next(r for r in range(4,12) if '%' in s.row_values(r))
            cols=[c for c in range(1,s.ncols) if s.cell_value(u,c) in ['%',"'000",'$b']]
            def note(r,c):
                n=s.cell_note_map.get((r,c));return clean(n.text) if n else ''
            headers=[]
            for c in cols:
                parts=[]; inherited=[];left=1
                for r in range(4,u):
                    starts=[k for k in range(left,c+1) if s.cell_value(r,k)!='']
                    if not starts: continue
                    k=starts[-1]
                    # Sparse subheadings have finite spans, not the whole remaining row.
                    if tid=='3-2' and r==5 and c>=11: continue
                    if topic==7 and r==4:
                        width=12 if number==1 else 14
                        local=(c-1)%width+1
                        if local not in ([4,5,6] if number==1 else [3,4,5]):continue
                    if tid=='2-3' and r==4 and c==5:continue
                    if tid=='2-4' and r==5 and c%5==0:continue
                    if tid=='2-5' and r==4 and c>=4:continue
                    if tid=='2-6' and r==5 and (c-1)%5>=3:continue
                    part=clean(s.cell_value(r,k))
                    part=next((p for p in POPULATIONS if p.lower()==popkey(part)),part)
                    if part not in parts:parts.append(part)
                    if note(r,k):inherited.append(note(r,k))
                    left=k
                population=next((p for p in parts if p in POPULATIONS),'All businesses')
                measure=' / '.join(p for p in parts if p not in POPULATIONS) or 'Share of businesses'
                if tid=='4-1':measure=parts[-1]
                denominator='Businesses in the selected category and population.'
                if tid=='3-1':
                    denominator=('All businesses in the selected category.' if c==1 else 'Businesses that sought debt or equity finance.' if c<=3 else 'Businesses that sought debt finance.' if c<=6 else 'Businesses that sought equity finance.')
                elif tid=='3-2':denominator='All businesses in the selected category and population.' if c==1 else 'Businesses that sought debt or equity finance in the selected category and population.'
                elif topic==4:
                    denominator={1:'All businesses in the selected category and population.',2:'Businesses with broadband as their main Internet connection at 30 June 2014.',3:'All businesses in the selected category and population.',4:'Published distribution by Internet-income share; read the original table definition below.'}[number]
                    if number==3 and c==3:denominator='Internet income in billions of Australian dollars; source advises caution.'
                    if number==4:inherited.append(note(3,0))
                elif tid=='2-7':denominator='All businesses in the selected category.' if c==1 else 'Businesses relying on a small number of clients, customers or buyers.'
                elif tid in ['2-10','2-11']:denominator='Businesses reporting some degree of competition in the selected category and population.'
                if s.cell_value(u,c)=="'000":denominator='Estimated number of businesses at 30 June 2014, in thousands; contextual information only.'
                denominator+=' Coverage includes Agriculture, Forestry and Fishing.'
                if tid=='5-9':
                    population='Innovation-active businesses';denominator='Innovation-active businesses in the selected industry and employment-size category.'
                headers.append({'column':c,'parts':parts,'label':' / '.join(parts),'population':population,'measure':measure,'unit':s.cell_value(u,c),'denominator':denominator,'notes':list(dict.fromkeys(inherited))})
            rows=[];section='Industry' if tid=='5-9' else 'Measures';row_population=None;pop_order=[]
            for r in range(u+1,s.nrows):
                label=clean(s.cell_value(r,0))
                if not label or 'Commonwealth' in label:continue
                matched=next((p for p in POPULATIONS if p.lower()==popkey(label)),None)
                if matched:
                    row_population=matched;section='Employment size'
                    if matched not in pop_order:pop_order.append(matched)
                    continue
                if not any(s.cell_type(r,c)==xlrd.XL_CELL_NUMBER or note(r,c) for c in cols):section=label;continue
                group='Overall' if label in ['Total','Total All Industries'] and section in ['Employment size','Industry','Region','State/territory'] else section
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
            tables.append({'id':actual_id,'topic':topic,'title':clean(s.cell_value(3,0)),'sheet':s.name,'source':path.relative_to(ROOT).as_posix(),'headers':headers,'rows':rows,'notes':[{'sourceRow':r+1,'sourceColumn':c,'cell':xlrd.formula.colname(c)+str(r+1),'text':clean(n.text)} for (r,c),n in s.cell_note_map.items() if r<=u or c==0]})
    return {'period':'2013\u201314','year':'2013-14','released':'20 August 2015','tables':tables,'ui':{
        'topics':[['Innovation',5],['Technology',4],['Skills',8],['Markets & procurement',2],['Finance',3],['Ownership, work & IP',1],['Performance',6],['Barriers',7]],
        'initialTopic':5,
        'cards':[['Internet access','4-1',10],['Web presence','4-1',11],['Received orders online','4-1',14],['Introduced goods or services innovation','5-1',2]],
        'overview':[['5-1',2,'Goods & services'],['5-3',4,'Operational processes'],['5-5',5,'Organisation & management'],['5-7',5,'Marketing methods']],
        'overviewLabel':'Innovation'}}
if __name__=='__main__':
    data=extract();encoded=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    for ext,content in [('json',encoded),('js','window.BUSINESS_DATA = '+encoded+';\n')]:
        (ROOT/'data'/f'dashboard-2013-14.{ext}').write_text(content,encoding='utf-8')
    print(f"Extracted {len(data['tables'])} tables and {sum(len(r['cells']) for t in data['tables'] for r in t['rows']):,} observations")
