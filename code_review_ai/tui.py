import os
import asyncio
from pathlib import Path
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .models import CodeReviewResult, Severity
from .chunker import ASTChunker
from .client import LLMReviewClient

env_path = Path.home() / ".code_review_ai.env"
load_dotenv(env_path)
console = Console()

def run_tui():
    """Simple interactive CLI wizard using questionary."""
    console.print(Panel.fit("[bold cyan]CodeReviewAI Interactive Mode[/bold cyan]", border_style="cyan"))
    
    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Run Code Review",
                "Configure API Keys",
                "Exit"
            ],
            style=questionary.Style([('highlighted', 'fg:cyan bold')])
        ).ask()
        
        if action == "Exit" or not action:
            console.print("[dim]Goodbye![/dim]")
            break
            
        if action == "Configure API Keys":
            configure_keys()
        elif action == "Run Code Review":
            interactive_review()
            
def configure_keys():
    providers = ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    
    provider_to_set = questionary.select(
        "Which provider's API key do you want to configure?",
        choices=providers + ["Back"],
        style=questionary.Style([('highlighted', 'fg:yellow bold')])
    ).ask()
    
    if provider_to_set == "Back" or not provider_to_set:
        return
        
    new_key = questionary.password(
        f"Enter new {provider_to_set} (leave blank to cancel):"
    ).ask()
    
    if new_key:
        os.environ[provider_to_set] = new_key
        # update global .env file in home directory
        env_path = Path.home() / ".code_review_ai.env"
        lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
                
        # rewrite matching line or append
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{provider_to_set}="):
                lines[i] = f"{provider_to_set}={new_key}\n"
                found = True
        
        if not found:
            lines.append(f"{provider_to_set}={new_key}\n")
            
        with open(env_path, "w") as f:
            f.writelines(lines)
            
        console.print(f"[green]Successfully saved {provider_to_set} globally to {env_path}.[/green]\n")

def interactive_review():
    path_str = questionary.path(
        "Enter file or directory path to review:",
        default="."
    ).ask()
    
    if not path_str: return
    
    provider = questionary.select(
        "Select AI Provider:",
        choices=["gemini", "openai", "anthropic", "ollama"],
        style=questionary.Style([('highlighted', 'fg:green bold')])
    ).ask()
    
    if not provider: return

    path = Path(path_str)
    if not path.exists():
        console.print(f"[bold red]Error: Path {path_str} does not exist.[/bold red]")
        return

    chunker = ASTChunker()
    client = LLMReviewClient(provider=provider)

    files_to_review = []
    if path.is_file():
        files_to_review.append(path)
    else:
        extensions = [".py", ".java", ".cpp", ".c", ".h", ".hpp", ".js", ".ts", ".go", ".rs", ".rb"]
        ignore_dirs = {".venv", "venv", "node_modules", ".git", "__pycache__"}
        
        for ext in extensions:
            for p in path.rglob(f"*{ext}"):
                if not any(part in ignore_dirs for part in p.parts):
                    files_to_review.append(p)

    if not files_to_review:
        console.print("[yellow]No supported code files found in the directory.[/yellow]")
        return

    chunks_data = []
    for file in files_to_review:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        chunks = chunker.get_logical_chunks(str(file), content)
        for chunk in chunks:
            chunks_data.append({
                "file_path": chunk.file_path,
                "content": chunk.content
            })

    # Show a simple spinner while reviewing
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description=f"Analyzing {len(chunks_data)} code chunks with {provider.upper()}...", total=None)
        # Wrap just the async network call in asyncio.run
        results = asyncio.run(client.review_multiple(chunks_data))

    if not results or all(len(res.issues) == 0 for res in results):
        console.print(Panel("[bold green]No issues found! LGTM![/bold green]", border_style="green"))
        return

    # Display results nicely using rich table (like the main CLI does)
    table = Table(title="AI Code Review Results", show_lines=True, padding=(1, 2))
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Severity", justify="center")
    table.add_column("Category", style="magenta")
    table.add_column("Issue & Fix", style="green")

    total_issues = 0
    for res in results:
        for issue in res.issues:
            total_issues += 1
            sev_color = "red" if issue.severity == Severity.HIGH else "yellow" if issue.severity == Severity.MEDIUM else "blue"
            
            fix_md = Markdown(f"**Explanation:** {issue.explanation}\n\n**Fix:**\n{issue.suggested_fix}")
            
            table.add_row(
                f"{issue.file}:{issue.line_number}",
                f"[bold {sev_color}]{issue.severity.value}[/bold {sev_color}]",
                issue.category,
                fix_md
            )

    if total_issues > 0:
        console.print(table)
