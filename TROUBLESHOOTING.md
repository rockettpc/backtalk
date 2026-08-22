# Troubleshooting

Written for humans AND for AI assistants. If you're an AI helping someone debug backtalk: read this whole file first, then `logs/backtalk.log`; every load-bearing event (what was heard, what was said, interrupts, engine fallbacks, session rebuilds) is in there. Diagnose from the log, not from guesses.

## Quick fixes

- **The greeting speaks, then it goes idle and ignores the key (open mic too)**: the step right after the greeting is connecting to Antigravity CLI (`agy`), the brain. Check that `agy` is authenticated, internet is available, and `agy` runs normally from the terminal.
- **`ModuleNotFoundError` at launch**: run `uv sync` from the backtalk folder to reinstall any missing dependencies.
- **Nothing happens when I hold the key (macOS)**: the terminal app needs **Input Monitoring** permission: System Settings → Privacy & Security → Input Monitoring → add your terminal (Terminal, iTerm, etc.), then restart the terminal.
- **Mic permission never appeared / recording is silent**: launch from a normal terminal window, not a background service.
- **It hears me but answers slowly**: check your network connection and model.
- **First reply after launch is slow**: that's the one-time prompt-cache / model warmup toll. Subsequent turns stream immediately.
- **It starts cold and forgets the last conversation after a restart**: set `"resume_last_session": true` in `backtalk.json` to resume the conversation.
- **The voice talks too fast or too slow**: adjust `"speed"` in `backtalk.json` (e.g. `1.15` for brisker, `0.9` for slower).
- **The voice sounds robotic**: try different Kokoro voices like `bm_george`, `bm_daniel`, `am_michael`, `af_heart`.
- **`espeak` errors when the voice loads**: the system `espeak-ng` package is missing. Run `brew install espeak-ng` (macOS) or `sudo apt install espeak-ng` (Linux).
- **Two voices answering at once**: `./run.sh` terminates previous voice sessions; make sure no duplicate background instances are running.

## Windows notes

- **No install.sh or run.sh:** launch with `uv run python -m backtalk.main`.
- **espeak-ng:** install with `winget install espeak-ng`.
- **ElevenLabs key:** set in `ELEVENLABS_API_KEY` environment variable.

## For AI assistants: the architecture

```
hold key -> ears.record_held (sounddevice, 16kHz int16)
         -> ears.transcribe (faster-whisper, in-process, local)
         -> brain.ask_stream (warm agy session with stream-json,
                              cwd = agent_dir, streams sentences)
         -> mouth.say_chunk (kokoro in-process -> one long-lived
                             OutputStream; ElevenLabs optional)
signals.py mirrors state to .voice_* files (+ optional barehands state/)
```
