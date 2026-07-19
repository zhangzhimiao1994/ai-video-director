"""Build versioned, non-overwriting finished-film editing handoff bundles."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from timeline_adapters import (
    AdapterError,
    ffmpeg_command_plan,
    write_construction_csv,
    write_construction_markdown,
    write_fcpxml,
    write_jianying_instructions,
    write_otio,
    write_srt,
)
from validate_edit_plan import validate_edit_plan


class BuildError(ValueError):
    """Raised when a safe editing bundle cannot be built or executed."""


_VERSION_NAME = re.compile(r"^v([0-9]{3,})$")


def _filesystem_root(path: Path) -> Path:
    return Path(path.anchor).resolve()


def next_version_dir(output_root: Path) -> Path:
    """Return the next monotonically increasing ``vNNN`` path without creating it."""

    try:
        root = Path(output_root).resolve()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"invalid output root: {exc}") from None
    if not root.anchor or root == _filesystem_root(root):
        raise BuildError("output_root must not be a filesystem root")
    if root.exists() and not root.is_dir():
        raise BuildError("output_root must be a directory")

    highest = 0
    if root.exists():
        try:
            entries = tuple(root.iterdir())
        except OSError as exc:
            raise BuildError(f"could not inspect output_root: {exc}") from None
        for entry in entries:
            match = _VERSION_NAME.fullmatch(entry.name)
            if match is not None:
                highest = max(highest, int(match.group(1)))
    return root / f"v{highest + 1:03d}"


def _write_json_exclusive(destination: Path, value: object) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("x", encoding="utf-8", newline="") as output:
            json.dump(value, output, ensure_ascii=False, indent=2, sort_keys=True)
            output.write("\n")
    except FileExistsError:
        raise BuildError(f"artifact already exists: {destination}") from None
    return destination


def _replace_owned_json(destination: Path, value: object) -> None:
    """Replace a file created by this invocation inside its fresh version directory."""

    destination.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _timeline_slug(timeline: dict[str, Any]) -> str:
    aspect = timeline.get("aspect_ratio")
    if not isinstance(aspect, str) or re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", aspect) is None:
        raise BuildError("timeline aspect_ratio must use WIDTH:HEIGHT")
    return aspect.replace(":", "x")


def _delivery_for_timeline(
    plan: dict[str, Any], timeline_id: object
) -> dict[str, Any]:
    matches = [
        delivery
        for delivery in plan["delivery_specs"]
        if delivery.get("timeline_id") == timeline_id
    ]
    if len(matches) != 1:
        raise BuildError(
            f"timeline {timeline_id} must have exactly one delivery specification"
        )
    return matches[0]


def _tier_stages(version_role: object) -> list[str]:
    common = ["assembly"]
    fine = [
        "selected_takes",
        "approved_cut_points",
        "transitions",
        "reframe",
        "text_instructions",
        "audio_instructions",
    ]
    final = ["final_look", "loudness", "encoding", "probe_requirements"]
    if version_role == "rough_cut":
        return common
    if version_role == "fine_cut":
        return common + fine
    if version_role == "final_master":
        return common + fine + final
    raise BuildError(f"unsupported delivery tier {version_role}")


def _artifact_names(version_dir: Path) -> list[str]:
    return sorted(
        path.relative_to(version_dir).as_posix()
        for path in version_dir.rglob("*")
        if path.is_file() and path.name != "bundle_manifest.json"
    )


def _manifest(plan: dict[str, Any], version_dir: Path, status: str) -> dict[str, Any]:
    execution = plan.get("execution")
    manifest_id = execution.get("dry_run_manifest_id") if isinstance(execution, dict) else None
    return {
        "manifest_id": manifest_id,
        "edit_plan_id": plan.get("edit_plan_id"),
        "status": status,
        "version_directory": str(version_dir),
        "artifacts": _artifact_names(version_dir),
    }


def _build_handoffs(
    plan: dict[str, Any], version_dir: Path, ffmpeg_path: str
) -> list[dict[str, Any]]:
    command_deliveries: list[dict[str, Any]] = []
    try:
        for timeline in plan["timelines"]:
            slug = _timeline_slug(timeline)
            write_construction_markdown(
                plan, timeline, version_dir / f"edit_construction_{slug}.md"
            )
            write_construction_csv(
                plan, timeline, version_dir / f"edit_construction_{slug}.csv"
            )
            write_srt(plan, timeline, version_dir / f"subtitles_{slug}.srt")
            write_otio(plan, timeline, version_dir / f"timeline_{slug}.otio")
            write_fcpxml(plan, timeline, version_dir / f"timeline_{slug}.fcpxml")

            delivery = _delivery_for_timeline(plan, timeline.get("timeline_id"))
            command_deliveries.append(
                {
                    "delivery_id": delivery.get("delivery_id"),
                    "timeline_id": timeline.get("timeline_id"),
                    "version_role": delivery.get("version_role"),
                    "stages": _tier_stages(delivery.get("version_role")),
                    "commands": ffmpeg_command_plan(
                        plan,
                        timeline,
                        version_dir,
                        delivery,
                        ffmpeg_path=ffmpeg_path,
                    ),
                }
            )

        targets = {
            item.get("target")
            for item in plan["software_targets"]
            if isinstance(item, dict)
        }
        reports: dict[str, dict[str, str]] = {
            "ffmpeg": {
                "status": "planned",
                "artifact": "ffmpeg_commands.json",
            },
            "otio": {"status": "generated", "format": "public_schema"},
            "fcpxml": {"status": "generated", "format": "FCPXML 1.10"},
        }
        if "jianying_capcut" in targets:
            write_jianying_instructions(
                plan, version_dir / "jianying_capcut_instructions.md"
            )
            reports["jianying_capcut"] = {
                "status": "manual_or_unverified",
                "artifact": "jianying_capcut_instructions.md",
            }
        if "ai_editor" in targets:
            reports["ai_editor"] = {
                "status": "strict_json_handoff",
                "artifact": "edit_master_plan.json",
            }
        _write_json_exclusive(
            version_dir / "ffmpeg_commands.json",
            {"schema_version": 1, "deliveries": command_deliveries},
        )
        _write_json_exclusive(version_dir / "adapter_reports.json", reports)
    except (AdapterError, KeyError, TypeError) as exc:
        raise BuildError(str(exc)) from None
    return command_deliveries


def _execute_minimal(
    version_dir: Path,
    command_deliveries: list[dict[str, Any]],
    runner: Callable[..., subprocess.CompletedProcess],
) -> str:
    """Run a planned command list and record state; Task 6 adds full media/probe gates."""

    execution_log: dict[str, Any] = {
        "status": "running",
        "commands": [],
        "rendered_outputs": [],
    }
    blocked = False
    for delivery in command_deliveries:
        delivery_id = delivery["delivery_id"]
        commands = delivery["commands"]
        for args in commands:
            try:
                completed = runner(
                    args,
                    cwd=version_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                record = {
                    "delivery_id": delivery_id,
                    "args": args,
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            except OSError as exc:
                record = {
                    "delivery_id": delivery_id,
                    "args": args,
                    "returncode": None,
                    "stdout": "",
                    "stderr": str(exc),
                }
            execution_log["commands"].append(record)
            expected_output = Path(args[-1])
            if record["returncode"] != 0 or not expected_output.is_file():
                if record["returncode"] == 0:
                    record["stderr"] = (
                        (record["stderr"] + "\n").lstrip("\n")
                        + f"expected output is missing: {expected_output}"
                    )
                blocked = True
                break
        if blocked:
            break
        final_output = Path(commands[-1][-1])
        execution_log["rendered_outputs"].append(
            {
                "delivery_id": delivery_id,
                "output_ref": final_output.relative_to(version_dir).as_posix(),
                "status": "rendered",
            }
        )

    execution_log["status"] = "blocked" if blocked else "rendered"
    _write_json_exclusive(version_dir / "execution_log.json", execution_log)
    return execution_log["status"]


def build_edit_bundle(
    plan_path: Path,
    output_root: Path,
    *,
    execute: bool = False,
    ffmpeg_path: str | None = None,
    ffprobe_path: str | None = None,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> Path:
    """Validate a Canon plan and create a fresh dry-run (or authorized) bundle."""

    del ffprobe_path  # Reserved for Task 6 probe verification.
    source_path = Path(plan_path)
    with source_path.open("r", encoding="utf-8") as source:
        plan = json.load(source)

    errors = validate_edit_plan(plan)
    if errors:
        raise BuildError("\n".join(errors))
    if not isinstance(plan, dict):  # Kept explicit for type narrowing and callers.
        raise BuildError("edit plan: expected object")
    execution = plan.get("execution")
    if execute and (
        not isinstance(execution, dict)
        or execution.get("operation_authorization") != "approved"
    ):
        raise BuildError("operation authorization is required")

    version_dir = next_version_dir(Path(output_root))
    root = Path(output_root).resolve()
    try:
        version_dir.resolve().relative_to(root)
    except ValueError:
        raise BuildError("version directory escapes output_root") from None
    try:
        version_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise BuildError(f"version directory already exists: {version_dir}") from None
    except OSError as exc:
        raise BuildError(f"could not create version directory: {exc}") from None

    _write_json_exclusive(version_dir / "edit_master_plan.json", plan)
    command_deliveries = _build_handoffs(
        plan, version_dir, ffmpeg_path or "ffmpeg"
    )
    manifest_path = version_dir / "bundle_manifest.json"
    manifest = _manifest(plan, version_dir, "dry_run_passed")
    _write_json_exclusive(manifest_path, manifest)

    if not execute:
        return version_dir
    if ffmpeg_path is None or not str(ffmpeg_path).strip():
        manifest["status"] = "blocked"
        _replace_owned_json(manifest_path, manifest)
        raise BuildError("ffmpeg is unavailable")

    status = _execute_minimal(version_dir, command_deliveries, runner)
    manifest["status"] = status
    manifest["artifacts"] = _artifact_names(version_dir)
    _replace_owned_json(manifest_path, manifest)
    return version_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a versioned finished-film editing handoff bundle."
    )
    parser.add_argument("plan", type=Path, help="UTF-8 edit_master_plan JSON")
    parser.add_argument("--out", type=Path, required=True, help="Bundle output root")
    parser.add_argument("--execute", action="store_true", help="Run an authorized FFmpeg plan")
    parser.add_argument("--ffmpeg", help="Explicit FFmpeg executable path")
    parser.add_argument("--ffprobe", help="Explicit ffprobe executable path")
    args = parser.parse_args(argv)

    try:
        version_dir = build_edit_bundle(
            args.plan,
            args.out,
            execute=args.execute,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, MemoryError) as exc:
        detail = str(exc) or type(exc).__name__
        print(f"ERROR: could not load edit plan: {detail}", file=sys.stderr)
        return 2
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    manifest = json.loads(
        (version_dir / "bundle_manifest.json").read_text(encoding="utf-8")
    )
    print(version_dir)
    print(f"Bundle status: {manifest['status']}")
    return 0 if manifest["status"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
