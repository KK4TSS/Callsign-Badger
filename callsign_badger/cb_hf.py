# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 KK4TSS
"""Optional HF Propagation launcher handoff."""
def open_hf(state,file_exists,reset):
    destination='/system/apps/hf_propagation'
    try:
        if not (file_exists(destination+'/__init__.py') or file_exists(destination+'/__init__.mpy')):
            return 'Install HF Propagation first'
        menu={'active':0}
        state.load('menu',menu)
        menu['running']=destination
        state.modify('menu',menu)
        persisted={}
        state.load('menu',persisted)
        if persisted.get('running')!=destination:return 'Could not open HF - retry'
        reset()
    except OSError:
        return 'Could not open HF - retry'
    return None
