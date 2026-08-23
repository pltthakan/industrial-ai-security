# Project State

Last updated: 2026-08-23

## Current phase

Phase 2 — Local MP4 video processing: complete.

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

## Next

Phase 3 — YOLO person detection.

Expected scope:

- Add PyTorch and Ultralytics YOLO through `uv`.
- Detect only the `person` class in decoded frames.
- Keep detection separate from tracking; ByteTrack belongs to Phase 4.
- Add typed detection output and focused tests.
- Run the detector against the supplied factory-floor video.

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
