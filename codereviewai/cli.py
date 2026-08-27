import argparse
import os
import sys
from pathlib import Path
from typing import List

from rich.console import Console

from codereviewai.client import CodeReviewClient, DEFAULT_MODELS
from codereviewai.config import get_api_key, get_provider_env_var_name
from codereviewai.models import CodeReviewResult, ReviewIssue
from codereviewai.ui import print_issue_table, print_summary

console = Console()

SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs",
    ".cpp", ".c", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
    ".kt", ".scala", ".sql", ".sh", ".html", ".css"
}

IGNORED_DIRS = {
    ".git", "node_modules", "target", "build", "dist", ".idea",
    ".vscode", "__pycache__", ".venv", "venv", "env", ".tox"
}


def find_files_to_review(target_path: Path, custom_extensions: List[str] = None) -> List[Path]:
    allowed_exts = set(custom_extensions) if custom_extensions else SUPPORTED_EXTENSIONS
    
    if target_path.is_file():
        return [target_path]
    
    if not target_path.is_dir():
        return []

    collected_files = []
    for root, dirs, files in os.walk(target_path):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        
        for file in files:
            p = Path(root) / file
            if p.suffix.lower() in allowed_exts:
                collected_files.append(p)
                
    return sorted(collected_files)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-review-ai",
        description="AI-powered Code Review CLI running entirely in your terminal.",
    )
    parser.add_argument(
        "--path",
        "-p",
        required=True,
        help="Path to a file or directory to review.",
    )
    parser.add_argument(
        "--provider",
        choices=["gemini", "openai", "anthropic"],
        default="gemini",
        help="AI provider to use (default: gemini).",
    )
    parser.add_argument(
        "--model",
        "-m",
        default=None,
        help="Custom model name override (e.g. gemini-2.5-pro, gpt-4o-mini, claude-3-7-sonnet-20250219).",
    )
    parser.add_argument(
        "--extensions",
        "-e",
        default=None,
        help="Comma-separated file extensions to include for directory review (e.g. .py,.ts,.go).",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    target_path = Path(args.path).resolve()
    if not target_path.exists():
        console.print(f"[bold red]ERROR:[/bold red] Target path does not exist: [yellow]{args.path}[/yellow]")
        sys.exit(1)

    provider = args.provider.lower()
    env_var_name = get_provider_env_var_name(provider)
    api_key = get_api_key(provider)

    if not api_key:
        console.print(
            f"[bold red]ERROR:[/bold red] {env_var_name} is not set in environment or [cyan]~/.code_review_ai.env[/cyan]."
        )
        console.print(
            f"\nPlease set your API key:\n"
            f"  [green]export {env_var_name}=\"your_api_key\"[/green]\n"
            f"or add it to [cyan]~/.code_review_ai.env[/cyan]:\n"
            f"  [green]{env_var_name}=your_api_key[/green]"
        )
        sys.exit(1)

    custom_exts = [f".{ext.lstrip('.')}" for ext in args.extensions.split(",")] if args.extensions else None
    files_to_review = find_files_to_review(target_path, custom_exts)

    if not files_to_review:
        console.print(f"[bold yellow]Warning:[/bold yellow] No supported source files found in [cyan]{target_path}[/cyan].")
        sys.exit(0)

    chosen_model = args.model or DEFAULT_MODELS.get(provider, "gemini-3.6-flash")
    console.print(f"[bold cyan]Starting AI Code Review on:[/bold cyan] [white]{target_path}[/white]")
    console.print(
        f"[yellow]Analyzing using {provider.upper()} ({chosen_model}) across {len(files_to_review)} file(s)... Please wait.[/yellow]\n"
    )

    client = CodeReviewClient(provider=provider, api_key=api_key, model=chosen_model)

    all_issues: List[ReviewIssue] = []
    summaries: List[str] = []

    for file_path in files_to_review:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            rel_path = file_path.relative_to(target_path) if target_path.is_dir() else file_path.name
            result: CodeReviewResult = client.review_code(content, filename=str(rel_path))

            for issue in result.issues:
                # Ensure the file path displayed matches context
                if not issue.file or issue.file == "<filename>" or issue.file == "code":
                    issue.file = str(rel_path)
                all_issues.append(issue)
                print_issue_table(issue)
                console.print()

            if result.summary:
                summaries.append(f"[bold]{rel_path}:[/bold] {result.summary}" if len(files_to_review) > 1 else result.summary)

        except Exception as e:
            console.print(f"[bold red]Execution Failed for {file_path.name}:[/bold red] {e}")

    overall_summary = "\n".join(summaries) if summaries else "Review finished with no extra remarks."
    print_summary(overall_summary, total_issues=len(all_issues))


if __name__ == "__main__":
    main()
