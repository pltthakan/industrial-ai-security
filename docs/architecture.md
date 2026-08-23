# Sistem Mimarisi

## Amaç ve kapsam

Sistem, bir fabrika CCTV kaynağındaki kişileri algılar ve izler, tanımlı sanal
bölge kurallarını uygular, ihlalleri olay olarak saklar ve dashboard'a gerçek
zamanlı olarak iletir. İlk MVP yalnızca `person` sınıfı ve `ZONE_INTRUSION`
olayını kapsar. PPE sınıfları daha sonraki bir fazdadır.

## Uçtan uca veri akışı

```text
Local MP4 (later RTSP)
          |
          v
Python CV Engine
OpenCV -> YOLO -> ByteTrack -> Zone Rules
          |
          | IncidentEvent JSON
          v
Kafka: security.incidents
          |
          v
Spring Boot Backend
   |          |           |
   v          v           v
PostgreSQL  Redis      WebSocket
                            |
                            v
                      React Dashboard
```

## Computer vision engine

Python worker'ı OpenCV ile MP4/RTSP frame'lerini okur. Ultralytics YOLO ilk MVP'de
yalnızca `person` algılar. Ultralytics'in yerleşik ByteTrack entegrasyonu, kareler
arasında kalıcı `track_id` üretir. Bölge motoru, kişinin bounding box alt-orta
noktasını polygon'a karşı değerlendirir.

Bir ihlal oluştuğunda CV engine typed bir `IncidentEvent` üretip
`security.incidents` Kafka topic'ine yollar. CV engine PostgreSQL veya Redis'e
bağlanmaz. Snapshot gerekiyorsa Kafka mesajına binary eklenmez; yalnızca ayrı
saklanan dosyanın referansı taşınır.

Planlanan olayın asgari semantiği:

```json
{
  "event_id": "uuid",
  "incident_type": "ZONE_INTRUSION",
  "occurred_at": "ISO-8601 UTC timestamp",
  "camera_id": "CAM-001",
  "zone_id": "ZONE-001",
  "track_id": 42,
  "confidence": 0.91,
  "snapshot_ref": null
}
```

Kesin şema Phase 6'da testlerle birlikte tanımlanacaktır.

## Backend

Spring Boot, Kafka olaylarının tek tüketicisidir. Olayı doğrular, yinelenen
olayları ele alır, PostgreSQL'e kaydeder, Redis'te cooldown/aktif alarm durumunu
yönetir ve REST/WebSocket yüzeylerini sunar.

Backend tek Spring Boot uygulaması ve tek deploy edilebilir container olarak
geliştirilen bir **modüler monolith** olacaktır. Bu karar tüm sistemin monolith
olduğu anlamına gelmez: Python CV engine ayrı bir process'tir ve Kafka iki
çalışma zamanı arasındaki event-driven entegrasyon sınırıdır.

Hedef package-by-feature yapısı, modüller gerçekten ihtiyaç olduğunda şu biçimde
oluşturulur:

```text
backend/src/main/java/.../
├── incident/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── camera/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── zone/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
└── shared/
```

Bu ağaç bir başlangıçta boş klasör üretme talimatı değildir. Phase 8'de önce
Kafka incident tüketimi için gereken en küçük `incident` yüzeyi oluşturulur;
`camera`, `zone`, `notification` veya başka bir modül yalnızca aktif use case
gerektirdiğinde eklenir.

### Modül sınırları

- Her modül kendi domain modelinin, application service'lerinin,
  repository/adapters'ının ve tablolarının sahibidir.
- Başka bir modülün repository'si veya JPA entity'si doğrudan kullanılmaz.
- Modüller arası referanslar `cameraId` ve `zoneId` gibi kararlı kimliklerle
  tutulur; modüller arası JPA entity ilişkisi kurulmaz.
- Senkron bilgi gerektiğinde sağlayan modülün dar application interface'i
  çağrılır. Gerçekten asenkron veya birden fazla tüketicili davranış varsa
  internal event kullanılabilir; her metot çağrısı event'e çevrilmez.
- `shared` yalnızca teknik ve sahipsiz primitive'leri içerir; business logic
  burada biriktirilmez.
- Modülleri aşan SQL ve repository erişimi kullanılmaz. Zorunlu bir istisna ADR
  ile gerekçelendirilir.

Kafka incident consumer'ı ayrı bir `event` domain modülü değildir;
`incident.infrastructure.messaging` altında bulunur. JPA repository
implementasyonları ve REST/WebSocket adapter'ları da sahip olan modülün
infrastructure katmanında kalır.

### Sorumluluk ve SOLID yaklaşımı

Modül sorumluluğu teknik işlem sayısına göre değil, business capability ve
değişim nedenine göre belirlenir. `incident` modülü incident kabulü,
duplicate/idempotency kontrolü, lifecycle, persistence ve sorgulamadan;
`camera` kamera tanımı, durum ve heartbeat'ten; `zone` sanal bölge ve polygon
configuration'dan sorumludur.

SOLID pragmatik uygulanır. Domain/application kuralları Kafka, JPA, Redis veya
WebSocket implementasyonlarına doğrudan bağlanmaz; gerçek mimari sınırlar dar
port/interface'lerle temsil edilir. Her sınıf için interface, gelecekte lazım
olabilir düşüncesiyle abstraction veya gereksiz design pattern oluşturulmaz.

### Senkron ve asenkron iletişim

Sistem hibrit iletişim modeli kullanır:

```text
CV Engine -> Kafka -> Backend                 asenkron
Backend -> React WebSocket                    asenkron
Gelecekte notification/analytics/archive     asenkron

React -> Backend REST                         senkron
Camera/Zone CRUD                              senkron
Backend module application interface calls   senkron
PostgreSQL ve Redis işlemleri                 senkron
```

In-process modül çağrılarında varsayılan senkron application interface'tir.
Internal event yalnızca zaman ayrıştırması, birden fazla tüketici veya bağımsız
hata/ölçekleme davranışı gerektiğinde kullanılır.

Kafka teslimatı tekrar edebileceği için incident consumer `event_id` üzerinden
idempotent çalışır ve `event_id` database seviyesinde unique tutulur. Kafka
mesajı kalıcı database transaction başarıyla tamamlanmadan işlenmiş sayılmaz.
WebSocket bildirimi source of truth değildir ve başarılı kalıcı kayıttan sonra
gönderilir.

### Database ve credential sahipliği

Modüler monolith aşamasında tek backend process'in tek PostgreSQL bağlantısı ve
tek database credential kullanması normaldir. Buna rağmen tablo, repository ve
Flyway migration sahipliği modül sınırlarını takip eder.

Bir modül ileride mikroservise çıkarılırsa kendi database/schema kullanıcısına
ve credential'ına sahip olur. Başka servisin şifresini, tablo/kolon isimlerini
ve repository implementasyonunu bilmez; yalnızca API veya event contract'ını
bilir. Credential'lar repository'ye yazılmaz.

İlk aşamada tek PostgreSQL instance ve tek Spring transaction runtime'ı vardır.
Tablo/migration sahipliği yine de modül sınırlarını izler. Böylece bağımsız
ölçekleme, deployment, availability, security, veri veya ekip sahipliği gibi
ölçülmüş bir ihtiyaç doğarsa uygun modül daha sonra servis olarak çıkarılabilir.

PostgreSQL şeması yalnızca Flyway migration'larıyla değiştirilir; Hibernate
şemayı `validate` eder. Redis kalıcı kayıt sistemi değildir.

## Frontend

React dashboard geçmiş olayları Axios üzerinden REST API'den, yeni olayları ise
native WebSocket üzerinden alır. Frontend hiçbir veri deposuna veya CV worker'a
doğrudan bağlanmaz.

## Video kaynakları

İlk kaynak sabit bir yerel MP4 dosyasıdır. Phase 2'de OpenCV tabanlı local video
reader; kaynak açma, metadata validation, frame iteration, deterministik resource
release ve end-of-stream detection ile tamamlanmıştır. RTSP bu pipeline'dan ayrı
bir video işleme yolu oluşturmayacak, ileride aynı kaynak sınırını kullanacaktır.

Local pipeline tamamlanmadan RTSP eklenmez. Phase 14'te FFmpeg ile test videosu
MediaMTX'e yayınlanarak fiziksel kamera olmadan RTSP davranışı simüle edilir.

## Dağıtım sınırları

Hedef Docker Compose ortamı `cv-engine`, `backend`, `frontend`, `postgres`,
`redis`, `kafka` ve ilerleyen fazda `mediamtx` servislerinden oluşur. Servisler
yalnızca ilgili faz geldiğinde eklenir.
