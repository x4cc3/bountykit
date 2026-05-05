#!/bin/bash
# =============================================================================
# Bug Bounty Tool Installer
# Prefers native package managers and never auto-installs Homebrew.
# Usage: core/install.sh [--yes] [--with-brew]
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

AUTO_YES=false
ALLOW_BREW=false
SUBFINDER_VERSION="v2.6.9"
HTTPX_VERSION="v1.6.10"
NUCLEI_VERSION="v3.3.8"
AMASS_VERSION="v4.2.0"
GAU_VERSION="v2.2.4"
DALFOX_VERSION="v2.11.0"
SUBJACK_VERSION="v1.2.0"

log_ok()   { echo -e "${GREEN}[+]${NC} $1"; }
log_err()  { echo -e "${RED}[-]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_info() { echo -e "${CYAN}[*]${NC} $1"; }

usage() {
    cat <<'EOF'
Usage: core/install.sh [--yes] [--with-brew]

Options:
  --yes        Non-interactive mode for native package manager installs
  --with-brew  Allow using Homebrew if it is already installed
  -h, --help   Show this help

Notes:
  - This script never installs Homebrew for you.
  - Native package-manager support: apt-get, dnf, pacman, apk, zypper.
  - Go-based tools are installed with `go install` when Go is available.
EOF
}

confirm() {
    local prompt="$1"
    if [ "$AUTO_YES" = true ]; then
        return 0
    fi
    read -r -p "$prompt [y/N] " reply
    case "$reply" in
        y|Y|yes|YES) return 0 ;;
        *) return 1 ;;
    esac
}

have_cmd() {
    command -v "$1" >/dev/null 2>&1
}

detect_package_manager() {
    if have_cmd apt-get; then
        echo "apt"
    elif have_cmd dnf; then
        echo "dnf"
    elif have_cmd pacman; then
        echo "pacman"
    elif have_cmd apk; then
        echo "apk"
    elif have_cmd zypper; then
        echo "zypper"
    elif have_cmd brew && [ "$ALLOW_BREW" = true ]; then
        echo "brew"
    else
        echo "none"
    fi
}

native_pkg_name() {
    local manager="$1"
    local tool="$2"

    case "$manager:$tool" in
        apt:go) echo "golang-go" ;;
        dnf:go) echo "golang" ;;
        pacman:go) echo "go" ;;
        apk:go) echo "go" ;;
        zypper:go) echo "go" ;;
        brew:go) echo "go" ;;
        *:ffuf) echo "ffuf" ;;
        *:nmap) echo "nmap" ;;
        *) return 1 ;;
    esac
}

install_with_apt() {
    local packages=("$@")
    if [ ${#packages[@]} -eq 0 ]; then
        return 0
    fi

    log_info "Using apt-get for native packages: ${packages[*]}"
    if ! confirm "Install native packages with sudo apt-get?"; then
        log_warn "Skipped apt-get install"
        return 0
    fi

    sudo apt-get update
    sudo apt-get install -y "${packages[@]}"
}

install_with_dnf() {
    local packages=("$@")
    if [ ${#packages[@]} -eq 0 ]; then
        return 0
    fi

    log_info "Using dnf for native packages: ${packages[*]}"
    if ! confirm "Install native packages with sudo dnf?"; then
        log_warn "Skipped dnf install"
        return 0
    fi

    sudo dnf install -y "${packages[@]}"
}

install_with_pacman() {
    local packages=("$@")
    if [ ${#packages[@]} -eq 0 ]; then
        return 0
    fi

    log_info "Using pacman for native packages: ${packages[*]}"
    if ! confirm "Install native packages with sudo pacman?"; then
        log_warn "Skipped pacman install"
        return 0
    fi

    sudo pacman -Sy --needed --noconfirm "${packages[@]}"
}

install_with_apk() {
    local packages=("$@")
    if [ ${#packages[@]} -eq 0 ]; then
        return 0
    fi

    log_info "Using apk for native packages: ${packages[*]}"
    if ! confirm "Install native packages with sudo apk?"; then
        log_warn "Skipped apk install"
        return 0
    fi

    sudo apk add "${packages[@]}"
}

install_with_zypper() {
    local packages=("$@")
    if [ ${#packages[@]} -eq 0 ]; then
        return 0
    fi

    log_info "Using zypper for native packages: ${packages[*]}"
    if ! confirm "Install native packages with sudo zypper?"; then
        log_warn "Skipped zypper install"
        return 0
    fi

    sudo zypper install -y "${packages[@]}"
}

install_with_brew() {
    local packages=("$@")
    if [ ${#packages[@]} -eq 0 ]; then
        return 0
    fi

    log_info "Using existing Homebrew for native packages: ${packages[*]}"
    brew install "${packages[@]}"
}

install_go_tool() {
    local tool_name="$1"
    local tool_path="$2"

    if have_cmd "$tool_name"; then
        log_ok "$tool_name already installed ($(command -v "$tool_name"))"
        return 0
    fi

    if ! have_cmd go; then
        log_warn "Skipping $tool_name because Go is not installed"
        return 0
    fi

    log_info "Installing $tool_name via go install"
    if go install "$tool_path"; then
        log_ok "$tool_name installed successfully"
    else
        log_err "$tool_name failed to install"
    fi
}

while [ $# -gt 0 ]; do
    case "$1" in
        --yes)
            AUTO_YES=true
            shift
            ;;
        --with-brew)
            ALLOW_BREW=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            exit 1
            ;;
    esac
done

install_native_packages() {
    local manager="$1"
    shift
    local packages=("$@")

    case "$manager" in
        apt) install_with_apt "${packages[@]}" ;;
        dnf) install_with_dnf "${packages[@]}" ;;
        pacman) install_with_pacman "${packages[@]}" ;;
        apk) install_with_apk "${packages[@]}" ;;
        zypper) install_with_zypper "${packages[@]}" ;;
        brew) install_with_brew "${packages[@]}" ;;
        none)
            log_warn "No supported native package manager detected"
            ;;
    esac
}

build_native_package_list() {
    local manager="$1"
    shift
    local requested_tools=("$@")
    local tool package

    NATIVE_PACKAGES=()
    for tool in "${requested_tools[@]}"; do
        if have_cmd "$tool"; then
            log_ok "$tool already installed ($(command -v "$tool"))"
            continue
        fi

        if package="$(native_pkg_name "$manager" "$tool" 2>/dev/null)"; then
            NATIVE_PACKAGES+=("$package")
        else
            log_warn "No native package mapping for $tool on $manager"
        fi
    done
}

echo "============================================="
echo "  Bug Bounty Tool Installer"
echo "============================================="

OS="$(uname -s)"
PKG_MANAGER="$(detect_package_manager)"

log_info "Detected OS: $OS"
log_info "Detected package manager: $PKG_MANAGER"

NATIVE_TOOL_TARGETS=(go nmap ffuf)

if [ "$PKG_MANAGER" = "none" ]; then
    log_warn "No supported native package manager detected"
    log_warn "Install these manually if missing: go, nmap, ffuf"
    log_warn "Re-run with --with-brew only if you already use Homebrew"
else
    build_native_package_list "$PKG_MANAGER" "${NATIVE_TOOL_TARGETS[@]}"
    install_native_packages "$PKG_MANAGER" "${NATIVE_PACKAGES[@]}"
fi

echo ""
log_info "Installing tools via Go when available"

install_go_tool "subfinder" "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@$SUBFINDER_VERSION"
install_go_tool "httpx" "github.com/projectdiscovery/httpx/cmd/httpx@$HTTPX_VERSION"
install_go_tool "nuclei" "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@$NUCLEI_VERSION"
install_go_tool "amass" "github.com/owasp-amass/amass/v4/cmd/amass@$AMASS_VERSION"
install_go_tool "gau" "github.com/lc/gau/v2/cmd/gau@$GAU_VERSION"
install_go_tool "dalfox" "github.com/hahwul/dalfox/v2@$DALFOX_VERSION"
install_go_tool "subjack" "github.com/haccer/subjack@$SUBJACK_VERSION"

echo ""
log_info "Updating nuclei templates"
if have_cmd nuclei; then
    nuclei -update-templates 2>/dev/null || true
    log_ok "Nuclei templates updated"
else
    log_warn "Skipping nuclei template update because nuclei is not installed"
fi

GOPATH_VALUE="${GOPATH:-$HOME/go}"
if [ -d "$GOPATH_VALUE/bin" ] && [[ ":$PATH:" != *":$GOPATH_VALUE/bin:"* ]]; then
    log_warn "Add Go bin to your PATH:"
    echo "    export PATH=\$PATH:$GOPATH_VALUE/bin"
fi

echo ""
echo "============================================="
echo "[*] Installation Verification"
echo "============================================="

ALL_CORE=(subfinder httpx nuclei ffuf nmap amass gau dalfox subjack go)
INSTALLED=0
MISSING=0

for tool in "${ALL_CORE[@]}"; do
    if have_cmd "$tool"; then
        log_ok "$tool: $(command -v "$tool")"
        INSTALLED=$((INSTALLED + 1))
    else
        log_err "$tool: NOT FOUND"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
echo "============================================="
echo "  Installed: $INSTALLED / ${#ALL_CORE[@]}"
[ "$MISSING" -gt 0 ] && echo "  Missing: $MISSING (install manually or re-run after adding prerequisites)"
echo "============================================="
