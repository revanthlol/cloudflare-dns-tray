#!/usr/bin/env python3
"""
Cloudflare DNS Status Bar Toggle
A lightweight 1-click system tray toggle for Cloudflare 1.1.1.1 (DoH / WARP) on KDE Plasma and Linux desktops.
Author: Revanth (revanthlol)
License: MIT
"""

import sys
import shutil
import subprocess
import threading
from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu
)
from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QColor,
    QBrush,
    QPen,
    QPainterPath,
    QFont,
    QAction,
    QActionGroup
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

def run_cmd(cmd_list, timeout=5):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip()
    except Exception:
        return ""

def send_notification(title, message, urgency="normal"):
    try:
        subprocess.Popen([
            "notify-send",
            "-a", "Cloudflare DNS",
            "-u", urgency,
            title,
            message
        ])
    except Exception:
        pass

class WorkerSignals(QObject):
    status_ready = pyqtSignal(str, str) # status, mode
    notification = pyqtSignal(str, str)

class CloudflareTray:
    def __init__(self, app):
        self.app = app
        self.signals = WorkerSignals()
        self.signals.status_ready.connect(self.on_status_updated)
        self.signals.notification.connect(send_notification)

        self.current_status = "Unknown"  # "Connected", "Connecting", "Disconnected", "ServiceStopped"
        self.current_mode = "doh"       # "doh", "warp"
        self.is_busy = False

        self.warp_cli_path = shutil.which("warp-cli")

        self.icon_connected = self.render_icon(state="connected")
        self.icon_disconnected = self.render_icon(state="disconnected")
        self.icon_busy = self.render_icon(state="busy")
        self.icon_error = self.render_icon(state="error")

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon_disconnected)
        self.tray.setToolTip("Cloudflare DNS: Initializing...")

        self.tray.activated.connect(self.on_tray_activated)

        self.build_menu()
        self.tray.show()

        # Polling timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_status_async)
        self.timer.start(2500)

        # Initial check
        self.check_status_async()

    def render_icon(self, state="disconnected"):
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if state == "connected":
            cloud_color = QColor("#F38020") # Cloudflare Orange
            dot_color = QColor("#10B981")   # Emerald Green
        elif state == "busy":
            cloud_color = QColor("#F59E0B") # Amber
            dot_color = QColor("#F59E0B")
        elif state == "error":
            cloud_color = QColor("#9CA3AF") # Gray
            dot_color = QColor("#DC2626")   # Dark Red
        else:
            cloud_color = QColor("#6B7280") # Neutral Slate Gray
            dot_color = QColor("#EF4444")   # Muted Red / Off

        # Draw Cloud shape
        path = QPainterPath()
        path.moveTo(18, 44)
        path.lineTo(46, 44)
        path.arcTo(36, 28, 18, 18, 270, 180)
        path.arcTo(22, 18, 24, 24, 0, 180)
        path.arcTo(10, 26, 18, 18, 90, 180)
        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(cloud_color))
        painter.drawPath(path)

        # Bottom-right status indicator badge
        painter.setBrush(QBrush(dot_color))
        painter.setPen(QPen(QColor("#18181B"), 2))
        painter.drawEllipse(42, 36, 18, 18)

        painter.end()
        return QIcon(pixmap)

    def build_menu(self):
        self.menu = QMenu()

        self.status_header = QAction("Cloudflare DNS: Checking...", self.menu)
        font = self.status_header.font()
        font.setBold(True)
        self.status_header.setFont(font)
        self.status_header.setEnabled(False)
        self.menu.addAction(self.status_header)

        self.toggle_action = QAction("⚡ Toggle Connection", self.menu)
        self.toggle_action.triggered.connect(self.toggle_connection)
        self.menu.addAction(self.toggle_action)

        self.menu.addSeparator()

        # Mode Submenu
        self.mode_menu = self.menu.addMenu("⚙️ Operating Mode")
        self.mode_group = QActionGroup(self.mode_menu)
        self.mode_group.setExclusive(True)

        self.action_mode_doh = QAction("1.1.1.1 (DNS-over-HTTPS)", self.mode_menu, checkable=True)
        self.action_mode_doh.setChecked(True)
        self.action_mode_doh.triggered.connect(lambda: self.set_mode("doh"))
        self.mode_group.addAction(self.action_mode_doh)
        self.mode_menu.addAction(self.action_mode_doh)

        self.action_mode_warp = QAction("WARP (Full VPN Tunnel)", self.mode_menu, checkable=True)
        self.action_mode_warp.triggered.connect(lambda: self.set_mode("warp"))
        self.mode_group.addAction(self.action_mode_warp)
        self.mode_menu.addAction(self.action_mode_warp)

        self.menu.addSeparator()

        self.test_action = QAction("🌐 Test DNS Resolution", self.menu)
        self.test_action.triggered.connect(self.test_dns_resolution)
        self.menu.addAction(self.test_action)

        self.gui_action = QAction("🖥️ Open Cloudflare Official App", self.menu)
        self.gui_action.triggered.connect(self.launch_warp_taskbar)
        self.menu.addAction(self.gui_action)

        self.menu.addSeparator()

        self.quit_action = QAction("❌ Quit Toggle", self.menu)
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)

    def on_tray_activated(self, reason):
        # On single left-click (Trigger) or middle click, toggle immediately
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.MiddleClick):
            self.toggle_connection()

    def check_status_async(self):
        if self.is_busy:
            return

        def task():
            if not self.warp_cli_path:
                self.signals.status_ready.emit("MissingCli", "doh")
                return

            status_out = run_cmd(["warp-cli", "status"])
            if "daemon is not running" in status_out or "Unable to connect" in status_out:
                self.signals.status_ready.emit("ServiceStopped", "doh")
                return

            settings_out = run_cmd(["warp-cli", "settings"])

            status = "Disconnected"
            if "Status update: Connected" in status_out:
                status = "Connected"
            elif "Connecting" in status_out:
                status = "Connecting"

            mode = "doh"
            if "Mode: Warp" in settings_out:
                mode = "warp"
            elif "Mode: DnsOverHttps" in settings_out:
                mode = "doh"

            self.signals.status_ready.emit(status, mode)

        threading.Thread(target=task, daemon=True).start()

    def on_status_updated(self, status, mode):
        self.current_status = status
        self.current_mode = mode

        if mode == "warp":
            self.action_mode_warp.setChecked(True)
            mode_desc = "WARP VPN"
        else:
            self.action_mode_doh.setChecked(True)
            mode_desc = "1.1.1.1 DoH"

        if status == "Connected":
            self.tray.setIcon(self.icon_connected)
            self.tray.setToolTip(f"Cloudflare DNS: Connected ({mode_desc})\nLeft-click to disable")
            self.status_header.setText(f"● Cloudflare DNS: Connected ({mode_desc})")
            self.toggle_action.setText("🔴 Disconnect Cloudflare DNS")
            self.toggle_action.setEnabled(True)
        elif status == "Connecting":
            self.tray.setIcon(self.icon_busy)
            self.tray.setToolTip("Cloudflare DNS: Connecting...")
            self.status_header.setText("⏳ Cloudflare DNS: Connecting...")
            self.toggle_action.setText("⏳ Connecting...")
            self.toggle_action.setEnabled(False)
        elif status == "ServiceStopped":
            self.tray.setIcon(self.icon_error)
            self.tray.setToolTip("Cloudflare Service Stopped\nRun: sudo systemctl start warp-svc")
            self.status_header.setText("⚠️ warp-svc.service is stopped")
            self.toggle_action.setText("⚠️ Start warp-svc first")
            self.toggle_action.setEnabled(False)
        elif status == "MissingCli":
            self.tray.setIcon(self.icon_error)
            self.tray.setToolTip("warp-cli not found\nInstall cloudflare-warp-bin")
            self.status_header.setText("⚠️ warp-cli missing")
            self.toggle_action.setText("⚠️ Install cloudflare-warp-bin")
            self.toggle_action.setEnabled(False)
        else:
            self.tray.setIcon(self.icon_disconnected)
            self.tray.setToolTip(f"Cloudflare DNS: Disabled\nLeft-click to enable ({mode_desc})")
            self.status_header.setText("○ Cloudflare DNS: Disabled")
            self.toggle_action.setText("🟢 Enable Cloudflare DNS")
            self.toggle_action.setEnabled(True)

    def toggle_connection(self):
        if self.is_busy or self.current_status in ("ServiceStopped", "MissingCli"):
            return

        self.is_busy = True
        self.tray.setIcon(self.icon_busy)

        def task():
            if self.current_status == "Connected":
                run_cmd(["warp-cli", "disconnect"])
                self.signals.notification.emit("Cloudflare DNS", "Disconnected (reverted to default DNS)")
            else:
                run_cmd(["warp-cli", "connect"])
                mode_str = "WARP Tunnel" if self.current_mode == "warp" else "1.1.1.1 DNS over HTTPS"
                self.signals.notification.emit("Cloudflare DNS", f"Connected via {mode_str}")

            self.is_busy = False
            self.check_status_async()

        threading.Thread(target=task, daemon=True).start()

    def set_mode(self, mode):
        def task():
            run_cmd(["warp-cli", "mode", mode])
            self.signals.notification.emit("Cloudflare DNS", f"Mode switched to {mode.upper()}")
            self.check_status_async()

        threading.Thread(target=task, daemon=True).start()

    def test_dns_resolution(self):
        def task():
            out = run_cmd(["dig", "+short", "whoami.cloudflare", "@127.0.2.2"])
            if not out:
                out = run_cmd(["dig", "+short", "cloudflare.com"])
            if out:
                msg = f"DNS Resolution working!\nResolved: {out.splitlines()[0]}"
            else:
                msg = "DNS query failed. Check network connection."
            self.signals.notification.emit("Cloudflare DNS Test", msg)

        threading.Thread(target=task, daemon=True).start()

    def launch_warp_taskbar(self):
        taskbar = shutil.which("warp-taskbar")
        if taskbar:
            try:
                subprocess.Popen([taskbar])
            except Exception as e:
                send_notification("Cloudflare Error", f"Failed to launch warp-taskbar: {e}")
        else:
            send_notification("Cloudflare Error", "warp-taskbar binary not found")

    def quit_app(self):
        self.tray.hide()
        self.app.quit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        send_notification("Cloudflare DNS", "System tray is not available on this desktop environment.")
        sys.exit(1)

    tray_app = CloudflareTray(app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
