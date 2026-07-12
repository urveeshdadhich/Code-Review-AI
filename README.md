# CodeReviewAI

A highly advanced, AI-powered Code Review CLI designed to run entirely within your terminal. 

CodeReviewAI intelligently analyzes your codebase for security vulnerabilities, clean code violations, performance bottlenecks, and logic bugs. It seamlessly bridges the gap between modern Large Language Models and your local development environment, outputting beautifully rendered markdown tables and utilizing an interactive wizard for a flawless developer experience.

---

## Core Features

- **Multi-Language Intelligence**  
  Seamlessly analyzes files of any language natively using core Java NIO utilities, sending raw contextual strings directly to advanced LLMs.
  
- **Bring Your Own AI**  
  Connects directly to OpenAI, Anthropic (Claude), and Google Gemini.


- **Global Configuration**  
  API keys are saved securely to your home directory (`~/.code_review_ai.env`), ensuring they remain isolated from your project code with zero risk of accidental git leaks.

---

## Prerequisites

Before running CodeReviewAI, ensure you have the following installed:
- **Java 21** or higher
- **Maven** (for building the project)

## Build Instructions

To build the executable JAR file, run the following command from the project root:

```bash
mvn clean package
```
This will generate a `code-review-ai-1.0.jar` file in the `target/` directory.

---

## Configuration

CodeReviewAI requires API keys for cloud AI providers. You can configure them using either environment variables or a global configuration file.

### 1. Environment Variables
Export the corresponding API key directly in your terminal:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

### 2. Global Configuration File (Recommended)
Create a `.code_review_ai.env` file in your home directory (`~/.code_review_ai.env`) to store your keys permanently and securely. Add your keys in the following format:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```



---

## Usage

You can run the tool using the `java` command from the root of the project:

```bash
# Review the current directory using the default provider (Gemini)
java -jar target/code-review-ai-1.0.jar --path .

# Review a specific file using Anthropic's Claude 3.5 Sonnet
java -jar target/code-review-ai-1.0.jar --path ./src/main.rs --provider anthropic
```

> **Tip:** To run the tool easily from any directory on your machine, you can create an alias in your `~/.bashrc` or `~/.zshrc` file using the **absolute path** to the compiled JAR:
> ```bash
> alias cr="java -jar /absolute/path/to/CodeReviewAI/target/code-review-ai-1.0.jar"
> ```
> Once added, you can run the tool from anywhere like this: 
> `cr --path ./my-code.py --provider gemini`

---

## Security & Privacy

CodeReviewAI enforces strict security boundaries. Your API keys are stored permanently in your local user directory (`~/.code_review_ai.env`). This guarantees that your sensitive credentials are fundamentally isolated from your active workspace and cannot be committed to version control.
