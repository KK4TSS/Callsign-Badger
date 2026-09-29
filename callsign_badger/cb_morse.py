# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 KK4TSS
"""Nonblocking Morse transmitter for the four monochrome case lights."""
CODES=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
('.-','-...','-.-.','-..','.','..-.','--.','....','..','.---','-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-','..-','...-','.--','-..-','-.--','--..','-----','.----','..---','...--','....-','.....','-....','--...','---..','----.')))
CODES.update({'/':'-..-.','?':'..--..','.':'.-.-.-',',':'--..--','=':'-...-','-':'-....-'})


def sequence(message):
    steps=[]
    words=message.upper().split()
    for wi,word in enumerate(words):
        for ci,c in enumerate(word):
            code=CODES[c]
            for si,symbol in enumerate(code):
                steps.append((True,3 if symbol=='-' else 1))
                if si<len(code)-1:steps.append((False,1))
            steps.append((False,7 if ci==len(word)-1 else 3))
    return steps


class Morse:
    def __init__(self,badge,clock):
        self.badge=badge;self.clock=clock;self.enabled=False;self.steps=[]
        self.stop()

    def configure(self,settings):
        self.stop()
        self.steps=sequence(settings['morse']['message'] or settings['callsign'])
        self.unit=round(1200/settings['morse']['wpm'])
        self.brightness=settings['morse']['brightness']/100

    def stop(self):
        self.enabled=False;self.badge.caselights(0)

    def start(self,now):
        if not self.steps:return
        self.enabled=True;self.index=0;self.show(now)

    def toggle(self,now):
        if self.enabled:self.stop()
        else:self.start(now)

    def show(self,now):
        on,units=self.steps[self.index]
        self.badge.caselights(self.brightness if on else 0)
        self.deadline=self.clock.ticks_add(now,units*self.unit)

    def tick(self,now):
        if self.enabled and self.clock.ticks_diff(now,self.deadline)>=0:
            self.index=(self.index+1)%len(self.steps);self.show(now)
