"""Offline runner regressions; use the existing SkillEvaluator interpreter for YAML."""

from __future__ import annotations

import argparse
import ast
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_skill_eval as runner


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="skill-runner-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def skill(self, name: str = "arbitrary-python-skill") -> Path:
        root = self.root / "skills" / name
        root.mkdir(parents=True)
        (root / "SKILL.md").write_text(f"---\nname: {name}\ndescription: A test skill.\n---\nDo the task.\n")
        (root / "evals").mkdir()
        for filename in ("evals.json", "acceptance.json", "fresh-v2.json"):
            (root / "evals" / filename).write_text(json.dumps({
                "skill_name": name, "evals": [{"id": filename, "prompt": "Synthetic test"}],
            }))
        return root

    def result(self) -> dict:
        scores = {dimension: 0.0 for dimension in runner.DIMENSIONS}
        return {
            "execution_status": "succeeded", "report_status": "complete",
            "expected_attempts": 2, "scored_attempts": 2,
            "agents": {"opencode": {
                "execution_status": "succeeded", "num_trials_with": 1, "num_trials_without": 1,
                "with_skill": scores.copy(), "without_skill": scores.copy(), "execution_errors": [],
                "agent_runtime_failures": {"with_skill": [], "without_skill": []},
                "trial_failures": {"with_skill": [], "without_skill": []},
                "job_failures": {"with_skill": "", "without_skill": ""},
            }},
        }

    def test_discovers_unrelated_new_skills_without_name_list(self) -> None:
        first, second = self.skill(), self.skill("writing-sql")
        self.assertEqual(runner.discover([self.root / "skills"]), sorted([first.resolve(), second.resolve()]))
        self.assertEqual(runner.skill_name(first), "arbitrary-python-skill")

    def test_discovery_stops_at_skill_boundary(self) -> None:
        skill = self.skill()
        nested = skill / "assets" / "template"
        nested.mkdir(parents=True)
        (nested / "SKILL.md").write_text("A template, not an installed skill")
        self.assertEqual(runner.discover([self.root / "skills"]), [skill.resolve()])

    def test_ambiguous_plugin_root_requires_explicit_choice(self) -> None:
        self.skill()
        (self.root / "SKILL.md").write_text("legacy")
        with self.assertRaisesRegex(ValueError, "Choose"):
            runner.discover([self.root])

    def test_rejects_symlink_and_credentials_before_copy(self) -> None:
        skill = self.skill()
        (skill / "escape").symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, "Symlinks"):
            runner.files(skill)
        (skill / "escape").unlink()
        (skill / ".env.private").write_text("DO_NOT_COPY=synthetic")
        with self.assertRaisesRegex(ValueError, "Credential-like"):
            runner.files(skill)

    def test_content_fingerprint_not_mtime(self) -> None:
        skill = self.skill()
        before = runner.tree_digest(skill)
        os.utime(skill / "SKILL.md", None)
        self.assertEqual(before, runner.tree_digest(skill))
        (skill / "SKILL.md").write_text("Different")
        self.assertNotEqual(before, runner.tree_digest(skill))

    def test_transient_build_output_excluded(self) -> None:
        skill = self.skill()
        before = runner.tree_digest(skill)
        (skill / "target").mkdir()
        (skill / "target" / "compiled").write_text("not an input")
        self.assertEqual(before, runner.tree_digest(skill))

    def test_patch_requires_clean_reviewed_source(self) -> None:
        for old, new in runner.PATCHES.values():
            self.assertEqual(runner.patch_source(old, old, new), new)
            with self.assertRaises(ValueError):
                runner.patch_source(new, old, new)
            with self.assertRaises(ValueError):
                runner.patch_source("changed upstream", old, new)

    def test_neon_and_native_routes(self) -> None:
        self.assertEqual(runner.agent_base("https://unit.neon.tech/v1", "auto", None),
                         "https://unit.neon.tech/openai/v1")
        self.assertEqual(runner.agent_base("https://unit.example/v1", "neon", None),
                         "https://unit.example/openai/v1")
        self.assertIsNone(runner.agent_base("https://api.openai.com/v1", "auto", None))
        self.assertIsNone(runner.agent_base("https://unit.neon.tech/v1", "none", None))

    def test_explicit_token_key_preserves_numeric_budget(self) -> None:
        for filename, (old, template) in runner.TOKEN_LIMIT_SELECTORS.items():
            for key in ("max_tokens", "max_completion_tokens"):
                patched = runner.patch_source(old, old, template.replace("TOKEN_KEY", key))
                namespace = {}
                if filename == "inference/client.py":
                    exec("from __future__ import annotations\n" + patched, namespace)
                    self.assertEqual(namespace["_token_limit_kwargs"](None, 1024), {key: 1024})
                    self.assertEqual(namespace["_token_limit_kwargs"](None, None), {})
                else:
                    exec("def payload(max_tokens):\n" + patched + "\n    return {token_key: max_tokens}", namespace)
                    self.assertEqual(namespace["payload"](1024), {key: 1024})
                with self.assertRaises(ValueError):
                    runner.patch_source(patched, old, template.replace("TOKEN_KEY", key))

    def handoff_command(self) -> str:
        replacement = runner.PATCHES["tier3/harbor/secure_docker_environment.py"][1]
        line = next(line.strip() for line in replacement.splitlines() if "umask 077;" in line)
        return ast.literal_eval(line.rstrip(","))

    def test_handoff_completes_without_eof_and_preserves_private_exact_bytes(self) -> None:
        payload = "export SYNTHETIC='Unicode λ and quotes'\n".encode()
        target = self.root / "handoff.sh"
        process = subprocess.Popen(
            ["sh", "-c", self.handoff_command(), "sh", str(target), str(len(payload))],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            process.stdin.write(payload)
            process.stdin.flush()
            self.assertEqual(process.wait(timeout=3), 0)
            self.assertFalse(process.stdin.closed)
            self.assertEqual(target.read_bytes(), payload)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate()

    def test_handoff_rejects_truncated_payload(self) -> None:
        target = self.root / "handoff.sh"
        result = subprocess.run(
            ["sh", "-c", self.handoff_command(), "sh", str(target), "100"],
            input=b"too short", capture_output=True, timeout=3,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_scanner_concurrency_allowlist_does_not_forward_arbitrary_environment(self) -> None:
        replacement = runner.PATCHES["validators/security.py"][1]
        namespace = {}
        exec(replacement + '\n        "PATH",\n    }\n)', namespace)
        allowed = namespace["_SKILLSPECTOR_PROCESS_ENV_NAMES"]
        environment = {"SKILLSPECTOR_MAX_LLM_CONCURRENCY": "1", "PATH": "/retained", "UNRELATED_SECRET": "private"}
        self.assertEqual({key: value for key, value in environment.items() if key in allowed},
                         {"SKILLSPECTOR_MAX_LLM_CONCURRENCY": "1", "PATH": "/retained"})

    def test_harbor_uses_current_vendor_not_ambient_pythonpath(self) -> None:
        replacement = runner.PATCHES["tier3/harbor/runner.py"][1]
        body = replacement.split("\n\ndef ", 1)[0]
        source = self.root / "vendor/skillevaluator/tier3/harbor/runner.py"
        namespace = {"Path": Path, "__file__": str(source)}
        exec("def build(environment):\n" + body, namespace)
        result = namespace["build"]({"PYTHONPATH": "/untrusted", "PATH": "/retained"})
        self.assertEqual(result, {"PYTHONPATH": str((self.root / "vendor").resolve()), "PATH": "/retained"})

    def test_case_retry_stages_only_requested_cases_without_changing_source(self) -> None:
        skill = self.skill()
        dataset = skill / "evals/evals.json"
        data = json.loads(dataset.read_text())
        data["evals"].append({"id": "second", "prompt": "Another case"})
        dataset.write_text(json.dumps(data))
        before = runner.tree_digest(skill)
        target = self.root / "subset"
        runner.stage_skill(skill, target, "working", True, None, ["second"])
        staged = json.loads((target / "evals/evals.json").read_text())
        self.assertEqual(staged["evals"], [data["evals"][1]])
        self.assertEqual(runner.tree_digest(skill), before)
        with self.assertRaisesRegex(ValueError, "Unknown --case-id"):
            runner.stage_skill(skill, self.root / "invalid", "working", True, None, ["missing"])

    def test_case_retry_accepts_upstream_integer_ids(self) -> None:
        skill = self.skill()
        dataset = skill / "evals/evals.json"
        data = json.loads(dataset.read_text())
        data["evals"][0]["id"] = 42
        dataset.write_text(json.dumps(data))
        target = self.root / "numeric-subset"
        runner.stage_skill(skill, target, "working", True, None, ["42"])
        self.assertEqual(json.loads((target / "evals/evals.json").read_text())["evals"], data["evals"])

    def test_case_retry_rejects_native_tasks_with_or_without_endpoint_override(self) -> None:
        skill = self.skill()
        (skill / "evals/config.yaml").write_text("harbor:\n  task_source: native_harbor\n")
        before = runner.tree_digest(skill)
        for index, base in enumerate([None, "https://unit.example/v1"]):
            with self.subTest(base=base), self.assertRaisesRegex(ValueError, "native_harbor"):
                runner.stage_skill(skill, self.root / f"native-{index}", "working", True, base, ["evals.json"])
        self.assertEqual(runner.tree_digest(skill), before)

    def test_case_retry_rejects_missing_json_before_native_fallback(self) -> None:
        with self.assertRaisesRegex(ValueError, "existing JSON dataset"):
            runner.stage_skill(self.skill(), self.root / "missing", "missing.json", True, None, ["42"])

    def test_token_override_rejects_changed_selector_with_matching_return(self) -> None:
        old, template = runner.TOKEN_LIMIT_SELECTORS["inference/client.py"]
        changed = old.replace('startswith("gpt-5")', 'startswith("gpt-6")')
        for key in ("max_tokens", "max_completion_tokens"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                runner.patch_source(changed, old, template.replace("TOKEN_KEY", key))
        for filename, (old, template) in runner.TOKEN_LIMIT_SELECTORS.items():
            if filename == "inference/client.py":
                continue
            changed = '    token_key = "max_tokens" if condition else "max_completion_tokens"'
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                runner.patch_source(changed, old, template.replace("TOKEN_KEY", "max_tokens"))

    def test_override_rejects_cross_origin_and_embedded_credentials(self) -> None:
        for destination in ("https://other.example/v1", "https://secret@unit.example/v1",
                            "https://unit.example/v1?key=secret"):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                runner.agent_base("https://unit.example/v1", "none", destination)

    def test_custom_dataset_staging_preserves_source_and_runtime_config(self) -> None:
        skill = self.skill()
        config = {"schema_version": 1, "harbor": {"runtime_env": {
            "OTHER_INPUT": "retained", "OPENCODE_CONFIG_CONTENT": json.dumps({
                "provider": {"openai": {"options": {"timeout": 123}}}, "theme": "test",
            }),
        }}}
        (skill / "evals/config.yml").write_text(json.dumps(config))
        before = runner.tree_digest(skill)
        target = self.root / "copy"
        runner.stage_skill(skill, target, "evals/fresh-v2.json", True, "https://unit.example/openai/v1")
        self.assertEqual(before, runner.tree_digest(skill))
        self.assertFalse((target / "evals/acceptance.json").exists())
        self.assertFalse((target / "evals/fresh-v2.json").exists())
        self.assertEqual(json.loads((target / "evals/evals.json").read_text())["evals"][0]["id"], "fresh-v2.json")
        import yaml
        runtime = yaml.safe_load((target / "evals/config.yml").read_text())["harbor"]["runtime_env"]
        self.assertEqual(runtime["OTHER_INPUT"], "retained")
        options = json.loads(runtime["OPENCODE_CONFIG_CONTENT"])["provider"]["openai"]["options"]
        self.assertEqual(options["timeout"], 123)
        self.assertEqual(options["apiKey"], "{env:OPENAI_API_KEY}")

    def test_missing_requested_dataset_cannot_fall_back_to_working(self) -> None:
        target = self.root / "copy"
        runner.stage_skill(self.skill(), target, "evals/missing.json", True, None)
        self.assertFalse((target / "evals/evals.json").exists())

    def test_dataset_escape_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "inside"):
            runner.stage_skill(self.skill(), self.root / "copy", "../outside.json", True, None)

    def test_non_tier3_skill_does_not_need_evaluations(self) -> None:
        skill = self.skill()
        for path in (skill / "evals").iterdir():
            path.unlink()
        (skill / "evals").rmdir()
        runner.stage_skill(skill, self.root / "copy", "working", False, None)
        self.assertTrue((self.root / "copy/SKILL.md").exists())

    def test_conflicting_sdk_rejected(self) -> None:
        skill = self.skill()
        (skill / "evals/config.yml").write_text(json.dumps({"harbor": {"runtime_env": {
            "OPENCODE_CONFIG_CONTENT": json.dumps({"provider": {"openai": {"npm": "@ai-sdk/openai-compatible"}}}),
        }}}))
        with self.assertRaisesRegex(ValueError, "native OpenAI SDK"):
            runner.stage_skill(skill, self.root / "copy", "working", True, "https://unit.example/openai/v1")

    def test_low_scores_are_completed_results_not_infrastructure_failures(self) -> None:
        self.assertTrue(runner.complete_tier3(self.result(), 1))

    def test_partial_unpaired_missing_scores_and_errors_rejected(self) -> None:
        for mutate in (
            lambda r: r.update(scored_attempts=1),
            lambda r: r.update(report_status="partial"),
            lambda r: r["agents"]["opencode"].update(num_trials_without=0),
            lambda r: r["agents"]["opencode"]["with_skill"].pop("accuracy"),
            lambda r: r["agents"]["opencode"]["with_skill"].update(accuracy=float("nan")),
            lambda r: r["agents"]["opencode"].update(execution_errors=1),
        ):
            result = copy.deepcopy(self.result())
            mutate(result)
            self.assertFalse(runner.complete_tier3(result, 1))

    def test_paired_failure_maps_reject_errors_and_unknown_arms(self) -> None:
        for key in ("agent_runtime_failures", "job_failures", "trial_failures"):
            for arm in ("with_skill", "without_skill", "unexpected"):
                with self.subTest(key=key, arm=arm):
                    result = self.result()
                    result["agents"]["opencode"][key][arm] = "failed"
                    self.assertFalse(runner.complete_tier3(result, 1))
            result = self.result()
            result["agents"]["opencode"][key].pop("without_skill")
            self.assertFalse(runner.complete_tier3(result, 1))

    def test_malformed_failure_records_are_not_completed_results(self) -> None:
        for key in ("agent_runtime_failures", "job_failures", "trial_failures"):
            for value in (None, False, 0, {}, "" if key != "job_failures" else []):
                result = self.result()
                result["agents"]["opencode"][key]["with_skill"] = value
                with self.subTest(key=key, value=value):
                    self.assertFalse(runner.complete_tier3(result, 1))
        for value in (None, False, 0, {}, ""):
            result = self.result()
            result["agents"]["opencode"]["execution_errors"] = value
            self.assertFalse(runner.complete_tier3(result, 1))

    def test_malformed_report_containers_are_incomplete(self) -> None:
        for value in (None, [], "invalid"):
            result = self.result()
            result["agents"] = value
            self.assertFalse(runner.complete_tier3(result, 1))
            result = self.result()
            result["agents"]["opencode"] = value
            self.assertFalse(runner.complete_tier3(result, 1))
            for arm in ("with_skill", "without_skill"):
                result = self.result()
                result["agents"]["opencode"][arm] = value
                self.assertFalse(runner.complete_tier3(result, 1))

    def test_trial_json_is_not_a_second_canonical_report(self) -> None:
        canonical = self.root / "skill/run/result.json"
        canonical.parent.mkdir(parents=True)
        canonical.write_text(json.dumps(self.result()))
        (canonical.parent.parent / "latest").symlink_to(canonical.parent, target_is_directory=True)
        trial = canonical.parent / "opencode/with-skill/trials/test/result.json"
        trial.parent.mkdir(parents=True)
        trial.write_text("{}")
        self.assertTrue(runner.behavior_report_complete(self.root, 1))
        canonical.write_text("{broken")
        self.assertFalse(runner.behavior_report_complete(self.root, 1))

    def test_two_canonical_runs_cannot_be_combined(self) -> None:
        for run in ("run-one", "run-two"):
            path = self.root / "skill" / run / "result.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(self.result()))
        self.assertFalse(runner.behavior_report_complete(self.root, 1))

    def test_commands_preserve_baseline_preflight_and_scoring(self) -> None:
        args = argparse.Namespace(n_concurrent=1, timeout_multiplier=2.0)
        command = runner.evaluator_args("behavior", self.root, self.root / "out", "test-model",
                                        "openai/test-model", args)
        self.assertIn("skillevaluator.cli", command)
        self.assertIn("--agent-runtime-preflight", command)
        self.assertIn("--no-stop-on-pass", command)
        self.assertNotIn("--skip-baseline", command)
        self.assertNotIn("--copy-repo", command)
        self.assertNotIn("--autopilot", command)
        self.assertIn("isolated", command)

    def test_redacts_file_loaded_credentials_and_urls(self) -> None:
        value = runner.redact("key=synthetic-secret https://unit.example/v1 model=private-model",
                              {"SKILL_EVAL_LLM_API_KEY": "synthetic-secret", "SKILL_EVAL_LLM_MODEL": "private-model"})
        self.assertNotIn("synthetic-secret", value)
        self.assertNotIn("unit.example", value)
        self.assertNotIn("private-model", value)

    def test_real_subprocess_exit_and_redacted_log(self) -> None:
        output = self.root / "command"
        result = runner.command([sys.executable, "-c", "print('synthetic-secret'); raise SystemExit(7)"],
                                {**os.environ, "TEST_API_KEY": "synthetic-secret"}, output, 5)
        self.assertEqual(result["returncode"], 7)
        self.assertEqual(result["status"], "finished")
        self.assertNotIn("synthetic-secret", (output / "command.log").read_text())
        self.assertFalse((output / "stdout.private").exists())

    def test_real_subprocess_timeout_is_not_success(self) -> None:
        result = runner.command([sys.executable, "-c", "import time; time.sleep(60)"],
                                os.environ.copy(), self.root / "timeout", 0.1)
        self.assertEqual(result["status"], "timed_out")
        self.assertEqual(result["returncode"], 124)

    def test_docker_missing_is_explicit_unavailable(self) -> None:
        with patch.object(runner.subprocess, "run", side_effect=FileNotFoundError):
            self.assertFalse(runner.docker_ready())

    def test_stages_do_not_depend_on_five_workflow_names(self) -> None:
        skills = {"writing-sql": self.root / "skills/writing-sql"}
        kinds = [kind for _, kind, _ in runner.stages(skills, {"1", "2", "3"})]
        self.assertEqual(kinds, ["static", "rubric", "context", "strict", "behavior"])
        skills["making-pdfs"] = self.root / "skills/making-pdfs"
        kinds = [kind for _, kind, _ in runner.stages(skills, {"2"})]
        self.assertEqual(kinds, ["context", "context", "descriptions", "full-body"])

    def test_collection_checks_finish_before_behavioral_execution(self) -> None:
        skills = {name: self.root / "skills" / name for name in ("writing-sql", "making-pdfs")}
        tier = {"static": 1, "rubric": 1, "context": 2, "descriptions": 2,
                "full-body": 2, "strict": 3, "behavior": 3}
        sequence = [tier[kind] for _, kind, _ in runner.stages(skills, {"1", "2", "3"})]
        self.assertEqual(sequence, sorted(sequence))

    def test_docker_preflight_uses_selected_tool_environment(self) -> None:
        environment = {"PATH": "/selected/docker/bin"}
        with patch.object(runner.subprocess, "run") as command:
            command.return_value.returncode = 0
            self.assertTrue(runner.docker_ready(environment))
        self.assertEqual(command.call_args.kwargs["env"], environment)


if __name__ == "__main__":
    unittest.main()
