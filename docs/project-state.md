# Project State

Last updated: 2026-08-23

## Current phase

Phase 3 — YOLO person detection: complete.

## Completed

- Added durable repository rules in `AGENTS.md`.
- Recorded the target architecture and component boundaries.
- Recorded the phased roadmap and current state.
- Added initial architecture decision records.
- Added placeholder component directories without introducing dependencies.
- Inspected the supplied factory-floor video: H.264, 1920x1080, 6 FPS,
  approximately 17.09 seconds.
- Added GitHub Actions CI with repository, CV engine, backend, frontend, and
  Docker Compose jobs.
- Documented the gated CD design; deployment remains disabled until deployable
  containers and a target environment exist.
- Accepted the Spring Boot backend as a modular monolith with explicit module,
  repository, entity, and table ownership boundaries.
- Translated `AGENTS.md` to Turkish and formalized pragmatic SOLID, module
  responsibility, hybrid sync/async communication, idempotent Kafka processing,
  and future service-level database credential ownership.
- Initialized the Python 3.12 CV engine with `uv`, `pyproject.toml`, and a
  committed `uv.lock`.
- Added typed local-video settings, validated metadata models, deterministic
  OpenCV capture lifecycle, frame iteration, and end-of-stream probing.
- Added focused tests using a generated synthetic video so CI does not depend on
  a large sample asset.
- Verified 19 tests with 98.86% branch-aware production-package coverage on
  Python 3.12.14.
- Probed the supplied 1920x1080 H.264 video end to end: all 102 frames decoded
  and end of stream was reached.
- Added locked PyTorch 2.13 and Ultralytics 8.4 dependencies with CPU-only
  PyTorch wheels and retained `opencv-python-headless` instead of the GUI build.
- Added a YOLO26n adapter that explicitly requests only COCO class `0`
  (`person`) and converts external detections into validated Pydantic contracts.
- Added configurable confidence, IoU, image size, device, source, output, and
  frame-limit settings plus the `cv-person-detect` CLI.
- Compared 640/0.35, 960/0.25, and 1280/0.25 configurations on the supplied
  scene. Selected 960/0.25 because visual review recovered small distant people
  while the final sequential run observed 48.38 ms/frame, below the 166.67 ms
  source frame budget. The sequential 1280 run observed 82.41 ms/frame and did
  not provide a useful visual gain.
- Added annotated-video orchestration while keeping detection independent from
  tracking, zone, incident, and Kafka behavior.
- Recorded model source, SHA-256, framework version, and Ultralytics licensing
  note in `cv-engine/models/yolo26n.json`; weights remain ignored by Git.
- Verified 45 tests with 97.32% branch-aware production-package coverage. Tests
  use an inference double and do not download model weights in CI.
- Ran the selected YOLO26n baseline on all 102 frames of the supplied
  factory-floor video: 643 person detections across 102 frames and approximately
  48.38 ms average inference per frame in the final sequential run.
- Verified the annotated output as MPEG-4, 1920x1080, 6 FPS, 102 frames and
  visually inspected its midpoint. This is a functional integration result,
  not a model-accuracy benchmark.

## Next

Phase 4 — ByteTrack object tracking.

Expected scope:

- Use Ultralytics' built-in ByteTrack integration; do not add a separate
  tracking package.
- Assign stable track IDs to person detections across frames.
- Keep tracking output typed and independent from zone/incident behavior.
- Add deterministic tests for track ID propagation and lifecycle boundaries.
- Run tracking against the supplied factory-floor video.

## Environment observations

The workstation tools observed during Phase 1 do not yet match the project
baseline:

- Python: system default is 3.14.7; `uv` manages Python 3.12.14 for the CV
  engine.
- Java: installed 17; required 21 LTS.
- Node.js: installed 24.11.1; required 22 LTS.
- `uv`: 0.12.5 installed through Homebrew.
- Docker and Docker Compose are available.

Java and Node can be aligned when their phases begin.

## Known issues

- The user-level `/Users/hakan/.local` directory is owned by root, so local `uv`
  verification used writable macOS Library paths for managed Python and cache.
- The factory-floor MP4 is present locally under `samples/` and intentionally
  ignored by Git.
