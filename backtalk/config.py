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
"""Configuration — backtalk.json in the repo root, merged over defaults.

backtalk deliberately owns NO personality. Your agent's identity lives in
the GEMINI.md / AGENTS.md of whatever folder `agent_dir` points at — backtalk just
gives that agent a mouth and ears. The only voice-related instruction it
adds is the spoken-delivery discipline below, which is about the MEDIUM
(writing for the ear), never the character.
"""
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO / "backtalk.json"

DEFAULTS = {
    # The folder whose GEMINI.md / AGENTS.md defines WHO your agent is. The voice
    # session runs there, so it's the same assistant as your terminal
    # sessions — same name, same personality, same memory.
    "agent_dir": "~",
    # Display name, used in logs and to build the quit phrases
    # ("goodbye <name>" hangs up). Match your agent's actual name.
    "name": "Assistant",
    # The brain model. Empty string uses Antigravity's default model.
    # Specify explicit model if desired (e.g. gemini-2.5-flash).
    "model": "",
    # The deep-work model for the voice console's "switch to the deep
    # model" command ("back to the fast model" returns to "model"
    # above).
    "deep_model": "",
    # Tool permissions for the voice session.
    # "bypassPermissions" is AUTO-APPROVE: runs with --dangerously-skip-permissions.
    # "ask" is interactive permission checks.
    "permission_mode": "bypassPermissions",
    # Whether to pass --dangerously-skip-permissions to agy.
    "dangerously_skip_permissions": True,
    # Extra folders the agent may access beyond agent_dir (e.g. your
    # notes vault). Absolute paths or ~ paths.
    "extra_dirs": [],
    # Hold-to-talk key. Named keys ("home", "f13", "right_alt", ...)
    # or a single character.
    "ptt_key": "right_alt",
    # The microphone mode. "ptt" (push to talk, the default and the
    # recommendation): the mic is closed except while the key is held,
    # so room audio and your own speakers can never trigger the agent.
    # "open" (hands-free listening): always listening with voice
    # detection; a video, music with vocals, or another person in the
    # room CAN trigger it, and with open speakers it can hear itself
    # (headphones recommended). The key still works in hands-free
    # listening: it interrupts, and holding it always gets you heard.
    # Switch live by voice: "go hands free" / "push to talk mode"
    # (the switch saves itself here). The --open-mic launch flag
    # forces "open" for one session.
    "mic_mode": "ptt",
    # Playback speed for the built-in voice: 1.0 is Kokoro's native
    # pace, 1.15 is noticeably brisker, 0.9 is slower.
    "speed": 1.0,
    # Resume the previous conversation on launch. OFF by default: a
    # fresh session every launch is the predictable behavior. Set true
    # and backtalk saves the session id after every completed turn
    # (signals_dir/.backtalk_session) and reattaches to it at the next
    # launch.
    "resume_last_session": False,
    # Reasoning effort for the voice session: "" inherits the model's
    # default; "low" / "medium" / "high" applies at launch.
    "effort": "",
    # The voice (Kokoro, local, free). bm_lewis is the proven default —
    # British male, the butler register. Others: bm_george, bm_daniel,
    # bm_fable, am_michael, af_heart... The first letter picks the
    # language pipeline (a=American, b=British, e/f/h/i/j/p/z = other
    # languages), so keep voice and accent matched.
    "voice": "bm_lewis",
    # Speech recognition (faster-whisper, local, free).
    # Models: tiny.en / base.en / small.en / medium.en — small.en is the
    # accuracy/speed sweet spot on a normal machine.
    "stt_model": "small.en",
    # "auto" uses CUDA when present, otherwise CPU. int8 keeps CPU fast.
    "stt_device": "auto",
    "stt_compute": "int8",
    # Optional cloud voice: OpenRouter GPT Audio streaming TTS.
    "openrouter": {
        "enabled": False,
        "api_key": "",
        "model": "openai/gpt-audio-mini",
        "voice": "fable",
    },
    # Optional premium voice: ElevenLabs on YOUR key. The key NEVER
    # goes in a file: it's read from the macOS Keychain (item
    # `backtalk-elevenlabs`) or Linux secret-tool, with the
    # ELEVENLABS_API_KEY env var as last-resort fallback.
    "elevenlabs": {
        "enabled": False,
        "voice_id": "",
        "model": "eleven_turbo_v2_5",
        "master": ("atempo=1.12,highpass=f=70,"
                   "equalizer=f=3200:t=q:w=1.2:g=3.5,"
                   "equalizer=f=140:t=q:w=1:g=1.5,"
                   "acompressor=threshold=-18dB:ratio=2.5:attack=8:"
                   "release=120:makeup=4dB,alimiter=limit=0.95"),
    },
    # Where the signal-bus files are written (.voice_state,
    # .voice_waveform, .voice_loading_pid) — anything can watch them;
    # visualizers pair with this contract. Default: the repo root.
    "signals_dir": "",
    # THE BAREHANDS SEAM: point this at a barehands checkout's state/
    # folder and its on-screen ring becomes your agent's face — it
    # breathes while idle, spins while thinking, pulses with the voice.
    "barehands_state_dir": "",
    # Sound played while the agent thinks, so a long pause never reads as
    # a dead line. The bundled one ships in assets/; a relative path
    # resolves against this repo. Set "" to think in silence.
    "thinking_sound": "assets/thinking.wav",
    # Spoken lines. {name} is replaced with "name" above.
    "greeting": "Voice line online. Hold {ptt_key} and talk to me.",
    "signoff": "Voice line closing. I'll be here when you need me.",
}

# The spoken-delivery discipline — the MEDIUM half of what used to be a
# persona. The CHARACTER half deliberately is not here: it's whatever
# lives in the agent_dir's GEMINI.md / AGENTS.md. One identity, one place.
DISCIPLINE = (
    "VOICE SESSION (your reply is spoken aloud through a TTS engine, "
    "not displayed): you are SPEAKING, in your own voice and "
    "personality — your GEMINI.md / AGENTS.md is who you are. The TTS engine "
    "PERFORMS your punctuation, so write like a performance, never "
    "like a memo: contractions always, punchy conversational "
    "sentences, and if a line could open a quarterly report, rewrite "
    "it like you're telling a friend. Keep replies to a few short "
    "sentences; go longer only when the question genuinely needs it. "
    "No markdown, no lists, no code blocks, no emoji, no URLs. Say "
    "numbers the way a human says them out loud — never raw figures "
    "or symbols. Skip any startup sequence; answer directly. "
    "VOICE CONSOLE FACTS, answer from these whenever the person asks "
    "you to change a voice-line setting: this session is controlled "
    "by exact spoken phrases, never by you. Permissions: 'stop "
    "asking for permission' (then 'confirm'), or 'start asking "
    "again'. Microphone: 'go hands free', or 'push to talk mode'. "
    "Also: 'clear the session', 'compact the session', 'switch to "
    "the deep model', 'back to the fast model', 'set effort to low' "
    "(or medium, high, max), and 'usage report'. You cannot flip "
    "these live yourself, so when asked, give the person the exact "
    "phrase to SAY. Editing backtalk.json only changes the default "
    "for the NEXT launch."
)


def _expand(p: str) -> str:
    return os.path.expanduser(p) if p else p


def load() -> dict:
    cfg = json.loads(json.dumps(DEFAULTS))          # deep copy
    try:
        user = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    except FileNotFoundError:
        pass
    except ValueError as e:
        print(f"[config] backtalk.json is not valid JSON ({e}) — "
              f"using defaults", flush=True)
    cfg["agent_dir"] = _expand(cfg["agent_dir"])
    cfg["extra_dirs"] = [_expand(d) for d in cfg.get("extra_dirs", [])]
    cfg["signals_dir"] = _expand(cfg.get("signals_dir", "")) or str(REPO)
    cfg["barehands_state_dir"] = _expand(cfg.get("barehands_state_dir", ""))
    thinking = _expand(cfg.get("thinking_sound", ""))
    if thinking and not os.path.isabs(thinking):
        thinking = str(REPO / thinking)
    cfg["thinking_sound"] = thinking
    name = str(cfg.get("name") or "Assistant")
    low = name.lower()
    cfg["quit_phrases"] = tuple(cfg.get("quit_phrases") or (
        f"goodbye {low}", f"good bye {low}", "end voice mode",
        f"hang up {low}", "hang up"))
    key_label = "the " + str(cfg.get("ptt_key", "home")).replace("_", " ") \
                + " key"
    cfg["greeting"] = str(cfg["greeting"]).replace(
        "{name}", name).replace("{ptt_key}", key_label)
    cfg["signoff"] = str(cfg["signoff"]).replace("{name}", name)
    return cfg


CFG = load()
