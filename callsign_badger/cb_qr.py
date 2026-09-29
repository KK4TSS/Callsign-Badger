# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 KK4TSS
"""Offline QR destinations and bounded on-device encoding."""
from cb_config import ConfigError


def escape(text):
    return text.replace('\\','\\\\').replace(';','\\;').replace(':','\\:').replace(',','\\,')


def payload(settings):
    q=settings['qr'];kind=q['type']
    if kind=='none':return ''
    if kind=='qrz':return 'https://www.qrz.com/db/'+settings['callsign'].replace('/','%2F')
    if kind=='url':return q['url']
    value='MECARD:N:'+escape(settings['name'] or settings['callsign'])+';'
    for key,tag in (('phone','TEL'),('email','EMAIL')):
        if q['contact'][key]:value+=tag+':'+escape(q['contact'][key])+';'
    return value+'NOTE:'+escape(settings['callsign'])+';;'


def matrix(settings):
    value=payload(settings)
    if not value:return None
    if len(value.encode('utf-8'))>120:
        raise ConfigError(['qr: destination exceeds 120 bytes','Shorten the URL/contact fields or use a contact-page URL'])
    from cb_uqr import QRCode, ERROR_CORRECT_M
    qr=QRCode(error_correction=ERROR_CORRECT_M,border=4)
    qr.add_data(value.encode('utf-8'),optimize=0)
    qr.make(fit=True)
    result=qr.get_matrix()
    if len(result)>53:raise ConfigError(['qr: too dense for this display; use a shorter destination'])
    return result
