import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich import box

from codereviewai.models import ReviewIssue, Severity

console = Console()

SEVERITY_STYLES = {
    Severity.HIGH: "bold red",
    Severity.MEDIUM: "bold yellow",
    Severity.LOW: "bold cyan",
}


def print_issue_table(issue: ReviewIssue):
    table = Table(
        box=box.ROUNDED,
        show_header=False,
        show_edge=True,
        expand=True,
        pad_edge=False,
        border_style="bright_black",
    )
    table.add_column("Field", style="bold white", width=12, no_wrap=True)
    table.add_column("Details", style="white")

    # 1. Severity
    sev_style = SEVERITY_STYLES.get(issue.severity, "bold white")
    table.add_row("Severity", Text(issue.severity.value, style=sev_style))

    # 2. File & Line
    file_loc = f"{issue.file} : {issue.line_number}"
    table.add_row("File", Text(file_loc, style="bold magenta"))

    # 3. Category
    table.add_row("Category", Text(issue.category, style="cyan"))

    # 4. Issue explanation
    table.add_row("Issue", issue.explanation)

    # 5. Fix
    fix_renderable = _format_fix_content(issue.suggested_fix, issue.file)
    table.add_row("Fix", fix_renderable)

    console.print(table)


def _format_fix_content(content: str, filename: str):
    # Detect code block in suggested fix
    code_match = re.search(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", content, re.DOTALL)
    if code_match:
        lang = code_match.group(1).strip()
        code_body = code_match.group(2).rstrip()
        
        # Deduce language from filename if empty
        if not lang and "." in filename:
            ext = filename.rsplit(".", 1)[-1].lower()
            lang_map = {
                "py": "python",
                "java": "java",
                "js": "javascript",
                "ts": "typescript",
                "cpp": "cpp",
                "c": "c",
                "go": "go",
                "rs": "rust",
                "rb": "ruby",
                "php": "php",
                "html": "html",
                "css": "css",
                "json": "json",
            }
            lang = lang_map.get(ext, "text")
        
        prefix = content[: code_match.start()].strip()
        suffix = content[code_match.end() :].strip()

        renderables = []
        if prefix:
            renderables.append(Text(prefix))
        renderables.append(
            Syntax(code_body, lang or "python", theme="monokai", line_numbers=False, word_wrap=True)
        )
        if suffix:
            renderables.append(Text(suffix))

        if len(renderables) == 1:
            return renderables[0]
        
        # Return a composite table for multiple parts
        subtable = Table.grid(padding=1)
        for r in renderables:
            subtable.add_row(r)
        return subtable

    return Text(content)


def print_summary(summary: str, total_issues: int = 0):
    console.print(
        Panel(
            f"[bold green]Summary:[/bold green] {summary}\n[dim]Total issues identified: {total_issues}[/dim]",
            title="[bold green]Review Complete[/bold green]",
            border_style="green",
        )
    )
