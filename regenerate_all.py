"""Run the thesis result workflows from one reproducible command.

``regenerate_all.py`` is the central entry point for regenerating financial
summaries, MACCs, sensitivity heatmaps, and executed notebook copies. It does
not contain scientific calculation logic: it calls the existing project
commands, gives every run a user-selected name, and collects the outputs in one
isolated directory with logs and a reproducibility manifest.

Run commands from the repository root. The standard named run generates NPV,
LPM, and LCOX financial summaries for all five sectors::

    PYTHONPATH=src .venv/bin/python regenerate_all.py --run-name thesis_results

The complete workflow, including both MACC variants, all selected heatmaps, and
non-destructive execution of every notebook, is one command::

    PYTHONPATH=src .venv/bin/python regenerate_all.py --run-name thesis_results_full --full

Optional analyses can also be selected separately::

    # Financial summaries plus deterministic and simulated MACCs.
    PYTHONPATH=src .venv/bin/python regenerate_all.py --run-name thesis_results_macc --macc-mode both

    # Financial summaries plus sensitivity CSVs and heatmaps.
    PYTHONPATH=src .venv/bin/python regenerate_all.py --run-name thesis_results_heatmaps --include-heatmaps

Use ``--sectors`` and ``--metrics`` to limit the scope; ``--sample-size``,
``--random-seed``, and ``--retrofit-bau-mode`` configure simulations;
``--output-root`` changes the parent directory; and ``--dry-run`` previews the
exact commands without creating files. Run ``python regenerate_all.py --help``
for all options, examples, and the output layout.

Every completed run is stored below ``results/runs/<run-name>/`` by default.
Its ``manifest.json`` records all active global assumptions (including carbon
price and interest rate), settings, Git state, environment, commands, logs, and
file hashes. An existing run directory is never overwritten.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import re
import shlex
import subprocess
import sys
import time
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from general_parameters import CARBON_PRICE_EUR_PER_T, INTEREST_RATE  # noqa: E402


SECTORS = ("electricity", "cement", "steel", "ammonia", "hydrogen")
METRICS = ("NPV", "LPM", "LCOX")
MACC_SECTORS = ("cement", "steel", "ammonia", "hydrogen")
RETROFIT_BAU_MODES = ("sampled", "deterministic")
MACC_MODES = ("none", "deterministic", "simulated", "both")
RUN_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class Step:
    """One existing project command executed by the regeneration workflow."""

    name: str
    command: tuple[str, ...]


class RegenerationError(RuntimeError):
    """Raised when one regeneration step returns a non-zero exit status."""


def build_parser() -> argparse.ArgumentParser:
    """Create the documented command-line interface."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the thesis financial summaries and optional MACC, heatmap, "
            "and notebook workflows into one named, reproducible result set."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview every command without creating files.
  PYTHONPATH=src .venv/bin/python regenerate_all.py --run-name preview --dry-run

  # Core NPV/LPM/LCOX summaries for all sectors.
  PYTHONPATH=src .venv/bin/python regenerate_all.py --run-name thesis_results

  # A quick electricity/cement NPV run.
  PYTHONPATH=src .venv/bin/python regenerate_all.py --run-name quick_check \\
      --sectors electricity cement --metrics NPV --sample-size 100

  # Complete workflow: summaries, both MACC modes, heatmaps, and notebooks.
  PYTHONPATH=src .venv/bin/python regenerate_all.py \\
      --run-name thesis_results_full --full

  # Select optional analyses individually instead of using --full.
  PYTHONPATH=src .venv/bin/python regenerate_all.py \\
      --run-name thesis_results_selected \\
      --macc-mode deterministic --include-heatmaps

Output layout:
  results/runs/<run-name>/
    manifest.json
    logs/
    financial/<sector>/<metric>/{figures,raw,processed}/
    macc/<sector>/<deterministic|simulated>/{figures,processed}/
    heatmaps/<metric>/{figures,processed}/
    notebook_verification/                 # only with --verify-notebooks

The command refuses to reuse an existing run directory. Choose a new run name
to prevent different result sets from being silently overwritten.
""",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help=(
            "Name of the isolated run directory. Defaults to a timestamp. "
            "Use a descriptive value such as thesis_results or baseline_v2."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "results" / "runs",
        help="Parent directory for run folders (default: results/runs).",
    )
    parser.add_argument(
        "--sectors",
        nargs="+",
        choices=SECTORS,
        default=list(SECTORS),
        help="Sectors to regenerate (default: all five).",
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=METRICS,
        default=list(METRICS),
        help="Financial metrics to regenerate (default: NPV LPM LCOX).",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100_000,
        help="Monte Carlo draws per technology (default: 100000).",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Top-level Monte Carlo random seed (default: 42).",
    )
    parser.add_argument(
        "--retrofit-bau-mode",
        choices=RETROFIT_BAU_MODES,
        default="sampled",
        help=(
            "BAU inputs used for Monte Carlo retrofit comparisons "
            "(default: sampled)."
        ),
    )
    parser.add_argument(
        "--macc-mode",
        choices=MACC_MODES,
        default="none",
        help=(
            "Optionally generate deterministic MACCs, simulated mean MACCs, "
            "or both (default: none). Electricity has no MACC module."
        ),
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "Run the complete workflow: financial summaries, both MACC modes, "
            "sensitivity heatmaps, and notebook verification. Sector, metric, "
            "simulation, and output options still apply."
        ),
    )
    parser.add_argument(
        "--include-heatmaps",
        dest="include_heatmaps",
        action="store_true",
        help=(
            "Generate one standardized sensitivity CSV and one heatmap per "
            "selected sector and metric."
        ),
    )
    parser.add_argument(
        "--include-sensitivity",
        dest="include_heatmaps",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--sensitivity-variation-percent",
        type=float,
        default=20.0,
        help="One-at-a-time sensitivity movement in percent (default: 20).",
    )
    parser.add_argument(
        "--verify-notebooks",
        action="store_true",
        help=(
            "Execute all project notebooks and retain the executed copies in "
            "the run directory. Notebook source files are never overwritten."
        ),
    )
    parser.add_argument(
        "--notebook-timeout",
        type=int,
        default=600,
        help="Maximum execution time per notebook in seconds (default: 600).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the run plan without creating directories or running commands.",
    )
    return parser


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    """Remove repeated CLI selections while preserving their order."""

    return tuple(dict.fromkeys(values))


def _resolve_output_root(output_root: Path) -> Path:
    """Resolve a relative output root against the repository root."""

    expanded = output_root.expanduser()
    return expanded.resolve() if expanded.is_absolute() else (PROJECT_ROOT / expanded).resolve()


def _validate_arguments(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """Reject unsafe or scientifically invalid command-line settings."""

    if args.sample_size <= 0:
        parser.error("--sample-size must be positive")
    if args.notebook_timeout <= 0:
        parser.error("--notebook-timeout must be positive")
    if not 0.0 < args.sensitivity_variation_percent < 100.0:
        parser.error("--sensitivity-variation-percent must be between 0 and 100")
    if args.run_name is not None and not RUN_NAME_PATTERN.fullmatch(args.run_name):
        parser.error(
            "--run-name must start with a letter or number and contain only "
            "letters, numbers, dots, underscores, or hyphens"
        )


def _financial_steps(
    sectors: tuple[str, ...],
    metrics: tuple[str, ...],
    run_dir: Path,
    sample_size: int,
    random_seed: int,
    retrofit_bau_mode: str,
) -> list[Step]:
    """Build financial-summary commands for every selected sector and metric."""

    steps = []
    for sector in sectors:
        for metric in metrics:
            target = run_dir / "financial" / sector / metric
            steps.append(
                Step(
                    name=f"financial_{sector}_{metric.lower()}",
                    command=(
                        sys.executable,
                        "-m",
                        f"{sector}.{sector}_financial_summary",
                        "--sample-size",
                        str(sample_size),
                        "--random-seed",
                        str(random_seed),
                        "--retrofit-bau-mode",
                        retrofit_bau_mode,
                        "--metric",
                        metric,
                        "--ranking-output",
                        "both",
                        "--output-dir",
                        str(target / "figures"),
                        "--raw-data-dir",
                        str(target / "raw"),
                        "--processed-data-dir",
                        str(target / "processed"),
                    ),
                )
            )
    return steps


def _macc_steps(
    sectors: tuple[str, ...],
    run_dir: Path,
    macc_mode: str,
    sample_size: int,
    random_seed: int,
    retrofit_bau_mode: str,
) -> list[Step]:
    """Build optional deterministic and/or simulated MACC commands."""

    if macc_mode == "none":
        return []
    modes = ("deterministic", "simulated") if macc_mode == "both" else (macc_mode,)
    steps = []
    for sector in sectors:
        if sector not in MACC_SECTORS:
            continue
        for mode in modes:
            target = run_dir / "macc" / sector / mode
            command = [
                sys.executable,
                "-m",
                f"{sector}.{sector}_macc",
                "--project-root",
                str(PROJECT_ROOT),
                "--processed-data-dir",
                str(target / "processed"),
                "--figure-dir",
                str(target / "figures"),
                "--sample-size",
                str(sample_size),
                "--random-seed",
                str(random_seed),
            ]
            if mode == "simulated":
                command.append("--simulated")
            if sector in {"steel", "ammonia", "hydrogen"}:
                command.extend(("--retrofit-bau-mode", retrofit_bau_mode))
            steps.append(Step(f"macc_{sector}_{mode}", tuple(command)))
    return steps


def _heatmap_steps(
    sectors: tuple[str, ...],
    metrics: tuple[str, ...],
    run_dir: Path,
    variation_percent: float,
) -> list[Step]:
    """Build optional standardized sensitivity-heatmap commands."""

    steps = []
    for metric in metrics:
        target = run_dir / "heatmaps" / metric
        steps.append(
            Step(
                name=f"heatmaps_{metric.lower()}",
                command=(
                    sys.executable,
                    "-m",
                    "sensitivity_deep_dive",
                    "--project-root",
                    str(PROJECT_ROOT),
                    "--processed-data-dir",
                    str(target / "processed"),
                    "--figure-dir",
                    str(target / "figures"),
                    "--variation",
                    str(variation_percent / 100.0),
                    "--metric",
                    metric,
                    "--sectors",
                    *sectors,
                ),
            )
        )
    return steps


def _notebook_steps(run_dir: Path, timeout: int) -> list[Step]:
    """Build non-destructive execution commands for all project notebooks."""

    output_dir = run_dir / "notebook_verification"
    steps = []
    for notebook in sorted((PROJECT_ROOT / "notebooks").rglob("*.ipynb")):
        relative = notebook.relative_to(PROJECT_ROOT)
        output_name = "_".join(relative.parts)
        step_name = "notebook_" + "_".join(relative.with_suffix("").parts)
        steps.append(
            Step(
                name=step_name,
                command=(
                    sys.executable,
                    "-m",
                    "jupyter",
                    "nbconvert",
                    "--to",
                    "notebook",
                    "--execute",
                    str(relative),
                    "--output",
                    output_name,
                    "--output-dir",
                    str(output_dir),
                    f"--ExecutePreprocessor.timeout={timeout}",
                ),
            )
        )
    return steps


def build_steps(args: argparse.Namespace, run_dir: Path) -> list[Step]:
    """Build the complete ordered regeneration plan."""

    sectors = _unique(args.sectors)
    metrics = _unique(args.metrics)
    steps = _financial_steps(
        sectors=sectors,
        metrics=metrics,
        run_dir=run_dir,
        sample_size=args.sample_size,
        random_seed=args.random_seed,
        retrofit_bau_mode=args.retrofit_bau_mode,
    )
    steps.extend(
        _macc_steps(
            sectors=sectors,
            run_dir=run_dir,
            macc_mode=args.macc_mode,
            sample_size=args.sample_size,
            random_seed=args.random_seed,
            retrofit_bau_mode=args.retrofit_bau_mode,
        )
    )
    if args.include_heatmaps:
        steps.extend(
            _heatmap_steps(
                sectors=sectors,
                metrics=metrics,
                run_dir=run_dir,
                variation_percent=args.sensitivity_variation_percent,
            )
        )
    if args.verify_notebooks:
        steps.extend(_notebook_steps(run_dir, args.notebook_timeout))
    return steps


def _git_text(*arguments: str) -> str | None:
    """Return stripped Git output, or ``None`` outside a working tree."""

    result = subprocess.run(
        ("git", *arguments),
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _dependency_versions() -> dict[str, str]:
    """Record the principal packages that can affect numerical or visual output."""

    versions = {}
    for package in (
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "jupyter",
        "nbconvert",
        "streamlit",
    ):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "not installed"
    return versions


def _initial_manifest(
    args: argparse.Namespace,
    run_name: str,
    run_dir: Path,
    steps: Sequence[Step],
) -> dict[str, object]:
    """Create the manifest before any calculation starts."""

    git_status = _git_text("status", "--porcelain")
    return {
        "schema_version": 1,
        "status": "running",
        "run_name": run_name,
        "run_directory": str(run_dir),
        "started_at": datetime.now().astimezone().isoformat(),
        "finished_at": None,
        "active_assumptions": {
            "carbon_price_eur_per_t": CARBON_PRICE_EUR_PER_T.value,
            "interest_rate": INTEREST_RATE.value,
            "source": "src/general_parameters.py",
        },
        "settings": {
            "sectors": list(_unique(args.sectors)),
            "metrics": list(_unique(args.metrics)),
            "sample_size": args.sample_size,
            "random_seed": args.random_seed,
            "retrofit_bau_mode": args.retrofit_bau_mode,
            "macc_mode": args.macc_mode,
            "full_workflow": args.full,
            "include_heatmaps": args.include_heatmaps,
            "sensitivity_variation_percent": args.sensitivity_variation_percent,
            "verify_notebooks": args.verify_notebooks,
            "notebook_timeout_seconds": args.notebook_timeout,
        },
        "environment": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "dependencies": _dependency_versions(),
        },
        "git": {
            "commit": _git_text("rev-parse", "HEAD"),
            "branch": _git_text("branch", "--show-current"),
            "dirty": bool(git_status),
            "status": git_status.splitlines() if git_status else [],
        },
        "planned_step_count": len(steps),
        "completed_step_count": 0,
        "commands": [],
        "generated_files": [],
        "error": None,
    }


def _write_manifest(run_dir: Path, manifest: dict[str, object]) -> None:
    """Write the manifest atomically so interrupted runs remain diagnosable."""

    manifest_path = run_dir / "manifest.json"
    temporary_path = run_dir / "manifest.json.tmp"
    temporary_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(manifest_path)


def _command_environment() -> dict[str, str]:
    """Return a subprocess environment that imports this repository's source."""

    environment = os.environ.copy()
    current_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(SRC_DIR)
        if not current_pythonpath
        else str(SRC_DIR) + os.pathsep + current_pythonpath
    )
    return environment


def _run_step(
    step: Step,
    index: int,
    total: int,
    run_dir: Path,
) -> dict[str, object]:
    """Execute one step, retain its log, and return manifest metadata."""

    print(f"[{index}/{total}] {step.name}", flush=True)
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{index:03d}_{step.name}.log"
    started_at = datetime.now().astimezone()
    started_clock = time.perf_counter()
    result = subprocess.run(
        step.command,
        cwd=PROJECT_ROOT,
        env=_command_environment(),
        text=True,
        capture_output=True,
        check=False,
    )
    duration_seconds = time.perf_counter() - started_clock
    command_text = shlex.join(step.command)
    log_path.write_text(
        f"Command: {command_text}\n\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}\n",
        encoding="utf-8",
    )
    record = {
        "step": step.name,
        "command": list(step.command),
        "started_at": started_at.isoformat(),
        "duration_seconds": round(duration_seconds, 6),
        "return_code": result.returncode,
        "log": str(log_path.relative_to(run_dir)),
    }
    return record


def _sha256(path: Path) -> str:
    """Calculate a file hash without loading a potentially large CSV at once."""

    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for block in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _generated_file_inventory(run_dir: Path) -> list[dict[str, object]]:
    """Describe every generated file except the self-referential manifest."""

    inventory = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file() or path.name in {"manifest.json", "manifest.json.tmp"}:
            continue
        inventory.append(
            {
                "path": str(path.relative_to(run_dir)),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return inventory


def _print_plan(run_dir: Path, steps: Sequence[Step]) -> None:
    """Print an auditable dry-run plan without changing the filesystem."""

    print(f"Run directory: {run_dir}")
    print(
        "Recorded global assumptions: "
        f"CO2 price={CARBON_PRICE_EUR_PER_T.value:g} EUR/tCO2, "
        f"interest rate={INTEREST_RATE.value:g}"
    )
    print(f"Planned steps: {len(steps)}")
    for index, step in enumerate(steps, start=1):
        print(f"[{index}/{len(steps)}] {step.name}")
        print(f"  {shlex.join(step.command)}")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse options, execute the plan, and finalize the run manifest."""

    parser = build_parser()
    args = parser.parse_args(argv)
    if args.full:
        args.macc_mode = "both"
        args.include_heatmaps = True
        args.verify_notebooks = True
    _validate_arguments(args, parser)
    run_name = args.run_name or datetime.now().astimezone().strftime(
        "run-%Y%m%d-%H%M%S"
    )
    output_root = _resolve_output_root(args.output_root)
    run_dir = output_root / run_name
    steps = build_steps(args, run_dir)

    if args.dry_run:
        _print_plan(run_dir, steps)
        return 0
    if run_dir.exists():
        parser.error(
            f"run directory already exists: {run_dir}. Choose a new --run-name."
        )

    run_dir.mkdir(parents=True)
    manifest = _initial_manifest(args, run_name, run_dir, steps)
    _write_manifest(run_dir, manifest)
    try:
        for index, step in enumerate(steps, start=1):
            record = _run_step(step, index, len(steps), run_dir)
            manifest["commands"].append(record)
            if record["return_code"] != 0:
                raise RegenerationError(
                    f"{step.name} failed with exit code {record['return_code']}; "
                    f"see {run_dir / record['log']}"
                )
            manifest["completed_step_count"] = index
            _write_manifest(run_dir, manifest)
    except Exception as error:
        manifest["status"] = "failed"
        manifest["error"] = str(error)
        manifest["finished_at"] = datetime.now().astimezone().isoformat()
        manifest["generated_files"] = _generated_file_inventory(run_dir)
        _write_manifest(run_dir, manifest)
        print(f"Regeneration failed: {error}", file=sys.stderr)
        return 1

    manifest["status"] = "complete"
    manifest["finished_at"] = datetime.now().astimezone().isoformat()
    manifest["generated_files"] = _generated_file_inventory(run_dir)
    _write_manifest(run_dir, manifest)
    print(f"Completed {len(steps)} steps.")
    print(f"Outputs: {run_dir}")
    print(f"Manifest: {run_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
