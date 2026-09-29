# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 KK4TSS
"""Callsign Badger — standalone Badgeware v3 app."""
import time
from cb_config import load, ConfigError, clone
from cb_state import Controls
from cb_saved import Saved
from cb_hf import open_hf
from cb_morse import Morse
from cb_battery import Indicator
from cb_view import View
from cb_qr import payload, matrix

view=View(screen,font,image,color,vec2)
saved=Saved()
battery=Indicator()
morse=Morse(badge,time)
errors=[];error_index=0;dirty=True;detail_count=1
last_input=time.ticks_ms();last_detail=last_input
cached_payload=None;cached_qr=None
notice=None

try:
    profiles,initial=load()
    # Reject excessive destinations before showing any personal details.
    for profile in profiles:
        if len(payload(profile['settings']).encode('utf-8'))>120:
            raise ConfigError(['profiles.'+profile['id']+'.qr: destination exceeds 120 bytes',
                               'Shorten the URL/contact fields or link to a contact page'])
    controls=Controls(profiles,initial,time.ticks_diff)
    saved.restore(controls)
    morse.configure(controls.current['settings'])
except ConfigError as e:
    errors=e.errors


def configure_morse():
    settings=clone(controls.current['settings'])
    # Privacy must not leak hidden contact information through a custom message.
    if controls.private:settings['morse']['message']=''
    morse.configure(settings)


if not errors:configure_morse()


def update():
    global dirty,last_input,last_detail,detail_count,error_index,cached_payload,cached_qr,errors,notice
    badge.poll();now=time.ticks_ms()
    if badge.pressed():
        last_input=now
        if notice:notice=None;dirty=True
    if errors:
        if badge.pressed(BUTTON_UP):error_index=(error_index+1)%len(errors);dirty=True
        elif badge.pressed(BUTTON_DOWN):error_index=(error_index-1)%len(errors);dirty=True
        if dirty:view.error(errors,error_index);badge.update();dirty=False
        if time.ticks_diff(now,last_input)>=30000 and not badge.usb_connected():
            morse.stop();badge.sleep();last_input=time.ticks_ms()
        time.sleep_ms(20)
        return

    pressed=set()
    for name,key in (('A',BUTTON_A),('B',BUTTON_B),('C',BUTTON_C),('UP',BUTTON_UP),('DOWN',BUTTON_DOWN)):
        if badge.pressed(key):pressed.add(name)
    down=badge.pressed(BUTTON_DOWN) or badge.held(BUTTON_DOWN)
    c_held=badge.pressed(BUTTON_C) or badge.held(BUTTON_C)
    b_held=badge.pressed(BUTTON_B) or badge.held(BUTTON_B)
    events=controls.update(now,pressed,down,c_held,b_held)
    if 'hf' in events:
        morse.stop();saved.save(controls)
        notice=open_hf(State,file_exists,reset);dirty=True
    if 'profile' in events or 'privacy' in events:
        configure_morse();last_detail=now
    if 'draw' in events:
        dirty=True;saved.save(controls)
    if 'morse' in events:morse.toggle(now);dirty=True
    cfg=controls.current['settings']
    if battery.update(badge,now,time.ticks_diff) and cfg['display']['show_battery']:dirty=True
    if detail_count>1 and time.ticks_diff(now,last_detail)>=cfg['display']['details_seconds']*1000:
        controls.detail=(controls.detail+1)%detail_count;dirty=True

    if dirty:
        resume=morse.enabled;morse.stop()
        try:
            key=payload(cfg)
            if key!=cached_payload:
                cached_qr=matrix(cfg);cached_payload=key
            if notice:
                view.notice(notice);detail_count=1
            elif controls.qr_view:
                detail_count=view.full_qr(controls.current,controls.private,cached_qr)
            else:detail_count=view.draw(controls.current,controls.design,controls.private,
                                  controls.detail,cached_qr,battery,resume)
            badge.update();dirty=False;last_detail=time.ticks_ms()
        except ConfigError as e:
            errors=e.errors;error_index=0;dirty=True;return
        if resume:morse.start(time.ticks_ms())
    now=time.ticks_ms();morse.tick(now)
    # Do not fall asleep before optional information has cycled through.
    sleep_after=max(30000,detail_count*cfg['display']['details_seconds']*1000+1000)
    if not morse.enabled and not down and not c_held and not b_held and time.ticks_diff(now,last_input)>=sleep_after and not badge.usb_connected():
        morse.stop();badge.sleep();last_input=time.ticks_ms()
    time.sleep_ms(10)


def on_exit():morse.stop()


try:
    run(update)
finally:
    on_exit()
