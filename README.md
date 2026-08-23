# Industrial AI Security

[![CI](https://github.com/pltthakan/industrial-ai-security/actions/workflows/ci.yml/badge.svg)](https://github.com/pltthakan/industrial-ai-security/actions/workflows/ci.yml)

Fabrika kamera görüntülerinde kişileri algılayan, takip eden ve sanal bölge
ihlallerini gerçek zamanlı olaylara dönüştüren uçtan uca güvenlik platformu.

İlk MVP akışı:

```text
Factory CCTV MP4
  -> OpenCV
  -> YOLO person detection
  -> ByteTrack
  -> Virtual zone
  -> ZONE_INTRUSION
  -> Kafka
  -> Spring Boot
  -> PostgreSQL
  -> WebSocket
  -> React dashboard
```

## Proje durumu

Phase 1 tamamlandı: repository kuralları, mimari dokümanı ve proje durum
kaydı oluşturuldu. Sıradaki çalışma Phase 2'de yerel MP4 okuma pipeline'ıdır.
Güncel ve ayrıntılı durum için [`docs/project-state.md`](docs/project-state.md)
dosyasına bakın.

GitHub Actions, `main` push ve pull request'lerinde bileşen bazlı kontrolleri
çalıştırır. CI job'ları ve CD aktivasyon koşulları
[`docs/ci-cd.md`](docs/ci-cd.md) dosyasında açıklanmıştır.

## Klasörler

```text
cv-engine/       Python görüntü işleme worker'ı (Phase 2+)
backend/         Spring Boot uygulaması (Phase 8+)
frontend/        React dashboard (Phase 13+)
samples/         Yerel geliştirme video girdileri
docs/            Mimari, proje durumu ve karar kayıtları
```

## Sabit teknoloji sürümleri

- Python 3.12
- Java 21 ve Spring Boot 3.5.x
- Node.js 22, React 19 ve Vite 8
- PostgreSQL 17
- Redis 7.4
- Kafka (KRaft)

Geliştirme ortamındaki araçlar bu sürümlerle eşleşmelidir. Ayrıntılı kurallar
[`AGENTS.md`](AGENTS.md), mimari ise
[`docs/architecture.md`](docs/architecture.md) içindedir.

## Örnek video

Video dosyaları boyutları ve lisans koşulları nedeniyle Git'e eklenmez. Phase 2
çalıştırmasından önce test videosunu aşağıdaki konuma kopyalayın:

```text
samples/factory-floor.mp4
```
