def corroborate(case,result,before,after):
    def counts(lines):return {l.split('] ',1)[1]:int(l[1:].split(':')[0]) for l in lines}
    a,b=counts(before),counts(after)
    if set(a)!=set(b):return False
    drops=sum(b[k]-a[k] for k in a if k.endswith(' -j DROP'))
    if case['expect']!='BLOCKED':return result['actual']==case['expect'] and (result['actual']!='DNS_REPLY' or result.get('rcode')==0)
    if result.get('bound')!=[case['source_ip'],case['source_port']]:return False
    if result['actual']=='EPERM':return result.get('errno')==1 and result.get('stage') in ('send','connect') and drops>=1
    if result['actual']=='TIMEOUT':return result.get('stage') in ('recv','connect') and drops>=1
    return False
