# backtalk

> **Google Antigravity CLI (`agy`) Edition**  
> *Forked and migrated to Google Antigravity CLI by [@rockettpc](https://github.com/rockettpc). Original backtalk voice loop created by **Jared Rhodenizer** ([@jaredrhod](https://github.com/jaredrhod/backtalk)).*

**Runs on:** Google Antigravity CLI (`agy`). The voice connects to your local `agy` session using asynchronous streaming.

Talk to your Antigravity agent out loud. Hold a key, say the thing, and it answers through your speakers in a real voice about a second later, with all its tools, your project context, and its own personality. Your AI finally has something to say back.

The hearing and the voice run local: free, offline models on your machine, no voice API keys, no per-word costs. The brain is the Google Antigravity CLI you already have.

## What it does

- **Hold a key, talk, release.** Your words are transcribed locally and handed to a live Antigravity CLI session. The reply is spoken sentence by sentence as it's generated, with first audio in about 1 to 2 seconds on warm turns. Prefer no button at all? **Hands-free listening** is one spoken sentence away ("go hands free"), and the key keeps working there as your interrupt.
- **It's YOUR agent talking.** The session runs in the folder whose `GEMINI.md` / `AGENTS.md` defines your assistant: same name, same personality, same memory as your terminal sessions. backtalk has no personality of its own; it's a mouth and ears for whoever you already have. (No agent yet? The [ai-memory-vault](https://github.com/rockettpc/ai-memory-vault) build ships with Jarvis, ready to use.)
- **Interrupt it.** Press the key while it's talking and it shuts up and listens. No headphones needed, because the mic only opens while you hold the key, so it never hears the speakers.
- **Type instead whenever you want.** Typing in the terminal is the same conversation, and the reply is still spoken.
- **Auto-approve with `--dangerously-skip-permissions`.** When auto-approve is active, the agent can execute commands and write notes seamlessly.
- **The voice console.** Session control by voice, so you never go back to the keyboard: "clear the session", "compact the session", "switch to the deep model" / "back to the fast model", "set effort to low" (or medium, high, max), "usage report", "go hands free" / "push to talk mode" for the microphone, "stop asking for permission" / "start asking again" for approvals.
- **It can pick up where it left off.** Set `"resume_last_session": true` in the config and every launch reattaches to your previous conversation using `--conversation`.
- **Music ducks while it speaks** (Spotify, macOS) and comes back up after.
- **It thinks out loud.** While the agent works, you hear the processing sound, so a pause never reads as a dead line. Silence it with `"thinking_sound": ""` in the config.

## Install

```bash
git clone https://github.com/rockettpc/backtalk
cd backtalk
./install.sh
```

The installer sets up a Python environment, the two local AI models (speech-to-text and the voice), and the one system library they need. First run downloads the models (about 1 GB total); everything after is instant. Prerequisites: [Google Antigravity CLI (`agy`)](https://antigravity.google/docs/cli/reference), and `uv` (the installer offers to install it).

**The easy way to configure it:** open this folder in Antigravity CLI and say *"read backtalk.md and set me up."* The wizard picks your agent folder, your key, and your voice with you, then test-fires the whole loop.

**Already in an Antigravity CLI session with your agent?** One sentence does the whole install: *"clone https://github.com/rockettpc/backtalk.git, then read backtalk/backtalk.md and set me up."* Your agent runs the installer and the wizard for you.

**The manual way:** copy `backtalk.json.example` to `backtalk.json` (your copy is untracked, so updates never touch it), then edit it. Point `agent_dir` at the folder whose `GEMINI.md` is your agent, set `name` to your agent's name, pick a `ptt_key`. Then:

```bash
./run.sh
```

Hold the key. Talk. Let go.

## Windows

Windows setup runs through the wizard (`install.sh` and `run.sh` are Mac and Linux). Open this folder in Antigravity CLI and say *"read backtalk.md and set me up"*: the wizard installs uv, espeak-ng, the environment, and the models natively, then launches with `uv run python -m backtalk.main`.

## The voice

Three engines:

**Built-in (Kokoro), the free one.** Local, offline, no accounts, no per-word costs. The default voice is `bm_lewis`, a British male butler register. Around 60 voices ship free; set `voice` in `backtalk.json`.

**OpenRouter TTS, the versatile cloud option.** OpenAI-compatible TTS endpoint via OpenRouter (`openai/tts-1`, `openai/tts-1-hd`, `openai/gpt-audio-mini`, etc.). Set your key in `OPENROUTER_API_KEY` or `backtalk.json`.

**ElevenLabs, the ultra-natural one.** The human-sounding voice on your own API key. The wizard walks the whole thing with you.

## Give it a face (optional)

backtalk writes state files while it listens, thinks, and speaks:

- **[ai-visualizer](https://github.com/rockettpc/ai-visualizer)**: four full-screen visualizers including the living circuit board.
- **[barehands](https://github.com/rockettpc/barehands)**: on-screen ring and gesture control.

## Credits and Attribution

- **Original Author:** **Jared Rhodenizer** ([@jaredrhod](https://github.com/jaredrhod/backtalk)).
- **Antigravity CLI Port:** Maintained by [@rockettpc](https://github.com/rockettpc).
- **Libraries & Models:** Speech recognition by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (MIT) running [OpenAI Whisper](https://github.com/openai/whisper) models (MIT). Voice by [Kokoro](https://github.com/hexgrad/kokoro) (Apache 2.0) with [espeak-ng](https://github.com/espeak-ng/espeak-ng) (GPL-3.0) for phonemization. Powered by Google Antigravity CLI (`agy`).

## License

Copyright (c) 2026 Jared Rhodenizer.

Licensed under the GNU Affero General Public License, version 3 or later (AGPL-3.0-or-later).
