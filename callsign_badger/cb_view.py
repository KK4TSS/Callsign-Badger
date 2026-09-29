# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 KK4TSS
"""Three responsive layouts; uses native antialiased vector text."""
from cb_config import ConfigError

def visible_fields(settings,private):
    p=settings['privacy']
    hide_name=private and p['hide_name'];hide_location=private and p['hide_location']
    fields=[]
    if settings['name'] and not hide_name:fields.append((settings['name'],18))
    for key in ('event_message','location','grid','club','pronouns','license_class','event_role','find_me'):
        if not settings[key]:continue
        if key in ('location','grid') and hide_location:continue
        if key=='pronouns' and hide_name:continue
        prefix={'license_class':'Class: ','find_me':'On: '}.get(key,'')
        fields.append((prefix+settings[key],15))
    return fields


def wrap(text,width,size,measure):
    lines=[];line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if measure(candidate,size)[0]<=width:line=candidate;continue
        if line:lines.append(line);line=''
        for c in word:
            if line and measure(line+c,size)[0]>width:lines.append(line);line=''
            line+=c
    if line:lines.append(line)
    return lines


def paginate(fields,width,measure,height=99):
    pages=[[]];used=0
    for text,size in fields:
        for line in wrap(text,width,size,measure):
            line_height=max(size+3,int(measure(line,size)[1])+2)
            if used+line_height>height and pages[-1]:pages.append([]);used=0
            pages[-1].append((line,size,used));used+=line_height
    return pages


class View:
    def __init__(self,screen,font_api,image_api,palette,point=None):
        self.screen=screen;self.color=palette;self.font_api=font_api
        self.face=font_api.load('assets/MonaSans-SemiBold.af')
        self.screen.font=self.face;self.screen.antialias=image_api.X4
        self._pages_key=None;self._pages=None
        self.image=image_api;self.point=point;self.logo_path=None;self.logo=None

    def measure(self,text,size):return self.screen.measure_text(text,font_size=size)

    def text(self,text,x,y,size=12):self.screen.text(text,x,y,font_size=size)

    def fitted(self,text,x,y,width,size=42,minimum=8,center=False):
        while size>minimum and self.measure(text,size)[0]>width:size-=1
        if center:x+=max(0,(width-self.measure(text,size)[0])/2)
        self.text(text,int(x),y,size)

    def draw(self,profile,design,private,detail,qr,battery,morse=False):
        s=self.screen;c=self.color;cfg=profile['settings']
        theme=cfg['display']['theme']
        dark=theme=='dark' or (theme=='auto' and design=='C')
        bg=c.black if dark else c.white;fg=c.white if dark else c.black
        s.font=self.face;s.pen=bg;s.clear()
        band=(design=='A')
        header_fg=bg if band else fg;header_bg=fg if band else bg
        if band:s.pen=header_bg;s.rectangle(0,0,264,51)
        s.pen=header_fg
        # Reserved battery area is never used by profile text.
        self.fitted(profile['label'],8,1,204,11,8)
        self.fitted(cfg['callsign'],8,14,248,36,8,True)
        s.pen=fg
        if design=='B':s.rectangle(8,50,248,1)
        show_qr=qr is not None and not (private and cfg['privacy']['hide_qr'])
        text_x=120 if design=='B' and show_qr else 8
        text_width=136 if show_qr else 248
        fields=visible_fields(cfg,private)
        body_y=55;body_height=99
        if cfg['logo']:
            if self.logo_path!=cfg['logo']:
                try:self.logo=self.image.load(cfg['logo'],32,32)
                except (OSError,ValueError,RuntimeError):
                    raise ConfigError(['logo: cannot load '+cfg['logo'],'Use a valid PNG inside assets/'])
                self.logo_path=cfg['logo']
            s.pen=c.white;s.rectangle(text_x,55,32,32)
            s.blit(self.logo,self.point(text_x,55));s.pen=fg
            body_y=91;body_height=63
        key=(tuple(fields),text_width,body_height)
        if key!=self._pages_key:
            self._pages=paginate(fields,text_width,self.measure,body_height);self._pages_key=key
        pages=self._pages
        detail%=len(pages)
        for text,size,offset in pages[detail]:self.text(text,text_x,body_y+offset,size)
        if show_qr:
            count=len(qr);scale=min(3,106//count);side=count*scale
            x=(6 if design=='B' else 152)+(106-side)//2
            y=52+(106-side)//2
            self.qr(qr,x,y,scale)
        s.pen=fg;s.rectangle(8,158,248,1)
        footer=('PRIVATE' if private else 'CALLSIGN BADGER')
        if morse:footer+=' / CW'
        if len(pages)>1:footer+='  %d/%d'%(detail+1,len(pages))
        self.fitted(footer,8,160,248,13,11)
        if cfg['display']['show_battery']:
            battery.draw(s,c,inverted=(not dark if band else dark))
        return len(pages)

    def qr(self,qr,x,y,scale):
        s=self.screen;c=self.color;count=len(qr)
        s.pen=c.white;s.rectangle(x,y,count*scale,count*scale)
        s.pen=c.black
        for row,bits in enumerate(qr):
            start=None
            for col in range(count+1):
                on=col<count and bits[col]
                if on and start is None:start=col
                if not on and start is not None:
                    s.rectangle(x+start*scale,y+row*scale,(col-start)*scale,scale)
                    start=None

    def full_qr(self,profile,private,qr):
        cfg=profile['settings'];s=self.screen;c=self.color
        s.font=self.face;s.pen=c.white;s.clear();s.pen=c.black
        if qr is None or (private and cfg['privacy']['hide_qr']):
            self.text('QR hidden',8,65,24)
        else:
            scale=176//len(qr);side=len(qr)*scale
            self.qr(qr,(264-side)//2,(176-side)//2,scale)
        return 1

    def notice(self,message):
        s=self.screen;s.font=self.face;s.pen=self.color.white;s.clear();s.pen=self.color.black
        self.text('HF PROPAGATION',8,12,22)
        for i,line in enumerate(wrap(message,248,18,self.measure)):
            self.text(line,8,55+i*22,18)
        self.text('Press a button to return',8,151,15)

    def error(self,errors,index=0):
        s=self.screen;c=self.color;s.font=self.face;s.pen=c.white;s.clear();s.pen=c.black
        self.text('CHECK CONFIG.JSON',8,7,20)
        message=errors[index%len(errors)]
        lines=wrap(message,248,14,self.measure)
        for i,line in enumerate(lines[:6]):self.text(line,8,39+i*17,14)
        self.text('Error %d/%d | UP/DOWN: more'%(index+1,len(errors)),8,149,10)
        self.text('Edit file, eject disk, reopen app.',8,163,10)
