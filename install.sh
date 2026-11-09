#!/usr/bin/env bash
set -e

echo "=== Cloudflare DNS Tray Installer ==="

# Check if running on Arch-based distribution
if command -v makepkg >/dev/null 2>&1; then
    echo ":: Building and installing via makepkg..."
    makepkg -si --noconfirm
else
    echo ":: makepkg not found, performing direct system install..."
    sudo install -Dm755 cloudflare-dns-tray.py /usr/bin/cloudflare-dns-tray
    sudo install -Dm644 cloudflare-dns-tray.desktop /usr/share/applications/cloudflare-dns-tray.desktop
    sudo install -Dm644 cloudflare-dns-tray.desktop /etc/xdg/autostart/cloudflare-dns-tray.desktop
    sudo install -Dm644 cloudflare-dns-tray.service /usr/lib/systemd/user/cloudflare-dns-tray.service
fi

echo ":: Reloading systemd user services..."
systemctl --user daemon-reload
systemctl --user enable --now cloudflare-dns-tray.service

echo ""
echo ":: Make sure Cloudflare daemon is enabled:"
echo "   sudo systemctl enable --now warp-svc"
echo ""
echo "✓ Installation complete! The toggle is now active in your status bar."
