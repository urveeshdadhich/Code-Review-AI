import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from codereviewai.models import CodeReviewResult, ReviewIssue, Severity
from codereviewai.client import CodeReviewClient
from codereviewai.config import get_api_key, get_provider_env_var_name, load_env_file_key
from codereviewai.cli import find_files_to_review, build_parser, main
from codereviewai.ui import print_issue_table, print_summary, _format_fix_content


class TestModels(unittest.TestCase):
    def test_models_validation(self):
        json_data = {
            "issues": [
                {
                    "file": "sample.py",
                    "line_number": 10,
                    "severity": "HIGH",
                    "category": "Security",
                    "explanation": "Hardcoded secret detected",
                    "suggested_fix": "```python\nimport os\napi_key = os.getenv('API_KEY')\n```"
                }
            ],
            "summary": "Found 1 critical security vulnerability."
        }
        res = CodeReviewResult.model_validate(json_data)
        self.assertEqual(len(res.issues), 1)
        self.assertEqual(res.issues[0].severity, Severity.HIGH)
        self.assertEqual(res.issues[0].line_number, 10)
        self.assertEqual(res.issues[0].category, "Security")


class TestConfig(unittest.TestCase):
    def test_provider_env_var_name(self):
        self.assertEqual(get_provider_env_var_name("gemini"), "GEMINI_API_KEY")
        self.assertEqual(get_provider_env_var_name("openai"), "OPENAI_API_KEY")
        self.assertEqual(get_provider_env_var_name("anthropic"), "ANTHROPIC_API_KEY")

    def test_get_api_key_from_env(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-env-key"}):
            self.assertEqual(get_api_key("gemini"), "test-env-key")

    def test_get_api_key_from_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".code_review_ai.env"
            env_file.write_text("OPENAI_API_KEY=sk-test-secret-key\nGEMINI_API_KEY=gemini-secret\n")
            with patch("pathlib.Path.home", return_value=Path(tmpdir)), \
                 patch.dict(os.environ, {}, clear=True):
                self.assertEqual(get_api_key("openai"), "sk-test-secret-key")
                self.assertEqual(get_api_key("gemini"), "gemini-secret")


class TestClient(unittest.TestCase):
    @patch("requests.post")
    def test_gemini_client(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": '```json\n{"issues": [], "summary": "Gemini clean code"}\n```'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        client = CodeReviewClient(provider="gemini", api_key="fake-gemini-key")
        result = client.review_code("def add(a, b): return a + b", filename="sample.py")
        self.assertEqual(result.summary, "Gemini clean code")
        self.assertEqual(len(result.issues), 0)

    @patch("requests.post")
    def test_openai_client(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"issues": [], "summary": "OpenAI clean code"}'
                }
            }]
        }
        mock_post.return_value = mock_response

        client = CodeReviewClient(provider="openai", api_key="fake-openai-key")
        result = client.review_code("const x = 1;", filename="sample.js")
        self.assertEqual(result.summary, "OpenAI clean code")

    @patch("requests.post")
    def test_anthropic_client(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{
                "text": '```json\n{"issues": [], "summary": "Anthropic clean code"}\n```'
            }]
        }
        mock_post.return_value = mock_response

        client = CodeReviewClient(provider="anthropic", api_key="fake-claude-key")
        result = client.review_code("fn main() {}", filename="sample.rs")
        self.assertEqual(result.summary, "Anthropic clean code")


class TestCLI(unittest.TestCase):
    def test_find_files_to_review(self):
        sample_dir = Path("./sample_code").resolve()
        files = find_files_to_review(sample_dir)
        extensions = {f.suffix for f in files}
        self.assertIn(".py", extensions)
        self.assertIn(".java", extensions)
        self.assertIn(".cpp", extensions)
        self.assertIn(".go", extensions)
        self.assertIn(".js", extensions)

    def test_find_files_with_extension_filter(self):
        sample_dir = Path("./sample_code").resolve()
        files = find_files_to_review(sample_dir, custom_extensions=[".py", ".go"])
        extensions = {f.suffix for f in files}
        self.assertEqual(extensions, {".py", ".go"})

    def test_parser(self):
        parser = build_parser()
        args = parser.parse_args(["--path", "sample.py", "--provider", "openai", "--model", "gpt-4o-mini"])
        self.assertEqual(args.path, "sample.py")
        self.assertEqual(args.provider, "openai")
        self.assertEqual(args.model, "gpt-4o-mini")


class TestUI(unittest.TestCase):
    def test_ui_table_and_summary(self):
        issue = ReviewIssue(
            file="sample.py",
            line_number=42,
            severity=Severity.HIGH,
            category="Security",
            explanation="SQL injection vulnerability in query builder",
            suggested_fix="```python\ncursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))\n```"
        )
        print_issue_table(issue)
        print_summary("Review completed successfully.", total_issues=1)

    def test_format_fix_content(self):
        renderable = _format_fix_content("```python\nprint('hello')\n```", "test.py")
        self.assertIsNotNone(renderable)


if __name__ == "__main__":
    unittest.main()
