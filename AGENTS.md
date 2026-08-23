# Industrial AI Security — Repository Kuralları

Bu dosya, repository içindeki tüm değişiklikler için uzun süre geçerli olacak
mühendislik kurallarını içerir. Geçici görevler ve faza özel çalışma notları
buraya değil, `docs/project-state.md` dosyasına yazılır.

## Desteklenen teknoloji tabanı

- Computer vision: Python 3.12, `uv`, PyTorch, Ultralytics YOLO,
  `opencv-python-headless`, NumPy, Pydantic 2, `pydantic-settings` 2,
  `confluent-kafka`, pytest ve pytest-cov.
- Tracking: Ultralytics'in yerleşik ByteTrack entegrasyonu. Ayrı ByteTrack,
  DeepSORT veya supervision paketi kurulmaz.
- Backend: Java 21 LTS, Spring Boot 3.5.x, Maven Wrapper, Spring Web,
  Validation, Data JPA, Kafka, Data Redis, WebSocket ve Actuator.
- Veri ve mesajlaşma: PostgreSQL 17, Redis 7.4, KRaft modunda Apache Kafka ve
  Flyway migration'ları.
- Frontend: Node.js 22 LTS, React 19, TypeScript, Vite 8, Axios ve native browser
  WebSocket API.
- Altyapı: Docker ve Docker Compose v2.
- Video girdisi: Önce local MP4; local pipeline çalıştıktan sonra FFmpeg ve
  MediaMTX üzerinden RTSP.

Kullanıcı açıkça istemedikçe major sürüm değiştirilmez ve framework
değiştirilmez.

## Sistem mimarisi sınırları

Aşağıdaki olay akışı korunur:

```text
MP4 / RTSP -> CV Engine -> Kafka -> Spring Boot Backend
                                      |       |       |
                                      v       v       v
                                PostgreSQL  Redis  WebSocket -> React
```

- CV engine incident event'lerini Kafka'ya yayınlar; PostgreSQL veya Redis'e
  doğrudan bağlanmaz.
- Frontend yalnızca Spring Boot backend ile iletişim kurar; database'e doğrudan
  bağlanmaz ve CV engine'e business API çağrısı yapmaz.
- Kafka mesajında metadata ve snapshot referansı bulunur; büyük image binary
  taşınmaz.
- Spring Boot uygulamanın HTTP backend'idir. Kullanıcı açıkça bir CV yönetim API
  istemedikçe FastAPI eklenmez.
- Kullanıcı açıkça istemedikçe TRASSIR entegrasyonu eklenmez.
- İlk incident stream'i için `security.incidents` topic'i kullanılır.

## Arka uç modülerliği

- Backend, tek deploy edilen Spring Boot uygulaması içinde modüler monolith
  olarak geliştirilir. Her domain için varsayılan olarak ayrı Spring Boot
  servisi oluşturulmaz.
- Kod package-by-feature düzenlenir. İlk domain adayları `incident`, `camera` ve
  `zone` modülleridir; bir modül yalnızca aktif fazda gerçek use case varsa
  oluşturulur. Notification veya analytics gibi boş gelecek modülleri açılmaz.
- Bir modül kendi domain modelinin, application service'lerinin,
  repository/adapters'ının, tablolarının ve Flyway migration'larının sahibidir.
  Internal tipleri public API değildir.
- Bir modül başka bir modülün repository'sini inject etmez, JPA entity'sine
  bağımlı olmaz ve tablosuna doğrudan SQL çalıştırmaz.
- Modüller arası ilişkiler `cameraId` ve `zoneId` gibi kararlı kimliklerle
  tutulur; modüller arası JPA entity ilişkisi kurulmaz.
- Modüller arası senkron çağrılar, sağlayan modülün sahip olduğu dar bir public
  application interface üzerinden yapılır.
- Gerçekten asenkron veya birden fazla tüketicili davranışlarda internal
  domain/application event kullanılabilir. Her in-process metot çağrısı event'e
  dönüştürülmez.
- `shared` yalnızca domain sahibi olmayan teknik primitive'leri içerir; business
  logic'in toplandığı bir klasöre dönüştürülmez.
- Bir modül ancak bağımsız ölçekleme, deployment, availability, security, veri
  sahipliği veya ekip sahipliği ihtiyacı ölçülerek kanıtlanırsa mikroservise
  çıkarılır. Bu değişiklik yeni bir ADR gerektirir.

## Modül sorumlulukları

Tek sorumluluk, bir modülün yalnızca tek metodu olması değil, tek ve tutarlı bir
business capability'nin sahibi olmasıdır.

- `incident`: Incident kabulü, duplicate/idempotency kontrolü, lifecycle,
  persistence ve sorgulama davranışlarının sahibidir.
- `camera`: Kamera tanımı, durumu ve heartbeat davranışlarının sahibidir.
- `zone`: Sanal bölge tanımı ve polygon configuration davranışlarının sahibidir.
- Notification, analytics ve archive modülleri ancak ilgili use case geldiğinde
  oluşturulur.
- `security.incidents` consumer'ı ayrı ve anlamsız bir `event` domain modülü
  değildir; `incident.infrastructure.messaging` altında yer alır.
- JPA repository implementasyonları ilgili modülün infrastructure katmanında
  bulunur. Controller ve dış sistem adapter'ları da sahip olan modülde kalır.

Bir modül kendi capability'si içindeki birden fazla ilişkili use case'i
yürütebilir. Sorumluluk sınırı teknik işlem sayısına göre değil, değişim nedeni
ve domain sahipliğine göre belirlenir.

## Senkron ve asenkron iletişim politikası

Sistem hibrit iletişim modeli kullanır. Her iletişim zorla asenkron veya zorla
senkron yapılmaz.

Asenkron olması gereken ana akışlar:

- CV Engine -> Kafka -> Spring Boot Backend incident akışı.
- Backend -> React gerçek zamanlı WebSocket bildirimleri.
- İleride e-posta, SMS ve notification gibi ana işlemi bekletmemesi gereken yan
  etkiler.
- İleride analytics, arşivleme ve ağır raporlama işleri.

Senkron olması gereken ana akışlar:

- React -> Backend REST istekleri ve hemen cevap gerektiren doğrulamalar.
- Kamera ve bölge CRUD işlemleri.
- Backend modülleri arasındaki basit bilgi sorguları ve command çağrıları.
- İlk mimaride Spring Data JPA/PostgreSQL ve Spring Data Redis işlemleri.

Uygulama kuralları:

- In-process modül iletişiminde varsayılan, dar application interface üzerinden
  senkron çağrıdır. Event ancak zaman ayrıştırması, birden fazla tüketici veya
  bağımsız hata/ölçekleme davranışı gerektiğinde seçilir.
- WebSocket bildirimi source of truth değildir; kalıcı incident kaydı
  PostgreSQL'dir.
- Kafka consumer duplicate teslimata dayanıklı ve `event_id` üzerinden
  idempotent olmalıdır. `event_id` database seviyesinde unique olmalıdır.
- Kafka mesajı, gerekli database transaction başarıyla tamamlanmadan işlenmiş
  sayılmaz. WebSocket ve benzeri yan etkiler kalıcı kayıt başarılı olduktan
  sonra çalıştırılır.
- API ve event contract'ları versionlanabilir, typed ve implementation
  detaylarından bağımsız tutulur.

## Veri ve kimlik bilgisi sahipliği

- Modüler monolith aşamasında tek backend process, tek PostgreSQL instance ve
  tek backend database credential kullanabilir. Aynı process içindeki her modül
  için yapay biçimde ayrı credential oluşturulmaz.
- Tek credential kullanılsa bile tablo, repository ve migration sahipliği modül
  sınırlarını izler. Bir modül başka modülün verisini doğrudan sorgulamaz.
- Bir modül gelecekte mikroservise çıkarılırsa kendi database veya schema'sına,
  database kullanıcısına ve credential'ına sahip olur.
- Bir servis başka servisin database şifresini, tablo/kolon isimlerini,
  repository implementasyonunu veya persistence detaylarını bilmez.
- Servisler birbirlerinin verisine API contract veya event contract üzerinden
  erişir. Sağlayan servisin PostgreSQL, Redis ya da başka bir storage kullanması
  tüketenin bilgisi değildir.
- Secret ve credential'lar repository dosyalarına yazılmaz; environment secret,
  secret manager veya desteklenen yerde OIDC tabanlı kısa ömürlü kimlik bilgisi
  kullanılır.

## Pragmatik SOLID kuralları

SOLID ilkeleri değişiklik etkisini ve coupling'i azaltmak için uygulanır; daha
fazla sınıf, interface veya design pattern üretmek için kullanılmaz.

- SRP: Bir modül tek business capability'nin, bir sınıf ise tek tutarlı değişim
  nedeninin sahibi olmalıdır. Controller, orchestration, domain rule ve
  persistence sorumlulukları tek sınıfta biriktirilmez.
- DIP: Domain/application business kuralları Kafka, JPA, Redis, WebSocket veya
  dosya sistemi implementasyonlarını doğrudan çağırmaz. Gerekli dış sınırlar
  application tarafından tanımlanan dar port/interface'lerle temsil edilir ve
  infrastructure adapter'ları bunları uygular.
- ISP: Modüller ve adapter'lar tüketenin ihtiyacından büyük interface'lere
  zorlanmaz. Public module API'leri küçük ve use case odaklı tutulur.
- OCP ve LSP gerçek polymorphism veya değişen strateji ihtiyacı olduğunda
  korunur; gelecekte gerekebilir düşüncesiyle gereksiz inheritance hierarchy
  kurulmaz.
- Her sınıf için interface oluşturulmaz. Tek implementasyonu olan ve gerçek bir
  mimari sınır temsil etmeyen kod için soyutlama zorunlu değildir.
- Gereksiz factory, manager, util, facade ve generic base class oluşturulmaz.
  Önce en küçük açık çözüm uygulanır, tekrar veya değişim ihtiyacı kanıtlanınca
  refactor edilir.

## Bağımlılık ve derleme kuralları

- Python dependency'leri `pyproject.toml` içinde tanımlanır ve `uv.lock` içinde
  kilitlenir. Somut ihtiyaç olmadan lockfile silinmez veya yeniden üretilmez.
- Java dependency'leri Spring Boot dependency management kullanır. Spring
  Framework, Spring Kafka, Spring Data, Hibernate veya Jackson artifact'lerine
  manuel sürüm verilmez. `pom.xml`, `mvnw` ve `mvnw.cmd` repository'de tutulur.
- Frontend dependency'leri `package.json` ve `package-lock.json` kullanır.
- Yeni dependency eklemeden önce mevcut stack'in aynı ihtiyacı karşılayıp
  karşılamadığı kontrol edilir. Güncel ihtiyaç olmadan framework veya abstraction
  eklenmez.
- İlk mimariye FastAPI, TensorFlow, Keras, Detectron2, DeepSORT, supervision,
  Celery, ZooKeeper veya Kubernetes eklenmez.
- Sadece mikroservis görünümü oluşturmak için Spring Cloud, service discovery,
  circuit breaker veya distributed tracing eklenmez.
- ONNX Runtime, TensorRT, Prometheus, Grafana, MinIO, Spring Security ve JWT;
  temel sistem çalışıp kullanıcı ilgili fazı isteyene kadar ertelenir.

## Artımlı geliştirme

1. Her görevden önce repository ve `docs/project-state.md` incelenir.
2. Yalnızca kullanıcının istediği faz üzerinde çalışılır; sonraki fazlar fırsatçı
   biçimde uygulanmaz.
3. Çalışan kod korunur ve ilgisiz yeniden yazımlar yapılmaz.
4. İlgili fazın test veya build komutları çalıştırılır. Başarısız test/build ile
   faz tamamlanmış sayılmaz.
5. Her tamamlanan faz sonunda `docs/project-state.md` güncellenir.
6. Yalnızca önemli mimari kararlar `docs/decisions/` altında ADR olarak tutulur.

Planlanan faz sırası:

1. Repository ve proje dokümantasyonu
2. Local MP4 işleme
3. YOLO person detection
4. ByteTrack object tracking
5. Virtual zone detection
6. `ZONE_INTRUSION` event engine
7. Kafka producer
8. Spring Boot backend ve Kafka consumer
9. PostgreSQL ve Flyway
10. Incident REST API
11. Redis
12. WebSocket
13. React dashboard
14. RTSP, FFmpeg ve MediaMTX
15. PPE detection
16. Production hardening
17. ONNX ve performance optimization

## Test kuralları

- Python: pytest ve pytest-cov.
- Java: JUnit 5, Mockito ve Testcontainers.
- `.github/workflows/ci.yml` build edilebilen her bileşenle uyumlu tutulur. CI,
  pull request'lerde ve `main` branch push'larında çalışır.
- Workflow permission'ları en az yetkiyle sınırlandırılır ve third-party Actions
  tam commit SHA'sına sabitlenir.
- Deployment credential'ları repository dosyalarına yazılmaz. Production
  delivery, korumalı GitHub Environment ve açık bir deployment hedefi gerektirir.
- Point-in-polygon, zone intrusion, cooldown, incident generation,
  configuration validation, duplicate incident handling, Kafka consumption,
  persistence ve REST davranışı gibi gerçek business logic test edilir.
- Yalnızca coverage yükseltmek amacıyla anlamsız test yazılmaz.
- Modül sınırları için architecture test'leri eklenir: başka modülün repository,
  internal package veya JPA entity'sine yasak bağımlılık CI'da başarısız olmalıdır.
  Bunun için yeni dependency ancak Phase 8'de mevcut araçlar yetersizse eklenir.

## İsimlendirme ve veri sözleşmeleri

- Kod, identifier, configuration key, event field ve commit mesajları İngilizce
  yazılır.
- Dokümantasyon Türkçe veya İngilizce olabilir; tek dosyada dil tutarlı tutulur.
- CV tarafı configuration ve event'leri typed Pydantic modelleriyle temsil edilir.
- Timestamp'ler timezone-aware olur ve event timestamp'leri ISO 8601 UTC olarak
  serialize edilir.
- Her incident event'inde camera ID, zone ID, track ID ve incident type açıkça
  bulunur.
