from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReviewIssue(BaseModel):
    file: str = Field(..., description="File path or name where the issue occurs")
    line_number: int = Field(..., description="Line number of the issue")
    severity: Severity = Field(..., description="Severity level: HIGH, MEDIUM, or LOW")
    category: str = Field(..., description="Category, e.g. Bug, Security, Performance, Clean Code")
    explanation: str = Field(..., description="Detailed description of the issue")
    suggested_fix: str = Field(..., description="Suggested code fix (markdown block or explanation)")


class CodeReviewResult(BaseModel):
    issues: List[ReviewIssue] = Field(default_factory=list, description="List of detected code issues")
    summary: str = Field(..., description="High-level summary of review results")
