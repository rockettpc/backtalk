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
"""The warm brain — a persistent Antigravity CLI session via agy streaming JSON.

One agy subprocess lives for the whole voice session in stream-json mode:
no per-turn process spawn, no per-turn context reload. Partial-message streaming
means sentences are yielded the moment they're complete, so the mouth starts
speaking while the rest of the thought is still forming.

The session's cwd is YOUR agent's folder (agent_dir in backtalk.json) —
whatever GEMINI.md / AGENTS.md lives there defines who is speaking. backtalk adds
only the spoken-delivery discipline (config.DISCIPLINE): the medium,
never the character.
"""
import asyncio
import json
import os
import re
import signal

from backtalk.config import CFG, DISCIPLINE
from backtalk.vlog import log

_SENTENCE_END = re.compile(r"(?<=[.!?])\s")

SESSION_FILE = os.path.join(CFG["signals_dir"], ".backtalk_session")


class WarmBrain:
    def __init__(self, model: str | None = None, can_use_tool=None,
                 resume_id: str | None = None):
        self.model = model or CFG.get("model", "")
        self._can_use_tool = can_use_tool
        self.session = {
            "turns": 0,
            "out_tokens": 0,
            "in_tokens": 0,
            "cost": 0.0,
        }
        self._resume_id = resume_id
        self._dirty = False
        self._proc: asyncio.subprocess.Process | None = None
        self.conversation_id: str | None = None
        self._discipline_sent = False

    async def start(self):
        cmd = ["agy", "--input-format", "stream-json", "--output-format", "stream-json"]

        skip_perms = CFG.get("dangerously_skip_permissions", True) or CFG.get("permission_mode") == "bypassPermissions"
        if skip_perms:
            cmd.append("--dangerously-skip-permissions")

        if self.model:
            cmd.extend(["--model", self.model])

        effort = CFG.get("effort", "")
        if effort:
            cmd.extend(["--effort", effort])

        for d in CFG.get("extra_dirs", []):
            if d:
                cmd.extend(["--add-dir", d])

        resume = self._resume_id
        self._resume_id = None
        if resume:
            cmd.extend(["--conversation", resume])

        cwd = CFG["agent_dir"] or os.getcwd()
        log(f"[brain] spawning agy in {cwd}: {' '.join(cmd)}")

        try:
            self._proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
        except Exception as e:
            log(f"[brain] failed to launch agy: {e}")
            raise

        # Read init event
        try:
            line = await asyncio.wait_for(self._proc.stdout.readline(), 30)
            if line:
                init_data = json.loads(line.decode().strip())
                self.conversation_id = init_data.get("conversation_id")
                log(f"[brain] agy ready (pid {self._proc.pid}, conversation {self.conversation_id})")
        except Exception as e:
            log(f"[brain] failed reading init event from agy: {e}")

    async def set_permission_mode(self, backtalk_mode: str):
        CFG["permission_mode"] = backtalk_mode

    async def context_usage(self):
        return None

    def _remember_session(self, res):
        if not CFG.get("resume_last_session"):
            return
        cid = res.get("conversation_id") or self.conversation_id
        if not cid:
            return
        try:
            with open(SESSION_FILE, "w") as f:
                f.write(cid)
        except OSError:
            pass

    def _tally(self, res, count_turn=True):
        try:
            u = res.get("usage", {}) or {}
            s = self.session
            if count_turn:
                s["turns"] += 1
            s["out_tokens"] += int(u.get("output_tokens") or 0)
            s["in_tokens"] += int(u.get("input_tokens") or 0) + int(u.get("cache_read_tokens") or 0)
        except Exception:
            pass

    async def command(self, cmd: str) -> str:
        if not self._proc or self._proc.returncode is not None:
            await self.start()

        self._dirty = True
        payload = json.dumps({"event": "user", "message": {"content": cmd}}) + "\n"
        self._proc.stdin.write(payload.encode())
        await self._proc.stdin.drain()

        texts = []
        try:
            while True:
                line = await asyncio.wait_for(self._proc.stdout.readline(), 90)
                if not line:
                    break
                data = json.loads(line.decode().strip())
                ev = data.get("event")
                if ev == "step_update":
                    su = data.get("step_update", {})
                    delta = su.get("text_delta", "")
                    if delta:
                        texts.append(delta)
                elif ev == "result":
                    self._dirty = False
                    res = data.get("result", {})
                    self._tally(res, count_turn=False)
                    self._remember_session(res)
                    break
        except asyncio.TimeoutError:
            log(f"[brain] console command timed out: {cmd!r}")
            return "error: the command timed out"

        return "".join(texts).strip()

    async def interrupt(self):
        if self._proc and self._dirty:
            log("[brain] interrupting in-flight turn")
            try:
                self._proc.send_signal(signal.SIGINT)
            except Exception:
                pass

    async def reset_turn(self, timeout: float = 8.0):
        if not self._proc or not self._dirty:
            return

        try:
            self._proc.send_signal(signal.SIGINT)
        except Exception:
            pass

        async def _drain() -> int:
            n = 0
            while True:
                line = await self._proc.stdout.readline()
                if not line:
                    break
                n += 1
                try:
                    data = json.loads(line.decode().strip())
                    if data.get("event") == "result":
                        break
                except Exception:
                    pass
            return n

        try:
            drained = await asyncio.wait_for(_drain(), timeout)
            log(f"[brain] interrupted turn drained ({drained} stale messages)")
            self._dirty = False
        except Exception:
            log("[brain] stream desynced beyond repair — restarting agy process")
            await self.stop()
            await self.start()
            self._dirty = False

    async def stop(self):
        if self._proc:
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), 3.0)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            self._proc = None
            self._dirty = False

    async def ask_stream(self, utterance: str):
        if not self._proc or self._proc.returncode is not None:
            await self.start()

        self._dirty = True
        prompt = utterance
        if not self._discipline_sent and not utterance.startswith("Warmup ping"):
            prompt = f"[System directive for spoken voice session: {DISCIPLINE}]\n\nUser: {utterance}"
            self._discipline_sent = True

        payload = json.dumps({"event": "user", "message": {"content": prompt}}) + "\n"
        self._proc.stdin.write(payload.encode())
        await self._proc.stdin.drain()

        buf = ""
        while True:
            line = await self._proc.stdout.readline()
            if not line:
                break
            try:
                data = json.loads(line.decode().strip())
            except json.JSONDecodeError:
                continue

            ev = data.get("event")
            if ev == "step_update":
                su = data.get("step_update", {})
                delta = su.get("text_delta", "")
                if delta:
                    buf += delta
                    while True:
                        m = _SENTENCE_END.search(buf)
                        if not m:
                            break
                        sentence, buf = buf[:m.end()].strip(), buf[m.end():]
                        if sentence:
                            yield sentence
            elif ev == "result":
                self._dirty = False
                res = data.get("result", {})
                self._tally(res)
                self._remember_session(res)
                break

        tail = buf.strip()
        if tail:
            yield tail


if __name__ == "__main__":
    import time

    async def demo():
        b = WarmBrain()
        await b.start()
        for prompt in ("Voice check: greet me in one sentence.",
                       "And what is two plus two, spoken like yourself?"):
            t0 = time.time()
            async for s in b.ask_stream(prompt):
                print(f"  ({time.time()-t0:4.1f}s) {s}", flush=True)
        await b.stop()

    asyncio.run(demo())
