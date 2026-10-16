# Ses Açma - Piano Warm Up — Kurulum ve yayın rehberi

Tek kod, dört yer: **iPhone (App Store)**, **Mac**, **Windows** ve **Android (Google Play)**.
Uygulama 10 dilde: Türkçe, İngilizce, Almanca, Fransızca, İspanyolca, İtalyanca, Portekizce, Rusça, Japonca, Çince. Telefonun dili neyse o dilde açılır; Ayarlar > Dil'den değiştirilebilir.

| Platform | Ne üretilir | Nerede derlenir | Nasıl başlatılır |
|---|---|---|---|
| iPhone | App Store / TestFlight | Codemagic | **Ses Açma — App Store** → Start new build |
| Android | Google Play paketi (.aab) | Codemagic | **Ses Açma — Google Play** → Start new build |
| Windows | Kurulum sihirbazı `SesAcma-PianoWarmUp-Setup-1.1.0.exe` | GitHub Actions | Actions → **Masaüstü kurulum dosyaları** → Run workflow |
| Mac | `SesAcma-PianoWarmUp-1.1.0.dmg` (Intel + Apple Silicon) | GitHub Actions | Aynı iş, aynı anda |

Mağaza metinleri (ad, alt başlık, açıklama, anahtar kelimeler, yenilikler) 10 dilde hazır: [`appstore/listings/README.md`](appstore/listings/README.md).
Google Play görselleri: `appstore/googleplay/icon-512.png` ve `feature-graphic-1024x500.png`.

---

## 1. iPhone (App Store) — zaten kurulu
Codemagic'te **ses-acma → Start new build → branch `surum-1.1` → Ses Açma — App Store**.
App Store Connect'te 1.1 sürümünün sayfasında **Ad**'ı `Ses Açma - Piano Warm Up` yap ve diğer dilleri (sağ üstteki dil menüsünden **+**) ekleyip metinleri `appstore/listings/README.md`'den yapıştır.

**Mac için en kolay yol:** App Store Connect → uygulama → **Fiyatlandırma ve Kullanılabilirlik** → *iPhone and iPad Apps on Apple Silicon Macs* kutusunu açık bırak. Böylece iPhone uygulaması M1/M2/M3 Mac'lerde Mac App Store'dan da indirilebilir; ayrıca bir şey yapman gerekmez.

---

## 2. Google Play (Android)

### 2a. Bir kerelik hazırlık
1. **Google Play geliştirici hesabı:** play.google.com/console → kayıt (tek seferlik 25 USD). Bireysel hesap seç.
   Yeni bireysel hesaplarda Google, yayından önce **en az 12 test kullanıcısıyla 14 gün kapalı test** ister — ilk yüklemeyi *Kapalı test* kanalına yap.
2. **Uygulama oluştur:** Play Console → *Uygulama oluştur* → ad `Ses Açma - Piano Warm Up`, varsayılan dil Türkçe, *Uygulama*, *Ücretli* (ya da Ücretsiz).
   Paket adı ilk yüklemede `com.emccreationsstudio.sesacma` olarak sabitlenir.
3. **Yükleme anahtarı (keystore):** sana gönderdiğim `SesAcma-upload.jks` ve `BILGI.txt`.
   Codemagic → **Team settings → Code signing identities → Android keystores → Add keystore**:
   dosyayı seç, `BILGI.txt`'deki şifreleri gir, **Reference name: `sesacma_upload`** → Save.
   Bu iki dosyayı güvenli bir yerde sakla; GitHub'a koyma.

### 2b. Derle
Codemagic → ses-acma → **Start new build** → branch `surum-1.1` → workflow **Ses Açma — Google Play** → Start.
Bitince derleme sayfasının **Artifacts** kısmından `app-release.aab` dosyasını indir.

### 2c. Play Console'a yükle
1. *Test et ve yayınla → Kapalı test → Yeni sürüm oluştur* → **Play App Signing**'i kabul et → `.aab`'yi sürükle.
2. *Mağaza girişi*: metinler `appstore/listings/README.md` (Google Play sütunu: Uygulama adı, **Kısa açıklama (80)**, Tam açıklama). 10 dili *Çeviri ekle*'den ekle.
3. Görseller: ikon `icon-512.png`, öne çıkan görsel `feature-graphic-1024x500.png`, en az 2 telefon ekran görüntüsü (`appstore/screenshots/` içindekiler kullanılabilir).
4. *Uygulama içeriği*: Gizlilik politikası URL'si (`privacy.html`'in yayın adresi), Veri güvenliği → **Veri toplanmıyor**, Reklam yok, Hedef kitle 13+ (ya da tüm yaşlar), İçerik derecelendirme anketi.

İlk yüklemeden sonra her şeyi otomatik yapmak istersen `codemagic.yaml`'daki `publishing: google_play` kısmının açıklamasını oku.

---

## 3. Windows — kurulum sihirbazı (Setup.exe)

1. github.com/emccreationsstudio/ses-acma → **Actions** sekmesi → soldan **Masaüstü kurulum dosyaları** → **Run workflow** → branch `surum-1.1` → Run.
2. ~10 dakika sonra işin sayfasının altında **Artifacts** → `SesAcma-win` (zip) → içinde `SesAcma-PianoWarmUp-Setup-1.1.0.exe`.
3. Çift tıkla: dil seçimi (10 dil) → kurulum klasörü → masaüstü ve Başlat menüsü kısayolu → bitir, uygulama açılır.

**"Windows kişisel bilgisayarınızı korudu" uyarısı:** Kurulum dosyası henüz kod imzalı olmadığı için çıkar. **Ek bilgi → Yine de çalıştır**. Uyarının hiç çıkmaması için ileride bir kod imzalama sertifikası alınabilir ya da uygulama Microsoft Store'a konabilir.

Kaldırmak: Ayarlar → Uygulamalar → *Ses Açma - Piano Warm Up* → Kaldır.

---

## 4. Mac — .dmg

Aynı GitHub işi Mac dosyasını da üretir: **Artifacts** → `SesAcma-mac` → `SesAcma-PianoWarmUp-1.1.0.dmg`.
Aç → uygulamayı **Applications** klasörüne sürükle.

**İmzasız sürüm (şu an):** İlk açılışta "doğrulanamadı" der. **Sistem Ayarları → Gizlilik ve Güvenlik → yine de aç** (ya da uygulamaya sağ tık → Aç). Mikrofon izni sorulduğunda **İzin Ver**.

**İmzalı ve uyarısız sürüm (isteğe bağlı):** Apple Developer hesabınla:
1. developer.apple.com → Certificates → **+** → *Developer ID Application* → sertifikayı oluştur, Mac'te Anahtar Zinciri'nden `.p12` olarak dışa aktar (şifre ver).
2. appleid.apple.com → *Uygulamaya özel parola* oluştur.
3. GitHub → repo → **Settings → Secrets and variables → Actions → New repository secret**:
   - `MAC_CERT_P12_BASE64` → `.p12` dosyasının base64 hâli (Terminal: `base64 -i sertifika.p12 | pbcopy`)
   - `MAC_CERT_PASSWORD` → `.p12` şifresi
   - `APPLE_ID` → Apple ID e-postan
   - `APPLE_APP_SPECIFIC_PASSWORD` → 2. adımdaki parola
   - `APPLE_TEAM_ID` → developer.apple.com → Membership'teki Team ID
4. İşi tekrar çalıştır: .dmg imzalanır ve Apple'a onaylatılır (notarize), uyarı çıkmaz.

---

## Dil paketi
- Arayüz metinleri: `src/index.html` içinde (`LANG_PACK`). Kaynak dosyalar `i18n/<dil>.js`; yapı kontrolü `node i18n/validate.js de`.
- Testler 10 dilin hepsinde her metnin var olduğunu ve aynı yapıda olduğunu kontrol eder: `npm test`.
- Not adları her dilde o ülkenin alışkanlığıyla: Do Re Mi (tr, fr, es, it, pt, ru, ja), C D E (en, zh), C D E … H (de).
