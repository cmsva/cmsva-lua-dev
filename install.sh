#!/data/data/com.termux/files/usr/bin/bash

# =========================================================
# CMSVA SCRIPT INSTALLER
# =========================================================

URL_REPO="https://raw.githubusercontent.com/cmsva/cmsva-lua-dev/main/scripts.json"
SAVE_DIR="/storage/emulated/0/xxx"

# =========================================================
# APP CONFIG
# Sửa tên app và đường dẫn tại đây
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
# COLORS
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

need_cmd() {
    command -v "$1" >/dev/null 2>&1
}

install_dependencies() {
    echo -e "${YELLOW}[*] Kiểm tra thư viện...${NC}"

    if ! need_cmd curl || ! need_cmd jq || ! need_cmd base64; then
        pkg update -y
        pkg install -y curl jq coreutils
    fi
}

check_storage() {
    if [ ! -d "/storage/emulated/0" ]; then
        die "Termux chưa có quyền bộ nhớ. Hãy chạy: termux-setup-storage"
    fi

    mkdir -p "$SAVE_DIR" || die "Không thể tạo thư mục: $SAVE_DIR"
}

download_json() {
    echo -e "${YELLOW}[*] Đang tải danh sách script...${NC}"

    JSON_DATA="$(curl -fsSL --connect-timeout 10 --max-time 20 "$URL_REPO")" \
        || die "Không thể tải file JSON."

    [ -n "$JSON_DATA" ] || die "JSON trả về rỗng."

    printf '%s' "$JSON_DATA" | jq empty >/dev/null 2>&1 \
        || die "File JSON không hợp lệ."

    SCRIPT_COUNT="$(printf '%s' "$JSON_DATA" | jq '.scripts | length')"

    [ "$SCRIPT_COUNT" -gt 0 ] || die "Không có script nào trong JSON."
}

show_scripts() {
    echo
    echo -e "${GREEN}Danh sách script:${NC}"
    echo

    printf '%s' "$JSON_DATA" | jq -r '
        .scripts[] |
        "\(.id). \(.name)"
    '

    echo
    echo -e "${CYAN}----------------------------------------${NC}"
}

select_script() {
    read -r -p "Bạn muốn cài script nào? Nhập ID: " SCRIPT_ID

    [[ "$SCRIPT_ID" =~ ^[0-9]+$ ]] \
        || die "ID không hợp lệ."

    SCRIPT_EXISTS="$(printf '%s' "$JSON_DATA" | jq \
        --argjson id "$SCRIPT_ID" \
        '[.scripts[] | select(.id == $id)] | length'
    )"

    [ "$SCRIPT_EXISTS" -gt 0 ] \
        || die "Script không tồn tại."

    SCRIPT_NAME="$(printf '%s' "$JSON_DATA" | jq -r \
        --argjson id "$SCRIPT_ID" \
        '.scripts[] | select(.id == $id) | .name'
    )"

    SCRIPT_BASE64="$(printf '%s' "$JSON_DATA" | jq -r \
        --argjson id "$SCRIPT_ID" \
        '.scripts[] | select(.id == $id) | .script'
    )"

    ENV_KEY="$(printf '%s' "$JSON_DATA" | jq -r \
        --argjson id "$SCRIPT_ID" \
        '.scripts[] | select(.id == $id) | .env_key // ""'
    )"

    USE_ENV_KEY="$(printf '%s' "$JSON_DATA" | jq -r \
        --argjson id "$SCRIPT_ID" \
        '.scripts[] | select(.id == $id) | .use_env_key // false'
    )"

    [ -n "$SCRIPT_BASE64" ] && [ "$SCRIPT_BASE64" != "null" ] \
        || die "Script không có dữ liệu."

    echo
    echo -e "${GREEN}[+] Đã chọn:${NC}"
    echo "ID      : $SCRIPT_ID"
    echo "Tên     : $SCRIPT_NAME"
    echo "ENV Key : $ENV_KEY"
    echo "Use ENV : $USE_ENV_KEY"
}

decode_script() {
    TEMP_FILE="$(mktemp)" || die "Không thể tạo file tạm."

    if ! printf '%s' "$SCRIPT_BASE64" | base64 -d > "$TEMP_FILE" 2>/dev/null; then
        rm -f "$TEMP_FILE"
        die "Dữ liệu Base64 không hợp lệ."
    fi

    if [ ! -s "$TEMP_FILE" ]; then
        rm -f "$TEMP_FILE"
        die "Nội dung sau khi giải mã bị rỗng."
    fi
}

create_output_file() {
    echo
    echo -e "${YELLOW}[*] Đang xóa file .txt cũ trong thư mục chính...${NC}"

    find "$SAVE_DIR" \
        -maxdepth 1 \
        -type f \
        -name "*.txt" \
        -delete

    while true; do
        RANDOM_NAME="$(tr -dc 'a-z' < /dev/urandom | head -c 5)"
        [ -n "$RANDOM_NAME" ] || continue

        OUTPUT_FILE="$SAVE_DIR/${RANDOM_NAME}.txt"

        if [ ! -e "$OUTPUT_FILE" ]; then
            break
        fi
    done

    mv "$TEMP_FILE" "$OUTPUT_FILE" \
        || die "Không thể tạo file script."

    echo
    echo -e "${GREEN}[+] Đã tạo:${NC}"
    echo "$OUTPUT_FILE"
}

show_apps() {
    echo
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}              CHỌN APP                  ${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo
    echo "Bạn muốn thêm script vào app nào?"
    echo

    for i in "${!APP_NAMES[@]}"; do
        echo "$((i + 1)). ${APP_NAMES[$i]}"
    done

    echo
}

select_app() {
    read -r -p "Nhập số app: " APP_SELECT

    [[ "$APP_SELECT" =~ ^[0-9]+$ ]] \
        || die "Số app không hợp lệ."

    APP_INDEX=$((APP_SELECT - 1))

    if [ "$APP_INDEX" -lt 0 ] || [ "$APP_INDEX" -ge "${#APP_NAMES[@]}" ]; then
        die "App không tồn tại."
    fi

    SELECTED_APP="${APP_NAMES[$APP_INDEX]}"
    SELECTED_DIR="${APP_DIRS[$APP_INDEX]}"
}

copy_to_app() {
    mkdir -p "$SELECTED_DIR" \
        || die "Không thể tạo thư mục app: $SELECTED_DIR"

    echo
    echo -e "${YELLOW}[*] Đang xóa file .txt cũ trong ${SELECTED_APP}...${NC}"

    find "$SELECTED_DIR" \
        -maxdepth 1 \
        -type f \
        -name "*.txt" \
        -delete

    APP_OUTPUT="$SELECTED_DIR/${RANDOM_NAME}.txt"

    cp "$OUTPUT_FILE" "$APP_OUTPUT" \
        || die "Không thể copy file vào app."
}

finish() {
    echo
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}               HOÀN TẤT                 ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo -e "Script : ${CYAN}$SCRIPT_NAME${NC}"
    echo -e "ID     : ${CYAN}$SCRIPT_ID${NC}"
    echo -e "App    : ${CYAN}$SELECTED_APP${NC}"
    echo
    echo "File gốc:"
    echo "$OUTPUT_FILE"
    echo
    echo "File trong app:"
    echo "$APP_OUTPUT"
    echo
    echo -e "${GREEN}[✓] Cài đặt thành công.${NC}"
}

# =========================================================
# MAIN
# =========================================================

clear

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}        CMSVA SCRIPT INSTALLER          ${NC}"
echo -e "${CYAN}========================================${NC}"
echo

install_dependencies
check_storage
download_json
show_scripts
select_script
decode_script
create_output_file
show_apps
select_app
copy_to_app
finish
