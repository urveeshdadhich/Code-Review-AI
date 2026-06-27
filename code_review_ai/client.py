import asyncio
import os
import logging
import json
import subprocess
from typing import List
from .models import CodeReviewResult
import litellm
from pydantic import ValidationError

logger = logging.getLogger(__name__)

def ensure_ollama_model(model_name: str):
    """Checks if ollama is installed and pulls the model if missing."""
    actual_model = model_name.replace("ollama/", "").replace("local/", "")
    
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n[bold red]Error:[/bold red] Ollama executable not found. Please install Ollama from https://ollama.com\n")
        return

    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            if "could not connect" in result.stderr.lower() or "is it running" in result.stderr.lower() or "connection refused" in result.stderr.lower():
                from rich.console import Console
                c = Console()
                c.print("\n[bold yellow]Ollama server is not running. Starting it in the background...[/bold yellow]")
                # Start ollama serve in the background and detach
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import time
                time.sleep(3)  # Give it a few seconds to spin up
                # Retry listing
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            else:
                print(f"[Warning] Failed to query Ollama: {result.stderr}")
                return

        # Check if actual_model is in the output (basic string match is sufficient for ollama list)
        if actual_model not in result.stdout:
            from rich.console import Console
            c = Console()
            c.print(f"\n[bold yellow]Model '{actual_model}' not found locally. Downloading now... (This may take a few minutes)[/bold yellow]")
            # Run pull without capturing output so the user sees the native download progress bar
            subprocess.run(["ollama", "pull", actual_model], check=True)
            c.print(f"[bold green]Successfully downloaded '{actual_model}'![/bold green]\n")
    except Exception as e:
        print(f"[Warning] Failed to check or pull ollama model: {e}")

# Suppress noisy litellm logs
litellm.suppress_debug_info = True

class LLMReviewClient:
    def __init__(self, provider: str = "gemini", model: str = None, max_concurrent: int = 5):
        self.provider = provider.lower()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Determine the correct model string formatting for litellm
        if not model:
            if self.provider == "openai":
                self.model = "openai/gpt-4o"
            elif self.provider in ["anthropic", "claude"]:
                self.model = "anthropic/claude-3-5-sonnet-20240620"
            elif self.provider in ["ollama", "local"]:
                self.model = "ollama/llama3.2"
            else:
                self.model = "gemini/gemini-2.5-flash"
        else:
            if "/" not in model:
                if self.provider in ["ollama", "local"]:
                    self.model = f"ollama/{model}"
                else:
                    self.model = f"{self.provider}/{model}"
            else:
                self.model = model
                
        if self.provider in ["ollama", "local"]:
            ensure_ollama_model(self.model)

    async def review_chunk(self, file_path: str, content: str) -> CodeReviewResult:
        """
        Sends a code chunk to the LLM via litellm which unifies 100+ providers under one API.
        """
        prompt = f"""
        You are an expert Principal Staff Engineer and security auditor.
        Review the following code for security vulnerabilities, performance bottlenecks, clean code principles, and bugs.
        
        CRITICAL: For every issue you find, the `suggested_fix` MUST contain the EXACT, fully-functioning replacement code block (using markdown code blocks) so the user can copy-paste it directly. Do not just describe the fix.
        
        File: {file_path}
        
        Code:
        ```
        {content}
        ```
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a stringent code review assistant. You MUST output ONLY valid JSON that strictly adheres to the requested schema. Do not include markdown blocks around the JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        async with self.semaphore:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # litellm translates this single call to OpenAI, Gemini, Claude, Ollama, etc.
                    response = await litellm.acompletion(
                        model=self.model,
                        messages=messages,
                        response_format=CodeReviewResult,
                        temperature=0.0
                    )
                    
                    content = response.choices[0].message.content
                    
                    try:
                        # Some providers return stringified JSON, others might parse directly
                        if isinstance(content, str):
                            # Clean up markdown if the model hallucinated code blocks around the JSON
                            content = content.strip()
                            if content.startswith("```json"):
                                content = content[7:-3].strip()
                            elif content.startswith("```"):
                                content = content[3:-3].strip()
                                
                            return CodeReviewResult.model_validate_json(content)
                        else:
                            return CodeReviewResult.model_validate(content)
                            
                    except ValidationError as ve:
                        logger.error(f"JSON Parsing Error on {file_path}: {ve}")
                        return CodeReviewResult(summary=f"Failed to parse LLM output. Ensure provider supports JSON schema. Error: {ve}", issues=[])

                except Exception as e:
                    err_str = str(e)
                    # Handle Rate Limits across all providers
                    if "429" in err_str or "503" in err_str or "RateLimit" in err_str:
                        if attempt < max_retries - 1:
                            wait_time = 15 * (attempt + 1)
                            print(f"[Warning] Rate limited by {self.provider.upper()}. Retrying {file_path} in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                            
                    logger.error(f"Error calling {self.provider} for {file_path}: {e}")
                    return CodeReviewResult(summary=f"API Error: {str(e)}", issues=[])
                    
    async def review_multiple(self, chunks: List[dict]) -> List[CodeReviewResult]:
        tasks = [self.review_chunk(c['file_path'], c['content']) for c in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Task failed with exception: {r}")
            elif isinstance(r, CodeReviewResult):
                valid_results.append(r)
                
        return valid_results
