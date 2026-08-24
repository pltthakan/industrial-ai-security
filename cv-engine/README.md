# CV Engine

Python 3.12 video-processing worker for Industrial AI Security.

Phase 3 adds CPU-first YOLO26n person detection to the Phase 2 local MP4
pipeline. The detector requests only COCO class `0`, converts Ultralytics output
to validated Pydantic contracts, and writes an annotated video. Tracking is not
part of this command; ByteTrack starts in Phase 4.

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

## Detect people

The first run downloads the ignored `yolo26n.pt` weight file. Run the full
factory-floor sample from the repository root:

```bash
uv run --project cv-engine cv-person-detect
```

The annotated output is written to
`artifacts/phase3/factory-floor-person-detection.mp4`. Configuration can be
provided with CLI options or `CV_` environment variables:

```bash
uv run --project cv-engine cv-person-detect \
  --source samples/factory-floor.mp4 \
  --output artifacts/phase3/persons.mp4 \
  --confidence 0.25 \
  --image-size 960 \
  --device cpu \
  --max-frames 30
```

The CPU build of PyTorch is locked for reproducible local and CI installs.
Accelerator selection is intentionally deferred to the performance phase.
The 960-pixel, 0.25-confidence baseline was selected against the supplied
1920x1080/6 FPS scene: it retained real-time headroom while recovering small,
distant workers missed by the initial 640-pixel trial. This is a functional
baseline, not a production accuracy claim.
Model provenance, checksum, and licensing notes are recorded in
[`models/yolo26n.json`](models/yolo26n.json). The model weights and generated
videos are not committed.

## Test

```bash
uv run --directory cv-engine pytest \
  --cov=industrial_ai_security_cv \
  --cov-report=term-missing
```

Tests generate a tiny temporary video and use an inference test double, so CI
does not download model weights or depend on the ignored factory sample. The
real sample run remains an explicit integration check.
