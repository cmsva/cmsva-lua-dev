import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Cấu hình thư mục
WATCH_DIRECTORY = "/storage/emulated/0/Android/data/com.dts.freefireth"
TMP_DIRECTORY = "/storage/emulated/0/freefire"

class DirectoryMonitorHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"[TẠO MỚI] File: {event.src_path}")
            
            # Thực hiện copy file mới tạo sang thư mục tmp
            try:
                shutil.copy2(event.src_path, TMP_DIRECTORY)
                file_name = os.path.basename(event.src_path)
                print(f"[ĐÃ COPY] -> {os.path.join(TMP_DIRECTORY, file_name)}")
            except Exception as e:
                print(f"[LỖI COPY] Không thể copy {event.src_path}: {e}")

    def on_modified(self, event):
        if not event.is_directory:
            pass # Ẩn bớt log thay đổi để dễ nhìn quá trình copy file mới

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[XÓA] File: {event.src_path}")
            
    def on_moved(self, event):
        if not event.is_directory:
            print(f"[ĐỔI TÊN/DI CHUYỂN] Từ {event.src_path} -> {event.dest_path}")

def start_monitoring():
    # Kiểm tra và tạo thư mục nếu chưa tồn tại
    if not os.path.exists(WATCH_DIRECTORY):
        print(f"[LỖI] Không tìm thấy thư mục gốc: {WATCH_DIRECTORY}")
        return
        
    if not os.path.exists(TMP_DIRECTORY):
        os.makedirs(TMP_DIRECTORY)
        print(f"[HỆ THỐNG] Đã tạo thư mục đích: {TMP_DIRECTORY}")

    event_handler = DirectoryMonitorHandler()
    observer = Observer()
    
    observer.schedule(event_handler, WATCH_DIRECTORY, recursive=True)
    
    print("=" * 50)
    print(f"ĐANG THEO DÕI : {WATCH_DIRECTORY}")
    print(f"COPY ĐẾN      : {TMP_DIRECTORY}")
    print("Bấm Ctrl + C để thoát")
    print("=" * 50)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[HỆ THỐNG] Đã dừng theo dõi.")
    
    observer.join()

if __name__ == "__main__":
    start_monitoring()
