# Nautilus Trader plugin: adversarial instruction audit

Date: 2026-09-18. Baseline: `kmshdev/plugins` commit
`b8b32b74be21c2b7f83d8dd394e79d9c345175c4`, extracted locally with plugin-creator.
Publication is not authorized. Findings below distinguish inspected defects,
predicted interactions and retained intentional constraints. This is not a claim
that every upstream file, session or external plugin reference was reviewed.

## Highest-impact findings

### 1. Stale materialization advice and grading expectation — confirmed

Files: `plugins/nautilus-trader/references/market-data.md`, catalog replay;
`references/pitfalls.md`; data/backtesting skill `references/guide.md`;
`evals/workflows.json`, `chunk-memory`.

Excerpt: “Multiple configs are fully loaded and merged before chunk execution”.
The pinned source and installed registry crate instead implement a lazy
`run_streaming`/`merge_streams` path (`crates/backtest/src/node.rs:403-466`).
The evaluator penalized an agent for correcting this stale claim. The transcript
contains its actual source fetch; the judge's assertion of no recorded source
inspection was also wrong.

Disposition: clarify boundary; fixed. Exact replacement core:

> With `chunk_size=Some(...)`, native catalog iterators are merged lazily across
> data configs, retaining one lookahead item per stream. Equal timestamps retain
> config order. The non-chunked path loads data before running; dynamic custom
> queries separately materialize `Vec<Data>`.

Retain the warning that equal-time expansion, query buffers and retained engine
state prevent a hard RAM guarantee. Correct the dataset expectation, regenerate
the portable case, and preserve old scores as evidence of the old expectation,
not valid measurements of the corrected revision. Source/hash validation alone
did not detect stale prose: inspect the cited behavior before accepting a grade.

### 2. Evaluation receipts incorrectly reject completed paired reports — confirmed

File: `plugins/nautilus-trader/scripts/run_skill_eval.py`,
`complete_tier3` and `behavior_report_complete`.

Excerpts: `any(agent.get(key) for key in (...))` and
`results = list(reports.glob("*/*/result.json"))`.

SkillEvaluator 0.2.1 returns nonempty dictionaries containing empty per-arm
failure lists/strings. Their dictionaries are truthy even when both arms passed.
Its `latest` symlink also exposes the same report twice to the glob. The completed
backtesting run was consequently labeled incomplete, inviting unnecessary paid
retries. Neither defect establishes a skill-content failure.

Disposition: clarify boundary; fixed. Inspect each arm's values, reject unexpected
arm keys, resolve aliases to one canonical in-directory report, and retain all
coverage/score/status gates. Tests cover empty maps, either failing arm, unknown
arms, aliases, multiple runs and incomplete results. Historical raw results are
not rewritten or silently rescored.

### 3. Environment mismatch prevents meaningful evaluation — confirmed

File: `plugins/nautilus-trader/scripts/run_skill_eval.py`, `docker_ready`,
`prepare_vendor`, CLI options; `evals/README.md`, reproduction instructions.

Excerpt: Docker preflight previously omitted `env=environment`; the evaluator
selected `max_tokens` for the qualified Azure route, which returned HTTP 400.

Disposition: clarify boundary; fixed. Pass the selected environment to Docker
preflight. Add explicit `--completion-token-key {max_tokens,max_completion_tokens}`
to isolated host/container selectors, keeping numeric budgets and recording the
setting in the resume identity. Concrete scanner executables avoid an unselected
Gitleaks shim. The global evaluator and global tools are not patched.
Patch preparation requires a fresh, exact reviewed source block; already-patched
or changed source is rejected rather than accepted through a substring match.

Preserved constraint: endpoint compatibility is not permission to alter grading,
remove runtime preflight, combine incomplete arms or suppress scanner findings.

### 4. Collection Tier 2 ran after Tier 3 — confirmed

File: `plugins/nautilus-trader/scripts/run_skill_eval.py`, `stages`;
`evals/README.md`, workflow ordering.

Excerpt: collection `descriptions` / `full-body` stages were appended after the
per-skill loop containing behavior evaluation.

Disposition: clarify boundary; fixed. Schedule all Tier 1, all Tier 2 including
collection checks, then Tier 3. Preserve diagnostic continuation after findings,
strict dataset gates, separate outputs and both behavioral arms.

### 5. Installation and publication metadata drift — confirmed

Files: root `README.md`; `plugins/nautilus-trader/README.md`, installation;
`.codex-plugin/plugin.json`, publication URLs; `decisions/003-codex-plugin.md`.

Excerpt: the old installation text described the sixth skill as awaiting merge
and used the source monorepo marketplace. The standalone package still advertised
that monorepo as its destination.

Disposition: shorten/clarify boundary; fixed. Local instructions now read:

```sh
codex plugin marketplace add .
codex plugin add nautilus-trader@nautilus-trader --json
```

Run from the standalone repository root; start a new thread. Preserve source
lineage and the existing MIT license. Omit public repository/homepage fields
until publication is reviewed; retain the author identity. No remote is created.

### 6. Documentation sweep may amplify a small task — hypothesis

Location: user-supplied Global Working Agreements, “Sweep docs at checkpoints”.
Excerpt: “Whenever a documentation pass is needed, review the codebase in full”.

A typo can activate a repository-wide review despite the separate direction to
avoid unnecessary testing and scope creep. This is user-owned policy, not plugin
authority; no setting or agreement is changed here.

Disposition: narrow trigger. Proposed replacement for user review:

> At documentation checkpoints, inspect implementation and documentation affected
> by the change, including linked contracts and examples. Expand repository-wide
> when the change alters shared architecture or exposes systemic drift. Record
> coverage and unresolved gaps; verify edited claims against implementation.

Preserves current, implementation-grounded docs without requiring unrelated
reading for every wording change. Compare a typo task and a shared-architecture
task before adopting it. The identical beta-phase paragraph appears twice in
the supplied agreements; keep one unchanged copy, if the owner approves.

### 7. Two evaluator diagnostics are not plugin defects — confirmed

Locations: installed SkillEvaluator 0.2.1 `validators/rubric_eval.py`, prompt
construction; isolated SkillSpector 2.11.2, reference resolution/reporting.

Rubric excerpt: `SKILL.md Content:\n---\n{skill_content}\n---`. The wrapper places
an extra delimiter immediately before the skill's valid YAML opening. Five
rubric reports then diagnose an empty frontmatter block. The actual source has
one opening delimiter and passes the official skill validator. Referenced assets
omitted/truncated from the judge's input are also not proof of missing files.

SkillSpector reports `reference_unresolved` on the metadata version line
`version: "0.64.0"`, causing LOW risk plus CAUTION and incomplete coverage.
A two-fixture local experiment reproduces this: including that version gives
partial coverage; removing only that line gives complete coverage and SAFE.
The evaluator rejects the severity/recommendation combination before LLM
enrichment. Do not remove useful version metadata to game this scanner.

Disposition: investigate upstream removal/correction, not skill rewriting.
Proposed rubric fix for a separately qualified evaluator revision: use labeled
XML-like document boundaries instead of additional YAML delimiters. Proposed
scanner fix: parse frontmatter scalars and exclude semantic-version metadata from
local-file reference candidates, while retaining actual linked-path checks.
Neither external tool patch is applied here; raw failures remain visible.

The additional NVIDIA author policy requires `Name <email@host>` while the
skills identify `kmshdev`. Preserve the real author; request an approved contact
before a submission profile requiring email. Do not invent one. None of these
observations establishes a completed security scan.

## Inventory, loading and authority

| Layer | Inspected coverage | Loading / scope |
| --- | --- | --- |
| Current system/developer and user agreements | Supplied instructions | Always in this session; plugin text cannot override them |
| Local repository instructions | No applicable filesystem AGENTS found in the inspected repository/parents | Not evidence that all machine-wide configuration was inspected |
| Manifest and marketplace | Both complete files | Discovery and installation metadata, not operating authorization |
| Six SKILL.md entrypoints | All complete bodies and descriptions | Discovery metadata is available to selection; body is read on selection |
| Six agents/openai.yaml files | All | Appearance and implicit-invocation metadata; not custom subagents |
| Shared references | Foundation, architecture, version/integration, testing, workflow and storage/delivery references; source evidence and examples as relevant | Conditional linked content, not all always loaded |
| Maintenance layer | Resource generator, evaluation runner and associated tests; scaffold and storage implementation | Development/verification, not ordinary task prerequisites |
| Package inventory | 226 initial package files, 107 Markdown files | Inventory is not line-by-line review of all files |
| Upstream Nautilus | Version-qualified source contracts and hashes from the pinned 0.64.0 checkout | Selected implementation paths, not a whole-upstream audit |
| Session evidence | Fresh isolated onboarding transcript, retained evaluation reports and historical build/review notes | No exhaustive strategy-session timeline was reconstructed in this standalone pass |
| External exemplars | Manifests, structures, discovery headers and selected bodies listed below | Not every linked reference or executable asset |

Platform precedence remains system → developer → user → scoped project guidance;
more-specific project guidance governs its subtree without overruling higher
authority. A selected skill supplies task procedure, not approval to trade,
discover credentials, publish images, migrate a database or deploy.

The runtime package has six directly selectable skills, no root router, no custom
subagent pipeline, no hooks and no MCP service. Adding any of those would add
complexity without a demonstrated missing capability. Generated duplicate
references preserve independent skill portability. On-disk duplication is not
automatically duplicated context. Change canonical references and regenerate;
do not hand-edit each child copy.

Access/coverage gaps: no complete machine-wide instruction inventory, no hidden
host-routing internals, no exhaustive strategy-session scan, no physical broker
or cloud validation, and no full inspection of every exemplar reference. Earlier
session conclusions in retained notes are historical evidence, not fresh proof.

## Skill descriptions and entrypoints

| Skill | Selection boundary | Finding / disposition |
| --- | --- | --- |
| building-nautilus-actors | Signal/observer actors, no order ownership | Keep |
| building-nautilus-strategies | Strategy-owned orders and execution state | Keep |
| backtesting-nautilus-strategies | Replay, fills, economics; excludes broker ops and generic tooling | Keep |
| integrating-nautilus-data | Instrument identity, ingestion, subscriptions, codecs/catalogs | Keep |
| running-nautilus-live | Runtime composition, readiness, reconciliation and shutdown | Keep; runtime persistence can legitimately intersect delivery |
| deploying-nautilus-runs | CI/container/cloud storage and independent run delivery | Keep; explicitly excludes unrelated infrastructure and trading rules |

No evidence supports rewriting these descriptions solely to satisfy generic
lexical heuristics. Their entrypoints are already short: measured word counts
were respectively 329, 317, 340, 355, 360 and 389. No context saving is claimed.
The live/deployment persistence overlap is an integration boundary, not proof of
duplicate skills. Test routing with requests that separately ask for runtime
capture and container delivery before narrowing it further.

Each body identifies inputs/outputs, a bounded workflow, task-specific references
and completion evidence. Optional source/version checks are scoped to upgrades
and workarounds. Keep native dispatch, chronology, order ownership, source
identity and persistence readback procedures: removing those would discard
correctness constraints, not repay instruction debt.

Completion is already explicit in `references/version-and-integration.md`:
“For implementation requests, continue from diagnosis through the local change
and meaningful checks”; review/proposal requests do not authorize edits. Keep
passing checks for unchanged code. Complete independent work before requesting
the missing authorization, entitlement or product decision.

## Lessons from the example plugins

Inspected revision: `openai/plugins`
`1dc195897af4161d039b80d8471ec0a10c9bbc89`.

| Example | Observed design | Decision |
| --- | --- | --- |
| Expo | Narrow Expo/EAS CI skill and schema-specific validation; a different data-fetching skill uses an overbroad “ANY network request” trigger | Borrow boundary-specific verification, not broad mandatory activation |
| Hyperframes | Large discovery description and visual-identity gate; CLI workflow uses lint, rendered inspection and output evidence | Borrow evidence at the actual changed boundary; do not impose UI-style gates on Rust-only work |
| Remotion | Best-practices router to specialist references; map guidance selects one self-contained technique | Keep selective disclosure; six directly selectable Nautilus workflows do not need another router |

## Paper interaction walkthroughs

These are hypotheses, not executed tasks or measured routing accuracy.

| Request | Activated instructions and reading | Actions / approval boundary / stopping condition |
| --- | --- | --- |
| Typo fix | Global agreements and affected document; no Nautilus workflow solely because the repository uses trading crates | Correct wording, inspect diff/links; no execution approval needed. Finish after focused verification. Full-codebase docs wording may unnecessarily expand this task |
| Database migration | Deployment skill only for Nautilus run persistence; storage/delivery plus application migration policy | Inspect native schema/DB ownership, prepare requested migration and relevant validation. Explicit authorization before applying it. Redis flush is not drain; PostgreSQL isolation cannot be assumed from a namespace setting. Finish proposal-only work without applying it |
| UI change needing visual inspection | Project UI guidance; no Nautilus skill for an unrelated UI | Implement and inspect actual UI at the affected states; do not substitute Rust compile output for visual evidence. Finish with observed checks or state blocked browser/access. Plugin does not supply a generic visual-testing workflow |
| Failing local test | Generic tooling failures do not trigger backtesting; runtime dispatch failure selects owning actor/strategy skill and relevant test reference | Diagnose and fix in scope, rerun focused failing check and required gates. No provider access for a synthetic reproducer. Finish on validated correction; report unrelated failures rather than launching unlimited broader tests |
| Deployment requiring approval | Deployment skill; delivery/storage guide, live skill only if native runtime changes | Scaffold/build offline, then pause before cloud writes, migration, image publication or live trading. Finish authorized local work and identify exact withheld action. Approval for an image push does not authorize a broker session |

## Smallest useful cleanup batch and checks

1. Keep the standalone packaging/install corrections; verify the actual fresh
   entry point, not only manifest syntax.
2. Keep evaluator environment, ordering and result-classification fixes; validate
   them against actual reports and focused regressions. Do not repeatedly pay to
   rerun a completed case because a wrapper misclassified it.
3. Correct the catalog streaming claim and stale grading expectation, retaining
   the original evidence rather than rescoring it silently.
4. Retain all six runtime skills and conditional reference architecture. Do not
   add a router, subagents, mandatory full-source reading or a new production gate.
5. Leave user agreements and author-contact policy decisions for owner review.

Fresh onboarding succeeded using only the local installation guidance and an
isolated Codex home with the authorized Azure profile: automatic actor selection,
`cargo test --locked --offline` (2 passed), and an executed observer reporting
`inputs=5 quotes=4 signals=1 orders=0 positions=0`. The Rust prerequisite was
handled with the already-installed required toolchain in the project. There were
no copied login files, provider connections or orders. Host/toolchain and Cargo
caches were not made pristine; this is isolated Codex onboarding, not a clean OS.

Compare description routing on the same positive/negative requests before and
after any later rewrite; measure files actually loaded rather than directory
size. Treat reused working/acceptance prompts as regressions, not fresh holdouts.
NVIDIA scanner policy failures, rubric-input artifacts, unavailable services and
incomplete paired trials must remain visible in the separate evaluation receipt.
