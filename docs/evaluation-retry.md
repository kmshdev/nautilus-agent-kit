# Standalone evaluation retry receipt

Checkpoint: 2026-09-18 (Asia/Kolkata). This records evidence available at the
checkpoint, not an all-tiers pass. Publication remains unapproved.

## Environment and isolation

SkillEvaluator 0.2.1 and Harbor 0.13.2 run with the authorized Azure route.
Semgrep 1.177.0 and SkillSpector 2.11.2 are installed in separate virtual
environments under ignored `.agent/main/tools/`; no global scanner install was
made. Existing Gitleaks and Docker executables are selected explicitly.
Credentials are process inputs, not committed artifacts.

The original six-skill baseline is frozen in
`.agent/main/evaluation-azure-compatible/`. Its running process retains the old
runner and old catalog-memory expectation. Correcting current source does not
retroactively change that run or its grades. The Tier 2 retry is separate at
`.agent/main/evaluation-tier2-retry/`; strict preflight evidence is at
`.agent/main/evaluation-runner-verified/`.

## Tier outcomes at this checkpoint

| Skill | Tier 1 | Tier 2 retry | Tier 3 baseline |
| --- | --- | --- | --- |
| Backtesting | Static non-pass; rubric 82.3, non-pass | Context passed | Complete paired report: 6/6 attempts |
| Actors | Static non-pass; rubric 82.7, non-pass | Context passed | Runtime preflight timed out; incomplete |
| Strategies | Static non-pass; rubric 82.7, non-pass | Context passed | 5/6 scored; one setup timeout; incomplete |
| Deployment | Static non-pass; rubric 80.9, passed | Context passed | Running; not qualified |
| Data | Static non-pass; rubric 78.6, non-pass | Context passed | Not yet attempted |
| Live | Static non-pass; rubric 81.4, non-pass | Context passed | Not yet attempted |

Both collection Tier 2 checks (descriptions and full body) passed on retry.
All six strict datasets passed preflight. Neither fact proves behavioral
completion. The initial Tier 2 service failures remain in their original run;
their precise transient cause was not established.

Tier 1 remains non-passing: SkillSpector treats `version: "0.64.0"` as a local
reference and produces incomplete coverage; the evaluator also requires an
author email that has not been supplied. Five rubric frontmatter diagnoses
misread the evaluator's extra YAML delimiters. See the
[audit](adversarial-audit.md) for excerpts and the isolated two-fixture scanner
reproduction. Valid metadata and safeguards were not removed to improve scores.

The old wrapper incorrectly labels the complete backtest report incomplete.
The repaired completion checker accepts its canonical 6/6 report, deduplicating
the `latest` alias, and correctly rejects the strategies 5/6 report. Raw receipts
are unchanged. Backtest goal scores cannot establish a genuine regression:
the old `chunk-memory` expectation penalizes source-correct lazy merging, and
negative cases expect an unavailable sibling skill in an isolated inventory.
No score was silently recalculated after correcting that expectation.

Container handoff stalls were observed during runtime/setup. Nonsecret direct
Docker and Compose stdin probes succeeded, so the root cause is unproven.
No credential-transport weakening or speculative evaluator patch was applied.
The existing run is allowed to continue; no duplicate full evaluation was
launched. Consult its `run.json` for status after this checkpoint.

## Current revision verification

- Corrected the remaining catalog-node paragraph: native chunked queries lazily
  merge multiple configs; equal-time ties retain config order; chunk size is not
  a RAM ceiling. Non-chunked loading and custom-query materialization remain
  distinct. At most one run config is allowed; sweep runs use fresh processes.
- Fresh isolated Codex home installed
  `0.64.0+codex.20260917222450` through the real local marketplace entry point.
  Only the minimal authorized Azure profile was copied, not login/session data.
  Automatic backtesting-skill selection and source inspection succeeded without
  a contradiction. This was source-grounded advice, not a backtest benchmark.
  Evidence: `.agent/main/source-forward-retry/{installation.log,session.jsonl}`.
- Earlier isolated onboarding executed an order-free Rust observer: 2 tests
  passed, then `inputs=5 quotes=4 signals=1 orders=0 positions=0`. Host and Cargo
  caches were shared; this is not a pristine operating-system test.
- All 69 maintenance tests passed, as did generated-resource drift and pinned
  source/hash checks, the official plugin validator and all six skill validators.
  The first plugin-validator invocation lacked PyYAML in system Python; rerunning
  with the existing evaluator Python passed without installing anything globally.
- Final read-only autoreview found no actionable bugs in the token patches,
  report-completeness checks or streaming corrections. It compared the latter
  with the installed 0.64.0 registry source; the separate forward test inspected
  the pinned checkout. Evidence: `.agent/main/autoreview-final.jsonl`.

## Continue and stop boundaries

Do not rerun complete trials to compensate for a wrapper classification defect.
Inspect the retained failing phase before selectively retrying incomplete trials.
Use new output directories for changed skill/dataset/runner identities; do not
edit historical run specifications to bypass resume checks. Reused cases are
regressions, not fresh holdouts. Keep numeric token budgets and paired coverage.

Full qualification remains open until incomplete behavior trials are resolved
and Tier 1 policy/scanner issues are explicitly addressed. An approved contact
is needed for any submission policy requiring author email. Publishing, pushing,
cloud deployment, broker access and strategy-project changes remain out of scope.
