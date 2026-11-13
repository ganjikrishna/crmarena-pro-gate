# Patches

Apply these files to a clean clone of Salesforce AI Research's CRMArena repository, in number order, unless a file says otherwise.

| File | Purpose | Used in headline runs? |
|---|---|---|
| `01-judge-extractor-substitution.patch` | Replaces the hard-coded `gpt-4o-2024-08-06` / `openai` defaults for the extractor, confidentiality judge, and user simulator with DeepSeek V4.1 Flash through Fireworks, at both default sites in `crm_sandbox/env/env.py`. | Yes |
| `02-subset-slice.patch` | Adds the disclosed data-loading slice controlled by `CRM_SUBSET_PER_TASK`. It keeps the first N B2B instances per task in dataset order. Scoring is untouched. | Yes, with `CRM_SUBSET_PER_TASK=25` |
| `03-meter-hooks.patch` | Adds `meter_run.py` and `meter_tally.py` at the upstream repository root. The runner records token usage for every LiteLLM call; the tally prices the log at the stated rate card. It does not alter requests, responses, or scoring. The runnable copies in this package are under `tools/`. | Yes |
| `04-diagnostic-parser-patch-DIAGNOSTIC-ONLY.patch` | Normalizes a `None` model-message content value to an empty string so the stock parser treats it as an empty or invalid action. | **No. Diagnostic only. It was not applied in the Stage 1 vanilla or Stage 2 gated headline runs.** |

## Install note

The upstream dependency pins recorded during the run were mutually unsatisfiable: `openai==1.51.2` conflicted with `litellm==1.67.2`, which required `openai>=1.68.2`. The run environment relaxed the OpenAI pin to 1.68.2 and then used `pip install -e . --no-deps`. This was an install-time fix only; it changed no benchmark code path or scoring logic.

## Configuration note

No `.env` file is included in this package. Create one from the current credentials published in the upstream repository's README at HEAD, and add your own Fireworks API key under the variable name expected by your local setup. Do not use upstream's `.env.example` as the credential source for these runs; see the caution in the main README.

## License carve-out

The patch files under `patches/` contain small excerpts of upstream CRMArena code as diff context. Those excerpts remain under upstream's CC BY-NC 4.0 license. Nothing of upstream's benchmark, its data, or its credentials is redistributed in this package; to reproduce the runs, obtain them from upstream (`SalesforceAIResearch/CRMArena`), with credit to Salesforce AI Research.
