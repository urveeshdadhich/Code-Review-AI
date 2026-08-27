import os
from pathlib import Path
from typing import Optional

PROVIDER_ENV_VARS = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


def get_provider_env_var_name(provider: str) -> str:
    return PROVIDER_ENV_VARS.get(provider.lower(), f"{provider.upper()}_API_KEY")


def load_env_file_key(key_name: str) -> Optional[str]:
    env_file = Path.home() / ".code_review_ai.env"
    if not env_file.is_file():
        return None
    
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k == key_name:
                    return v
    except Exception:
        return None
    return None


def get_api_key(provider: str) -> Optional[str]:
    key_name = get_provider_env_var_name(provider)
    # Check OS environment first
    api_key = os.environ.get(key_name)
    if api_key:
        return api_key.strip()
    
    # Fallback to ~/.code_review_ai.env
    return load_env_file_key(key_name)
