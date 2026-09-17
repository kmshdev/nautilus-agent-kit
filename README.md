# Nautilus Trader for Codex

An independent Codex plugin for NautilusTrader 0.64.0 Rust workflows:
actors, strategies, data, backtests, live nodes, and persistent run delivery.

## Install from this checkout

Run from the repository root:

```sh
codex plugin marketplace add .
codex plugin add nautilus-trader@nautilus-trader --json
```

Start a new Codex thread, then ask for a Nautilus Rust task. Agent execution
requires your own Codex login or configured model-provider profile. Installation
does not provide credentials, connect to a broker, or deploy infrastructure.

See the [plugin guide](plugins/nautilus-trader/README.md) for examples and
verification, and the [evaluation contract](plugins/nautilus-trader/evals/README.md)
for NVIDIA SkillEvaluator requirements.

The [adversarial audit](docs/adversarial-audit.md) records findings, intentional
constraints, instruction coverage and verification limits.
The [evaluation retry receipt](docs/evaluation-retry.md) separates successful
checks from scanner failures and incomplete behavioral runs.

## Provenance and layout

Extracted from `kmshdev/plugins` commit
`b8b32b74be21c2b7f83d8dd394e79d9c345175c4`. The existing
MIT license is retained. NautilusTrader dependencies retain their own licenses.
This is community-maintained, not an official NautilusTrader or OpenAI plugin.

The single `plugins/nautilus-trader/` package and repository marketplace follow
the Codex plugin-creator layout. The six skills are independently copyable;
there is no mandatory router, custom subagent, service, or hidden checkout.

## Maintain

```sh
cd plugins/nautilus-trader
python3 scripts/sync_resources.py --check
python3 scripts/check.py
uv run --with-requirements scripts/requirements-maintenance.txt python -m unittest discover -s scripts -p 'test_*.py'
```

Keep scratch evidence under the ignored, branch-specific `.agent/main/`.
No public submission is made by creating this checkout.
