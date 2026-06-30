#!/bin/bash
echo "Starting Java CodeReviewAI Installation..."

# Install JDK 21 and Maven if missing
if ! javac -version 2>&1 | grep -q "21\."; then
    echo "Installing JDK 21 and Maven (this requires sudo)..."
    if command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm jdk21-openjdk maven
    elif command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y openjdk-21-jdk maven
    else
        echo "Please install JDK 21 and Maven manually!"
        exit 1
    fi
fi

# Dynamically find JAVA_HOME for Java 21
if [ -d "/usr/lib/jvm/java-21-openjdk" ]; then
    export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
elif [ -d "/usr/lib/jvm/java-21-openjdk-amd64" ]; then
    export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
else
    export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))
fi

echo "Compiling Native Java Executable..."
mvn clean package

if [ $? -ne 0 ]; then
    echo "Maven build failed!"
    exit 1
fi

INSTALL_DIR="$HOME/.code_review_ai_java"
mkdir -p "$INSTALL_DIR"
cp target/code-review-ai-1.0.jar "$INSTALL_DIR/app.jar"

BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

echo '#!/bin/bash' > "$BIN_DIR/cr"
echo 'java -jar "$HOME/.code_review_ai_java/app.jar" "$@"' >> "$BIN_DIR/cr"
chmod +x "$BIN_DIR/cr"

# Ensure ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo ""
    echo "========================================================="
    echo "Added ~/.local/bin to your PATH."
    echo "Please run 'source ~/.bashrc' or restart your terminal."
    echo "========================================================="
fi

echo ""
echo "Installation complete! You can now run 'cr' from anywhere to open the TUI."
