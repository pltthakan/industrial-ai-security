# ADR 002: Ana uygulama backend'i olarak Spring Boot

- Status: Accepted
- Date: 2026-08-23

## Context

Sistemin Kafka tüketimi, kalıcı veri, cache/cooldown, REST ve WebSocket
sorumlulukları için tek bir uygulama backend'ine ihtiyacı vardır.

## Decision

Ana backend Java 21 ve Spring Boot 3.5.x ile geliştirilir. Python bileşeni video
pipeline worker'ı olarak kalır. Başlangıç mimarisine FastAPI eklenmez.

## Consequences

- HTTP ve WebSocket yüzeyleri Spring Boot'ta merkezileşir.
- React yalnızca backend ile iletişim kurar.
- İkinci bir HTTP backend'in operasyonel ve sözleşmesel karmaşıklığı oluşmaz.

