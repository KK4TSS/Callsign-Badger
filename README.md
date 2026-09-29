# Callsign Badger 1.0

A standalone, configurable ham-radio badge for **Pimoroni Badger 2350** running
**Badgeware v3**. Edit one JSON file on the badge. Badge designs and QR codes
work offline without a QRZ account.

Three designs, event profiles, optional identity fields, QR links/contact cards,
Morse callsign lighting, a battery indicator, and a quick privacy mode.

## Install and personalize

1. Download and unzip the version 1.0 release or repository source on your computer.
2. Connect Badger 2350 using a USB data cable. Double-tap **RESET**.
3. Copy the entire **callsign_badger** directory into **apps** on the Badger disk.
4. Open `apps/callsign_badger/config.json` in a plain-text editor.
5. Replace `N0CALL`, `Your Name`, and `Your Town` with your details. Leave any
   unwanted optional field as `""`. Save as UTF-8 plain text.
6. Safely eject the disk and open **Callsign Badger** in the launcher.

The supplied configuration uses placeholder identity fields and has the optional
HF Propagation shortcut disabled. Personalize the file on your device.

After editing settings, eject and reopen the app. To update the software later,
back up your `config.json` and retain it instead of replacing it with the sample.
Keep the `assets` and `licenses` folders with the app.

## Controls

| Button | Action |
| --- | --- |
| A / B / C | Select a badge design |
| Hold C for 0.8 seconds | Full-screen QR; A, B, or C returns to a badge design |
| Up | Toggle Morse lighting |
| Tap Down, then release | Next event profile |
| Hold Down for 0.8 seconds | Toggle privacy; release does not change profile |
| Home | Return to the Badgeware launcher; lights turn off |

Profile, design, privacy, and the full-screen QR selection are remembered in
`state.json`. Morse always starts off. Set `display.remember_last` to false to
use the configured starting profile/design instead. Delete `state.json` to reset
saved selections. A removed saved profile falls back to the configured default.
`privacy.start_enabled: true` always takes precedence over saved privacy.

## Your fields

The top-level `callsign`, `name`, `location`, `grid`, `club`, `pronouns`,
`license_class`, `event_role`, and `find_me` apply to all profiles unless overridden.

- Callsigns are normalized to uppercase; up to 16 letters/digits/slashes.
- Optional fields accept up to 80 characters. Blank fields disappear.
- `find_me` can contain a monitoring frequency, repeater, AllStar node, or other
  contact information; the screen prefixes it with `On:`.
- This first version accepts printable ASCII identity text. For accented names,
  use an ASCII spelling for now; unsupported characters produce a clear error.
- Callsigns fit to the available width. Long details wrap without clipping.
  Overflow information cycles through additional panels every `details_seconds`.
  A panel counter appears at the bottom, while the callsign and QR stay visible.

## Configuration reference

Omitted settings use defaults; existing configuration files remain compatible. JSON uses double quotes and lowercase
`true` / `false`; it does not allow comments or trailing commas.

```json
{
  "hf_propagation": false,
  "logo": "",
  "event_message": "",
  "callsign": "N0CALL",
  "name": "Your Name",
  "location": "Your Town",
  "grid": "AA00aa",
  "club": "Example Radio Club",
  "pronouns": "",
  "license_class": "",
  "event_role": "Volunteer",
  "find_me": "AllStar node 12345",
  "qr": {"type": "qrz"},
  "display": {"design": "A", "theme": "auto", "show_battery": true, "details_seconds": 12, "remember_last": true},
  "morse": {"wpm": 10, "brightness": 90, "message": ""},
  "privacy": {"hide_name": true, "hide_location": true, "hide_qr": true, "start_enabled": false},
  "default_profile": "hamfest",
  "profiles": [
    {"id": "hamfest", "label": "Hamfest", "overrides": {}},
    {"id": "pota", "label": "POTA", "overrides": {"event_role": "POTA Operator", "display": {"design": "B"}}},
    {"id": "club", "label": "Club Meeting", "overrides": {"display": {"design": "C"}}}
  ]
}
```

### Profiles

Define 1–8 profiles. Each has a unique lowercase `id`, a short `label`, and an
`overrides` object. Nested overrides merge with the shared settings: setting only
`display.design` retains your battery and theme preferences. An override of `""`
removes that field in that profile. `default_profile` must match an existing id.
When no profiles are supplied, the app creates a single Everyday profile.

### QR destination

- `{"type": "qrz"}`: automatically links to `https://www.qrz.com/db/YOURCALL`.
- `{"type": "url", "url": "https://example.org/club"}`: a club or contact-page URL.
- `{"type": "contact", "contact": {"phone": "", "email": ""}}`:
  an offline **MECARD** contact containing the configured name/callsign and any
  nonblank phone/email. Camera/contact support varies by phone.
- `{"type": "none"}`: no QR; text uses the full display width.

QR contents are limited to **120 encoded bytes** to keep modules readable on this
small display. An oversized contact or URL produces a setting error; shorten it
or link to a contact page. Codes use medium error correction, integer pixel sizes,
and the full four-module white quiet zone. The badge makes them locally.
A phone needs internet to open web destinations; contact cards do not.

### Display

`design`: `A`, `B`, or `C`. `theme`: `auto`, `light`, or `dark`.
Auto gives A a contrasting header, B a light minimal layout, and C a dark layout.
`show_battery`: boolean. `details_seconds`: integer 5–60 (default 12).

Smooth vector text uses the bundled, open-licensed Mona Sans SemiBold font. The battery
icon uses the device's approximate voltage-based estimate, with a charging mark.
It checks once per minute while awake and redraws only if the indicator changes.

### Morse

`wpm`: 5–30. `brightness`: 1–100 percent. Empty `message` flashes the callsign.
A custom message may contain A–Z, 0–9, spaces, and `/ ? . , = -` (maximum 80
characters). All four monochrome rear-light zones flash together; they are not RGB.
Spacing is 1 unit within letters, 3 between letters, and 7 between words/repeats.

Page redraws pause the lights and restart the message afterward so the blocking
e-paper refresh does not stretch a dot into a dash. Changing profiles, toggling
privacy, or leaving the app stops Morse. Up can restart it.

### Privacy

`hide_name` hides the name and pronouns. `hide_location` hides location and grid.
`hide_qr` defaults to true so the link/contact does not reveal the hidden identity.
Callsign, club, class, event role, and `find_me` remain visible; avoid putting
private details in those fields. This is a display convenience, not anonymity:
a visible callsign can still be looked up publicly.

Privacy stays on when switching profiles until explicitly toggled off. Custom
Morse messages are replaced by the callsign while privacy is enabled.
`start_enabled` can force privacy on at launch, including a remembered screen.

## Configuration errors

A readable error screen identifies the setting that needs fixing. Up/Down cycle
through multiple errors. Edit `config.json`, eject the disk, and reopen the app.
Malformed JSON, wrong value types, unknown keys, duplicate profile IDs, missing
files, and excessive QR contents are handled without displaying stale identity
information. File size limit: 16 KB.

## Battery and sleep

Morse keeps the badge awake. With Morse off, the app sleeps on battery after
30 seconds without input, or after enough time to display one complete overflow
cycle. E-paper retains the last image. The battery icon is not live while asleep.
Use the device's normal wake control. USB power keeps the app awake.

## Licensing and sources

Original Callsign Badger code: **GNU General Public License version 3 only**
(`GPL-3.0-only`; see `LICENSE`). Copyright (c) 2026 KK4TSS.
Vendored uQR: BSD/MIT notices in `callsign_badger/licenses/uQR.txt`.
Mona Sans font: SIL OFL 1.1 in `callsign_badger/licenses/MonaSans-OFL.txt`.
See `THIRD_PARTY.md` for provenance. This project is not affiliated with Pimoroni
or QRZ.

- [Badger 2350 / Badgeware](https://github.com/pimoroni/badger2350)
- [Badgeware image/text API](https://github.com/pimoroni/badgeware-docs/blob/main/api/image.md)
- [uQR](https://github.com/JASchilz/uQR)
- [Mona Sans](https://github.com/github/mona-sans)

## Club logo and event message

Add these optional settings at the top level or inside any profile's `overrides`:

```json
"logo": "assets/club-logo.png",
"event_message": "Meet us at booth 12"
```

Copy your own PNG into `callsign_badger/assets/`. Logos are displayed at 32 x 32
pixels on a white tile above the details. Use square artwork with bold, simple
shapes; pad a rectangular logo to a square beforehand to avoid distortion.
The included `assets/example-logo.png` is a generic antenna example, not a club logo.
Use `"logo": ""` to hide it. A missing or invalid image produces a readable error.
Loading uses the [Badgeware image API](https://github.com/pimoroni/badgeware-docs/blob/main/api/image.md).

`event_message` accepts up to 80 printable ASCII characters, wraps at the current
readable detail size, and appears after the name. Long content cycles through
panels. Empty text hides the message. Logo and event message remain visible in
privacy mode, like the club name; use public information in them.

## Full-screen QR and saved selection

Hold C for 0.8 seconds to expand the active profile's QR using the largest whole
pixel modules that fit the 176-pixel height, with its full white quiet zone.
Press A, B, or C to return to that design. Down still changes profiles, returning
to a badge; holding Down toggles privacy and returns to a badge. QR expansion is
unavailable when QR is disabled or privacy hides it. No battery icon, text, or logo
is drawn over the expanded code.

`display.remember_last` defaults to true. The app saves only selection changes,
not every refresh, battery check, or cycling detail panel. `state.json` stores the
profile ID, A/B/C design, QR view, and privacy flag. Corrupt or outdated state is
ignored. If storage is full or read-only the badge keeps working, but cannot save
new selections. Saved state is never included in distribution archives.

## Optional HF Propagation shortcut

Add `"hf_propagation": true` at the top level of `config.json` (or in a profile's
`overrides`). It defaults to false, so a standalone installation works as before.
Install the separate HF Propagation app in `apps/hf_propagation` first.

When enabled:
- Tap Down and release to open HF Propagation.
- Hold B for 0.8 seconds to change event profiles; tapping B still selects design B.
- Hold Down for privacy, Up for Morse, and hold C for the full-screen QR as before.

The Down shortcut fires on release to distinguish it from a privacy hold. It uses
the Badgeware launcher handoff and stops Morse before leaving.
If HF is missing or the switch cannot be saved, a readable notice keeps you in the badge.

For HF to return here, edit `apps/hf_propagation/hf_settings.py`:

```python
BADGE_APP = "/system/apps/callsign_badger"
```

Use HF's Down return control. With `display.remember_last` enabled, Callsign Badger
restores your saved selection. The `/system/apps/` prefix is the firmware path;
the folder appears as `apps/` on the USB disk. Set HF's return destination to Callsign Badger as shown above. The existing HF app/settings are not overwritten by the Callsign Badger package.
