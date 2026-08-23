# Project State

Last updated: 2026-08-23

## Current phase

Phase 1 — Repository and project documentation: complete.

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

## Next

Phase 2 — Local MP4 video processing.

Expected scope:

- Initialize the Python 3.12 `cv-engine` project with `uv`.
- Read the supplied MP4 with `opencv-python-headless`.
- Validate source opening, frame iteration, metadata, and end-of-stream behavior.
- Add focused pytest coverage.
- Do not add YOLO yet; detection belongs to Phase 3.

## Environment observations

The workstation tools observed during Phase 1 do not yet match the project
baseline:

- Python: installed 3.14.7; required 3.12.x.
- Java: installed 17; required 21 LTS.
- Node.js: installed 24.11.1; required 22 LTS.
- `uv`: not installed.
- Docker and Docker Compose are available.

Only Python 3.12 and `uv` are needed for the next phase. Java and Node can be
aligned when their phases begin.

## Known issues

- No application code exists yet by design.
- The sample MP4 has not been copied into the repository.
