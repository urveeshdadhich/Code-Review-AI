# CodeReviewAI

A highly advanced, AI-powered Code Review CLI designed to run entirely within your terminal. 

CodeReviewAI intelligently analyzes your codebase for security vulnerabilities, clean code violations, performance bottlenecks, and logic bugs. It seamlessly bridges the gap between modern Large Language Models and your local development environment, outputting beautifully rendered markdown tables and utilizing an interactive wizard for a flawless developer experience.

---

## Core Features

- **Multi-Language Intelligence**  
  Natively parses and chunks Python, Java, C, C++, Rust, Go, JavaScript, TypeScript, and Ruby out of the box using `tree-sitter`.
  
- **Bring Your Own AI**  
  Connects directly to OpenAI, Anthropic (Claude), Google Gemini, and local offline Ollama models.

- **Self-Healing Local Environment**  
  When using local models via Ollama, the tool automatically detects if your server is down, silently starts it in the background, and dynamically pulls missing models before running the review.

- **Sleek Interactive Wizard**  
  A fully interactive, arrow-key-driven terminal UI built with `questionary`. No need to memorize CLI flags or complex arguments.

- **Global Configuration**  
  API keys are saved securely to your home directory (`~/.code_review_ai.env`), ensuring they remain isolated from your project code with zero risk of accidental git leaks.

---

## Installation

CodeReviewAI is fully cross-platform (Linux, macOS, and Windows).

### Mac / Linux
```bash
# 1. Make the script executable
chmod +x install.sh

# 2. Run the installer
./install.sh
```

### Windows
Double-click the `install.bat` file, or run it from Command Prompt:
```cmd
install.bat
```

### Uninstallation
To completely remove the tool and its isolated environment:
- **Mac/Linux**: Run `./uninstall.sh`
- **Windows**: Double-click `uninstall.bat`

---

## Usage

Once installed globally, you can run the tool from **any directory** on your machine using the `cr` command.

### Interactive Mode (Recommended)
Launch the minimal, step-by-step interactive wizard:
```bash
cr
```
*From the wizard, you can securely configure your API keys, select your target AI provider, and choose the files or directories you wish to review.*

### Headless CLI Mode (Fast Mode)
Bypass the wizard entirely for rapid, automated execution:

```bash
# Review the current directory using the default provider (Gemini)
cr --path .

# Review a specific file using Anthropic's Claude 3.5 Sonnet
cr --path ./src/main.rs --provider anthropic

# Review a project using a local, offline Ollama model
cr --path ./backend --provider ollama
```

---

## Security & Privacy

CodeReviewAI enforces strict security boundaries. Your API keys are stored permanently in your local user directory (`~/.code_review_ai.env`). This guarantees that your sensitive credentials are fundamentally isolated from your active workspace and cannot be committed to version control. When utilizing the Ollama integration, zero bytes of your proprietary source code are transmitted over the internet.
