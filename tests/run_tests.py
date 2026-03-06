#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        env={**os.environ, **(env or {})},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def fail(message: str, *, output: str | None = None, code: int = 1) -> None:
    print(f"FAIL: {message}")
    if output:
        print(output.rstrip())
    raise SystemExit(code)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {path}", output=str(exc))
    return {}


def require_file(path: Path, description: str) -> None:
    if not path.exists():
        fail(f"Missing {description}: {path}")


def demo_mode() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    report_path = ARTIFACTS_DIR / "governance_guardrails.json"
    guard = run([sys.executable, "tools/governance_guardrails.py", "--format", "json", "--out", str(report_path)])
    if guard.returncode != 0:
        fail("Governance guardrails failed (demo mode must be offline).", output=guard.stdout)

    report = load_json(report_path)
    if report.get("summary", {}).get("errors", 0) != 0:
        fail("Governance guardrails reported errors.", output=json.dumps(report.get("findings", []), indent=2))

    demo = run([sys.executable, "pipelines/pipeline_demo.py"])
    if demo.returncode != 0:
        fail("Offline demo pipeline failed.", output=demo.stdout)

    out_path = REPO_ROOT / "data" / "processed" / "events_jsonl" / "events.jsonl"
    require_file(out_path, "offline demo output")
    if out_path.stat().st_size == 0:
        fail("Offline demo output is empty.", output=str(out_path))

    for required in ["NOTICE.md", "COMMERCIAL_LICENSE.md", "GOVERNANCE.md"]:
        require_file(REPO_ROOT / required, required)

    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8", errors="replace")
    if "it.freddy.alvarez@gmail.com" not in license_text:
        fail("LICENSE must include the commercial licensing contact email.")

    print("OK: demo-mode tests passed (offline).")


def production_mode() -> None:
    if os.environ.get("PRODUCTION_TESTS_CONFIRM") != "1":
        fail(
            "Production-mode tests require an explicit opt-in.",
            output=(
                "Set `PRODUCTION_TESTS_CONFIRM=1` and rerun:\n"
                "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
            ),
            code=2,
        )

    missing: list[str] = []
    for mod in ["pandas", "pyarrow", "pandera", "pytest"]:
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)

    if missing:
        fail(
            "Missing Python dependencies for production-mode tests.",
            output=(
                "Create a venv and install requirements, then rerun:\n"
                "  make setup\n"
                "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n\n"
                f"Missing imports: {', '.join(missing)}\n"
            ),
            code=2,
        )

    pipeline = run([sys.executable, "pipelines/pipeline.py"])
    if pipeline.returncode != 0:
        fail("Production pipeline failed.", output=pipeline.stdout)

    pytest_run = run([sys.executable, "-m", "pytest", "-q"])
    if pytest_run.returncode != 0:
        fail("pytest failed.", output=pytest_run.stdout)

    print("OK: production-mode tests passed (integrations executed).")


def main() -> None:
    mode = os.environ.get("TEST_MODE", "demo").strip().lower()
    if mode not in {"demo", "production"}:
        fail("Invalid TEST_MODE. Expected 'demo' or 'production'.", code=2)

    if mode == "demo":
        demo_mode()
        return

    production_mode()


if __name__ == "__main__":
    main()

