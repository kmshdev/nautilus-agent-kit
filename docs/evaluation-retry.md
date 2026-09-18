# Standalone evaluation retry receipt

Checkpoint: 2026-09-18 (Asia/Kolkata). This records evidence available at the
checkpoint, not an all-tiers pass. The owner subsequently authorized a repository
push and PR under `kmshdev/nautilus-agent-kit`, not an OpenAI marketplace submission.

## Environment and isolation

SkillEvaluator 0.2.1 and Harbor 0.13.2 run with the authorized Azure route.
Semgrep 1.177.0 and SkillSpector 2.11.2 are installed in separate virtual
environments under ignored `.agent/main/tools/`; no global scanner install was
made. Existing Gitleaks and Docker executables are selected explicitly.
Credentials are process inputs, not committed artifacts.

The original six-skill baseline is frozen in
`.agent/main/evaluation-azure-compatible/`. Its completed process used the old
runner and old catalog-memory expectation. Correcting current source does not
retroactively change that run or its grades. The Tier 2 retry is separate at
`.agent/main/evaluation-tier2-retry/`; strict preflight evidence is at
`.agent/main/evaluation-runner-verified/`.

## Tier outcomes at this checkpoint

| Skill | Tier 1 | Tier 2 retry | Tier 3 baseline and separate retries |
| --- | --- | --- | --- |
| Backtesting | Static and rubric retry passed | Context passed | Complete paired report: 6/6 attempts |
| Actors | Rubric passed; static LLM scan incomplete; latest diagnostic reports connection failure | Context passed | Baseline preflight timed out; fixed retry 5/6; remaining case separately completed 2/2 on owner-requested retry |
| Strategies | Rubric retry passed; static retry pending | Context passed | Baseline 5/6; remaining case separately completed 2/2 on owner-requested retry |
| Deployment | Rubric retry passed; static retry pending | Context passed | 5/6 scored; failed case retry separately completed 2/2 |
| Data | Rubric retry passed; static retry pending | Context passed | Baseline 5/6; remaining case separately completed 2/2 on owner-requested retry |
| Live | Rubric retry passed; static retry pending | Context passed | Complete paired report: 6/6 attempts |

Both collection Tier 2 checks (descriptions and full body) passed on retry.
All six strict datasets passed preflight. Neither fact proves behavioral
completion. The initial Tier 2 service failures remain in their original run;
their precise transient cause was not established.

Tier 1's first retry is at `.agent/main/evaluation-tier1-fixed/`. All six rubric
reports pass after replacing the evaluator's extra YAML delimiters with labeled
document boundaries. The isolated SkillSpector version-reference patch passes
two regression tests and the synthetic fixture reports complete/SAFE. Real
LLM enrichment then failed with confirmed Azure HTTP 429. No scanner was disabled.
The owner has since approved `Keshav Mishra <me@kmsh.dev>`; all six skill author
fields use that contact. `.agent/main/evaluation-author-serial/` was deliberately
stopped after discovering that the evaluator drops the scanner concurrency
setting from its subprocess allowlist. Its stale running receipt is not a live
job or completed result. The isolated patch now forwards only that nonsecret
control. `.agent/main/evaluation-author-limited/` passed backtest static and rubric
checks with `SKILLSPECTOR_MAX_LLM_CONCURRENCY=1` and no concurrent paid evaluation
process; both reports have `overall_passed: true` and no incomplete scans.
Direct NVIDIA schema validation separately passes for all six approved authors.
The next serialized actor run at
`.agent/main/evaluation-author-limited-building-nautilus-actors/` passes its
rubric and schema but remains incomplete on LLM security enrichment. The
sanitized `.agent/main/scanner-probe/actor-limited-diagnostic.log` confirms
HTTP 429 even with the concurrency setting propagated. The finite serialized
scan loop stopped on that failure; the remaining four scans were not launched.
At that checkpoint, another unchanged scan retry was not justified until provider
capacity recovered.

A later isolated recovery attempt at
`.agent/main/evaluation-strategy-serial-recovery/` retried only
`negative-ingestion`, with `--n-concurrent 1` and no other evaluation process.
It finished with 1/2 scored: a required `goal_accuracy` judge still returned
Azure HTTP 429. The installed container grader invokes accuracy, goal and
behavior judges sequentially; there is no additional parallel judge pool to
disable. This confirmed provider capacity was a blocker beyond scanner
fan-out. No model, token budget, grading criterion or required judge was changed.

After the owner requested another retry, three sequential selected-case runs
completed with `execution_status: succeeded`, `report_status: complete`, both
required arms scored and no execution errors:

- `.agent/main/evaluation-strategy-retry-20260918T050020Z/`:
  `negative-ingestion`, 2/2. Accuracy and behavior are 1.0 in both arms; goal
  accuracy is 0.90 with the skill and 0.75 without it. Both correctly route the
  task to data ingestion and avoid strategy/order work. Goal deductions again
  concern the exact name of a sibling skill absent from the isolated inventory.
- `.agent/main/evaluation-actors-retry-20260918T050521Z/`:
  `negative-order-owner`, 2/2. Accuracy and goal accuracy are 1.0 in both arms;
  behavior is 0.50 in both. Advisory suggestion generation delayed CLI exit
  after the canonical reports were written, but ultimately finished with exit 0.
- `.agent/main/evaluation-data-retry-20260918T052055Z/`:
  `databento-node-bars`, 2/2. Accuracy, goal accuracy and behavior are 1.0 in
  both arms. The with-skill arm scores 1.0 on all six metrics; the baseline
  scores 0.50 for skill execution and 0.0893 for efficiency. Both distinguish
  factory-node support from direct-client symbology, reject unsupported live
  external bars, and recommend dated instruments with internal aggregation.
  Neither connects to a provider or broker.

These are complete subset reports, not replacement six-attempt aggregate
reports. They establish recovery for those calls, not sustained provider capacity
or completion of the remaining static scans. The historical failures remain intact.

The subsequent owner-requested Tier 1 resume retried only the failed actor static
stage; the completed rubric was reused with matching runner and snapshot identity.
Attempt `static/2-1789709386361756000` in
`.agent/main/evaluation-author-limited-building-nautilus-actors/` again finished
with exit 1 and `incomplete_scans: ["skillspector-llm"]`. Ten of eleven validators
passed; the security validator reports scanner exit 2 with redacted diagnostics.
It is an incomplete scan, not a clean security verdict.

A separate serialized diagnostic at
`.agent/main/scanner-probe/actor-owner-retry-diagnostic.log` reproduces scanner
exit 2. This time its meta-analyzer reports a connection error for
`references/adapter-development.md`, with one of two batches failed and incomplete
semantic runtime telemetry. It retains findings without a full LLM verdict.
Unlike the earlier diagnostics, this log does not report HTTP 429; the underlying
connection failure was not established. Model-registry fallback warnings also
appear, but do not prove the cause of the connection error. No scanner, judge,
model or numeric budget was changed. The remaining four static scans were not
launched after this failure; full qualification remains incomplete.

The old wrapper incorrectly labels the complete backtest and live reports incomplete.
The repaired completion checker accepts its canonical 6/6 report, deduplicating
the `latest` alias, and correctly rejects the strategies 5/6 report. Raw receipts
are unchanged. Backtest goal scores cannot establish a genuine regression:
the old `chunk-memory` expectation penalizes source-correct lazy merging, and
negative cases expect an unavailable sibling skill in an isolated inventory.
No score was silently recalculated after correcting that expectation.

Container handoff traces identify EOF-dependent `cat` waiting after a complete
943-byte script was received. The exact Docker/Compose race remains unproven:
40 direct nonsecret stdin probes succeeded. The isolated runner now sends the
payload byte count, reads that many bytes and fails closed on short input.
Credentials remain stdin-only; private permissions, ownership and cleanup are
unchanged. Harbor children now import the same reviewed vendor copy instead of
silently falling back to the global evaluator. Tests cover both boundaries.

The original baseline has finished. Separate retries retain their own snapshots:

- `.agent/main/evaluation-actors-fixed/`: setup recovered, 5/6 scored, remaining
  `negative-order-owner` judge failed with 429.
- `.agent/main/evaluation-strategy-case-fixed/`: both `negative-ingestion` agents
  reached grading, 0/2 scored because required judges returned 429.
- `.agent/main/evaluation-deployment-case-fixed/`: `persistent-scaffold` completed
  both arms, 2/2 scored. This is a subset result, not a new complete 6/6 report.
- `.agent/main/evaluation-fixed-preflight/`: all six strict datasets passed.

## Completed-report review

Backtest's old catalog-memory expectation is stale; its negative cases also ask
for an exact sibling name absent from the isolated inventory. Scores remain
unchanged, and no generic skill instructions were added to game those judges.
Strategies' cancel/fill race receives full relevant credit; native bracket and
data provider-timestamp behavior deductions cite truncated evidence despite
accuracy/goal credit. They do not establish omitted safeguards.

The actor selected-case retry preserves the order-free actor boundary. Its
behavior judge deducts credit for assigning capital reservations to shared risk
rather than explicitly assigning strategy-specific reservations to Strategy.
The generated advisory suggestions then recommend that same shared-authority
design and forbid Strategy-owned reservation ledgers. This is a confirmed
rubric/advice inconsistency, not evidence that either universal ownership rule
belongs in the actor skill. Keep the scores and review strategy-local commitment
tracking separately from account-wide allocation in a future source-grounded
comparison; do not add a compulsory shared-capital subsystem to game this case.

Live's 6/6 report gives with-skill accuracy 1.0, goal 0.9 and behavior 0.6944;
without-skill values are 1.0, 1.0 and 0.8056. Inspecting individual rationales
shows construction/readiness deductions cite truncated risk/IB evidence, while
the negative case penalizes not naming the absent actor skill. This does not
establish a runtime-safety regression or justify rewriting the entrypoint.

Deployment's successful subset gives accuracy 1.0 in both arms, goal 0.85/0.90
and behavior 0.50/0.25 (with/without). Both agents explicitly lacked the existing
strategy source needed for native wiring/compilation. The with-skill scaffold
preserved separate storage roles, run isolation and no-deployment boundaries.
Unproven native integration remains an acceptance gap, not a claimed pass.
The original without-skill security deduction identified an official Terraform
download command, not an upload; that evidence does not establish exfiltration.

Earlier required judge failures in actor/strategy/data retries and the interrupted
autoreview are confirmed shared-provider 429s. The latest three behavior subsets
completed, while the scanner diagnostic instead reports a connection failure.
Concurrency contributed load but
the exact quota and other clients' activity were not measured. Serialize remaining
retries, preserve paired cases and stop if throttling persists rather than
silently dropping judges or changing models/budgets.

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
- The earlier 69 maintenance tests passed, as did generated-resource drift and pinned
  source/hash checks, the official plugin validator and all six skill validators.
  The first plugin-validator invocation lacked PyYAML in system Python; rerunning
  with the existing evaluator Python passed without installing anything globally.
- Final read-only autoreview found no actionable bugs in the token patches,
  report-completeness checks or streaming corrections. It compared the latter
  with the installed 0.64.0 registry source; the separate forward test inspected
  the pinned checkout. Evidence: `.agent/main/autoreview-final.jsonl`.
- Current revision: all 77 maintenance tests, both scanner-patch tests, official
  plugin and six skill validators, generated-resource drift and pinned-source
  checks pass. A package-escaping build-log link found by relocation tests was
  changed to a plain repository-relative locator; historical results are intact.
- The retry-fix autoreview reached code inspection but exhausted Azure 429
  reconnects. `.agent/main/autoreview-retry-fixes.jsonl` is not a completed review.
- The subsequent read-only `.agent/main/autoreview-current.jsonl` completed. It
  identified that explicit native Harbor sources bypassed JSON case filtering.
  The runner now rejects that unsupported selection (including missing JSON)
  before any evaluation; regressions cover both endpoint configurations and
  unchanged source. The review found no other actionable issue in the scoped
  runner changes. Its model-list refresh warning did not prevent completion.
- Reinstalled `0.64.0+codex.20260918014415` in the existing isolated Codex test
  home. The approved author is present in all six installed skill files, and
  the manifest carries the same name/email. This is a metadata/cache check,
  not a second claim of fresh end-to-end onboarding.

## Continue and stop boundaries

Do not rerun complete trials to compensate for a wrapper classification defect.
Inspect the retained failing phase before selectively retrying incomplete trials.
Use new output directories for changed skill/dataset/runner identities; do not
edit historical run specifications to bypass resume checks. Reused cases are
regressions, not fresh holdouts. Keep numeric token budgets and paired coverage.

The previously missing behavior cases now have separate complete paired retry
reports; no aggregate report or historical score has been rewritten. Full
qualification remains open until the actor LLM scan completes and the remaining
four Tier 1 scans are retried and reviewed. The later repository push and PR
authorization does not change these evaluation results. OpenAI marketplace
submission, cloud deployment, broker access and strategy-project changes remain
out of scope.
