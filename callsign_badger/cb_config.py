# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 KK4TSS
"""Validated JSON settings. No desktop build or network required."""
import json

FIELDS = ('callsign', 'name', 'location', 'grid', 'club', 'pronouns', 'license_class', 'event_role', 'find_me', 'event_message')
DEFAULTS = {
 'callsign':'N0CALL', 'name':'Your Name', 'location':'', 'grid':'', 'club':'',
 'pronouns':'', 'license_class':'', 'event_role':'', 'find_me':'', 'event_message':'', 'logo':'',
 'hf_propagation':False,
 'qr':{'type':'qrz','url':'','contact':{'phone':'','email':''}},
 'display':{'design':'A','theme':'auto','show_battery':True,'details_seconds':12,'remember_last':True},
 'morse':{'wpm':10,'brightness':90,'message':''},
 'privacy':{'hide_name':True,'hide_location':True,'hide_qr':True,'start_enabled':False}
}

class ConfigError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('; '.join(errors))


def clone(value):
    if isinstance(value,dict): return {k:clone(v) for k,v in value.items()}
    if isinstance(value,list): return [clone(v) for v in value]
    return value


def merge(base, override):
    out = clone(base)
    for k,v in override.items():
        out[k] = merge(out[k],v) if k in out and isinstance(out[k],dict) and isinstance(v,dict) else clone(v)
    return out


def validate(raw):
    errors=[]
    def fail(path,msg): errors.append(path + ': ' + msg)
    if not isinstance(raw,dict): raise ConfigError(['config.json: expected a JSON object'])
    root_keys=set(DEFAULTS)|{'profiles','default_profile'}
    for key in raw:
        if key not in root_keys:fail(key,'unknown setting')

    def settings(value,path,partial=False):
        if not isinstance(value,dict):
            fail(path,'expected an object');return clone(DEFAULTS)
        for key in value:
            if key not in DEFAULTS:fail(path+key,'unknown setting')
        out=merge(DEFAULTS,value)
        for key in FIELDS:
            v=out[key]
            if not isinstance(v,str):fail(path+key,'use text in double quotes');continue
            v=v.strip();out[key]=v
            limit=16 if key=='callsign' else 80
            if len(v)>limit:fail(path+key,'maximum %d characters'%limit)
            if any(ord(c)<32 or ord(c)>126 for c in v):fail(path+key,'use printable ASCII letters/numbers')
        if type(out['hf_propagation']) is not bool:fail(path+'hf_propagation','use true or false')
        logo=out['logo']
        if not isinstance(logo,str) or (logo and (not logo.startswith('assets/') or not logo.endswith('.png') or any(part in ('','..','.') for part in logo.split('/')) or '\\' in logo)):
            fail(path+'logo','use an assets/filename.png path, or empty text')
        call=out['callsign']
        if isinstance(call,str):
            out['callsign']=call.upper()
            if not call or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/' for c in call.upper()):fail(path+'callsign','use letters, numbers and /')
        for section in ('qr','display','morse','privacy'):
            obj=out[section]
            if not isinstance(obj,dict):fail(path+section,'expected an object');out[section]=clone(DEFAULTS[section]);continue
            for key in obj:
                if key not in DEFAULTS[section]:fail(path+section+'.'+key,'unknown setting')
        q,d,m,p=out['qr'],out['display'],out['morse'],out['privacy']
        for key,choices,obj in [('type',('qrz','url','contact','none'),q),('design',('A','B','C'),d),('theme',('auto','light','dark'),d)]:
            if obj[key] not in choices:fail(path+('qr.' if obj is q else 'display.')+key,'choose '+', '.join(choices))
        for key in ('show_battery','remember_last'):
            if type(d[key]) is not bool:fail(path+'display.'+key,'use true or false')
        for key in DEFAULTS['privacy']:
            if type(p[key]) is not bool:fail(path+'privacy.'+key,'use true or false')
        for obj,section,key,lo,hi in [(m,'morse','wpm',5,30),(m,'morse','brightness',1,100),(d,'display','details_seconds',5,60)]:
            if type(obj[key]) is not int or not lo<=obj[key]<=hi:fail(path+section+'.'+key,'use an integer %d-%d'%(lo,hi))
        msg=m['message']
        if not isinstance(msg,str) or len(msg)>80 or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 /?.,=-' for c in msg.upper()):fail(path+'morse.message','up to 80 Morse letters, digits, spaces or /?.,=-')
        else:m['message']=msg.upper().strip()
        if not isinstance(q['url'],str):fail(path+'qr.url','expected text')
        elif q['type']=='url' and (not q['url'].startswith(('https://','http://')) or any(c.isspace() for c in q['url'])):fail(path+'qr.url','use a complete http:// or https:// URL without spaces')
        contact=q['contact']
        if not isinstance(contact,dict):fail(path+'qr.contact','expected an object');q['contact']=clone(DEFAULTS['qr']['contact'])
        else:
            for key in contact:
                if key not in ('phone','email'):fail(path+'qr.contact.'+key,'unknown setting')
            for key in ('phone','email'):
                v=contact[key]
                if not isinstance(v,str) or len(v)>80 or any(ord(c)<32 or ord(c)>126 for c in v):fail(path+'qr.contact.'+key,'use up to 80 printable ASCII characters')
        return out

    base=settings({k:v for k,v in raw.items() if k in DEFAULTS},'')
    entries=raw.get('profiles',[{'id':'default','label':'Everyday','overrides':{}}])
    profiles=[]
    if not isinstance(entries,list) or not 1<=len(entries)<=8:
        fail('profiles','use a list of 1-8 profiles');entries=[]
    ids=set()
    for i,entry in enumerate(entries):
        path='profiles[%d].'%i
        if not isinstance(entry,dict):fail(path,'expected an object');continue
        for key in entry:
            if key not in ('id','label','overrides'):fail(path+key,'unknown setting')
        ident=entry.get('id','');label=entry.get('label',ident)
        if not isinstance(ident,str) or not ident or len(ident)>24 or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in ident):fail(path+'id','use 1-24 lowercase letters/digits/_/-');ident='invalid%d'%i
        if ident in ids:fail(path+'id','must be unique')
        ids.add(ident)
        if not isinstance(label,str) or not label or len(label)>24 or any(ord(c)<32 or ord(c)>126 for c in label):fail(path+'label','use 1-24 printable characters');label=ident
        override=entry.get('overrides',{})
        if not isinstance(override,dict):fail(path+'overrides','expected an object');override={}
        value=settings(merge(base,override),path+'overrides.')
        profiles.append({'id':ident,'label':label,'settings':value})
    default=raw.get('default_profile',profiles[0]['id'] if profiles else '')
    if not isinstance(default,str) or default not in ids:fail('default_profile','must match a profile id')
    if errors:raise ConfigError(errors)
    return profiles, next(i for i,p in enumerate(profiles) if p['id']==default)


def load(path='config.json'):
    try:
        with open(path) as f:
            text=f.read(16385)
    except OSError:raise ConfigError(['config.json: missing; copy the supplied example'])
    if len(text)>16384:raise ConfigError(['config.json: maximum size is 16 KB'])
    try:raw=json.loads(text)
    except ValueError:raise ConfigError(['config.json: invalid JSON; check commas and double quotes','No trailing commas or comments are allowed'])
    return validate(raw)
