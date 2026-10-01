# Ses Açma: Piyano Isınma — App Store'a satış rehberi

Şan öğrencileri, şarkıcılar ve koro üyeleri için piyano eşliğinde ses açma uygulaması. Türkçe + İngilizce, internetsiz çalışır, veri toplamaz.

## Klasörde neler var
```
src/index.html           Uygulamanın kaynağı (tek dosya: arayüz, piyano sesi, perde algılama, iki dil)
www/index.html           iPhone uygulamasına giren derlenmiş dosya (npm run build üretir)
assets/logo.svg          Logo (Altın Dalga), ikonun kaynağı
assets/icon-1024.png     App Store ikonu
assets/splash-2732.png   Açılış ekranı
appstore/listing.md      App Store Connect'e kopyalanacak tüm metinler (TR + EN)
appstore/privacy.html    Gizlilik politikası sayfası (TR + EN)
appstore/screenshots/    Hazır ekran görüntüleri: tr/ ve en/ (1320×2868, 6.9" iPhone)
scripts/                 Derleme, iOS ayarı, ikon, ekran görüntüsü ve metin kontrol betikleri
test/core.test.js        Testler (npm test)
```

---

## 1. Mac'te iPhone projesini oluşturun (bir kez)

Gerekenler: Xcode, Node.js (nodejs.org → LTS), Apple Developer hesabı.

1. Bundle ID hazır: `com.emccreationsstudio.sesacma` (`capacitor.config.json` ve `codemagic.yaml` içinde ayarlı). Sonradan değiştirilemez.
2. Terminal'de klasöre girin (`cd ` yazıp klasörü pencereye sürükleyin, Enter).
3. Sırayla:
   ```
   npm install
   npm run ios:add
   npm run ios:open
   ```
   `ios:add` şunları otomatik yapar: ikon, açılış ekranı, mikrofon izni metni, telefon sessizdeyken de ses çıkması, egzersiz sırasında ekranın kararmaması, Türkçe/İngilizce dil bilgisi, şifreleme beyanı ve yalnızca iPhone hedefi.
4. Xcode açılınca: sol üstte **App** → **Signing & Capabilities** → **Team** olarak geliştirici hesabınızı seçin.
5. iPhone'unuzu bağlayıp üstten seçin, ▶︎ ile çalıştırın.

**Telefonda kontrol edin:**
- Telefon sessiz moddayken piyano duyuluyor mu?
- Mikrofon açılınca izin soruyor mu, şarkı söyleyince gösterge hareket ediyor mu? (Kulaklıkla deneyin.)
- Telefon dili İngilizceyse uygulama İngilizce açılıyor mu?

Kodda değişiklik yaparsanız: `npm run ios:sync`

---

## 2. Gizlilik politikası bağlantısı

App Store Connect herkese açık bir gizlilik URL'si ve destek URL'si ister.
- Claude'da yayınlanan **Ses Açma Gizlilik Politikası** sayfasını **Paylaş (Share)** menüsünden herkese açık bağlantı yapın ve o bağlantıyı kullanın, **ya da**
- `appstore/privacy.html` dosyasını kendi sitenize / GitHub Pages'e koyun.

Destek URL'si sayfasında bir iletişim e-postası bulunmalıdır.

---

## 3. App Store Connect'te uygulamayı oluşturun

1. appstoreconnect.apple.com → **Uygulamalarım (My Apps)** → **+** → **Yeni Uygulama**
   - Platform: iOS · Ad: `Ses Açma: Piyano Isınma` · Birincil dil: Türkçe · Bundle ID: 1. adımda yazdığınız · SKU: `sesacma001`
2. **İş (Business)** bölümünde **Ücretli Uygulamalar Sözleşmesi**, banka ve vergi bilgilerini tamamlayın (yoksa ücretli uygulama yayınlanamaz).
3. **Uygulama Bilgileri**: kategori Müzik + Eğitim, gizlilik URL'si.
4. **Uygulama Gizliliği**: "Veri toplamıyoruz" seçin.
5. **Fiyatlandırma**: önerilen 2,99 USD seviyesi (sonra değiştirilebilir).
6. **iOS Uygulaması 1.0** sayfası:
   - Türkçe metinleri `appstore/listing.md` → Türkçe bölümünden kopyalayın, `appstore/screenshots/tr/` görsellerini yükleyin.
   - Sağ üstten **English (U.S.)** dilini ekleyip İngilizce metinleri ve `appstore/screenshots/en/` görsellerini yükleyin.
   - **Yaş derecelendirmesi**: tüm sorulara "Yok" → 4+
   - **İnceleme notu**: listing.md'deki İngilizce notu yapıştırın.

---

## 4. Yükleme ve incelemeye gönderme

1. Xcode'da üstten cihaz olarak **Any iOS Device (arm64)** seçin.
2. **Product > Archive** → açılan pencerede **Distribute App** → **App Store Connect** → **Upload**.
3. 10–30 dakika sonra yüklenen sürüm App Store Connect'te görünür. 1.0 sayfasında **Build** bölümünden seçin.
4. **İncelemeye Gönder (Submit for Review)**. İnceleme genelde 1–3 gün sürer.

İsterseniz önce **TestFlight** sekmesinden öğrencilerinize deneme sürümü gönderebilirsiniz.

---

## Notlar
- Ekran görüntüleri Linux'ta üretildiği için yazı tipi iPhone'dakinden biraz farklı. Birebir görünüm isterseniz Xcode Simülatöründe **iPhone 16 Pro Max** açıp ⌘S ile kendi görüntülerinizi alabilirsiniz.
- Uygulama içi destek e-postası göstermek için `src/index.html` içinde `SUPPORT_EMAIL` değerini doldurun.
- Testler: `npm test` · Metin uzunluğu kontrolü: `node scripts/check-listing.js` · İkonu yeniden çizmek: `npm run icon` · Ekran görüntülerini yeniden üretmek: `python3 scripts/screenshots.py`
