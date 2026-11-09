# Maintainer: Revanth <workofotb@gmail.com>
pkgname=cloudflare-dns-tray
pkgver=1.0.0
pkgrel=1
pkgdesc="Lightweight 1-click Cloudflare 1.1.1.1 DNS status bar toggle for KDE Plasma and Linux desktops"
arch=('any')
url="https://github.com/revanthlol/cloudflare-dns-tray"
license=('MIT')
depends=(
    'python'
    'python-pyqt6'
    'libnotify'
    'cloudflare-warp-bin'
)
optdepends=(
    'bind: for dig DNS resolution testing in context menu'
)
install=cloudflare-dns-tray.install
source=(
    'cloudflare-dns-tray.py'
    'cloudflare-dns-tray.desktop'
    'cloudflare-dns-tray.service'
    'LICENSE'
)
sha256sums=(
    'SKIP'
    'SKIP'
    'SKIP'
    'SKIP'
)

package() {
    cd "${srcdir}"

    # Executable binary
    install -Dm755 cloudflare-dns-tray.py "${pkgdir}/usr/bin/cloudflare-dns-tray"

    # Desktop application entry
    install -Dm644 cloudflare-dns-tray.desktop "${pkgdir}/usr/share/applications/cloudflare-dns-tray.desktop"

    # Autostart entry for all desktop sessions (KDE Plasma, GNOME, etc.)
    install -Dm644 cloudflare-dns-tray.desktop "${pkgdir}/etc/xdg/autostart/cloudflare-dns-tray.desktop"

    # Systemd user service
    install -Dm644 cloudflare-dns-tray.service "${pkgdir}/usr/lib/systemd/user/cloudflare-dns-tray.service"

    # License
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
