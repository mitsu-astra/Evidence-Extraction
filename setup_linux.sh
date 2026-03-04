#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  FORENSIC PLATFORM — WSL/Linux Setup Script
#  Called automatically by INSTALL.bat — do not run manually unless needed
# ─────────────────────────────────────────────────────────────────────────────

set -e  # exit on any error

# Colour helpers
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   FORENSIC PLATFORM — Linux / WSL Environment Setup    ${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""

# ── Resolve script location ──────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo -e "${GREEN}[OK]${NC} Working directory: $SCRIPT_DIR"
echo ""

# ── Step 1: System packages ──────────────────────────────────────────────────
echo -e "${YELLOW}[1/5] Updating apt and installing system packages...${NC}"
sudo apt-get update -y
sudo apt-get upgrade -y

sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    libtsk-dev \
    libewf-dev \
    build-essential \
    git

echo -e "${GREEN}[OK]${NC} System packages installed."
echo ""

# ── Step 2: Create virtual environment ──────────────────────────────────────
echo -e "${YELLOW}[2/5] Setting up Python 3.11 virtual environment (venv_linux)...${NC}"
if [ -d "venv_linux" ]; then
    echo -e "${GREEN}[OK]${NC} venv_linux already exists — skipping creation."
else
    python3.11 -m venv venv_linux
    echo -e "${GREEN}[OK]${NC} venv_linux created."
fi
echo ""

# ── Step 3: Activate venv ────────────────────────────────────────────────────
echo -e "${YELLOW}[3/5] Activating virtual environment...${NC}"
source venv_linux/bin/activate
echo -e "${GREEN}[OK]${NC} venv_linux activated. Python: $(python --version)"
echo ""

# ── Step 4: Install pip requirements ────────────────────────────────────────
echo -e "${YELLOW}[4/5] Installing Python packages from requirements_web.txt...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements_web.txt
echo -e "${GREEN}[OK]${NC} requirements_web.txt packages installed."
echo ""

# ── Step 5: Install pytsk3 and pyewf ────────────────────────────────────────
echo -e "${YELLOW}[5/5] Installing pytsk3 (Sleuth Kit) and pyewf (E01 support)...${NC}"
pip install pytsk3
pip install pyewf
echo -e "${GREEN}[OK]${NC} pytsk3 and pyewf installed."
echo ""

# ── Done ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Linux setup complete! All dependencies are ready.${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  You can now run the app by double-clicking  ${YELLOW}START_WEB_APP.bat${NC}"
echo ""
