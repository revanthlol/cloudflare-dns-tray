# 🛡️ cloudflare-dns-tray

> A lightweight, instant 1-click status bar toggle and indicator for **Cloudflare 1.1.1.1 DNS** (DNS-over-HTTPS / WARP) on **KDE Plasma** and Linux desktops.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Arch Linux](https://img.shields.io/badge/Arch%20Linux-AUR%20Ready-1793d1.svg)
![KDE Plasma](https://img.shields.io/badge/KDE-Plasma%206-38bdf8.svg)

---

## ✨ Features

- **⚡ Instant 1-Click Toggle**: Left-click the tray icon to immediately connect or disconnect Cloudflare DNS.
- **🎨 Dynamic Status Indicator**:
  - 🟠 **Orange Cloud + Emerald Dot**: Connected via Cloudflare 1.1.1.1 DoH.
  - ⚪ **Gray Cloud + Red Dot**: Disconnected (reverts to standard network DNS).
  - ⏳ **Amber Dot**: Reconnecting or busy state.
  - ⚠️ **Dark Red Dot**: Warning if `warp-svc` is stopped or CLI is missing.
- **⚙️ Operating Modes**: Switch between **1.1.1.1 (DNS-over-HTTPS)** and **Full WARP VPN Tunnel** directly from the context menu.
- **🌐 Built-in DNS Resolution Test**: One-click test to verify resolution via Cloudflare.
- **🔔 Native Desktop Notifications**: Clean popups via `libnotify` notifying on state changes.
- **🚀 Autostart Integration**: Starts automatically on desktop login via XDG Autostart & systemd user service.
- **🪶 Ultra-lightweight**: Pure PyQt6 StatusNotifierItem (~15 MB RAM), no heavy Electron/Flutter background runtime required.

---

## 📦 Installation

### Prerequisites
Make sure `cloudflare-warp-bin` (from AUR) is installed:
```bash
yay -S cloudflare-warp-bin
```
Enable the daemon (one-time setup):
```bash
sudo systemctl enable --now warp-svc
```

---

### Method 1: Using `makepkg` (Recommended)

```bash
git clone https://github.com/revanthlol/cloudflare-dns-tray.git
cd cloudflare-dns-tray
makepkg -si
```

### Method 2: Using `yay`

Inside the cloned directory:
```bash
git clone https://github.com/revanthlol/cloudflare-dns-tray.git
cd cloudflare-dns-tray
yay -Bi .
```

### Method 3: Quick Helper Script

```bash
git clone https://github.com/revanthlol/cloudflare-dns-tray.git
cd cloudflare-dns-tray
chmod +x install.sh
./install.sh
```

---

## 🚀 Usage

Once installed, the tray icon appears automatically in your status bar / system tray.

### Controls:
- **Left-Click**: Toggle DNS on/off immediately.
- **Right-Click**:
  - View live status & mode
  - Select mode: `1.1.1.1 DoH` or `WARP VPN`
  - Test DNS resolution (`dig` check)
  - Open Cloudflare Official GUI (`warp-taskbar`)
  - Quit toggle

### Manage Background Service:
```bash
# Check status
systemctl --user status cloudflare-dns-tray.service

# Restart
systemctl --user restart cloudflare-dns-tray.service

# Stop
systemctl --user stop cloudflare-dns-tray.service
```

---

## 🗑️ Uninstallation

If installed via `makepkg` or `yay`:
```bash
sudo pacman -R cloudflare-dns-tray
# or
yay -R cloudflare-dns-tray
```

---

## 📄 License

MIT © [revanthlol](https://github.com/revanthlol)
