#!/data/data/com.termux/files/usr/bin/bash

# =========================================================
# CONFIG
# =========================================================

URL_REPO="https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/scripts/main.json"

SAVE_DIR="/storage/emulated/0/{path_autoexecute}"

# =========================================================
# APP CONFIG
# =========================================================

APP_NAMES=(
    "Arceus X"
    "Delta"
    "Codex"
)

APP_DIRS=(
    "/storage/emulated/0/ArceusX"
    "/storage/emulated/0/Delta"
    "/storage/emulated/0/Codex"
)

# =========================================================
# COLOR
# =========================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# =========================================================
# FUNCTIONS
# =========================================================

die() {
    echo
    echo -e "${RED}[!] $1${NC}"
    exit 1
}

# =========================================================
# HEADER
# =========================================================

clear

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}        CMSVA SCRIPT INSTALLER          ${NC}"
echo -e "${CYAN}========================================${NC}"
echo

# =========================================================
# CHECK COMMANDS
# =========================================================

echo -e "${YELLOW}[*] Đang kiểm tra thư viện...${NC}"

if ! command -v curl >/dev/null 2>&1; then
    pkg install curl -y || die "Không thể cài curl."
fi

if ! command -v jq >/dev/null 2>&1; then
    pkg install jq -y || die "Không thể cài jq."
fi

if ! command -v base64 >/dev/null 2>&1; then
    pkg install coreutils -y || die "Không thể cài coreutils."
fi

# =========================================================
# CHECK STORAGE
# =========================================================

if [ ! -d "/storage/emulated/0" ]; then
    echo -e "${RED}[!] Termux chưa có quyền bộ nhớ.${NC}"
    echo
    echo "Hãy chạy:"
    echo
    echo "termux-setup-storage"
    echo

    exit 1
fi

# =========================================================
# CREATE SAVE DIR
# =========================================================

mkdir -p "$SAVE_DIR" || die "Không thể tạo thư mục $SAVE_DIR"

# =========================================================
# DOWNLOAD JSON
# =========================================================

echo
echo -e "${YELLOW}[*] Đang tải danh sách script...${NC}"

JSON_DATA=$(
    curl -fsSL \
        --connect-timeout 10 \
        --max-time 20 \
        "$URL_REPO"
)

if [ $? -ne 0 ] || [ -z "$JSON_DATA" ]; then
    die "Không thể tải JSON."
fi

# =========================================================
# VALIDATE JSON
# =========================================================

if ! printf '%s' "$JSON_DATA" | jq empty >/dev/null 2>&1; then
    die "JSON không hợp lệ."
fi

SCRIPT_COUNT=$(printf '%s' "$JSON_DATA" | jq '.scripts | length')

if [ "$SCRIPT_COUNT" -eq 0 ]; then
    die "Không có script nào."
fi

# =========================================================
# SHOW SCRIPT LIST
# =========================================================

echo
echo -e "${GREEN}Danh sách script:${NC}"
echo

printf '%s' "$JSON_DATA" | jq -r '
.scripts[] |
"\(.id). \(.name)"
'

echo
echo -e "${CYAN}----------------------------------------${NC}"
echo

read -r -p "Bạn muốn cài script nào? Nhập ID: " SCRIPT_ID

# =========================================================
# VALIDATE ID
# =========================================================

if [[ ! "$SCRIPT_ID" =~ ^[0-9]+$ ]]; then
    die "ID không hợp lệ."
fi

SCRIPT_EXISTS=$(
    printf '%s' "$JSON_DATA" |
        jq \
            --argjson id "$SCRIPT_ID" \
            '[.scripts[] | select(.id == $id)] | length'
)

if [ "$SCRIPT_EXISTS" -eq 0 ]; then
    die "Script không tồn tại."
fi

# =========================================================
# GET SCRIPT INFO
# =========================================================

SCRIPT_NAME=$(
    printf '%s' "$JSON_DATA" |
        jq -r \
            --argjson id "$SCRIPT_ID" \
            '.scripts[] | select(.id == $id) | .name'
)

SCRIPT_BASE64=$(
    printf '%s' "$JSON_DATA" |
        jq -r \
            --argjson id "$SCRIPT_ID" \
            '.scripts[] | select(.id == $id) | .script'
)

ENV_KEY=$(
    printf '%s' "$JSON_DATA" |
        jq -r \
            --argjson id "$SCRIPT_ID" \
            '.scripts[] | select(.id == $id) | .env_key // ""'
)

USE_ENV_KEY=$(
    printf '%s' "$JSON_DATA" |
        jq -r \
            --argjson id "$SCRIPT_ID" \
            '.scripts[] | select(.id == $id) | .use_env_key // false'
)

# =========================================================
# CHECK DATA
# =========================================================

if [ -z "$SCRIPT_BASE64" ] || [ "$SCRIPT_BASE64" = "null" ]; then
    die "Script không có dữ liệu."
fi

echo
echo -e "${GREEN}[+] Đã chọn script:${NC}"
echo
echo "ID      : $SCRIPT_ID"
echo "Tên     : $SCRIPT_NAME"
echo "ENV Key : $ENV_KEY"
echo "Use ENV : $USE_ENV_KEY"

# =========================================================
# DECODE BASE64
# =========================================================

echo
echo -e "${YELLOW}[*] Đang giải mã script...${NC}"

TEMP_FILE=$(mktemp)

if [ -z "$TEMP_FILE" ]; then
    die "Không thể tạo file tạm."
fi

if ! printf '%s' "$SCRIPT_BASE64" | base64 -d > "$TEMP_FILE" 2>/dev/null; then
    rm -f "$TEMP_FILE"
    die "Base64 không hợp lệ."
fi

if [ ! -s "$TEMP_FILE" ]; then
    rm -f "$TEMP_FILE"
    die "Script sau khi giải mã bị rỗng."
fi

# =========================================================
# DELETE OLD TXT
# =========================================================

echo
echo -e "${YELLOW}[*] Đang xóa file .txt cũ...${NC}"

find "$SAVE_DIR" \
    -maxdepth 1 \
    -type f \
    -name "*.txt" \
    -delete

# =========================================================
# GENERATE RANDOM FILE NAME
# =========================================================

echo -e "${YELLOW}[*] Đang tạo file mới...${NC}"

while true; do

    RANDOM_NAME=$(
        tr -dc 'a-z' < /dev/urandom |
            head -c 5
    )

    if [ -z "$RANDOM_NAME" ]; then
        continue
    fi

    OUTPUT_FILE="$SAVE_DIR/${RANDOM_NAME}.txt"

    if [ ! -e "$OUTPUT_FILE" ]; then
        break
    fi

done

# =========================================================
# SAVE SCRIPT
# =========================================================

mv "$TEMP_FILE" "$OUTPUT_FILE" || die "Không thể tạo file script."

# =========================================================
# VERIFY OUTPUT
# =========================================================

if [ ! -f "$OUTPUT_FILE" ]; then
    die "Không tìm thấy file sau khi tạo."
fi

if [ ! -s "$OUTPUT_FILE" ]; then
    rm -f "$OUTPUT_FILE"
    die "File script bị rỗng."
fi

# =========================================================
# DONE
# =========================================================

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}              HOÀN TẤT                  ${NC}"
echo -e "${GREEN}========================================${NC}"
echo

echo -e "Script : ${CYAN}$SCRIPT_NAME${NC}"
echo -e "ID     : ${CYAN}$SCRIPT_ID${NC}"
echo -e "File   : ${CYAN}$OUTPUT_FILE${NC}"

if [ "$USE_ENV_KEY" = "true" ]; then
    echo -e "ENV    : ${CYAN}$ENV_KEY${NC}"
fi

echo
echo -e "${GREEN}[✓] Cài script thành công.${NC}"
echo
