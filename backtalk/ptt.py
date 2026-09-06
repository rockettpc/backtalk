# backtalk: talk to your Google Antigravity agent out loud.
# Copyright (C) 2026 Jared Rhodenizer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Hold-to-talk — a global key listener.

HOLD the key -> mic opens. RELEASE -> mic closes and the utterance is
processed. The button IS the voice-activity detector, which is why this
mode is speaker-safe with no headphones: the mic simply isn't open while
the assistant talks, unless you press the key — and pressing while it
talks interrupts it.

THE KEY-REPEAT TRAP (the bug that kills every naive build): the OS fires
on_press events CONTINUOUSLY while a key is held. Without the held-state
filter below, every repeat reads as a fresh press and keeps cancelling
the reply before it can speak.

macOS needs Input Monitoring permission for the hosting terminal
(System Settings -> Privacy & Security -> Input Monitoring). Windows
works out of the box. On Linux / Wayland, global hotkeys require reading
/dev/input/event* via evdev, which requires the user to be in the `input`
group: `sudo usermod -aG input $USER` (followed by session re-login).
"""
import os
import platform
import select
import sys
import threading
import time

try:
    import evdev
    from evdev import ecodes, InputDevice
except ImportError:
    evdev = None

from pynput import keyboard


def resolve_pynput_key(name: str):
    """'home' / 'f13' / 'right_alt' / any single character -> pynput key."""
    name = (name or "right_alt").strip().lower()
    if len(name) == 1:
        return keyboard.KeyCode.from_char(name)
    aliases = {
        "right_alt": "alt_r", "left_alt": "alt_l",
        "right_option": "alt_r", "left_option": "alt_l",
        "right_ctrl": "ctrl_r", "left_ctrl": "ctrl_l",
        "right_cmd": "cmd_r", "left_cmd": "cmd_l",
        "right_super": "cmd_r", "left_super": "cmd_l",
        "right_shift": "shift_r", "left_shift": "shift_l",
    }
    name = aliases.get(name, name)
    try:
        return getattr(keyboard.Key, name)
    except AttributeError:
        print(f"[ptt] unknown pynput key {name!r} — falling back to 'right_alt'",
              flush=True)
        return keyboard.Key.alt_r


def resolve_evdev_key(name: str):
    """Resolve key name into an evdev ecodes integer."""
    if not evdev:
        return None
    name = (name or "right_alt").strip().lower()
    aliases = {
        "right_alt": "KEY_RIGHTALT", "alt_r": "KEY_RIGHTALT",
        "left_alt": "KEY_LEFTALT", "alt_l": "KEY_LEFTALT",
        "right_ctrl": "KEY_RIGHTCTRL", "ctrl_r": "KEY_RIGHTCTRL",
        "left_ctrl": "KEY_LEFTCTRL", "ctrl_l": "KEY_LEFTCTRL",
        "right_shift": "KEY_RIGHTSHIFT", "shift_r": "KEY_RIGHTSHIFT",
        "left_shift": "KEY_LEFTSHIFT", "shift_l": "KEY_LEFTSHIFT",
        "right_cmd": "KEY_RIGHTMETA", "cmd_r": "KEY_RIGHTMETA",
        "right_super": "KEY_RIGHTMETA", "super_r": "KEY_RIGHTMETA",
        "left_cmd": "KEY_LEFTMETA", "cmd_l": "KEY_LEFTMETA",
        "left_super": "KEY_LEFTMETA", "super_l": "KEY_LEFTMETA",
        "home": "KEY_HOME", "space": "KEY_SPACE",
        "enter": "KEY_ENTER", "return": "KEY_ENTER",
        "tab": "KEY_TAB", "escape": "KEY_ESC", "esc": "KEY_ESC",
        "backspace": "KEY_BACKSPACE", "caps_lock": "KEY_CAPSLOCK",
    }
    code_name = aliases.get(name)
    if code_name and hasattr(ecodes, code_name):
        return getattr(ecodes, code_name)

    candidate = f"KEY_{name.upper()}"
    if hasattr(ecodes, candidate):
        return getattr(ecodes, candidate)

    if len(name) == 1:
        if name.isalpha():
            candidate = f"KEY_{name.upper()}"
            if hasattr(ecodes, candidate):
                return getattr(ecodes, candidate)
        elif name.isdigit():
            candidate = f"KEY_{name}"
            if hasattr(ecodes, candidate):
                return getattr(ecodes, candidate)

    return ecodes.KEY_RIGHTALT


class EvdevPTTListener:
    """Linux kernel direct /dev/input listener (works across Wayland & X11 globally)."""
    def __init__(self, key="right_alt"):
        self._key_code = resolve_evdev_key(key)
        self._key_name = str(key)
        self._held = False
        self._press_evt = threading.Event()
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _get_keyboards(self):
        devices = []
        try:
            for path in evdev.list_devices():
                try:
                    dev = InputDevice(path)
                    caps = dev.capabilities().get(ecodes.EV_KEY, [])
                    if self._key_code in caps or (ecodes.KEY_A in caps and ecodes.KEY_ENTER in caps):
                        devices.append(dev)
                except (PermissionError, OSError):
                    continue
        except Exception:
            pass
        return devices

    def _run(self):
        last_scan = 0.0
        fd_to_dev = {}
        while self._running:
            now = time.monotonic()
            if now - last_scan > 5.0 or not fd_to_dev:
                last_scan = now
                found = self._get_keyboards()
                existing_paths = {d.path for d in fd_to_dev.values()}
                for d in found:
                    if d.path not in existing_paths:
                        fd_to_dev[d.fd] = d
                dead_fds = []
                for fd in list(fd_to_dev.keys()):
                    try:
                        os.fstat(fd)
                    except OSError:
                        dead_fds.append(fd)
                for fd in dead_fds:
                    fd_to_dev.pop(fd, None)

            if not fd_to_dev:
                time.sleep(0.5)
                continue

            try:
                r, _, _ = select.select(list(fd_to_dev.keys()), [], [], 1.0)
            except (ValueError, OSError):
                fd_to_dev.clear()
                continue

            for fd in r:
                dev = fd_to_dev.get(fd)
                if not dev:
                    continue
                try:
                    for event in dev.read():
                        if event.type == ecodes.EV_KEY and event.code == self._key_code:
                            if event.value == 1 and not self._held:   # Key Down (filter repeat)
                                self._held = True
                                self._press_evt.set()
                            elif event.value == 0:                     # Key Up
                                self._held = False
                except OSError:
                    fd_to_dev.pop(fd, None)

    def wait_press(self):
        """Block until the key goes DOWN (one event per physical press)."""
        self._press_evt.wait()
        self._press_evt.clear()

    def is_held(self) -> bool:
        return self._held


class PynputPTTListener:
    """Standard pynput listener (macOS, Windows, and X11 fallback)."""
    def __init__(self, key="right_alt"):
        self._key = resolve_pynput_key(key) if isinstance(key, str) else key
        self._held = False
        self._press_evt = threading.Event()
        self._listener = keyboard.Listener(on_press=self._on_press,
                                           on_release=self._on_release)
        self._listener.daemon = True
        self._listener.start()

    def _on_press(self, k):
        if k == self._key and not self._held:   # filter key-repeat
            self._held = True
            self._press_evt.set()

    def _on_release(self, k):
        if k == self._key:
            self._held = False

    def wait_press(self):
        """Block until the key goes DOWN (one event per physical press)."""
        self._press_evt.wait()
        self._press_evt.clear()

    def is_held(self) -> bool:
        return self._held


def PTTListener(key="right_alt"):
    """Factory: selects evdev on Linux if devices are accessible; falls back to pynput."""
    if platform.system() == "Linux" and evdev:
        try:
            accessible = False
            for path in evdev.list_devices():
                try:
                    dev = InputDevice(path)
                    caps = dev.capabilities().get(ecodes.EV_KEY, [])
                    if ecodes.KEY_A in caps or ecodes.KEY_ENTER in caps:
                        accessible = True
                        break
                except (PermissionError, OSError):
                    continue
            if accessible:
                return EvdevPTTListener(key)
            else:
                print("[ptt] Notice: /dev/input devices are not readable (user is not in 'input' group).", flush=True)
                print("[ptt] Global push-to-talk on Wayland requires: sudo usermod -aG input $USER", flush=True)
                print("[ptt] (After adding to input group, log out and log back into Linux).", flush=True)
                print("[ptt] Falling back to standard pynput listener (active window only under Wayland).", flush=True)
        except Exception as e:
            print(f"[ptt] evdev probe failed ({e}) — falling back to pynput", flush=True)

    return PynputPTTListener(key)
