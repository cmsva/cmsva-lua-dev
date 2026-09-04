# Hướng Dẫn Cài Đặt CMSVA Trên Termux

Tài liệu này dành cho người mới, chỉ cần làm lần lượt từng bước.

---

## 1. Cài Termux

Nên dùng bản Termux mới.

Sau khi cài xong, mở Termux lên.

---

## 2. Cấp Quyền Bộ Nhớ

Chạy lệnh:

```bash
termux-setup-storage
```

Android sẽ hỏi quyền truy cập bộ nhớ.

Chọn:

```text
Cho phép / Allow
```

Nếu không hiện thông báo cấp quyền, hãy vào:

```text
Cài đặt Android
→ Ứng dụng
→ Termux
→ Quyền
→ Cho phép truy cập tệp / bộ nhớ
```

---

## 3. Cài Đặt Tự Động

Chạy 1 dòng sau:

```bash
termux-setup-storage && pkg update -y && pkg install -y curl && curl -fsSL https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/install.sh | bash
```

Installer sẽ tự:

```text
Cài package cần thiết
↓
Cài Python
↓
Cài curl
↓
Cài jq
↓
Cài coreutils
↓
Tạo thư mục CMSVA
↓
Tải main.sh
↓
Tải help.txt / help.md
↓
Tải update.py
↓
Thiết lập autoexecute
↓
Hoàn tất
```

---

## 4. Nhập Đường Dẫn Autoexecute

Khi Termux hỏi:

```text
Đường dẫn autoexecute:
```

hãy nhập đúng đường dẫn thư mục autoexecute của app.

Ví dụ:

```text
Delta/autoexecute
```

Hoặc nhập full path:

```text
/storage/emulated/0/Delta/autoexecute
```

Sau đó nhấn:

```text
Enter
```

Hệ thống sẽ tự dùng đường dẫn này cho `main.sh`.

---

## 5. Thư Mục Cài Đặt

Thông thường project sẽ nằm tại:

```text
/storage/emulated/0/python
```

Nếu thư mục `python` đã tồn tại thì có thể dùng:

```text
/storage/emulated/0/python_cmsva
```

Kiểm tra:

```bash
ls /storage/emulated/0/python
```

Hoặc:

```bash
ls /storage/emulated/0/python_cmsva
```

---

## 6. Vào Thư Mục Project

Nếu project nằm ở `python`:

```bash
cd /storage/emulated/0/python
```

Nếu nằm ở `python_cmsva`:

```bash
cd /storage/emulated/0/python_cmsva
```

---

## 7. Chạy Main

File chính hiện tại là Bash:

```text
main.sh
```

Chạy:

```bash
bash main.sh
```

Không chạy:

```bash
python main.sh
```

---

## 8. Kiểm Tra Lỗi Cú Pháp Trước Khi Chạy

Có thể kiểm tra bằng:

```bash
bash -n main.sh
```

Nếu không hiện gì thì cú pháp Bash hợp lệ.

Sau đó chạy:

```bash
bash main.sh
```

---

## 9. Chọn Script

Khi chạy `main.sh`, hệ thống sẽ tải danh sách script từ GitHub.

Ví dụ:

```text
Danh sách script:

1. Script A
2. Script B
3. Script C

Bạn muốn cài script nào? Nhập ID:
```

Nếu muốn chọn script số 1:

```text
1
```

rồi nhấn Enter.

Nếu ID không tồn tại:

```text
[!] Script không tồn tại.
```

---

## 10. File Script Được Lưu Ở Đâu?

Sau khi chọn script thành công, hệ thống sẽ:

```text
Tải dữ liệu JSON
↓
Lấy script Base64
↓
Giải mã Base64
↓
Xóa file .txt cũ trong thư mục autoexecute
↓
Tạo file .txt mới
```

Tên file là 5 ký tự chữ thường ngẫu nhiên.

Ví dụ:

```text
abcde.txt
```

Đường dẫn có thể là:

```text
/storage/emulated/0/Delta/autoexecute/abcde.txt
```

---

## 11. Cập Nhật Phiên Bản Mới

Updater là:

```text
update.py
```

Nếu project nằm tại:

```text
/storage/emulated/0/python
```

chạy:

```bash
cd /storage/emulated/0/python && python update.py
```

Nếu nằm tại:

```text
/storage/emulated/0/python_cmsva
```

chạy:

```bash
cd /storage/emulated/0/python_cmsva && python update.py
```

Updater sẽ tự:

```text
Đọc cấu hình
↓
Nhớ path autoexecute
↓
Tải main.sh mới
↓
Tải help mới
↓
So sánh phiên bản
↓
Backup file cũ
↓
Cập nhật file mới
```

---

## 12. Nếu Không Có cmsva_config.json

Nếu gặp lỗi:

```text
FileNotFoundError: cmsva_config.json
```

thì có thể tải lại `main.sh` và nhập đường dẫn thủ công bằng lệnh:

```bash
cd /storage/emulated/0/python && curl -fsSL "https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/scripts/main.sh" -o main.sh.tmp && bash -n main.sh.tmp && read -r -p "Nhập đường dẫn autoexecute, ví dụ Delta/autoexecute: " P && P="${P#/storage/emulated/0/}" && sed "s|{path_autoexecute}|$P|g" main.sh.tmp > main.sh && rm -f main.sh.tmp && chmod +x main.sh && bash -n main.sh && bash main.sh
```

Khi hỏi:

```text
Nhập đường dẫn autoexecute, ví dụ Delta/autoexecute:
```

nhập:

```text
Delta/autoexecute
```

---

## 13. Lỗi Python SyntaxError Khi Chạy main.sh

Nếu thấy kiểu lỗi:

```text
SyntaxError
```

và bạn đã chạy:

```bash
python main.sh
```

thì đây là sai cách.

`main.sh` là Bash.

Phải chạy:

```bash
bash main.sh
```

---

## 14. Lỗi unexpected EOF

Nếu thấy:

```text
unexpected EOF while looking for matching
```

thường là file bị:

```text
Thiếu dấu '
Thiếu dấu "
Thiếu )
Thiếu fi
Thiếu done
```

Kiểm tra bằng:

```bash
bash -n main.sh
```

Nếu lỗi do file tải cũ, tải lại:

```bash
cd /storage/emulated/0/python
curl -fsSL "https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/scripts/main.sh" -o main.sh
chmod +x main.sh
bash -n main.sh
```

Nếu không còn lỗi:

```bash
bash main.sh
```

---

## 15. Lỗi curl Không Tồn Tại

Nếu thấy:

```text
curl: command not found
```

chạy:

```bash
pkg update -y
pkg install curl -y
```

---

## 16. Lỗi jq Không Tồn Tại

Nếu thấy:

```text
jq: command not found
```

chạy:

```bash
pkg install jq -y
```

---

## 17. Lỗi base64 Không Tồn Tại

Chạy:

```bash
pkg install coreutils -y
```

---

## 18. Lỗi Python Không Tồn Tại

Nếu:

```text
python: command not found
```

chạy:

```bash
pkg install python -y
```

Kiểm tra:

```bash
python --version
```

---

## 19. Lỗi Không Có Quyền Bộ Nhớ

Nếu không truy cập được:

```text
/storage/emulated/0
```

chạy lại:

```bash
termux-setup-storage
```

Sau đó cấp quyền cho Termux.

---

## 20. Xem File Trong Thư Mục

Dùng:

```bash
ls
```

Xem chi tiết:

```bash
ls -la
```

Ví dụ:

```bash
cd /storage/emulated/0/python
ls -la
```

---

## 21. Xem Nội Dung Help

Nếu dùng `help.txt`:

```bash
cat help.txt
```

Nếu dùng `help.md`:

```bash
cat help.md
```

---

## 22. Xóa Màn Hình Termux

```bash
clear
```

---

## 23. Cập Nhật Package Termux

```bash
pkg update -y && pkg upgrade -y
```

---

## 24. Quick Install

Cho người muốn cài nhanh:

```bash
termux-setup-storage && pkg update -y && pkg install -y curl && curl -fsSL https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/install.sh | bash
```

---

## 25. Quick Run

```bash
cd /storage/emulated/0/python && bash main.sh
```

---

## 26. Quick Update

```bash
cd /storage/emulated/0/python && python update.py
```

---

## Ghi Chú

- `main.sh` là file Bash.
- `update.py` là file Python.
- Không chạy `main.sh` bằng Python.
- Không xóa `cmsva_config.json` nếu muốn updater nhớ cấu hình.
- Luôn kiểm tra đường dẫn autoexecute trước khi cài.
- Nếu đổi app hoặc đổi đường dẫn autoexecute thì cần thiết lập lại.
- Không tắt mạng trong lúc tải file từ GitHub.
- Nếu gặp lỗi Bash, dùng `bash -n main.sh` để kiểm tra cú pháp.
- Nếu file local bị lỗi, nên tải lại bản mới nhất từ GitHub.

---

## Lệnh Quan Trọng Nhất

Cài:

```bash
termux-setup-storage && pkg update -y && pkg install -y curl && curl -fsSL https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/install.sh | bash
```

Chạy:

```bash
cd /storage/emulated/0/python && bash main.sh
```

Cập nhật:

```bash
cd /storage/emulated/0/python && python update.py
```
