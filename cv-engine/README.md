# CV Engine

Python 3.12 video-processing worker for Industrial AI Security.

Phase 2 implements local MP4 opening, validated metadata extraction, frame
iteration, deterministic resource release, and end-of-stream detection through
`opencv-python-headless`. Object detection intentionally starts in Phase 3.

## Setup

From the repository root:

```bash
uv sync --project cv-engine --locked --all-groups
```

`uv` uses `cv-engine/.python-version` and downloads Python 3.12 when a compatible
local interpreter is unavailable.

## Probe the factory-floor video

Place the ignored sample at `samples/factory-floor.mp4`, then run:

```bash
uv run --project cv-engine cv-video-probe
```

An explicit path or frame limit can be supplied:

```bash
uv run --project cv-engine cv-video-probe \
  --source samples/factory-floor.mp4 \
  --max-frames 30
```

Environment variables use the `CV_` prefix:

```bash
CV_SOURCE=samples/factory-floor.mp4 \
CV_MAX_FRAMES=30 \
uv run --project cv-engine cv-video-probe
```

## Test

```bash
uv run --directory cv-engine pytest \
  --cov=industrial_ai_security_cv \
  --cov-report=term-missing
```

Tests generate a tiny temporary video and do not depend on the ignored factory
sample being present in CI.
