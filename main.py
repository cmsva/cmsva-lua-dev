import os
import time
import socket
import threading
import subprocess
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =========================
# CONFIG
# =========================

WATCH_DIR = "/storage/emulated/0/Download"
LOG_FILE = "/storage/emulated/0/Download/network_monitor.log"
CHECK_INTERVAL = 1
MODIFY_DEBOUNCE = 0.5

# =========================

log_lock = threading.Lock()
known_connections = set()
last_modified = {}
dns_cache = {}


def write_log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {message}"
    print(line, flush=True)

    with log_lock:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            print(f"[LOG ERROR] Không thể ghi log: {e}")


def format_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def file_info(path):
    try:
        size = os.path.getsize(path)
        ext = os.path.splitext(path)[1].lower() or "[NO EXT]"
        return ext, size, format_size(size)
    except OSError:
        ext = os.path.splitext(path)[1].lower() or "[NO EXT]"
        return ext, 0, "0 B"


# =========================
# FILE MONITOR
# =========================

class FileHandler(FileSystemEventHandler):

    @staticmethod
    def is_log_file(path):
        return os.path.abspath(path) == os.path.abspath(LOG_FILE)

    def on_created(self, event):
        if self.is_log_file(event.src_path):
            return
        if event.is_directory:
            write_log(f"[FOLDER CREATED] {event.src_path}")
            return
        ext, size, size_text = file_info(event.src_path)
        write_log(f"[FILE CREATED] PATH={event.src_path} | EXT={ext} | SIZE={size_text}")

    def on_modified(self, event):
        if event.is_directory or self.is_log_file(event.src_path):
            return
        now = time.time()
        last = last_modified.get(event.src_path, 0)

        if now - last < MODIFY_DEBOUNCE:
            return

        last_modified[event.src_path] = now
        ext, size, size_text = file_info(event.src_path)
        write_log(f"[FILE MODIFIED] PATH={event.src_path} | EXT={ext} | SIZE={size_text}")

    def on_deleted(self, event):
        if self.is_log_file(event.src_path):
            return
        if event.is_directory:
            write_log(f"[FOLDER DELETED] {event.src_path}")
        else:
            ext = os.path.splitext(event.src_path)[1].lower() or "[NO EXT]"
            write_log(f"[FILE DELETED] PATH={event.src_path} | EXT={ext}")
        last_modified.pop(event.src_path, None)

    def on_moved(self, event):
        if self.is_log_file(event.src_path) or self.is_log_file(event.dest_path):
            return
        if event.is_directory:
            write_log(f"[FOLDER MOVED] FROM={event.src_path} -> TO={event.dest_path}")
            return
        ext, size, size_text = file_info(event.dest_path)
        write_log(f"[FILE MOVED] FROM={event.src_path} -> TO={event.dest_path} | SIZE={size_text}")
        last_modified.pop(event.src_path, None)


# =========================
# NETWORK
# =========================

def resolve_ip(ip):
    if ip in dns_cache:
        return dns_cache[ip]
    try:
        host = socket.gethostbyaddr(ip)[0]
    except Exception:
        host = "-"
    dns_cache[ip] = host
    return host


def parse_remote(remote):
    remote = remote.strip()
    if remote.startswith("[") and "]:" in remote:
        end = remote.rfind("]")
        return remote[1:end], remote[end + 2:]
    try:
        ip, port = remote.rsplit(":", 1)
        return ip.strip("[]"), port
    except ValueError:
        return None, None


def get_connections():
    try:
        result = subprocess.run(["ss", "-tun"], capture_output=True, text=True, timeout=5)
    except Exception:
        return set()

    connections = set()
    for line in result.stdout.splitlines():
        if "ESTAB" not in line:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        remote = parts[-1]
        ip, port = parse_remote(remote)

        if not ip or port not in ("80", "443"):
            continue
        connections.add((ip, port))
    return connections


def network_monitor():
    global known_connections
    known_connections = get_connections()
    write_log(f"[SYSTEM] Tìm thấy {len(known_connections)} kết nối mạng đang tồn tại.")
    
    while True:
        try:
            current = get_connections()
            for ip, port in current - known_connections:
                protocol = "HTTPS" if port == "443" else "HTTP"
                write_log(f"[NETWORK CONNECT] {protocol} | HOST={resolve_ip(ip)} | IP={ip}:{port}")

            for ip, port in known_connections - current:
                protocol = "HTTPS" if port == "443" else "HTTP"
                write_log(f"[NETWORK CLOSED] {protocol} | HOST={resolve_ip(ip)} | IP={ip}:{port}")

            known_connections = current
        except Exception:
            pass
        time.sleep(CHECK_INTERVAL)


# =========================
# MAIN
# =========================

def main():
    print("=" * 50, flush=True)
    print("ĐANG KHỞI ĐỘNG HỆ THỐNG GIÁM SÁT...", flush=True)
    print("=" * 50, flush=True)
    
    if not os.path.isdir(WATCH_DIR):
        print(f"[LỖI] Không tìm thấy thư mục: {WATCH_DIR}")
        print("Vui lòng chạy lệnh: termux-setup-storage")
        return

    # Khởi động Network Monitor
    network_thread = threading.Thread(target=network_monitor, daemon=True)
    network_thread.start()

    # Khởi động File Monitor
    observer = Observer()
    observer.schedule(FileHandler(), WATCH_DIR, recursive=True)
    observer.start()

    write_log("[START] Đang theo dõi File và Mạng. Bấm Ctrl+C để thoát.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        write_log("[STOP] Đã dừng giám sát.")
    observer.join()

if __name__ == "__main__":
    main()
