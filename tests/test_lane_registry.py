#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "skills" / "run-task" / "scripts" / "lane_registry.py"


class LaneRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.sandbox = Path(self.temporary.name)
        self.authority = self.sandbox / "authority"
        self.authority.mkdir()
        self.git("init")
        self.git("config", "user.name", "GMGN Test")
        self.git("config", "user.email", "gmgn@example.invalid")
        (self.authority / "seed.txt").write_text("seed\n", encoding="utf-8")
        self.git("add", "seed.txt")
        self.git("commit", "-m", "seed")
        self.head = self.git("rev-parse", "HEAD").stdout.strip()
        self.worktree_a = self.sandbox / "lane-a"
        self.worktree_b = self.sandbox / "lane-b"
        self.git("worktree", "add", "--detach", str(self.worktree_a), self.head)
        self.git("worktree", "add", "--detach", str(self.worktree_b), self.head)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.authority), *arguments],
            text=True,
            capture_output=True,
            check=True,
        )

    def command(self, operation: str, *arguments: str) -> list[str]:
        return [
            sys.executable,
            str(REGISTRY),
            "--project-root",
            str(self.authority),
            operation,
            *arguments,
        ]

    def run_registry(
        self, operation: str, *arguments: str, expected: int = 0
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            self.command(operation, *arguments),
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result, json.loads(result.stdout)

    def claim(
        self,
        card_id: str,
        worktree: Path,
        *,
        owner_thread: str = "thread-a",
        owner_run: str = "run-a",
    ) -> dict:
        arguments = [
            "--card-id",
            card_id,
            "--owner-thread-id",
            owner_thread,
            "--owner-run-id",
            owner_run,
            "--worktree-path",
            str(worktree),
            "--baseline-anchor",
            self.head,
        ]
        return self.run_registry("claim", *arguments)[1]

    def bind(
        self,
        card_id: str,
        worktree: Path,
        epoch: int,
        *,
        owner_thread: str,
        owner_run: str,
        coder_ref: str,
    ) -> dict:
        arguments = self.identity_arguments(
            card_id,
            worktree,
            epoch,
            owner_thread=owner_thread,
            owner_run=owner_run,
        )
        return self.run_registry(
            "bind-coder", *arguments, "--coder-ref", coder_ref
        )[1]

    def identity_arguments(
        self,
        card_id: str,
        worktree: Path,
        epoch: int,
        *,
        owner_thread: str,
        owner_run: str,
        coder_ref: str | None = None,
        coder_epoch: int = 1,
    ) -> list[str]:
        arguments = [
            "--card-id",
            card_id,
            "--owner-thread-id",
            owner_thread,
            "--owner-run-id",
            owner_run,
            "--ownership-epoch",
            str(epoch),
            "--worktree-path",
            str(worktree),
        ]
        if coder_ref is not None:
            arguments.extend(
                ("--coder-ref", coder_ref, "--coder-epoch", str(coder_epoch))
            )
        return arguments

    def commit_file(self, worktree: Path, relative_path: str, content: str) -> str:
        (worktree / relative_path).write_text(content, encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(worktree), "add", relative_path],
            text=True,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(worktree), "commit", "-m", f"add {relative_path}"],
            text=True,
            capture_output=True,
            check=True,
        )
        return subprocess.run(
            ["git", "-C", str(worktree), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

    def replace_with_clone(self, worktree: Path) -> None:
        shutil.rmtree(worktree)
        subprocess.run(
            ["git", "clone", "--no-local", str(self.authority), str(worktree)],
            text=True,
            capture_output=True,
            check=True,
        )
        replacement_head = subprocess.run(
            ["git", "-C", str(worktree), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        self.assertEqual(replacement_head, self.head)

    def test_same_card_different_paths_has_one_atomic_winner(self) -> None:
        commands = (
            self.command(
                "claim",
                "--card-id",
                "T0.6",
                "--owner-thread-id",
                "thread-a",
                "--owner-run-id",
                "run-a",
                "--worktree-path",
                str(self.worktree_a),
                "--baseline-anchor",
                self.head,
            ),
            self.command(
                "claim",
                "--card-id",
                "T0.6",
                "--owner-thread-id",
                "thread-b",
                "--owner-run-id",
                "run-b",
                "--worktree-path",
                str(self.worktree_b),
                "--baseline-anchor",
                self.head,
            ),
        )
        processes = [
            subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for command in commands
        ]
        results = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            results.append((process.returncode, json.loads(stdout), stderr))

        self.assertEqual(sorted(result[0] for result in results), [0, 2])
        loser = next(payload for code, payload, _ in results if code == 2)
        self.assertEqual(loser["error"]["code"], "card_claimed")

    def test_different_cards_cannot_claim_same_canonical_path(self) -> None:
        self.claim("T1", self.worktree_a)
        _, rejected = self.run_registry(
            "claim",
            "--card-id",
            "T2",
            "--owner-thread-id",
            "thread-b",
            "--owner-run-id",
            "run-b",
            "--worktree-path",
            str(self.worktree_a / "."),
            "--baseline-anchor",
            self.head,
            expected=2,
        )
        self.assertEqual(rejected["error"]["code"], "worktree_claimed")

    def test_old_owner_and_epoch_cannot_verify_anchor_or_release(self) -> None:
        first = self.claim("T1", self.worktree_a, owner_thread="thread-old", owner_run="run-old")
        old_epoch = first["lane"]["ownership_epoch"]
        self.bind(
            "T1",
            self.worktree_a,
            old_epoch,
            owner_thread="thread-old",
            owner_run="run-old",
            coder_ref="coder-old",
        )
        old_identity = self.identity_arguments(
            "T1",
            self.worktree_a,
            old_epoch,
            owner_thread="thread-old",
            owner_run="run-old",
            coder_ref="coder-old",
        )
        self.run_registry("release", *old_identity)

        second = self.claim("T1", self.worktree_b, owner_thread="thread-new", owner_run="run-new")
        self.assertEqual(second["lane"]["ownership_epoch"], old_epoch + 1)
        self.bind(
            "T1",
            self.worktree_b,
            second["lane"]["ownership_epoch"],
            owner_thread="thread-new",
            owner_run="run-new",
            coder_ref="coder-new",
        )

        for operation, suffix in (
            ("verify", []),
            ("anchor", ["--candidate-anchor", self.head]),
            ("release", []),
        ):
            with self.subTest(operation=operation):
                _, rejected = self.run_registry(
                    operation,
                    *old_identity,
                    *suffix,
                    expected=2,
                )
                self.assertEqual(rejected["error"]["code"], "ownership_mismatch")

    def test_release_keeps_tombstone_increments_epoch_and_frees_path(self) -> None:
        first = self.claim("T1", self.worktree_a)
        epoch = first["lane"]["ownership_epoch"]
        self.bind(
            "T1",
            self.worktree_a,
            epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        identity = self.identity_arguments(
            "T1",
            self.worktree_a,
            epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        self.run_registry("anchor", *identity, "--candidate-anchor", self.head)
        _, released = self.run_registry("release", *identity)
        self.assertFalse(released["lane"]["active"])
        self.assertEqual(released["lane"]["state"], "released")
        self.assertEqual(released["lane"]["candidate_anchor"], self.head)

        path_reuse = self.claim(
            "T2",
            self.worktree_a,
            owner_thread="thread-other",
            owner_run="run-other",
        )
        self.assertTrue(path_reuse["lane"]["active"])
        path_reuse_identity = self.identity_arguments(
            "T2",
            self.worktree_a,
            path_reuse["lane"]["ownership_epoch"],
            owner_thread="thread-other",
            owner_run="run-other",
        )
        self.run_registry("cancel-unbound", *path_reuse_identity)

        reclaimed = self.claim("T1", self.worktree_b, owner_thread="thread-b", owner_run="run-b")
        self.assertEqual(reclaimed["lane"]["ownership_epoch"], epoch + 1)

    def test_bind_coder_status_and_registry_leave_git_status_unchanged(self) -> None:
        before = self.git("status", "--porcelain=v1").stdout
        claimed = self.claim("T1", self.worktree_a)
        epoch = claimed["lane"]["ownership_epoch"]
        bound = self.bind(
            "T1",
            self.worktree_a,
            epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        self.assertEqual(bound["lane"]["coder_ref"], "coder-a")
        self.assertEqual(bound["lane"]["coder_epoch"], 1)
        self.assertEqual(bound["lane"]["run_id"], "run-a")
        self.assertEqual(
            bound["lane"]["project_scope_id"], bound["project_scope_id"]
        )

        _, one = self.run_registry("status", "--card-id", "T1")
        _, all_lanes = self.run_registry("status")
        self.assertEqual(one["lane"]["lane_key"], bound["lane"]["lane_key"])
        self.assertEqual([lane["card_id"] for lane in all_lanes["lanes"]], ["T1"])
        self.assertEqual(self.git("status", "--porcelain=v1").stdout, before)

    def test_authority_registry_accepts_worktree_from_another_repository(self) -> None:
        code_root = self.sandbox / "code-repository"
        code_root.mkdir()
        for arguments in (
            ("init",),
            ("config", "user.name", "GMGN Test"),
            ("config", "user.email", "gmgn@example.invalid"),
        ):
            subprocess.run(
                ["git", "-C", str(code_root), *arguments],
                text=True,
                capture_output=True,
                check=True,
            )
        (code_root / "code.txt").write_text("code\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(code_root), "add", "code.txt"],
            text=True,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(code_root), "commit", "-m", "code seed"],
            text=True,
            capture_output=True,
            check=True,
        )
        code_head = subprocess.run(
            ["git", "-C", str(code_root), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

        _, claimed = self.run_registry(
            "claim",
            "--card-id",
            "T-external",
            "--owner-thread-id",
            "thread-external",
            "--owner-run-id",
            "run-external",
            "--worktree-path",
            str(code_root),
            "--baseline-anchor",
            code_head,
        )
        self.assertEqual(claimed["lane"]["worktree_path"], str(code_root.resolve()))
        self.assertEqual(claimed["lane"]["baseline_anchor"], code_head)

    def test_bound_operations_require_exact_coder_ref(self) -> None:
        claimed = self.claim("T-bound", self.worktree_a)
        epoch = claimed["lane"]["ownership_epoch"]
        self.bind(
            "T-bound",
            self.worktree_a,
            epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        common = self.identity_arguments(
            "T-bound",
            self.worktree_a,
            epoch,
            owner_thread="thread-a",
            owner_run="run-a",
        )

        for operation, suffix in (
            ("verify", []),
            ("anchor", ["--candidate-anchor", self.head]),
            ("release", []),
        ):
            with self.subTest(operation=operation, case="omitted"):
                result = subprocess.run(
                    self.command(operation, *common, *suffix),
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("--coder-ref", result.stderr)

            with self.subTest(operation=operation, case="wrong"):
                _, rejected = self.run_registry(
                    operation,
                    *common,
                    "--coder-ref",
                    "coder-wrong",
                    "--coder-epoch",
                    "1",
                    *suffix,
                    expected=2,
                )
                self.assertEqual(rejected["error"]["code"], "ownership_mismatch")

    def test_anchor_before_bind_is_rejected_and_unbound_cancel_is_separate(self) -> None:
        claimed = self.claim("T-unbound", self.worktree_a)
        epoch = claimed["lane"]["ownership_epoch"]
        common = self.identity_arguments(
            "T-unbound",
            self.worktree_a,
            epoch,
            owner_thread="thread-a",
            owner_run="run-a",
        )
        _, rejected = self.run_registry(
            "anchor",
            *common,
            "--coder-ref",
            "coder-a",
            "--coder-epoch",
            "1",
            "--candidate-anchor",
            self.head,
            expected=2,
        )
        self.assertEqual(rejected["error"]["code"], "coder_unbound")

        _, cancelled = self.run_registry("cancel-unbound", *common)
        self.assertFalse(cancelled["lane"]["active"])
        self.assertEqual(cancelled["lane"]["state"], "cancelled-unbound")

    def test_claim_rejects_direct_coder_binding_and_bound_cancel(self) -> None:
        result = subprocess.run(
            self.command(
                "claim",
                "--card-id",
                "T-direct",
                "--owner-thread-id",
                "thread-a",
                "--owner-run-id",
                "run-a",
                "--worktree-path",
                str(self.worktree_a),
                "--baseline-anchor",
                self.head,
                "--coder-ref",
                "coder-a",
            ),
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)

        claimed = self.claim("T-cancel", self.worktree_a)
        epoch = claimed["lane"]["ownership_epoch"]
        self.bind(
            "T-cancel",
            self.worktree_a,
            epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        common = self.identity_arguments(
            "T-cancel",
            self.worktree_a,
            epoch,
            owner_thread="thread-a",
            owner_run="run-a",
        )
        _, rejected = self.run_registry(
            "cancel-unbound", *common, expected=2
        )
        self.assertEqual(rejected["error"]["code"], "lane_bound")

    def test_recreated_path_with_same_baseline_is_not_the_claimed_repository(self) -> None:
        unbound = self.claim("T-unbound", self.worktree_a)
        unbound_common = self.identity_arguments(
            "T-unbound",
            self.worktree_a,
            unbound["lane"]["ownership_epoch"],
            owner_thread="thread-a",
            owner_run="run-a",
        )
        self.replace_with_clone(self.worktree_a)
        for operation, suffix in (
            ("bind-coder", ["--coder-ref", "coder-a"]),
            ("cancel-unbound", []),
        ):
            with self.subTest(state="unbound", operation=operation):
                _, rejected = self.run_registry(
                    operation, *unbound_common, *suffix, expected=2
                )
                self.assertEqual(
                    rejected["error"]["code"], "repository_identity_mismatch"
                )

        bound = self.claim(
            "T-bound",
            self.worktree_b,
            owner_thread="thread-b",
            owner_run="run-b",
        )
        bound_epoch = bound["lane"]["ownership_epoch"]
        self.bind(
            "T-bound",
            self.worktree_b,
            bound_epoch,
            owner_thread="thread-b",
            owner_run="run-b",
            coder_ref="coder-b",
        )
        bound_identity = self.identity_arguments(
            "T-bound",
            self.worktree_b,
            bound_epoch,
            owner_thread="thread-b",
            owner_run="run-b",
            coder_ref="coder-b",
        )
        self.replace_with_clone(self.worktree_b)
        for operation, suffix in (
            ("verify", []),
            ("anchor", ["--candidate-anchor", self.head]),
            ("release", []),
        ):
            with self.subTest(state="bound", operation=operation):
                _, rejected = self.run_registry(
                    operation, *bound_identity, *suffix, expected=2
                )
                self.assertEqual(
                    rejected["error"]["code"], "repository_identity_mismatch"
                )

    def test_rotate_coder_advances_generation_and_rejects_old_returns(self) -> None:
        claimed = self.claim("T-rotate", self.worktree_a)
        ownership_epoch = claimed["lane"]["ownership_epoch"]
        self.bind(
            "T-rotate",
            self.worktree_a,
            ownership_epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        old_identity = self.identity_arguments(
            "T-rotate",
            self.worktree_a,
            ownership_epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        _, anchored = self.run_registry(
            "anchor", *old_identity, "--candidate-anchor", self.head
        )
        self.assertEqual(anchored["lane"]["candidate_coder_epoch"], 1)

        _, rotated = self.run_registry(
            "rotate-coder",
            *old_identity,
            "--new-coder-ref",
            "coder-b",
            "--candidate-anchor",
            self.head,
        )
        self.assertEqual(rotated["lane"]["coder_ref"], "coder-b")
        self.assertEqual(rotated["lane"]["coder_epoch"], 2)
        self.assertEqual(rotated["lane"]["state"], "coder-active")

        for operation, suffix in (
            ("verify", []),
            ("anchor", ["--candidate-anchor", self.head]),
            ("release", []),
        ):
            with self.subTest(operation=operation):
                _, rejected = self.run_registry(
                    operation, *old_identity, *suffix, expected=2
                )
                self.assertEqual(rejected["error"]["code"], "ownership_mismatch")

        new_identity = self.identity_arguments(
            "T-rotate",
            self.worktree_a,
            ownership_epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-b",
            coder_epoch=2,
        )
        self.run_registry("verify", *new_identity)
        _, revised = self.run_registry(
            "anchor", *new_identity, "--candidate-anchor", self.head
        )
        self.assertEqual(revised["lane"]["candidate_coder_epoch"], 2)

    def test_rotate_coder_requires_anchored_current_candidate_and_fresh_ref(self) -> None:
        claimed = self.claim("T-rotate", self.worktree_a)
        ownership_epoch = claimed["lane"]["ownership_epoch"]
        self.bind(
            "T-rotate",
            self.worktree_a,
            ownership_epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        identity = self.identity_arguments(
            "T-rotate",
            self.worktree_a,
            ownership_epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        _, unanchored = self.run_registry(
            "rotate-coder",
            *identity,
            "--new-coder-ref",
            "coder-b",
            "--candidate-anchor",
            self.head,
            expected=2,
        )
        self.assertEqual(unanchored["error"]["code"], "candidate_not_anchored")

        self.run_registry("anchor", *identity, "--candidate-anchor", self.head)
        _, unchanged = self.run_registry(
            "rotate-coder",
            *identity,
            "--new-coder-ref",
            "coder-a",
            "--candidate-anchor",
            self.head,
            expected=2,
        )
        self.assertEqual(unchanged["error"]["code"], "coder_unchanged")

    def test_completed_coder_attempt_cannot_be_reactivated_or_replace_candidate(self) -> None:
        claimed = self.claim("T-immutable", self.worktree_a)
        ownership_epoch = claimed["lane"]["ownership_epoch"]
        self.bind(
            "T-immutable",
            self.worktree_a,
            ownership_epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        identity = self.identity_arguments(
            "T-immutable",
            self.worktree_a,
            ownership_epoch,
            owner_thread="thread-a",
            owner_run="run-a",
            coder_ref="coder-a",
        )
        _, anchored = self.run_registry(
            "anchor", *identity, "--candidate-anchor", self.head
        )

        _, idempotent = self.run_registry(
            "anchor", *identity, "--candidate-anchor", self.head
        )
        self.assertEqual(idempotent["lane"]["candidate_anchor"], self.head)

        _, rejected_bind = self.run_registry(
            "bind-coder",
            *self.identity_arguments(
                "T-immutable",
                self.worktree_a,
                ownership_epoch,
                owner_thread="thread-a",
                owner_run="run-a",
            ),
            "--coder-ref",
            "coder-a",
            expected=2,
        )
        self.assertEqual(rejected_bind["error"]["code"], "coder_attempt_completed")

        second_candidate = self.commit_file(self.worktree_a, "second.txt", "second\n")
        _, rejected_anchor = self.run_registry(
            "anchor", *identity, "--candidate-anchor", second_candidate, expected=2
        )
        self.assertEqual(
            rejected_anchor["error"]["code"], "candidate_already_anchored"
        )
        self.assertEqual(anchored["lane"]["candidate_coder_epoch"], 1)


if __name__ == "__main__":
    unittest.main()
