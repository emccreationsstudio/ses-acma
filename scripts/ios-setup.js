// `npx cap add ios` sonrasında iOS projesini satışa hazır ayarlarla günceller.
// Tekrar çalıştırmak güvenlidir (aynı değişikliği iki kez yapmaz).
// Kullanım: node scripts/ios-setup.js
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const appDir = path.join(root, "ios", "App", "App");
if (!fs.existsSync(appDir)) {
  console.error("ios/App/App bulunamadı. Önce `npm run ios:add` çalıştırın.");
  process.exit(1);
}

const DISPLAY_NAME = "Ses Açma";
const MIC_TEXT =
  "Söylediğin notanın doğru olup olmadığını göstermek için mikrofon kullanılır; ses kaydedilmez. / " +
  "The microphone is used to check whether you are singing the right note; nothing is recorded.";

const done = [];

// 1) AppDelegate: sessiz moddayken de ses çıksın, egzersiz sırasında ekran kararmasın
const delegatePath = path.join(appDir, "AppDelegate.swift");
let delegate = fs.readFileSync(delegatePath, "utf8");
if (!delegate.includes("SesAcmaAudioSetup")) {
  if (!/import AVFoundation/.test(delegate)) {
    delegate = delegate.replace(/import UIKit\n/, "import UIKit\nimport AVFoundation\n");
  }
  const marker = /(didFinishLaunchingWithOptions[^{]*\{\n)/;
  if (!marker.test(delegate)) throw new Error("AppDelegate.swift içinde didFinishLaunchingWithOptions bulunamadı");
  delegate = delegate.replace(
    marker,
    `$1        // SesAcmaAudioSetup: telefon sessizdeyken de piyano duyulsun, ekran kararmasın
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default, options: [])
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Ses oturumu ayarlanamadı: \\(error)")
        }
        application.isIdleTimerDisabled = true

`
  );
  fs.writeFileSync(delegatePath, delegate);
  done.push("AppDelegate: sessiz modda çalma + ekran açık");
}

// 2) Info.plist: mikrofon izni, görünen ad, diller, şifreleme beyanı
const plistPath = path.join(appDir, "Info.plist");
let plist = fs.readFileSync(plistPath, "utf8");
function setKey(key, valueXml) {
  const re = new RegExp(`\\s*<key>${key}</key>\\s*(<string>[\\s\\S]*?</string>|<array>[\\s\\S]*?</array>|<true/>|<false/>)`);
  if (re.test(plist)) plist = plist.replace(re, `\n\t<key>${key}</key>\n\t${valueXml}`);
  else plist = plist.replace(/<\/dict>\s*<\/plist>\s*$/, `\t<key>${key}</key>\n\t${valueXml}\n</dict>\n</plist>\n`);
}
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
setKey("NSMicrophoneUsageDescription", `<string>${esc(MIC_TEXT)}</string>`);
setKey("CFBundleDisplayName", `<string>${esc(DISPLAY_NAME)}</string>`);
setKey("CFBundleLocalizations", "<array>\n\t\t<string>tr</string>\n\t\t<string>en</string>\n\t</array>");
setKey("ITSAppUsesNonExemptEncryption", "<false/>");
fs.writeFileSync(plistPath, plist);
done.push("Info.plist: mikrofon izni, ad, Türkçe/İngilizce, şifreleme beyanı");

// 3) Uygulama ikonu
const iconSet = path.join(appDir, "Assets.xcassets", "AppIcon.appiconset");
fs.mkdirSync(iconSet, { recursive: true });
for (const f of fs.readdirSync(iconSet)) if (f.endsWith(".png")) fs.unlinkSync(path.join(iconSet, f));
fs.copyFileSync(path.join(root, "assets", "icon-1024.png"), path.join(iconSet, "AppIcon-1024.png"));
fs.writeFileSync(
  path.join(iconSet, "Contents.json"),
  JSON.stringify({ images: [{ filename: "AppIcon-1024.png", idiom: "universal", platform: "ios", size: "1024x1024" }], info: { author: "xcode", version: 1 } }, null, 2)
);
done.push("Uygulama ikonu");

// 4) Açılış ekranı görselleri (Capacitor şablonundaki dosyaların yerine)
const splashSet = path.join(appDir, "Assets.xcassets", "Splash.imageset");
if (fs.existsSync(splashSet)) {
  const pngs = fs.readdirSync(splashSet).filter((f) => f.endsWith(".png"));
  for (const f of pngs) fs.copyFileSync(path.join(root, "assets", "splash-2732.png"), path.join(splashSet, f));
  if (pngs.length) done.push(`Açılış ekranı (${pngs.length} görsel)`);
}

// 5) Yalnızca iPhone (iPad ekran görüntüsü istenmesin; iPad'de iPhone uygulaması olarak yine çalışır)
const pbxPath = path.join(root, "ios", "App", "App.xcodeproj", "project.pbxproj");
if (fs.existsSync(pbxPath)) {
  const pbx = fs.readFileSync(pbxPath, "utf8");
  const updated = pbx.replace(/TARGETED_DEVICE_FAMILY = "1,2";/g, "TARGETED_DEVICE_FAMILY = 1;");
  if (updated !== pbx) {
    fs.writeFileSync(pbxPath, updated);
    done.push("Yalnızca iPhone hedefi");
  }
}

console.log("iOS projesi güncellendi:\n - " + done.join("\n - "));
