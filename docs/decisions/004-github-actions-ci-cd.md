# ADR 004: CI/CD platformu olarak GitHub Actions

- Status: Accepted
- Date: 2026-08-23

## Context

Repository GitHub üzerinde barındırılıyor ve Python, Java, React ile Docker
Compose bileşenleri farklı fazlarda eklenecek. Her commit için tekrar üretilebilir
kontroller ve ileride kontrollü bir container delivery akışı gerekiyor.

## Decision

CI/CD otomasyonu GitHub Actions ile yürütülür. CI, `main` push ve pull
request'lerinde bileşen test/build kontrollerini ayrı job'lar olarak çalıştırır.
Workflow token'ı en az yetkiyle sınırlandırılır ve Actions referansları tam commit
SHA'sına sabitlenir.

CD, deploy edilebilir container'lar ve hedef environment hazır olduğunda version
tag'leri üzerinden etkinleştirilir. Production dağıtımı korumalı GitHub
Environment onayı olmadan yapılmaz.

## Consequences

- Commit ve pull request ekranlarında her bileşenin sonucu ayrı görünür.
- Manifest/lockfile eklendikçe ilgili job gerçek testi otomatik çalıştırır.
- Şimdilik test edilemeyen veya credential gerektiren sahte deployment adımı
  tutulmaz.
- Container ve environment kararları geldiğinde delivery workflow'u ayrıca
  doğrulanmalıdır.

