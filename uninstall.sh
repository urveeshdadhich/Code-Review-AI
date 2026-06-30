#!/bin/bash
echo "Uninstalling Java CodeReviewAI..."

# Remove the executable wrapper
BIN_FILE="$HOME/.local/bin/cr"
if [ -f "$BIN_FILE" ]; then
    rm "$BIN_FILE"
    echo "Removed executable: $BIN_FILE"
else
    echo "Executable $BIN_FILE not found."
fi

# Remove the JAR and its directory
INSTALL_DIR="$HOME/.code_review_ai_java"
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "Removed app directory: $INSTALL_DIR"
else
    echo "App directory $INSTALL_DIR not found."
fi

ENV_FILE="$HOME/.code_review_ai.env"
if [ -f "$ENV_FILE" ]; then
    read -p "Do you want to remove your saved API keys? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$ENV_FILE"
        echo "Removed API keys file: $ENV_FILE"
    else
        echo "Kept API keys file."
    fi
fi

echo ""
echo "Note: JDK 21 and Maven were NOT uninstalled, as they might be used by other applications."
echo "If you wish to remove them from your system entirely, run:"
echo "  Arch Linux:    sudo pacman -Rns jdk21-openjdk maven"
echo "  Ubuntu/Debian: sudo apt remove --purge openjdk-21-jdk maven"
echo ""
echo "Uninstallation completely finished!"
