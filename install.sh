#!/bin/bash

set -e

echo "Starting CodeReviewAI Installation..."

# Ensure ~/.local/bin exists (standard directory for user binaries)
mkdir -p "$HOME/.local/bin"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found. Please install Python 3."
    exit 1
fi

echo "Creating an isolated virtual environment at ~/.code_review_ai_venv ..."
VENV_DIR="$HOME/.code_review_ai_venv"

# Create a fresh virtual environment
python3 -m venv "$VENV_DIR"

echo "Installing application and dependencies (this may take a minute)..."
"$VENV_DIR/bin/pip" install --upgrade pip --no-cache-dir
"$VENV_DIR/bin/pip" install . --no-cache-dir

echo "Creating global symlink in ~/.local/bin ..."
ln -sf "$VENV_DIR/bin/cr" "$HOME/.local/bin/cr"

echo "======================================================"
echo "Installation complete!"
echo "======================================================"
echo "You can now run 'cr' from any folder on your computer."
echo ""
echo "IMPORTANT: If you get a 'command not found' error, it means your local bin is not in your PATH."
echo "To fix it, run this command and then restart your terminal:"
echo '    echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc'
echo "    (Or ~/.zshrc if you use zsh)"
echo "======================================================"
