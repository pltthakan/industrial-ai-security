# ADR 005: Spring Boot backend için modüler monolith

- Status: Accepted
- Date: 2026-08-23

## Context

Python CV engine ile Spring Boot backend Kafka üzerinden zaten ayrı runtime'lar
olarak çalışır. Backend tarafında camera, zone, incident, notification ve
analytics gibi her kavramı başlangıçta ayrı servise dönüştürmek; henüz bağımsız
ölçekleme veya deployment ihtiyacı yokken network, retry, timeout, tracing ve
dağıtık veri yönetimi maliyeti oluşturur.

Buna karşın bütün backend kodunu sınırsız şekilde birbirine bağlamak da domain
sınırlarını kaybettirir ve ileride değişiklik yapmayı zorlaştırır.

## Decision

Backend tek Java 21 / Spring Boot 3.5.x uygulaması ve tek deploy edilebilir
container olarak geliştirilir. Uygulama package-by-feature düzeninde bir modüler
monolith olacaktır.

Bir modül:

- kendi domain modeline, application service'lerine, repository/adapters'ına ve
  veritabanı tablolarına sahip olur;
- başka bir modülün repository'sini veya JPA entity'sini doğrudan kullanmaz;
- başka aggregate'lere `cameraId`, `zoneId` gibi kararlı kimliklerle referans
  verir;
- gerekli modül iletişimini sağlayan modülün dar application interface'i veya
  gerçekten uygun olduğunda internal event üzerinden yürütür.

SOLID ilkeleri pragmatik uygulanır: modül ve sınıflar tutarlı bir değişim
nedenine sahip olur; domain/application kuralları infrastructure detaylarına
doğrudan bağlanmaz; public module interface'leri küçük ve use case odaklı
tutulur. Her sınıf için interface ya da kanıtlanmamış gelecekteki ihtiyaçlar için
abstraction oluşturulmaz.

Modüler monolith tek backend database credential kullanabilir. Bir modül ayrı
servise çıkarıldığında kendi database/schema kullanıcısını ve credential'ını
alır; başka servisin persistence detaylarını bilmez.

Modüller gelecekteki ihtimaller için boş olarak oluşturulmaz. Phase 8'de Kafka
incident tüketimi için gereken en küçük dilimle başlanır.

## Consequences

- Tek build ve deployment ile MVP'nin operasyonel maliyeti düşük kalır.
- Domain ve veri sahipliği kod içinde görünür olur.
- In-process çağrılar gerektiğinde basit ve transaction-aware kalabilir.
- Mikroservis altyapısı için Spring Cloud, service discovery veya circuit
  breaker eklenmez.
- Modül sınırları daha sonra API/event ve veri sahipliği sınırlarına
  dönüştürülebilir.
- Bağımsız ölçekleme, deployment, availability, security, veri veya ekip
  sahipliği kanıtlanırsa ilgili modül daha sonra ayrı servise çıkarılabilir; bu
  değişiklik yeni bir ADR gerektirir.
