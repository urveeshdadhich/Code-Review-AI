# CodeReviewAI

An AI-powered Code Review CLI designed to run entirely within your terminal.

CodeReviewAI intelligently analyzes your codebase for security vulnerabilities, clean code violations, performance bottlenecks, and logic bugs. It seamlessly bridges the gap between modern Large Language Models and your local development environment, outputting beautifully rendered terminal tables with syntax highlighting.

---

## Core Features

- **Multi-Language Intelligence**  
  Seamlessly analyzes files of any language natively, sending raw contextual source directly to advanced LLMs.
  
- **Single File & Directory Scanning**  
  Review a single code file or recursively analyze an entire project directory with customizable file extension filters.

- **Bring Your Own AI**  
  Connects directly to Google Gemini (default), OpenAI (GPT-4o), and Anthropic (Claude 3.5 Sonnet).

- **Model Flexibility**  
  Easily override the default model on the fly using `--model` (e.g. `gemini-2.5-pro`, `gpt-4o-mini`, `claude-3-7-sonnet-20250219`).

- **Global Configuration**  
  API keys can be set as environment variables or saved securely in your home directory (`~/.code_review_ai.env`), ensuring zero risk of accidental git leaks.

---

## Prerequisites

- **Python 3.10** or higher
- `pip` or `uv`

---

## Installation

### Using pip
```bash
# Clone the repository and install in editable mode
git clone https://github.com/urveeshdadhich/Code-Review-AI.git
cd Code-Review-AI
pip install -e .
```

### Using uv (Fast)
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

---

## Configuration

CodeReviewAI requires API keys for cloud AI providers. You can configure them using environment variables or a global configuration file.

### 1. Environment Variables
Export the corresponding API key directly in your terminal:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

### 2. Global Configuration File (Recommended)
Create a `.code_review_ai.env` file in your home directory (`~/.code_review_ai.env`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

---

## Usage

You can run CodeReviewAI using the installed console commands (`cr`, `codereviewai`, `code-review-ai`) or via `python -m codereviewai`:

```bash
# Review a single file using default provider (Gemini)
cr --path ./sample_code/Sample.java

# Review an entire directory recursively
cr --path ./sample_code/

# Review a specific file using Anthropic's Claude 3.5 Sonnet
cr --path ./sample_code/sample.cpp --provider anthropic

# Review using OpenAI with custom model override
cr --path ./sample_code/sample.py --provider openai --model gpt-4o-mini

# Review only specific extensions in a folder
cr --path ./src --extensions .py,.ts
```

### Quick Alias
If installed globally or in your favorite environment:
```bash
alias cr="code-review-ai"
```

---

## CLI Options

| Option | Shorthand | Description | Default |
| :--- | :--- | :--- | :--- |
| `--path` | `-p` | Path to a file or directory to review *(Required)* | - |
| `--provider` | | AI provider: `gemini`, `openai`, `anthropic` | `gemini` |
| `--model` | `-m` | Custom model name override | Provider default |
| `--extensions` | `-e` | Comma-separated file extensions for directory scans | Common code extensions |
| `--help` | `-h` | Show help and available options | - |

---

## Security & Privacy

CodeReviewAI enforces strict security boundaries. Your API keys are stored permanently in your local user directory (`~/.code_review_ai.env`) or injected via shell environment variables. Your sensitive credentials remain isolated from your active workspace and are never committed to version control.
