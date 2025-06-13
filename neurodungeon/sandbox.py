"""Docker-based sandbox for executing code."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

from pydantic import ConfigDict

from .models import FloorArtifact, Hint, Vote, NDModel


def docker_available() -> bool:
    """Return True if Docker is available on the host."""
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1,
            check=True,
        )
        return True
    except Exception:
        return False


class SandboxResult(NDModel):
    model_config = ConfigDict(frozen=True)
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool


class Sandbox:
    """Execute code inside a limited Docker container."""

    def __init__(self, cpu: float, memory_mb: int, timeout_s: int) -> None:
        self.cpu = cpu
        self.memory_mb = memory_mb
        self.timeout_s = timeout_s

    def run(self, code: str, tests: str) -> SandboxResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "code.py").write_text(code)
            (tmp / "test_code.py").write_text(tests)
            cmd = [
                "docker",
                "run",
                "--rm",
                f"--cpus={self.cpu}",
                f"--memory={self.memory_mb}m",
                "--network",
                "none",
                "-v",
                f"{tmpdir}:/work",
                "-w",
                "/work",
                "python:3.11-slim",
                "pytest",
                "-q",
            ]
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_s,
                    check=False,
                )
                stdout = proc.stdout
                stderr = proc.stderr
                ret = proc.returncode
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                stdout = (
                    exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                )
                stderr = (
                    exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                )
                ret = 1
                timed_out = True
            return SandboxResult(stdout=stdout, stderr=stderr, exit_code=ret, timed_out=timed_out)


class RuntimeEnemy:
    """Enemy rejecting artifacts that fail sandbox tests."""

    def __init__(self, sandbox: Sandbox, tests: str) -> None:
        self.sandbox = sandbox
        self.tests = tests

    def evaluate(self, artifact: FloorArtifact) -> tuple[Vote, tuple[Hint, ...]]:

        result = self.sandbox.run(artifact.content, self.tests)
        hints = []
        if result.timed_out:
            hints.append(Hint(text="timeout"))
        if result.exit_code != 0:
            hints.append(Hint(text="tests failed"))
        vote = Vote.ACCEPT if result.exit_code == 0 and not result.timed_out else Vote.REJECT
        return vote, tuple(hints)
