"""
Anchor — Prompt Loader.

Loads versioned prompt template files from the /prompts directory.
Never uses inline strings for system/developer/safety prompts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

# Root prompts directory: <repo_root>/prompts
PROMPTS_DIR = Path(__file__).resolve().parents[4] / "prompts"


class PromptLoader:
    """Loads versioned markdown prompt files."""

    def __init__(self, prompts_dir: Path | None = None) -> None:
        self.prompts_dir = prompts_dir or PROMPTS_DIR
        self._cache: Dict[str, str] = {}

    def get_prompt(self, relative_path: str, use_cache: bool = True) -> str:
        """
        Load a prompt file by relative path from /prompts.
        Example: get_prompt("companion.system.md")
        """
        if use_cache and relative_path in self._cache:
            return self._cache[relative_path]

        file_path = self.prompts_dir / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        self._cache[relative_path] = content
        return content


prompt_loader = PromptLoader()
