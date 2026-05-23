#!/usr/bin/env python3
"""Review Birch checker screenshots for egregious visual aberrations.

This script is intentionally narrow: it asks a VLM through fast-agent to find
visible rendering defects that deterministic HTML/geometry checks often miss,
then writes `vision-findings.json` for the GEPA evaluator to surface as ASI
feedback.

Usage:
  python3 scripts/review_birch_screenshots_with_vision.py <candidate_dir> <reports_dir>

Environment:
  BIRCH_VISION_MODEL       default: codexresponses.gpt-5.5
  BIRCH_VISION_MAX_IMAGES  default: 80
  BIRCH_VISION_BATCH_MODE  default: per-artifact
  BIRCH_VISION_TIMEOUT     default: 300 seconds per VLM request
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FAST_AGENT_ENV = ROOT / ".fast-agent"
FAST_AGENT_CONFIG = FAST_AGENT_ENV / "fast-agent.yaml"
FAST_AGENT_NAME = "birch-vision-reviewer"
DEFAULT_TIMEOUT = 300


PROMPT = """You are a visual smoke-test reviewer for rendered Birch HTML artifacts.

Look only for egregious visual rendering defects that a deterministic HTML
checker might miss. Do not judge taste, prose quality, or ordinary design
preferences. Report issues only when a human reviewer would likely say the
rendered artifact is visibly broken or misleading.

Flag examples:
- malformed charts/SVGs, especially filled black wedges instead of line marks;
- a line chart that appears as a thick filled triangle, wedge, ribbon, or
  polygon is a FAIL even if labels/data remain readable;
- any chart panel where the plotted mark is much thicker than intended or filled
  solid black should be flagged as `vision_chart_malformed`;
- chart marks, labels, bars, or axes badly overlapping;
- flowcharts/diagrams where connector lines visibly miss boxes, terminate in
  empty space, pass behind/through the wrong node, or make the flow ambiguous;
- horizontal/vertical connectors that are clipped at the screenshot edge or
  continue offscreen before/after a node should be flagged as
  `vision_flow_disconnected`;
- pipeline/flow diagrams whose boxes are arranged as separate disconnected
  columns or islands rather than one readable path through the major steps;
- missing connectors between adjacent/sequential boxes when the title, caption,
  labels, or layout imply those boxes are part of the same flow;
- diagrams where individual connector segments touch some boxes but the overall
  graph is not connected enough to understand the process order;
- visibly misaligned chart labels, axes, legends, table columns, or content
  blocks when the misalignment makes the artifact harder to read or misleading;
- huge unintended black regions;
- clipped or cut-off title/text;
- text absurdly oversized for its card/container;
- severe overlap or offscreen content;
- one-character-per-line or pathological wrapping;
- ordinary sentence/list text wrapping to one or two words, or only a few
  characters, per line inside an otherwise wide card/panel is a FAIL as
  `vision_pathological_wrapping`;
- checklist/list rows where the icon/marker column consumes layout and leaves
  the prose in a skinny vertical strip are a FAIL;
- a common failure looks like a normal-width card with a checkmark at the left
  and the sentence beside it rendered as a tall column of fragments such as
  "For / ea / ch / ev / al" or "Ca / ptu / re / wal / l- / clo / ck"; flag
  this even when the text is technically inside the card and not clipped;
- blank, unstyled, or mostly missing render;
- mobile layout unusable.

Ignore:
- minor aesthetic preferences;
- normal dense reports;
- content/rubric quality unless it creates a visible rendering defect.

Return JSON only. Use the exact screenshot file name for each artifact entry.

Use fail only for clearly broken renders. Use warn for suspicious but still
readable visual defects. Return an empty findings list when no aberration is
visible for a screenshot.

Before returning, deliberately inspect every visible chart panel/SVG in deep
screenshots. Do not stop after reviewing the first viewport. Deep screenshots
exist specifically to reveal below-the-fold visual aberrations.

Also deliberately inspect every visible flowchart or node-link diagram. Treat
disconnected connectors as a visual defect even when the boxes and labels are
readable, because the diagram conveys the wrong process structure. Do not limit
this to literal line-end gaps: isolated node columns, missing cross-column
links, or a pipeline with no continuous path through the major boxes should be
reported as `vision_flow_disconnected`.
"""

JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "artifacts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "artifact": {"type": "string"},
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "level": {"type": "string", "enum": ["fail", "warn"]},
                                "name": {
                                    "type": "string",
                                    "enum": [
                                        "vision_chart_malformed",
                                        "vision_oversized_type",
                                        "vision_overlap",
                                        "vision_clipped_content",
                                        "vision_unstyled_render",
                                        "vision_pathological_wrapping",
                                        "vision_alignment_issue",
                                        "vision_flow_disconnected",
                                        "vision_other",
                                    ],
                                },
                                "evidence": {"type": "string"},
                                "confidence": {"type": "number"},
                            },
                            "required": ["level", "name", "evidence", "confidence"],
                        },
                    },
                },
                "required": ["artifact", "findings"],
            },
        }
    },
    "required": ["artifacts"],
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_dir", type=Path)
    parser.add_argument("reports_dir", type=Path)
    parser.add_argument("--model", default=os.environ.get("BIRCH_VISION_MODEL", "codexresponses.gpt-5.5"))
    parser.add_argument("--max-images", type=int, default=int(os.environ.get("BIRCH_VISION_MAX_IMAGES", "80")))
    parser.add_argument(
        "--batch-mode",
        choices=["per-artifact", "per-screenshot", "all"],
        default=os.environ.get("BIRCH_VISION_BATCH_MODE", "per-artifact"),
        help="Review one eval artifact per VLM call, one screenshot per call, or all screenshots in one request.",
    )
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("BIRCH_VISION_TIMEOUT", DEFAULT_TIMEOUT)))
    args = parser.parse_args()

    out = args.reports_dir / "vision-findings.json"
    screenshots = find_screenshots(args.reports_dir, args.max_images)
    if not screenshots:
        write_json(out, {"artifacts": [], "skipped": "no screenshots found"})
        return

    try:
        payload = review_with_fast_agent(args.model, screenshots, args.batch_mode, args.timeout)
    except Exception as exc:  # noqa: BLE001 - preserve GEPA run, surface as feedback
        write_json(
            out,
            {
                "artifacts": [
                    {
                        "artifact": "vision-review",
                        "findings": [
                            {
                                "level": "warn",
                                "name": "vision_review_unavailable",
                                "evidence": f"{type(exc).__name__}: {exc}",
                                "confidence": 1.0,
                            }
                        ],
                    }
                ]
            },
        )
        return

    write_json(out, normalize_payload(payload, screenshots))


def find_screenshots(reports_dir: Path, max_images: int) -> list[Path]:
    screenshots_dir = reports_dir / "screenshots"
    if not screenshots_dir.exists():
        return []
    images = [
        p for p in sorted(screenshots_dir.glob("*.png"))
        if "__vs__" not in p.name and not p.name.endswith(("-diff.png", "-contact.png"))
    ]
    def priority(path: Path) -> tuple[int, str]:
        name = path.name
        # Deep screenshots include below-the-fold charts/tables and are most
        # valuable for VLM aberration review.
        if "-deep" in name:
            return (0, name)
        if "-desktop" in name:
            return (1, name)
        if "-mobile" in name:
            return (2, name)
        return (3, name)

    prioritized = sorted(images, key=priority)
    review_images = make_deep_tiles(prioritized, reports_dir)
    return review_images[:max(1, max_images)]


def make_deep_tiles(images: list[Path], reports_dir: Path) -> list[Path]:
    """Add readable vertical tiles for deep screenshots.

    Full-page screenshots are useful context, but VLMs often miss below-the-fold
    chart defects after the image is downsampled. Tiles keep chart panels at a
    similar scale to first-viewport screenshots.
    """

    try:
        from PIL import Image
    except Exception:
        return images
    crops_dir = reports_dir / "vision-crops"
    if crops_dir.exists():
        for old in crops_dir.glob("*.png"):
            old.unlink()
    crops_dir.mkdir(parents=True, exist_ok=True)

    out: list[Path] = []
    for path in images:
        if "-deep" not in path.name:
            out.append(path)
            continue
        image = Image.open(path).convert("RGB")
        tile_h = 900 if image.width > 700 else 1000
        overlap = 140
        y = 0
        idx = 1
        while y < image.height:
            bottom = min(image.height, y + tile_h)
            if bottom - y < 320:
                break
            tile = image.crop((0, y, image.width, bottom))
            tile_path = crops_dir / f"{path.stem}__tile-{idx:02d}.png"
            tile.save(tile_path, optimize=True)
            out.append(tile_path)
            idx += 1
            if bottom == image.height:
                break
            y = bottom - overlap
        out.append(path)
    return out


def review_with_fast_agent(model: str, screenshots: list[Path], batch_mode: str, timeout: int) -> dict[str, Any]:
    """Review screenshots with `fast-agent go --attach`."""

    groups = (
        list(group_screenshots_by_artifact(screenshots).values())
        if batch_mode == "per-artifact"
        else [[path] for path in screenshots]
        if batch_mode == "per-screenshot"
        else [screenshots]
    )
    artifacts: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="birch-vision-") as tmp:
        tmpdir = Path(tmp)
        schema_path = tmpdir / "schema.json"
        schema_path.write_text(json.dumps(JSON_SCHEMA), encoding="utf-8")
        results_dir = screenshots[0].parents[1] / "fast-agent-vision-results"
        results_dir.mkdir(parents=True, exist_ok=True)
        for index, group in enumerate(groups, start=1):
            prompt_path = tmpdir / f"prompt-{index:02d}.txt"
            prompt_path.write_text(prompt_for_group(group), encoding="utf-8")
            attachments = [attachment_path(path, tmpdir) for path in group]
            result_stem = artifact_key(group[0]) if group else f"batch-{index:02d}"
            result_stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", result_stem).strip("-") or f"batch-{index:02d}"
            results_path = results_dir / f"{index:02d}-{result_stem}.json"
            cmd = [
                "fast-agent",
                "--no-update-check",
                "--env",
                str(FAST_AGENT_ENV),
                "go",
                "--config-path",
                str(FAST_AGENT_CONFIG),
                "--name",
                FAST_AGENT_NAME,
                "--model",
                model,
                "--quiet",
                "--no-shell",
                "--prompt-file",
                str(prompt_path),
                "--json-schema",
                str(schema_path),
                "--results",
                str(results_path),
            ]
            for path in attachments:
                cmd.extend(["--attach", str(path)])
            proc = subprocess.run(
                cmd,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout,
            )
            if proc.returncode:
                detail = (proc.stderr or proc.stdout).strip()[-1200:]
                raise RuntimeError(f"fast-agent exited {proc.returncode}: {detail}")
            payload = json.loads(strip_json_fence(proc.stdout))
            artifacts.extend(normalize_payload(payload, group).get("artifacts", []))
    return {"artifacts": artifacts}


def prompt_for_group(group: list[Path]) -> str:
    names = "\n".join(f"- {path.name}" for path in group)
    return f"{PROMPT}\n\nAttached screenshots, in order:\n{names}\n"


def group_screenshots_by_artifact(screenshots: list[Path]) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = {}
    for path in screenshots:
        groups.setdefault(artifact_key(path), []).append(path)
    return groups


def artifact_key(path: Path) -> str:
    stem = re.sub(r"__tile-\d+$", "", path.stem)
    for suffix in ("-mobile-deep", "-desktop-deep", "-deep", "-desktop", "-mobile"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def attachment_path(path: Path, tmpdir: Path, max_width: int = 1000) -> Path:
    try:
        from PIL import Image
    except Exception:
        return path
    image = Image.open(path).convert("RGB")
    if image.width <= max_width:
        return path
    ratio = max_width / image.width
    resized = image.resize((max_width, max(1, int(image.height * ratio))))
    out = tmpdir / path.name
    if out.exists():
        out = tmpdir / f"{path.stem}-{abs(hash(path))}{path.suffix}"
    resized.save(out, format="PNG", optimize=True)
    return out


def strip_json_fence(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.I | re.S)
    return match.group(1).strip() if match else text


def normalize_payload(payload: Any, screenshots: list[Path]) -> dict[str, Any]:
    names = {p.name for p in screenshots}
    items = payload.get("artifacts") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return {"artifacts": []}
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        artifact = str(item.get("artifact") or item.get("screenshot") or "")
        if artifact and artifact not in names:
            # Keep VLM output, but make unclear labels obvious to downstream readers.
            artifact = artifact
        findings = []
        for finding in item.get("findings") or []:
            if not isinstance(finding, dict):
                continue
            level = finding.get("level")
            if level not in {"fail", "warn"}:
                continue
            findings.append(
                {
                    "level": level,
                    "name": str(finding.get("name") or "vision_other"),
                    "evidence": str(finding.get("evidence") or "")[:500],
                    "confidence": float(finding.get("confidence") or 0.0),
                }
            )
        out.append({"artifact": artifact or "screenshot", "findings": findings})
    return {"artifacts": out}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
