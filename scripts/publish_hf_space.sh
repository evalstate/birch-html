#!/usr/bin/env bash
# Publish the Birch HTML benchmark browser to Hugging Face.
#
# By default this uses a bucket for the large/static report payload and a tiny
# Docker Space that mounts the bucket read-only and serves it with FastAPI.
# Set PUBLISH_MODE=static to upload the static payload directly to an
# `sdk: static` Space instead. Static Spaces cannot read from mounted buckets;
# they serve files committed to the Space repo.
#
# Defaults:
#   bucket: <hf-user>/birch-html
#   space:  <hf-user>/birch-html
#
# Requirements:
#   - `hf` CLI installed and logged in (`hf auth login`)
#   - current eval run records present under eval-runs/
#
# Typical use:
#   scripts/publish_hf_space.sh
#
# Useful overrides:
#   HF_NAMESPACE=evalstate scripts/publish_hf_space.sh
#   HF_SITE_NAME=birch-html scripts/publish_hf_space.sh
#   LABEL_SUFFIX=publish-run scripts/publish_hf_space.sh
#   PUBLISH_MODE=static scripts/publish_hf_space.sh
#   DRY_RUN=1 scripts/publish_hf_space.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

HF_SITE_NAME="${HF_SITE_NAME:-birch-html}"
LABEL_SUFFIX="${LABEL_SUFFIX:-publish-run}"
HF_NAMESPACE="${HF_NAMESPACE:-}"
BUCKET_ID="${BUCKET_ID:-}"
SPACE_ID="${SPACE_ID:-}"
PUBLISH_ROOT="${PUBLISH_ROOT:-$ROOT/.publish}"
SITE_DIR="$PUBLISH_ROOT/$HF_SITE_NAME-bucket"
SPACE_DIR="$PUBLISH_ROOT/$HF_SITE_NAME-space"
DRY_RUN="${DRY_RUN:-0}"
SKIP_REBUILD="${SKIP_REBUILD:-0}"
PUBLISH_MODE="${PUBLISH_MODE:-bucket}" # bucket | static

run() {
  echo "+ $*"
  if [[ "$DRY_RUN" != "1" ]]; then
    "$@"
  fi
}

if [[ -z "$HF_NAMESPACE" ]]; then
  HF_NAMESPACE="$(hf auth whoami 2>/dev/null | awk '/user:/ {print $2; exit}')"
fi
if [[ -z "$HF_NAMESPACE" ]]; then
  echo "Could not infer HF namespace. Set HF_NAMESPACE=<user-or-org>." >&2
  exit 2
fi

BUCKET_ID="${BUCKET_ID:-$HF_NAMESPACE/$HF_SITE_NAME}"
SPACE_ID="${SPACE_ID:-$HF_NAMESPACE/$HF_SITE_NAME}"
BUCKET_URI="hf://buckets/$BUCKET_ID"

if [[ "$SKIP_REBUILD" != "1" ]]; then
  run python3 scripts/package_final_eval_runs.py --label-suffix "$LABEL_SUFFIX"
  run python3 scripts/build_publication_analysis.py --suite publish
  run python3 scripts/generate_responsive_report.py
fi

rm -rf "$SITE_DIR" "$SPACE_DIR"
mkdir -p "$SITE_DIR" "$SPACE_DIR"

# Bucket payload: keep the paths used by analysis/report.html intact.
cp -a analysis "$SITE_DIR/analysis"
mkdir -p "$SITE_DIR/results"
cp -a results/publish "$SITE_DIR/results/publish"

cat > "$SITE_DIR/index.html" <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=/analysis/report.html">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Birch HTML Benchmark</title>
</head>
<body>
  <p><a href="/analysis/report.html">Open the Birch HTML benchmark report</a>.</p>
</body>
</html>
HTML

if [[ "$PUBLISH_MODE" == "static" ]]; then
  # Static Space payload: files must live in the Space repo. There is no bucket
  # mount/runtime for sdk: static.
  cp -a "$SITE_DIR"/. "$SPACE_DIR"/
  cat > "$SPACE_DIR/README.md" <<EOF
---
title: Birch HTML
emoji: 🌿
colorFrom: green
colorTo: yellow
sdk: static
pinned: false
short_description: Birch HTML benchmark browser
---

# Birch HTML Benchmark

This static Space serves the Birch HTML benchmark browser directly from files
committed to the Space repository.

Entry point:

\`\`\`text
/analysis/report.html
\`\`\`
EOF
else
  # Docker Space payload: a tiny static-file server. The bucket is mounted at
  # /data. This keeps the large static report payload out of the Space git repo.
  cat > "$SPACE_DIR/Dockerfile" <<'DOCKER'
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SITE_ROOT=/data

RUN pip install --no-cache-dir fastapi "uvicorn[standard]"

WORKDIR /app
COPY app.py /app/app.py

EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
DOCKER

  cat > "$SPACE_DIR/app.py" <<'PY'
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


SITE_ROOT = Path(os.environ.get("SITE_ROOT", "/data")).resolve()
REPORT = SITE_ROOT / "analysis" / "report.html"

app = FastAPI(title="Birch HTML Benchmark")


@app.get("/")
def root():
    if REPORT.exists():
        return RedirectResponse("/analysis/report.html", status_code=302)
    return HTMLResponse(
        "<!doctype html><title>Birch HTML Benchmark</title>"
        "<h1>Birch HTML Benchmark</h1>"
        f"<p>Report not found at <code>{REPORT}</code>. "
        "Check that the bucket is mounted at <code>/data</code>.</p>",
        status_code=503,
    )


@app.get("/healthz")
def healthz():
    return {
        "ok": REPORT.exists(),
        "site_root": str(SITE_ROOT),
        "report": str(REPORT),
    }


@app.get("/analysis/report.html")
def report():
    if REPORT.exists():
        return FileResponse(REPORT)
    return root()


if SITE_ROOT.exists():
    app.mount("/", StaticFiles(directory=SITE_ROOT, html=True), name="site")
PY

  cat > "$SPACE_DIR/README.md" <<EOF
---
title: Birch HTML
emoji: 🌿
colorFrom: green
colorTo: yellow
sdk: docker
pinned: false
short_description: Birch HTML benchmark browser
---

# Birch HTML Benchmark

This Space serves the static Birch HTML benchmark browser from the mounted
Hugging Face bucket:

\`\`\`text
$BUCKET_URI -> /data
\`\`\`

Entry point:

\`\`\`text
/analysis/report.html
\`\`\`
EOF
fi

echo "Prepared static payload:"
du -sh "$SITE_DIR"
echo "Prepared Space payload:"
find "$SPACE_DIR" -maxdepth 2 -type f -print

if [[ "$PUBLISH_MODE" == "static" ]]; then
  run hf repos create "$SPACE_ID" \
    --type space \
    --space-sdk static \
    --public \
    --exist-ok
else
  run hf buckets create "$BUCKET_ID" --exist-ok
  run hf buckets sync "$SITE_DIR" "$BUCKET_URI" --delete

  # Create the Space with the bucket mounted read-only. If the Space already
  # exists, hf ignores creation-only settings; ensure the volume exists manually
  # if you created the Space earlier without this script.
  run hf repos create "$SPACE_ID" \
    --type space \
    --space-sdk docker \
    --public \
    --exist-ok \
    --volume "$BUCKET_URI:/data:ro"
fi

if [[ "$PUBLISH_MODE" == "static" ]]; then
  run hf upload "$SPACE_ID" "$SPACE_DIR" . \
    --repo-type space \
    --commit-message "Publish Birch HTML benchmark browser" \
    --delete "Dockerfile" \
    --delete "app.py"
else
  run hf upload "$SPACE_ID" "$SPACE_DIR" . \
    --repo-type space \
    --commit-message "Publish Birch HTML benchmark browser" \
    --delete "analysis/**" \
    --delete "results/**" \
    --delete "index.html"
fi

echo
if [[ "$PUBLISH_MODE" == "static" ]]; then
  echo "Published mode:   static Space repo"
else
  echo "Published bucket: $BUCKET_URI"
fi
echo "Published Space:  https://huggingface.co/spaces/$SPACE_ID"
echo "Report URL:        https://$HF_NAMESPACE-$HF_SITE_NAME.hf.space/analysis/report.html"
