# ADR 006: Hibrit senkron ve asenkron iletişim modeli

- Status: Accepted
- Date: 2026-08-23

## Context

Video incident üretimi, kullanıcı REST işlemleri, modül içi çağrılar ve gerçek
zamanlı UI bildirimleri aynı latency, coupling ve dayanıklılık ihtiyaçlarına
sahip değildir. Her iletişimi senkron yapmak CV worker'ı backend availability'ye
bağlar; her iletişimi event'e dönüştürmek ise tek process içindeki basit
işlemlere gereksiz eventual consistency ve debugging maliyeti ekler.

## Decision

Sistem hibrit model kullanır:

- CV Engine -> Kafka -> Backend incident akışı asenkrondur.
- Backend -> React WebSocket bildirimleri asenkrondur.
- Gelecekte notification, analytics ve archive yan etkileri asenkron olabilir.
- React -> Backend REST, camera/zone CRUD ve hemen cevap gerektiren doğrulamalar
  senkrondur.
- Backend modülleri arasındaki basit bilgi/command çağrıları dar application
  interface'leri üzerinden varsayılan olarak senkrondur.
- İlk mimaride PostgreSQL ve Redis erişimi blocking/senkron Spring stack'iyle
  yürütülür.

Kafka consumer duplicate teslimata dayanıklı tasarlanır. `event_id` database
seviyesinde unique olur, mesaj kalıcı transaction başarıyla tamamlanmadan
işlenmiş sayılmaz ve WebSocket bildirimi kayıttan sonra gönderilir.

## Consequences

- CV pipeline backend'in anlık availability durumundan ayrışır.
- Basit in-process use case'ler network/event karmaşıklığı taşımaz.
- UI düşük gecikmeli bildirim alır ancak source of truth olarak REST/PostgreSQL
  kullanılmaya devam eder.
- Internal event yalnızca zaman ayrıştırması, çoklu tüketici veya bağımsız
  hata/ölçekleme ihtiyacı olduğunda eklenir.
- Idempotency ve doğru Kafka acknowledgement davranışı Phase 8-9 testlerinde
  zorunludur.

