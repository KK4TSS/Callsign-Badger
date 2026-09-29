# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 KK4TSS
"""Small, versioned state file; only changed selections are written."""
import json
import os

class Saved:
    def __init__(self,path='state.json'):
        self.path=path;self.previous=None

    def snapshot(self,c):
        return {'version':1,'profile':c.current['id'],'design':c.design,
                'private':c.private,'qr_view':c.qr_view}

    def restore(self,c):
        if not c.current['settings']['display']['remember_last']:return
        try:
            with open(self.path) as f:s=json.loads(f.read(1025))
            if not isinstance(s,dict) or s.get('version')!=1:return
            index=next((i for i,p in enumerate(c.profiles) if p['id']==s.get('profile')),None)
            if index is None or s.get('design') not in ('A','B','C'):return
            if type(s.get('private')) is not bool or type(s.get('qr_view')) is not bool:return
            if not c.profiles[index]['settings']['display']['remember_last']:return
            c.profile=index;c.design=s['design']
            cfg=c.current['settings']
            c.private=s['private'] or cfg['privacy']['start_enabled']
            c.qr_view=s['qr_view'] and cfg['qr']['type']!='none' and not (c.private and cfg['privacy']['hide_qr'])
        except (OSError,ValueError):pass
        self.previous=self.snapshot(c)

    def save(self,c):
        if not c.current['settings']['display']['remember_last']:
            try:os.remove(self.path)
            except OSError:pass
            self.previous=None;return
        state=self.snapshot(c)
        if state==self.previous:return
        try:
            with open(self.path+'.tmp','w') as f:json.dump(state,f)
            os.rename(self.path+'.tmp',self.path)
            self.previous=state
        except OSError:pass  # A read-only/full disk must not stop the badge.
