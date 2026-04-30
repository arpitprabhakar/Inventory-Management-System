#!/bin/bash

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

print_step()  { echo -e "\n${CYAN}${BOLD}>> $1${RESET}"; }
print_ok()    { echo -e "${GREEN}[OK]${RESET} $1"; }
print_warn()  { echo -e "${YELLOW}[WARN]${RESET} $1"; }
print_error() { echo -e "${RED}[ERROR]${RESET} $1"; }

echo -e "${BOLD}"
echo "================================================="
echo "   Inventory Manager — Dependency Installer"
echo "================================================="
echo -e "${RESET}"


# ── 1. Check Python 3 ─────────────────────────────
print_step "Checking Python 3..."

if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version)
    print_ok "Found $PY_VERSION"
else
    print_error "Python 3 is not installed."
    echo ""
    echo "Install it from: https://www.python.org/downloads/"
    echo "Or via your package manager:"
    echo "  Ubuntu/Debian : sudo apt install python3"
    echo "  macOS (brew)  : brew install python3"
    echo "  Windows       : https://www.python.org/downloads/"
    exit 1
fi


# ── 2. Check pip ──────────────────────────────────
print_step "Checking pip..."

if command -v pip3 &>/dev/null; then
    print_ok "pip3 is available"
    PIP=pip3
elif command -v pip &>/dev/null; then
    print_ok "pip is available"
    PIP=pip
else
    print_warn "pip not found. Attempting to install via ensurepip..."
    python3 -m ensurepip --upgrade
    PIP="python3 -m pip"
fi


# ── 3. Tkinter ────────────────────────────────────
print_step "Checking tkinter..."

if python3 -c "import tkinter" &>/dev/null; then
    print_ok "tkinter is already installed"
else
    print_warn "tkinter not found. Attempting to install..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &>/dev/null; then
            sudo apt update -y && sudo apt install -y python3-tk
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3-tkinter
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm tk
        else
            print_error "Could not detect package manager. Install tkinter manually:"
            echo "  Ubuntu/Debian : sudo apt install python3-tk"
            echo "  Fedora        : sudo dnf install python3-tkinter"
            echo "  Arch          : sudo pacman -S tk"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &>/dev/null; then
            brew install python-tk
        else
            print_error "Homebrew not found. Install it from https://brew.sh then run: brew install python-tk"
            exit 1
        fi
    elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32" ]]; then
        print_warn "Windows detected."
        echo "  tkinter comes bundled with the official Python installer."
        echo "  If it's missing, re-run the Python installer from https://www.python.org"
        echo "  and make sure 'tcl/tk and IDLE' is checked during installation."
    else
        print_error "Unknown OS. Install tkinter manually for your platform."
        exit 1
    fi

    if python3 -c "import tkinter" &>/dev/null; then
        print_ok "tkinter installed successfully"
    else
        print_error "tkinter installation failed. Please install it manually."
        exit 1
    fi
fi


# ── 4. pip packages ───────────────────────────────
print_step "Installing Python packages (pandas, numpy)..."

$PIP install --upgrade pip --quiet
$PIP install pandas numpy

print_ok "pandas and numpy installed"


# ── 5. Verify all imports ─────────────────────────
print_step "Verifying all imports..."

python3 - <<'EOF'
import sys

modules = {
    "tkinter":  "tkinter",
    "pandas":   "pandas",
    "numpy":    "numpy",
    "os":       "os",
    "csv":      "csv",
    "datetime": "datetime",
}

all_ok = True
for name, mod in modules.items():
    try:
        __import__(mod)
        print(f"  \033[0;32m[OK]\033[0m   {name}")
    except ImportError as e:
        print(f"  \033[0;31m[FAIL]\033[0m {name} — {e}")
        all_ok = False

if not all_ok:
    print("\n\033[0;31mOne or more imports failed. Please check the errors above.\033[0m")
    sys.exit(1)
EOF

print_ok "All imports verified"


# ── Done ──────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}================================================="
echo "   Setup complete! You're good to go."
echo -e "=================================================${RESET}"
echo ""
echo "  Run the app with:"
echo -e "  ${BOLD}python3 inventory_manager.py${RESET}"
echo ""
