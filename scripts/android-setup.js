// `npx cap add android` sonrasında Android projesini Google Play'e hazır ayarlarla günceller.
// Tekrar çalıştırmak güvenlidir. Kullanım: node scripts/android-setup.js
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const app = path.join(root, "android", "app");
if (!fs.existsSync(app)) {
  console.error("android/app bulunamadı. Önce `npx cap add android` çalıştırın.");
  process.exit(1);
}
const done = [];
const pkg = require(path.join(root, "package.json"));
const VERSION_NAME = pkg.version.split(".").slice(0, 2).join(".");
const DISPLAY_NAME = "Ses Açma";

// 1) Mikrofon izni
const manifestPath = path.join(app, "src", "main", "AndroidManifest.xml");
let manifest = fs.readFileSync(manifestPath, "utf8");
for (const perm of ["android.permission.RECORD_AUDIO", "android.permission.MODIFY_AUDIO_SETTINGS"]) {
  if (!manifest.includes(perm)) manifest = manifest.replace(/<\/manifest>\s*$/, `    <uses-permission android:name="${perm}" />\n</manifest>\n`);
}
// Telefon dikey dursun (uygulama dikey ekran için tasarlandı)
if (!/android:screenOrientation/.test(manifest)) {
  manifest = manifest.replace(/(<activity\b)/, `$1\n            android:screenOrientation="portrait"`);
}
fs.writeFileSync(manifestPath, manifest);
done.push("Mikrofon izni, dikey ekran");

// 2) Uygulama adı (telefon ana ekranında görünen kısa ad)
const stringsPath = path.join(app, "src", "main", "res", "values", "strings.xml");
let strings = fs.readFileSync(stringsPath, "utf8");
strings = strings
  .replace(/<string name="app_name">[^<]*<\/string>/, `<string name="app_name">${DISPLAY_NAME}</string>`)
  .replace(/<string name="title_activity_main">[^<]*<\/string>/, `<string name="title_activity_main">${DISPLAY_NAME}</string>`);
fs.writeFileSync(stringsPath, strings);
done.push(`Ad: ${DISPLAY_NAME}`);

// 3) İkonlar (assets/android/res → android/app/src/main/res)
const iconSrc = path.join(root, "assets", "android", "res");
const resDst = path.join(app, "src", "main", "res");
for (const dir of fs.readdirSync(iconSrc)) {
  fs.mkdirSync(path.join(resDst, dir), { recursive: true });
  for (const f of fs.readdirSync(path.join(iconSrc, dir))) {
    // Capacitor şablonundaki eski ikon dosyalarını (ör. .webp) temizle
    const stem = f.replace(/\.[a-z]+$/, "");
    for (const old of fs.readdirSync(path.join(resDst, dir))) if (old.replace(/\.[a-z]+$/, "") === stem) fs.unlinkSync(path.join(resDst, dir, old));
    fs.copyFileSync(path.join(iconSrc, dir, f), path.join(resDst, dir, f));
  }
}
done.push("İkonlar");

// 4) Sürüm (package.json) + derleme numarası (Codemagic BUILD_NUMBER) + imzalama
const gradlePath = path.join(app, "build.gradle");
let gradle = fs.readFileSync(gradlePath, "utf8");
if (!/versionCode\s+\S+/.test(gradle) || !/buildTypes\s*\{\s*release\s*\{/.test(gradle)) throw new Error("android/app/build.gradle beklenen biçimde değil (versionCode / buildTypes.release bulunamadı)");
gradle = gradle
  .replace(/versionCode\s+\d+/, `versionCode Integer.parseInt(System.getenv("BUILD_NUMBER") ?: "1")`)
  .replace(/versionName\s+"[^"]*"/, `versionName "${VERSION_NAME}"`);
if (!gradle.includes("SesAcmaSigning")) {
  gradle = gradle.replace(
    /(\n\s*buildTypes\s*\{)/,
    `
    // SesAcmaSigning: Codemagic'teki yükleme anahtarıyla (upload keystore) imzala
    signingConfigs {
        release {
            if (System.getenv("CM_KEYSTORE_PATH")) {
                storeFile file(System.getenv("CM_KEYSTORE_PATH"))
                storePassword System.getenv("CM_KEYSTORE_PASSWORD")
                keyAlias System.getenv("CM_KEY_ALIAS")
                keyPassword System.getenv("CM_KEY_PASSWORD")
            }
        }
    }$1`
  );
  gradle = gradle.replace(/(buildTypes\s*\{\s*release\s*\{)/, `$1\n            if (System.getenv("CM_KEYSTORE_PATH")) signingConfig signingConfigs.release`);
}
fs.writeFileSync(gradlePath, gradle);
done.push(`Sürüm ${VERSION_NAME}, imzalama`);

console.log("Android projesi güncellendi:\n - " + done.join("\n - "));
