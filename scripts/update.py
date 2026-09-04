#!/data/data/com.termux/files/usr/bin/python

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

MAIN_URL = "https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/scripts/main.py"
HELP_URL = "https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/scripts/help.txt"

BASE_STORAGE = "/storage/emulated/0"
WORK_DIR = Path(__file__).resolve().parent

MAIN_FILE = WORK_DIR / "main.py"
HELP_FILE = WORK_DIR / "help.txt"
CONFIG_FILE = WORK_DIR / "cmsva_config.json"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def info(msg: str) -> None:
    print(f"{YELLOW}[*] {msg}{NC}")


def ok(msg: str) -> None:
    print(f"{GREEN}[✓] {msg}{NC}")


def fail(msg: str, code: int = 1) -> None:
    print(f"{RED}[!] {msg}{NC}")
    raise SystemExit(code)


def download_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CMSVA-Updater/1.0",
            "Cache-Control": "no-cache",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        fail(f"Lỗi HTTP {exc.code} khi tải: {url}")
    except urllib.error.URLError as exc:
        fail(f"Không thể kết nối GitHub: {exc.reason}")
    except Exception as exc:
        fail(f"Lỗi khi tải dữ liệu: {exc}")

    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"File tải về không phải UTF-8: {url}")

    return ""


def normalize_autoexecute_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    prefix = BASE_STORAGE.rstrip("/") + "/"

    if value.startswith(prefix):
        value = value[len(prefix):]
    else:
        value = value.lstrip("/")

    value = re.sub(r"/+", "/", value).strip("/")

    if not value:
        fail("Đường dẫn autoexecute không hợp lệ.")

    parts = [part for part in value.split("/") if part]
    if ".." in parts:
        fail("Đường dẫn autoexecute không được chứa '..'.")

    return value


def extract_path_from_main() -> str | None:
    if not MAIN_FILE.exists():
        return None

    try:
        data = MAIN_FILE.read_text(encoding="utf-8")
    except Exception:
        return None

    patterns = [
        r"SAVE_DIR\s*=\s*[\"']/storage/emulated/0/([^\"']+)[\"']",
        r"SAVE_DIR\s*=\s*[\"']([^\"']+)[\"']",
    ]

    for pattern in patterns:
        match = re.search(pattern, data)
        if not match:
            continue

        value = match.group(1).strip()

        if "{path_autoexecute}" in value:
            continue

        try:
            return normalize_autoexecute_path(value)
        except SystemExit:
            return None

    return None


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def save_config(path_autoexecute: str) -> None:
    payload = {
        "path_autoexecute": path_autoexecute,
        "autoexecute_dir": f"{BASE_STORAGE}/{path_autoexecute}",
        "main_url": MAIN_URL,
        "help_url": HELP_URL,
    }

    tmp = CONFIG_FILE.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(CONFIG_FILE)


def setup_automatically() -> str:
    config = load_config()

    configured = config.get("path_autoexecute")
    if isinstance(configured, str) and configured.strip():
        path = normalize_autoexecute_path(configured)
        save_config(path)
        ok(f"Đã tải cấu hình tự động: {BASE_STORAGE}/{path}")
        return path

    detected = extract_path_from_main()
    if detected:
        save_config(detected)
        ok(f"Tự phát hiện autoexecute: {BASE_STORAGE}/{detected}")
        return detected

    print()
    print(f"{CYAN}Thiết lập lần đầu{NC}")
    print("Không tìm thấy cấu hình cũ.")
    print("Nhập đường dẫn autoexecute một lần; lần sau update.py sẽ tự dùng.")
    print()
    print("Ví dụ:")
    print("  Delta/autoexecute")
    print("hoặc:")
    print("  /storage/emulated/0/Delta/autoexecute")
    print()

    while True:
        value = input("Đường dẫn autoexecute: ").strip()
        if not value:
            print(f"{RED}[!] Không được để trống.{NC}")
            continue

        path = normalize_autoexecute_path(value)
        save_config(path)
        ok("Đã lưu cấu hình.")
        return path


def patch_main(source: str, path_autoexecute: str) -> str:
    placeholder = "{path_autoexecute}"

    if placeholder in source:
        return source.replace(placeholder, path_autoexecute)

    pattern = r"SAVE_DIR\s*=\s*[\"']/storage/emulated/0/[^\"']*[\"']"
    replacement = f'SAVE_DIR="/storage/emulated/0/{path_autoexecute}"'

    patched, count = re.subn(pattern, replacement, source, count=1)

    if count:
        return patched

    fail("main.py mới không có {path_autoexecute} hoặc SAVE_DIR để cấu hình tự động.")
    return source


def atomic_write(path: Path, content: str) -> None:
    fd, temp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(WORK_DIR),
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)

        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None

    backup = path.with_suffix(path.suffix + ".bak")

    try:
        shutil.copy2(path, backup)
        return backup
    except Exception:
        return None


def main() -> None:
    print(f"{CYAN}========================================{NC}")
    print(f"{CYAN}           CMSVA AUTO UPDATER           {NC}")
    print(f"{CYAN}========================================{NC}")
    print()

    path_autoexecute = setup_automatically()

    info("Đang tải phiên bản mới từ GitHub...")
    new_main = download_text(MAIN_URL)
    new_help = download_text(HELP_URL)

    if not new_main.strip():
        fail("main.py trên GitHub đang rỗng.")

    patched_main = patch_main(new_main, path_autoexecute)

    old_main = MAIN_FILE.read_text(encoding="utf-8") if MAIN_FILE.exists() else ""
    old_help = HELP_FILE.read_text(encoding="utf-8") if HELP_FILE.exists() else ""

    main_changed = old_main != patched_main
    help_changed = old_help != new_help

    if not main_changed and not help_changed:
        ok("Bạn đang dùng phiên bản mới nhất.")
        print(f"Autoexecute: {BASE_STORAGE}/{path_autoexecute}")
        return

    if main_changed:
        backup = backup_file(MAIN_FILE)
        atomic_write(MAIN_FILE, patched_main)

        try:
            MAIN_FILE.chmod(0o755)
        except Exception:
            pass

        ok("Đã cập nhật main.py.")

        if backup:
            print(f"    Backup: {backup}")

    if help_changed:
        atomic_write(HELP_FILE, new_help)
        ok("Đã cập nhật help.txt.")

    save_config(path_autoexecute)

    print()
    print(f"{GREEN}========================================{NC}")
    print(f"{GREEN}           CẬP NHẬT HOÀN TẤT            {NC}")
    print(f"{GREEN}========================================{NC}")
    print()
    print(f"Thư mục     : {WORK_DIR}")
    print(f"Autoexecute : {BASE_STORAGE}/{path_autoexecute}")
    print(f"main.py     : {MAIN_FILE}")
    print(f"help.txt    : {HELP_FILE}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        fail("Đã hủy cập nhật.", 130)
