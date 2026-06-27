import pytest
from code_review_ai.chunker import ASTChunker
from code_review_ai.models import Severity

# Deliberately flawed code sequence for evaluation
VULNERABLE_CODE = """
import sqlite3

def get_user_by_name(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Security Bug: Basic SQL injection string concatenation
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()
"""

BAD_PERFORMANCE_CODE = """
def process_large_data(data_list):
    # Performance Bug: O(N^2) list membership check
    result = []
    for item in data_list:
        if item not in result:
            result.append(item)
    return result
"""

def test_ast_chunker():
    """Validates that ASTChunker properly identifies a function boundary and includes its body."""
    chunker = ASTChunker()
    chunks = chunker.get_logical_chunks("vuln_test.py", VULNERABLE_CODE)
    
    assert len(chunks) == 1
    assert chunks[0].node_type == "FunctionDef"
    assert "def get_user_by_name(username):" in chunks[0].content
    assert "query = " in chunks[0].content

def test_ast_chunker_multiple_functions():
    """Validates that ASTChunker chunks multiple functions independently."""
    combined = VULNERABLE_CODE + "\n" + BAD_PERFORMANCE_CODE
    chunker = ASTChunker()
    chunks = chunker.get_logical_chunks("combined_test.py", combined)
    
    assert len(chunks) == 2
    assert chunks[0].node_type == "FunctionDef"
    assert chunks[1].node_type == "FunctionDef"
    assert "get_user_by_name" in chunks[0].content
    assert "process_large_data" in chunks[1].content

def test_pydantic_schema_validation():
    """Validates the strict output parsing of the Pydantic schema used by the LLM."""
    from code_review_ai.models import CodeReviewResult, ReviewIssue
    
    mock_json = {
        "issues": [
            {
                "file": "vuln_test.py",
                "line_number": 7,
                "severity": "HIGH",
                "category": "security",
                "explanation": "String concatenation in SQL queries leads to SQL injection vulnerabilities.",
                "suggested_fix": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE username = ?', (username,))"
            }
        ],
        "summary": "Found 1 high severity security issue."
    }
    
    result = CodeReviewResult(**mock_json)
    
    assert len(result.issues) == 1
    assert result.issues[0].severity == Severity.HIGH
    assert result.issues[0].category == "security"
    assert "SQL injection" in result.issues[0].explanation
