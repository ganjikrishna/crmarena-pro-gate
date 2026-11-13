#!/usr/bin/env python3
"""Metered runner for CRMArena-Pro (disclosed instrumentation; scoring untouched).

Wraps every LiteLLM completion call made by run_tasks.py (agent loop,
extractor, confidentiality judge, user simulator) and appends per-call token
usage to meter/meter.jsonl. Pricing is computed separately by meter_tally.py
at the Fireworks rate card in the re-scope design.
"""
import os, sys, json, time

# Sanitize no_proxy before httpx/litellm import (bare ::1 breaks httpx URL parsing)
os.environ["no_proxy"] = "localhost,127.0.0.1"
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

METER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meter", "meter.jsonl")
os.makedirs(os.path.dirname(METER_PATH), exist_ok=True)

import litellm

_orig_completion = litellm.completion


def _get(obj, *names):
    for n in names:
        if obj is None:
            return None
        if isinstance(obj, dict):
            obj = obj.get(n)
        else:
            obj = getattr(obj, n, None)
    return obj


def _wrapped(*args, **kwargs):
    res = _orig_completion(*args, **kwargs)
    try:
        usage = getattr(res, "usage", None)
        prompt = _get(usage, "prompt_tokens") or 0
        completion = _get(usage, "completion_tokens") or 0
        cached = _get(usage, "prompt_tokens_details", "cached_tokens")
        if cached is None:
            cached = _get(usage, "prompt_cache_hit_tokens") or 0
        rec = {
            "ts": time.time(),
            "model": kwargs.get("model") or getattr(res, "model", None),
            "prompt_tokens": int(prompt),
            "completion_tokens": int(completion),
            "cached_tokens": int(cached or 0),
        }
        with open(METER_PATH, "a") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception as e:  # metering must never break a run
        print(f"[meter] failed to record usage: {e}", file=sys.stderr)
    return res


litellm.completion = _wrapped

# chat_agent and users imported `completion` by name; rebind there too.
import crm_sandbox.agents.chat_agent as _ca
_ca.completion = _wrapped
import crm_sandbox.env.users as _users
_users.completion = _wrapped

if __name__ == "__main__":
    import runpy
    sys.argv[0] = "run_tasks.py"
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_tasks.py"), run_name="__main__")
