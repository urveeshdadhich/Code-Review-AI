from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ReviewIssue(BaseModel):
    file: str = Field(description="The path to the file being reviewed.")
    line_number: int = Field(description="The line number where the issue was found.")
    severity: Severity = Field(description="The severity level of the issue.")
    category: str = Field(description="The category of the issue (e.g., security, performance, clean_code, bugs).")
    explanation: str = Field(description="A detailed explanation of why this is an issue.")
    suggested_fix: str = Field(description="A complete, copy-pasteable replacement code block (formatted with markdown backticks) that fully resolves the issue.")

class CodeReviewResult(BaseModel):
    issues: List[ReviewIssue] = Field(default_factory=list, description="A list of issues found during the review.")
    summary: str = Field(description="A high-level summary of the code review.")
