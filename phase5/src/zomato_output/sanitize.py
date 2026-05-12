from __future__ import annotations

import html


def escape_for_html(text: str) -> str:
    """Escape ``& < > " '`` for safe embedding in HTML (architecture §14 / M4)."""
    return html.escape(text or "", quote=True)
