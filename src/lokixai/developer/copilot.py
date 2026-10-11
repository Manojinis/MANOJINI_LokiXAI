"""Developer copilot for static code analysis, AST inspection, and patch suggestions."""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.lokixai.security.path_guard import PathGuard
from src.lokixai.security.redaction import SecretRedactor


class CodeSymbol(BaseModel):
    name: str
    symbol_type: str  # function, class, variable
    line_number: int
    docstring: Optional[str] = None


class ProjectSummary(BaseModel):
    root_path: str
    total_files: int
    languages: Dict[str, int]
    key_symbols: List[CodeSymbol] = Field(default_factory=list)


class DeveloperCopilot:
    """Read-only code inspection and developer assistance engine."""

    @staticmethod
    def inspect_file(file_path: str) -> Dict[str, Any]:
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                code_text = f.read()
        except Exception as e:
            raise RuntimeError(f"Could not read code file: {e}")

        # Redact secrets before returning
        safe_code = SecretRedactor.redact(code_text)

        symbols: List[CodeSymbol] = []
        if path.suffix.lower() == ".py":
            try:
                tree = ast.parse(code_text)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        doc = ast.get_docstring(node)
                        symbols.append(CodeSymbol(
                            name=node.name,
                            symbol_type="function",
                            line_number=node.lineno,
                            docstring=doc[:100] if doc else None,
                        ))
                    elif isinstance(node, ast.ClassDef):
                        doc = ast.get_docstring(node)
                        symbols.append(CodeSymbol(
                            name=node.name,
                            symbol_type="class",
                            line_number=node.lineno,
                            docstring=doc[:100] if doc else None,
                        ))
            except SyntaxError:
                pass

        return {
            "file_name": path.name,
            "path": str(path),
            "line_count": len(safe_code.splitlines()),
            "symbols": [s.model_dump() for s in symbols],
            "code_sample": safe_code[:2500],
        }

    @staticmethod
    def summarize_directory(dir_path: str, max_depth: int = 3) -> ProjectSummary:
        path = Path(dir_path).resolve()
        total_files = 0
        langs: Dict[str, int] = {}
        all_symbols: List[CodeSymbol] = []

        ignore_dirs = {".git", "__pycache__", "venv", "env", "node_modules", ".pytest_cache", "dist", "build"}

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            rel_depth = len(Path(root).relative_to(path).parts)
            if rel_depth > max_depth:
                continue

            for f in files:
                total_files += 1
                ext = os.path.splitext(f)[1].lower() or "no_ext"
                langs[ext] = langs.get(ext, 0) + 1

                if ext == ".py" and len(all_symbols) < 30:
                    try:
                        file_data = DeveloperCopilot.inspect_file(str(Path(root) / f))
                        for s_dict in file_data["symbols"]:
                            all_symbols.append(CodeSymbol(**s_dict))
                    except Exception:
                        pass

        return ProjectSummary(
            root_path=str(path),
            total_files=total_files,
            languages=langs,
            key_symbols=all_symbols[:30],
        )
