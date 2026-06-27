import asyncio
import typer
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text
from rich.markdown import Markdown
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

env_path = Path.home() / ".code_review_ai.env"
load_dotenv(env_path)

from .models import CodeReviewResult, Severity
from .chunker import ASTChunker
from .client import LLMReviewClient

app = typer.Typer(help="AI-Powered Code Review CLI Tool")
console = Console()

def display_results(results: list[CodeReviewResult]):
    """Renders the issues cleanly using a styled Rich Table."""
    if not results or all(len(res.issues) == 0 for res in results):
        console.print(Panel("[bold green]No issues found! LGTM![/bold green]", border_style="green", expand=False))
        return
        
    table = Table(
        title="\n[bold]AI Code Review Results[/bold]", 
        show_header=True, 
        header_style="bold magenta", 
        show_lines=True, # Adds beautiful horizontal separator lines between rows
        padding=(1, 2)   # Adds vertical and horizontal breathing room
    )
    
    table.add_column("Severity", justify="center", style="bold")
    table.add_column("Location", style="blue")
    table.add_column("Category", style="green")
    table.add_column("Details", overflow="fold")
    
    total_issues = 0
    for res in results:
        for issue in res.issues:
            total_issues += 1
            if issue.severity == Severity.HIGH:
                sev_color = "red"
            elif issue.severity == Severity.MEDIUM:
                sev_color = "yellow"
            else:
                sev_color = "cyan"
                
            location = f"{issue.file}\nLine: {issue.line_number}"
            
            # Combine the explanation and a fully rendered markdown fix into one cell
            explanation = Text(issue.explanation)
            fix_header = Text("\nSuggested Fix:", style="bold dim")
            fix_md = Markdown(issue.suggested_fix)
            
            details_group = Group(explanation, fix_header, fix_md)
            
            table.add_row(
                f"[{sev_color}]{issue.severity.value}[/{sev_color}]",
                location,
                issue.category.upper(),
                details_group
            )
            
    if total_issues > 0:
        console.print(table)

async def async_review_path(path: Path, provider: str, model: str):
    if not path.exists():
        console.print(f"[bold red]Error: Path {path} does not exist.[/bold red]")
        raise typer.Exit(code=1)
        
    chunker = ASTChunker()
    client = LLMReviewClient(provider=provider, model=model)
    
    files_to_review = []
    if path.is_file():
        # If the user explicitly passes a file, ALWAYS review it regardless of extension.
        files_to_review.append(path)
    else:
        # If it's a directory, search for common code file extensions but explicitly ignore massive dependency folders
        extensions = [".py", ".java", ".cpp", ".c", ".h", ".hpp", ".js", ".ts", ".go", ".rs", ".rb"]
        ignore_dirs = {".venv", "venv", "node_modules", ".git", "__pycache__"}
        
        for ext in extensions:
            for p in path.rglob(f"*{ext}"):
                # Check if any part of the path is in our ignore list
                if not any(part in ignore_dirs for part in p.parts):
                    files_to_review.append(p)
        
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
            
    with Progress() as progress:
        task = progress.add_task("[cyan]Analyzing code chunks with AI...", total=len(chunks_data))
        results = []
        
        # Dispatch tasks
        tasks = [client.review_chunk(c['file_path'], c['content']) for c in chunks_data]
        
        # Await as they complete
        for coro in asyncio.as_completed(tasks):
            res = await coro
            results.append(res)
            progress.advance(task)
            
    display_results(results)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    path: Optional[Path] = typer.Option(None, "--path", help="Local file or directory path to review."),
    pr: Optional[int] = typer.Option(None, "--pr", help="GitHub Pull Request number to review."),
    provider: str = typer.Option("gemini", "--provider", help="LLM Provider (gemini, openai, claude, ollama)."),
    model: str = typer.Option(None, "--model", help="Specific model name. Defaults to the provider's best model.")
):
    """
    AI-Powered Code Review CLI Tool
    """
    if ctx.invoked_subcommand is not None:
        return
        
    if path or pr:
        if path:
            asyncio.run(async_review_path(path, provider, model))
        elif pr:
            console.print(Panel(f"Fetching diff for PR #{pr}...", style="bold blue"))
            console.print("[yellow]PR diff fetching and remote execution is a stub.[/yellow]")
    else:
        from .tui import run_tui
        run_tui()

if __name__ == "__main__":
    app()
