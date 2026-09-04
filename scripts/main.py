#!/data/data/com.termux/files/usr/bin/bash

# =========================================================
# CONFIG
# =========================================================

URL_REPO="https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/refs/heads/main/scripts/main.json"

SAVE_DIR="/storage/emulated/0/{thư mục chạy script tự động}"

# =========================================================
# APP CONFIG
# Tên app và thư mục mà bạn muốn copy file vào
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

clear

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}        CMSVA SCRIPT INSTALLER          ${NC}"
echo -e "${CYAN}========================================${NC}"
echo

# =========================================================
# CHECK COMMANDS
# =========================================================

if ! command -v curl >/dev/null 2>&1; then
    pkg install curl -y
fi

if ! command -v jq >/dev/null 2>&1; then
    pkg install jq -y
fi

if ! command -v base64 >/dev/null 2>&1; then
    pkg install coreutils -y
fi

# =========================================================
# CHECK STORAGE
# =========================================================

if [ ! -d "/storage/emulated/0" ]; then

    echo -e "${RED}[!] Termux chưa có quyền bộ nhớ.${NC}"
    echo
    echo "Chạy:"
    echo
    echo "termux-setup-storage"

    exit 1
fi

mkdir -p "$SAVE_DIR"

# =========================================================
# DOWNLOAD JSON
# =========================================================

echo -e "${YELLOW}[*] Đang tải danh sách script...${NC}"

JSON_DATA=$(curl -fsSL \
    --connect-timeout 10 \
    --max-time 20 \
    "$URL_REPO"
)

if [ $? -ne 0 ] || [ -z "$JSON_DATA" ]; then

    echo -e "${RED}[!] Không thể tải JSON.${NC}"
    exit 1

fi

# =========================================================
# VALIDATE JSON
# =========================================================

if ! echo "$JSON_DATA" | jq empty >/dev/null 2>&1; then

    echo -e "${RED}[!] JSON không hợp lệ.${NC}"
    exit 1

fi

SCRIPT_COUNT=$(echo "$JSON_DATA" | jq '.scripts | length')

if [ "$SCRIPT_COUNT" -eq 0 ]; then

    echo -e "${RED}[!] Không có script.${NC}"
    exit 1

fi

# =========================================================
# SHOW SCRIPT LIST
# =========================================================

echo
echo -e "${GREEN}Danh sách script:${NC}"
echo

echo "$JSON_DATA" | jq -r '
.scripts[] |
"\(.id). \(.name)"
'

echo
echo -e "${CYAN}----------------------------------------${NC}"

read -r -p "Bạn muốn cài script nào? Nhập ID: " SCRIPT_ID

# =========================================================
# VALIDATE ID
# =========================================================

if [[ ! "$SCRIPT_ID" =~ ^[0-9]+$ ]]; then

    echo
    echo -e "${RED}[!] ID không hợp lệ.${NC}"
    exit 1

fi

SCRIPT_EXISTS=$(echo "$JSON_DATA" | jq \
    --argjson id "$SCRIPT_ID" \
    '[.scripts[] | select(.id == $id)] | length'
)

if [ "$SCRIPT_EXISTS" -eq 0 ]; then

    echo
    echo -e "${RED}[!] Script không tồn tại.${NC}"
    exit 1

fi

# =========================================================
# GET SCRIPT INFO
# =========================================================

SCRIPT_NAME=$(echo "$JSON_DATA" | jq -r \
    --argjson id "$SCRIPT_ID" \
    '.scripts[] | select(.id == $id) | .name'
)

SCRIPT_BASE64=$(echo "$JSON_DATA" | jq -r \
    --argjson id "$SCRIPT_ID" \
    '.scripts[] | select(.id == $id) | .script'
)

ENV_KEY=$(echo "$JSON_DATA" | jq -r \
    --argjson id "$SCRIPT_ID" \
    '.scripts[] | select(.id == $id) | .env_key
