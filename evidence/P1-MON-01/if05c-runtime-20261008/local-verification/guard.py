def patch_for(original,current,candidate,restore=False):
    assert current['metadata']['uid']==original['metadata']['uid'],'FOREIGN_UID'
    before=original['data'];after=candidate
    wanted=before if restore else after
    if restore and current['data']==before:return []
    assert current['data']==(after if restore else before),'FOREIGN_DATA'
    return [{'op':'test','path':'/metadata/uid','value':current['metadata']['uid']},
            {'op':'test','path':'/metadata/resourceVersion','value':current['metadata']['resourceVersion']},
            {'op':'test','path':'/data','value':current['data']},
            {'op':'replace','path':'/data','value':wanted}]
