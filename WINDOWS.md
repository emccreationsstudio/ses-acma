# Windows'tan App Store'a: GitHub + Codemagic

Mac gerekmez. Uygulama Codemagic'in bulut Mac'lerinde derlenir ve doğrudan App Store Connect'e yüklenir.

## 0. Bundle ID
`com.emccreationsstudio.sesacma` — `capacitor.config.json` ve `codemagic.yaml` içinde zaten ayarlı.

## 1. Projeyi GitHub'a yükleyin
1. github.com'da ücretsiz hesap açın → sağ üstte **+** → **New repository**
2. Ad: `ses-acma` · **Private** seçin · **Create repository**
3. Açılan sayfada **uploading an existing file** bağlantısına tıklayın.
4. Zip'ten çıkan `sesacma-web` klasörünü açın, **içindeki her şeyi** seçip tarayıcıya sürükleyin (klasörün kendisini değil, içini).
   `codemagic.yaml` ve `package.json` deponun en üst seviyesinde olmalı.
5. Alttaki **Commit changes** düğmesine basın.

## 2. Apple tarafı (tarayıcıdan)
1. **Bundle ID kaydı:** developer.apple.com/account → Certificates, IDs & Profiles → **Identifiers** → **+** → App IDs → App → Description: `Ses Acma`, Bundle ID: *Explicit* → `com.emccreationsstudio.sesacma` → Continue → Register.
2. **Uygulama kaydı:** appstoreconnect.apple.com → Uygulamalarım → **+** → Yeni Uygulama → iOS, ad `Ses Açma: Piyano Isınma`, dil Türkçe, Bundle ID'yi listeden seçin, SKU `sesacma001`.
3. **API anahtarı:** App Store Connect → **Kullanıcılar ve Erişim** → **Entegrasyonlar** → **App Store Connect API** → **Team Keys** → **+** → ad `Codemagic`, erişim **App Manager** → Oluştur.
   Sayfadaki **Issuer ID** ve anahtarın **Key ID** değerlerini not edin, **.p8 dosyasını indirin** (yalnızca bir kez indirilebilir).

## 3. Codemagic
1. **Kodunuzu bağlayın** ekranında **GitHub**'ı seçin → **Codemagic'i yetkilendir** → `ses-acma` deposunu seçin.
2. Sol menüden **Team settings → Team integrations → Developer Portal → Connect**:
   - API key name: `SesAcma` (codemagic.yaml'daki adla aynı)
   - Issuer ID, Key ID ve .p8 dosyasını girin → Save.
3. **Team settings → Code signing identities**:
   - **iOS certificates** sekmesi → **Generate certificate** → tür *Apple Distribution*, anahtar `SesAcma` → oluşturun (çıkan şifreyi bir yere kaydedin).
   - **iOS provisioning profiles** sekmesi → **Fetch profiles** → Bundle ID'nizin *App Store* profilini seçip ekleyin. Profil yoksa önce developer.apple.com'da Profiles → **+** → *App Store Connect* → Bundle ID → sertifika ile oluşturup tekrar **Fetch** edin.
4. Uygulama sayfasında **Start new build** → workflow: **Ses Açma — App Store** → Start.
   ~15–25 dakikada derlenir, testler çalışır, App Store Connect'e yüklenir.

## 4. Test ve yayın
1. iPhone'a **TestFlight** uygulamasını kurun; App Store Connect → TestFlight'tan kendinizi test kullanıcısı olarak ekleyin, sürümü telefonda deneyin.
2. App Store Connect'te **İş** bölümünde ücretli uygulama sözleşmesi, banka ve vergi bilgilerini tamamlayın.
3. 1.0 sayfasına `appstore/listing.md` metinlerini ve `appstore/screenshots/` görsellerini girin, Build bölümünden yüklenen sürümü seçin → **İncelemeye Gönder**.

Derleme hata verirse Codemagic'teki kırmızı adımın kaydını kopyalayıp Claude'a yapıştırın.
