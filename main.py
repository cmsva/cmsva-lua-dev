import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Cấu hình thư mục cần theo dõi 
# Đường dẫn chuẩn tới thư mục Download trên Android sau khi cấp quyền storage
WATCH_DIRECTORY = "/storage/emulated/0/Android/data/com.dts.freefireth"

class DirectoryMonitorHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"[TẠO MỚI] File: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[THAY ĐỔI] File: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[XÓA] File: {event.src_path}")
            
    def on_moved(self, event):
        if not event.is_directory:
            print(f"[DI CHUYỂN/ĐỔI TÊN] Từ {event.src_path} -> {event.dest_path}")

def start_monitoring():
    if not os.path.exists(WATCH_DIRECTORY):
        print(f"[LỖI] Không tìm thấy thư mục: {WATCH_DIRECTORY}")
        return

    event_handler = DirectoryMonitorHandler()
    observer = Observer()
    
    # recursive=True cho phép theo dõi cả các thư mục con bên trong
    observer.schedule(event_handler, WATCH_DIRECTORY, recursive=True)
    
    print("=" * 50)
    print(f"ĐANG THEO DÕI: {WATCH_DIRECTORY}")
    print("Bấm Ctrl + C để thoát")
    print("=" * 50)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[HỆ THỐNG] Đã dừng theo dõi thư mục.")
    
    observer.join()

if __name__ == "__main__":
    start_monitoring()
