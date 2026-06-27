#!/bin/bash

set -e

echo "Starting CodeReviewAI Uninstallation..."

# Remove the global symlink
if [ -L "$HOME/.local/bin/cr" ]; then
    echo "Removing global symlink from ~/.local/bin ..."
    rm "$HOME/.local/bin/cr"
elif [ -f "$HOME/.local/bin/cr" ]; then
    echo "Removing global binary from ~/.local/bin ..."
    rm "$HOME/.local/bin/cr"
fi

# Remove the isolated virtual environment
VENV_DIR="$HOME/.code_review_ai_venv"
if [ -d "$VENV_DIR" ]; then
    echo "Removing isolated virtual environment at $VENV_DIR ..."
    rm -rf "$VENV_DIR"
fi

# Ask about config file
CONFIG_FILE="$HOME/.code_review_ai.env"
if [ -f "$CONFIG_FILE" ]; then
    read -p "Do you also want to delete your saved API keys at $CONFIG_FILE? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$CONFIG_FILE"
        echo "Deleted config file."
    else
        echo "Kept config file intact."
    fi
fi

echo "======================================================"
echo "Uninstallation complete!"
echo "======================================================"
