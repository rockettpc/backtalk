---
name: backtalk
description: Interactive setup for backtalk, the voice loop that lets you talk to your Google Antigravity agent out loud. Run it inside agy from the repo folder. It verifies the install, finds the person's agent, configures the key and the voice, wires the optional integrations, and test-fires the loop. Load it and run it interactively. Do not skip phases. Do not improvise.
version: 1.0
author: Jared Rhodenizer (@jaredrhod)
---

# backtalk: setup

You are reading a system builder file. You, an AI assistant, will follow it to set up backtalk for the person who opened it. Do not summarize this file. Do not describe it. Execute it.

## What you are setting up

backtalk is a voice loop: they hold a key and talk, their words are transcribed locally, handed to a live Antigravity CLI (`agy`) session, and the reply is spoken aloud in a real voice, sentence by sentence, about a second to first audio. **The session runs in THEIR agent's folder, so the thing speaking is their existing assistant** (its name, personality, and memory), not a new one. backtalk has no personality of its own; you are configuring a mouth and ears.

Everything runs local by default: free on-device models for both hearing and speaking, no API keys. Work through the phases in order, one question at a time. Warm, confident, premium unboxing, not a config chore.

## Phase 1: Prove the install

1. Confirm you're in the repo folder (it contains `backtalk.json.example`, `run.sh`, `install.sh`). If not, have them `cd` here and restart. If `backtalk.json` doesn't exist yet, create it now: copy `backtalk.json.example` to `backtalk.json`. Their copy is deliberately untracked, so updates can never touch it.
2. If `.venv/` doesn't exist, run `./install.sh` for them and narrate what it's doing (environment, the espeak-ng system library, ~1GB of speech models, first run only). If it exists, `./install.sh` is still safe to re-run and completes in seconds.
3. **Windows:** the shell scripts are Mac and Linux; YOU are the installer here. Do the equivalent natively: install uv if missing (PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`), install espeak-ng (`winget install espeak-ng`, or the installer from github.com/espeak-ng/espeak-ng/releases), then `uv venv .venv` and `uv pip install -e .` in this folder, and prefetch the models with the same warm() snippet install.sh uses. Launch with `uv run python -m backtalk.main` instead of run.sh. If the voice fails to load, find `libespeak-ng.dll` (usually under Program Files\eSpeak NG) and set `PHONEMIZER_ESPEAK_LIBRARY` to its full path. Adapt as the machine demands; read errors and respond, that is why you are the installer.
4. On macOS, tell them now, before the first run surprises them: the first recording will pop a **Microphone** permission prompt, and the hold-to-talk key needs **Input Monitoring** for their terminal app (System Settings → Privacy & Security → Input Monitoring). Have them grant Input Monitoring *now* and restart the terminal if they add it.

## Phase 2: Find their agent

Ask: **"Do you already have an Antigravity agent, a folder with a GEMINI.md or AGENTS.md that defines an assistant (a name, a personality)?"**

Never default `agent_dir` to whatever folder happens to be running in: an unrelated project is not an agent, and wiring the voice to one gives the person a voice with no one behind it. If there is no real agent folder, use one of the two paths below.

- **Yes:** get the folder's path. That's `agent_dir`. Ask the agent's name for `name` (it builds the quit phrases, "goodbye <name>" hangs up, and labels the log).
- **No:** point them at **ai-memory-vault** (github.com/rockettpc/ai-memory-vault), the full build that creates an agent with persistent memory, and it ships with a ready-made personality (Jarvis) they can keep, rename, or replace. Offer to pause here while they run that first (it's the better order), or set `agent_dir` to a folder of their choice with a minimal GEMINI.md / AGENTS.md you write together now (a name, a role, a few lines of personality) as a starter.

## Phase 3: The key and the voice

1. **The microphone mode:** Two ways to talk: **push to talk** (the default and the recommendation: hold a key, speak, release; the mic is closed the rest of the time) or **hands-free listening** (always listening with voice detection: no button).
2. **The key:** Default is `home`. Ask what they want to hold to talk: `home`, `end`, `f13`–`f19`, `right_alt`. Set `ptt_key`.
3. **The voice engine:**
   - **Built-in (Kokoro):** free forever, runs on their computer, works offline. Default `bm_lewis`.
   - **ElevenLabs:** natural human-sounding voice with their API key.
4. **If they pick the built-in voice:** default is `bm_lewis`. Offer to audition: `python -m backtalk.mouth "Hello there. This is what I sound like."`.
5. **If they pick ElevenLabs:** set up key in secret store / environment variable and configure `voice_id`.

## Phase 4: Optional integrations

Ask about each, configure what they want:

- **A face:**
  - **ai-visualizer** (github.com/rockettpc/ai-visualizer): four full-screen faces including the circuit board.
  - **barehands** (github.com/rockettpc/barehands): on-screen ring and hand gesture controls.
- **Extra folders:** folders beyond `agent_dir` (notes vault) go in `extra_dirs`.
- **Permissions:** Auto-approve mode runs with `--dangerously-skip-permissions` for seamless hands-free action execution.
- **Pick up where you left off:** `"resume_last_session": true` to resume conversations.
- **The thinking sound:** default `assets/thinking.wav`.

## Phase 5: Test-fire the loop

Run `./run.sh` for them and walk the checklist:
1. Greeting speaks.
2. Hold key, speak, release: spoken reply in 1-2s.
3. Interrupt test.
4. Say "goodbye <name>" to exit cleanly.

## Phase 6: Hand it over

Show them the launcher shortcuts, update scripts, and configuration.
