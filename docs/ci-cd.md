# CI/CD

## Mevcut durum

GitHub Actions CI aktiftir. `.github/workflows/ci.yml` aşağıdaki olaylarda
çalışır:

- `main` branch'ine push
- `main` branch'ini hedefleyen pull request
- GitHub Actions ekranından manuel çalıştırma (`workflow_dispatch`)

Workflow aynı branch için eski çalışmayı iptal eder ve yalnızca repository
içeriğini okuma izni alır. Harici Actions bağımlılıkları değiştirilebilir tag
yerine doğrulanmış tam commit SHA'larına sabitlenmiştir.

## CI kontrolleri

| Job | Bugünkü davranış | Aktivasyon koşulu |
| --- | --- | --- |
| Repository validation | Zorunlu dosyaları ve Git'e eklenmiş sample videoları denetler | Her zaman |
| CV engine checks | Python 3.12, locked `uv` sync ve pytest/coverage | `pyproject.toml` + `uv.lock` |
| Backend checks | Java 21 ve Maven Wrapper `verify` | `pom.xml` + Maven Wrapper |
| Frontend checks | Node.js 22, `npm ci`, lint/test/build | `package.json` + `package-lock.json` |
| Docker Compose validation | `docker compose config --quiet` | Compose dosyası |

Bir bileşen henüz oluşturulmadıysa job başarılı bir notice üretir ve gereksiz
runtime/dependency kurulumu yapmaz. Manifestlerden yalnızca biri eklenirse CI
başarısız olur; böylece lockfile ve wrapper kuralları korunur.

## CD sınırı

Gerçek deployment şu anda bilinçli olarak etkin değildir. Repository'de henüz
deploy edilebilir uygulama, Dockerfile, image registry politikası veya hedef
environment bulunmuyor. Bu durumda bir “deploy” workflow'u eklemek çalışan CD
değil, test edilemeyen bir şablon olurdu.

CD aşağıdaki ön koşullar sağlandığında etkinleştirilecektir:

1. Servis Dockerfile'ları ve Docker Compose build'i çalışır durumda olmalı.
2. CI'ın tüm zorunlu job'ları başarılı olmalı.
3. Image registry seçilmeli; varsayılan aday GitHub Container Registry'dir.
4. `staging` ve gerekiyorsa `production` GitHub Environment'ları oluşturulmalı.
5. Production environment için required reviewer koruması tanımlanmalı.
6. Deployment hedefi ve rollback/health-check komutları belirlenmeli.

Planlanan delivery akışı:

```text
Pull request -> CI -> merge to main -> version tag
                                      |
                                      v
                              Build container images
                                      |
                                      v
                              Push immutable tags to GHCR
                                      |
                                      v
                              Deploy to staging
                                      |
                              protected approval
                                      |
                                      v
                              Deploy to production
```

Deployment credential'ları repository dosyalarına yazılmayacak; GitHub
Environment secret'ları veya tercihen OIDC tabanlı kısa ömürlü kimlik bilgileri
kullanılacaktır.

## GitHub ayarları

İlk başarılı workflow çalışmasından sonra `main` branch protection/ruleset
içinde aşağıdaki check'lerin merge öncesi zorunlu yapılması önerilir:

- `Repository validation`
- `CV engine checks`
- `Backend checks`
- `Frontend checks`
- `Docker Compose validation`

