"""Detection and redaction of credentials, API keys, and sensitive tokens."""

import re
from typing import Any, Dict, List, Union

# Common patterns for API keys, tokens, and secrets
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}", re.IGNORECASE),  # OpenAI keys
    re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{20,}", re.IGNORECASE),  # Bearer tokens
    re.compile(r"ghp_[A-Za-z0-9]{30,}", re.IGNORECASE),  # GitHub tokens
    re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE),  # AWS Access Key
    re.compile(r"(api[_-]?key|password|secret|token)\s*[:=]\s*['\"]?([^'\"\s\r\n]{8,})['\"]?", re.IGNORECASE),
]


class SecretRedactor:
    """Utility to mask secrets in text, dictionaries, and log messages."""

    @classmethod
    def redact(cls, text: str) -> str:
        if not isinstance(text, str):
            return text
        
        redacted = text
        for pattern in SECRET_PATTERNS:
            def _replace(match):
                if match.lastindex and match.lastindex >= 2:
                    # Specific key-value match
                    full = match.group(0)
                    secret = match.group(2)
                    return full.replace(secret, "[REDACTED_SECRET]")
                return "[REDACTED_SECRET]"
            
            redacted = pattern.sub(_replace, redacted)
        return redacted

    @classmethod
    def redact_structure(cls, data: Any) -> Any:
        """Recursively redact secrets in lists, dicts, or strings."""
        if isinstance(data, str):
            return cls.redact(data)
        elif isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                if any(s in k.lower() for s in ["key", "secret", "password", "token", "auth"]):
                    new_dict[k] = "[REDACTED_SECRET]"
                else:
                    new_dict[k] = cls.redact_structure(v)
            return new_dict
        elif isinstance(data, list):
            return [cls.redact_structure(item) for item in data]
        return data


def redact_text(text: str) -> str:
    """Convenience helper for masking secrets."""
    return SecretRedactor.redact(text)
