// Ses Açma - Piano Warm Up — masaüstü (Windows / Mac) kabuğu.
// Uygulamanın kendisi www/index.html; internetsiz çalışır.
const { app, BrowserWindow, session, systemPreferences, shell } = require("electron");
const path = require("path");

const TITLE = "Ses Açma - Piano Warm Up";
if (!app.requestSingleInstanceLock()) app.quit();

let win = null;
function createWindow() {
  win = new BrowserWindow({
    title: TITLE,
    width: 480, height: 900, minWidth: 360, minHeight: 640,
    backgroundColor: "#111022",
    autoHideMenuBar: true,
    show: false,
    webPreferences: { contextIsolation: true, sandbox: true, nodeIntegration: false, backgroundThrottling: false }
  });
  win.setMenuBarVisibility(false);
  win.loadFile(path.join(__dirname, "www", "index.html"));
  win.once("ready-to-show", () => win.show());
  win.on("page-title-updated", (e) => e.preventDefault());
  // Uygulama içindeki dış bağlantılar (ör. e-posta) varsayılan tarayıcıda açılsın
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: "deny" }; });
  win.webContents.on("will-navigate", (e, url) => { if (!url.startsWith("file:")) { e.preventDefault(); shell.openExternal(url); } });
}

app.on("second-instance", () => { if (win) { if (win.isMinimized()) win.restore(); win.focus(); } });

app.whenReady().then(async () => {
  // Yalnızca mikrofona izin ver (perde algılama için); başka izin isteme
  session.defaultSession.setPermissionRequestHandler((wc, permission, cb, details) => {
    const audioOnly = permission === "media" && (!details.mediaTypes || details.mediaTypes.every((t) => t === "audio"));
    cb(audioOnly);
  });
  session.defaultSession.setPermissionCheckHandler((wc, permission) => permission === "media");
  if (process.platform === "darwin") {
    try { await systemPreferences.askForMediaAccess("microphone"); } catch (e) {}
  }
  createWindow();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
