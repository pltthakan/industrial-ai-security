# ADR 003: Ultralytics üzerinden ByteTrack

- Status: Accepted
- Date: 2026-08-23

## Context

Sanal bölge olaylarını kişi bazında değerlendirmek için kareler arasında stabil
kimlik gerekir. Ultralytics, YOLO sonuçlarıyla uyumlu yerleşik ByteTrack desteği
sunar.

## Decision

Tracking için `model.track(..., tracker="bytetrack.yaml", persist=True)` akışı
kullanılır. Ayrı ByteTrack paketi, DeepSORT veya supervision eklenmez.

## Consequences

- Detection ve tracking entegrasyonu tek framework içinde kalır.
- Ek tracking bağımlılıklarının sürüm ve veri modeli uyumsuzluğu önlenir.
- Tracking davranışı Phase 4'te gerçek video üzerinde test edilir.

