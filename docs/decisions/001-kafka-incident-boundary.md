# ADR 001: Olay sınırı olarak Kafka

- Status: Accepted
- Date: 2026-08-23

## Context

Görüntü işleme worker'ı ile iş verisini yöneten backend farklı çalışma zamanı,
ölçekleme ve hata davranışlarına sahiptir. CV worker'ın veri katmanına doğrudan
bağlanması bu sorumlulukları birbirine bağlar.

## Decision

CV engine, incident olaylarını `security.incidents` Kafka topic'ine yayınlar.
Spring Boot backend topic'i tüketir ve PostgreSQL/Redis/WebSocket işlemlerini
yürütür. Kafka KRaft modunda çalışır; ZooKeeper kullanılmaz.

## Consequences

- CV engine PostgreSQL ve Redis istemcisi taşımaz.
- Backend olay dayanıklılığı, doğrulama ve tekrar işleme davranışından sorumludur.
- Mesajlar küçük tutulur; büyük image binary yerine snapshot referansı taşınır.

