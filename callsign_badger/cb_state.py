# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 KK4TSS
"""Button semantics independent of firmware and drawing."""
class Controls:
    HOLD_MS=800
    def __init__(self,profiles,start,ticks_diff):
        self.profiles=profiles;self.profile=start;self.diff=ticks_diff
        self.design=profiles[start]['settings']['display']['design']
        self.private=profiles[start]['settings']['privacy']['start_enabled']
        self.down_at=None;self.consumed=False;self.detail=0
        self.qr_view=False;self.c_at=None;self.c_consumed=False
        self.b_at=None;self.b_consumed=False

    @property
    def current(self):return self.profiles[self.profile]

    def update(self,now,pressed,down,c_held=False,b_held=False):
        events=[]
        for key in ('A','B','C'):
            if key in pressed and (key!=self.design or self.qr_view):
                self.design=key;self.detail=0;self.qr_view=False;events.append('draw')
        if 'C' in pressed:self.c_at=now;self.c_consumed=False
        if c_held and self.c_at is not None and not self.c_consumed and self.diff(now,self.c_at)>=self.HOLD_MS:
            self.c_consumed=True
            cfg=self.current['settings']
            if cfg['qr']['type']!='none' and not (self.private and cfg['privacy']['hide_qr']):
                self.qr_view=True;events.append('draw')
        if not c_held:self.c_at=None
        if 'DOWN' in pressed:
            self.down_at=now;self.consumed=False
        if down and self.down_at is not None and not self.consumed and self.diff(now,self.down_at)>=self.HOLD_MS:
            self.private=not self.private;self.qr_view=False;self.detail=0;self.consumed=True
            events.extend(('privacy','draw'))
        if not down and self.down_at is not None:
            if not self.consumed:
                if self.current['settings']['hf_propagation']:events.append('hf')
                else:self.next_profile();events.extend(('profile','draw'))
            self.down_at=None;self.consumed=False
        if 'B' in pressed:self.b_at=now;self.b_consumed=False
        if b_held and self.b_at is not None and not self.b_consumed and self.diff(now,self.b_at)>=self.HOLD_MS:
            self.b_consumed=True
            if self.current['settings']['hf_propagation']:
                self.next_profile();events.extend(('profile','draw'))
        if not b_held:self.b_at=None
        if 'UP' in pressed:events.append('morse')
        return events

    def next_profile(self):
        self.qr_view=False
        self.profile=(self.profile+1)%len(self.profiles)
        self.design=self.current['settings']['display']['design']
        self.detail=0
