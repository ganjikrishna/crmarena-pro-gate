#!/usr/bin/env python3
"""Tally meter/meter.jsonl at the re-scope rate card and append a snapshot to METER.md.

Rate card (Fireworks serverless, DeepSeek V4.1 Flash, per re-scope 2026-11-13):
  input $0.30 / 1M, cached input $0.006 / 1M, output $1.20 / 1M.
Cached tokens are counted only when the provider reports them; otherwise all
input is priced at the full rate (conservative upper bound).
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
METER_JSONL = os.path.join(HERE, "meter", "meter.jsonl")
METER_MD = os.path.join(HERE, "METER.md")
RATE_IN, RATE_CACHED, RATE_OUT = 0.30, 0.006, 1.20  # per 1M tokens


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
    calls = prompt = completion = cached = 0
    if os.path.exists(METER_JSONL):
        with open(METER_JSONL) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                calls += 1
                prompt += r.get("prompt_tokens", 0)
                completion += r.get("completion_tokens", 0)
                cached += r.get("cached_tokens", 0)
    noncached = max(prompt - cached, 0)
    cost = noncached * RATE_IN / 1e6 + cached * RATE_CACHED / 1e6 + completion * RATE_OUT / 1e6
    ts = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
    block = (
        f"\n## Snapshot — {label} — {ts}\n"
        f"- LLM calls metered: {calls}\n"
        f"- Prompt tokens: {prompt:,} (cached reported: {cached:,})\n"
        f"- Completion tokens: {completion:,}\n"
        f"- Metered cost at rate card (${RATE_IN} in / ${RATE_CACHED} cached / ${RATE_OUT} out per 1M): **${cost:.4f}**\n"
    )
    header = ""
    if not os.path.exists(METER_MD):
        header = ("# CRMArena-Pro run meter (Fireworks credits, $0 cash)\n"
                  "Rate card: DeepSeek V4.1 Flash $0.30 input / $0.006 cached input / $1.20 output per 1M tokens (re-scope 2026-11-13).\n"
                  "Hard stops: Stage 0 < $0.25; Stage 1 cumulative $10 including Stage 0.\n")
    with open(METER_MD, "a") as f:
        f.write(header + block)
    print(block)
    print(f"CUMULATIVE_METERED=${cost:.4f} calls={calls}")


if __name__ == "__main__":
    main()
