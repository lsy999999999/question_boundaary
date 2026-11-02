"""Actor-requested global alignment; exact blocks are sequence evidence, not structure."""
import difflib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from coordinator import save,event

def align(a,b):
    n,m=len(a),len(b)
    score=[[0]*(m+1) for _ in range(n+1)]
    back=[[None]*(m+1) for _ in range(n+1)]
    for i in range(1,n+1):score[i][0]=-2*i;back[i][0]='D'
    for j in range(1,m+1):score[0][j]=-2*j;back[0][j]='I'
    for i in range(1,n+1):
        for j in range(1,m+1):
            opts=[(score[i-1][j-1]+(2 if a[i-1]==b[j-1] else -1),'=' if a[i-1]==b[j-1] else 'X'),(score[i-1][j]-2,'D'),(score[i][j-1]-2,'I')]
            score[i][j],back[i][j]=max(opts,key=lambda x:x[0])
    i,j=n,m;cols=[]
    while i or j:
        op=back[i][j]
        if op in ['=','X']:cols.append((op,i,j,a[i-1],b[j-1]));i-=1;j-=1
        elif op=='D':cols.append((op,i,None,a[i-1],'-'));i-=1
        else:cols.append((op,None,j,'-',b[j-1]));j-=1
    cols.reverse(); edits=[]
    for c in cols:
        if c[0]=='=':continue
        if edits and edits[-1]['op']==c[0] and edits[-1]['last_alignment_column']==cols.index(c)-1:
            # Coordinates can repeat under gaps; use explicit grouped segments below instead.
            pass
    edits=[];start=0
    while start<len(cols):
        end=start+1
        while end<len(cols) and cols[end][0]==cols[start][0]:end+=1
        sub=cols[start:end]
        if sub[0][0]!='=':
            ri=[x[1] for x in sub if x[1] is not None];vi=[x[2] for x in sub if x[2] is not None]
            edits.append(dict(op=sub[0][0],reference_span_1based=[min(ri),max(ri)] if ri else None,variant_span_1based=[min(vi),max(vi)] if vi else None,reference=''.join(x[3] for x in sub),variant=''.join(x[4] for x in sub)))
        start=end
    return dict(score=score[n][m],counts={op:sum(c[0]==op for c in cols) for op in ['=','X','I','D']},edit_segments=edits,reference_aligned=''.join(c[3] for c in cols),variant_aligned=''.join(c[4] for c in cols))

def main():
    data=json.loads((ROOT/'agent_visible/sequence_measurements.json').read_text());ref=data['reference_sequence']
    rows=[]
    for row in data['other_reads']:
        b=row['sequence'];rc=b.translate(str.maketrans('ACGT','TGCA'))[::-1]
        blocks={}
        for orientation,seq in [('forward',b),('reverse_complement',rc)]:
            blocks[orientation]=[dict(reference_start_1based=x.a+1,variant_oriented_start_1based=x.b+1,length=x.size) for x in difflib.SequenceMatcher(None,ref,seq,autojunk=False).get_matching_blocks() if x.size>=15]
        rows.append(dict(length_nt=len(b),read_fraction=row['read_fraction'],global_alignment=align(ref,b),non_exhaustive_exact_blocks=blocks))
    result=dict(compute_id='C01',request_source='transcripts/researcher_01.md',reference_length_nt=len(ref),frequency_sum=data['reference_read_fraction']+sum(x['read_fraction'] for x in data['other_reads']),method='Needleman-Wunsch global alignment, match=2 mismatch=-1 gap=-2; one optimal traceback, ties resolved diagonal then deletion then insertion. difflib exact blocks >=15 bases in two orientations are non-exhaustive candidates.',rows=rows,limits=['Alignment is not unique in repeated/rearranged sequence and does not establish mutation events.','No arm-domain coordinates or folding annotations were supplied; physical arm/functional-unit annotation is unavailable. No author interpretation was added.','DNA read frequency is not RNA production or active-valence frequency.'])
    save(ROOT/'computations/C01_result.json',result)
    event('computation_completed',dict(compute_id='C01',request='transcripts/researcher_01.md',script='computations/c01_sequence_alignment.py',result='computations/C01_result.json',budget_unit=1))
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},ensure_ascii=False))
    print(json.dumps([dict(length=x['length_nt'],counts=x['global_alignment']['counts'],blocks=x['non_exhaustive_exact_blocks']) for x in rows],ensure_ascii=False))

if __name__=='__main__':main()
