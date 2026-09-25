"""
CALIP Universal Markdown & Legal Table Renderer
Converts raw Markdown briefings with tables, headers, blockquotes, and citations
into semantic HTML for web presentation.
"""

from __future__ import annotations

import html
import re


def render_markdown_to_html(md_text: str) -> str:
    """
    Transforms legal markdown text into clean semantic HTML.
    Supports GFM tables, headers (h1-h4), bold/italic, lists, blockquotes, and code blocks.
    """
    if not md_text:
        return ""

    lines = md_text.splitlines()
    html_out: list[str] = []
    in_table = False
    table_header_done = False
    table_rows: list[str] = []
    in_list = False
    in_code = False
    code_lines: list[str] = []

    def flush_table():
        nonlocal in_table, table_header_done, table_rows
        if not table_rows:
            in_table = False
            return ""
        
        tbl_html = ["<div class=\"table-responsive-wrapper\"><table class=\"legal-table\">"]
        tbl_html.extend(table_rows)
        tbl_html.append("</table></div>")
        in_table = False
        table_header_done = False
        table_rows = []
        return "".join(tbl_html)

    def flush_list():
        nonlocal in_list
        if in_list:
            in_list = False
            return "</ul>"
        return ""

    for line in lines:
        stripped = line.strip()

        # Handle fenced code blocks
        if stripped.startswith("```"):
            if in_code:
                in_code = False
                joined = html.escape("\n".join(code_lines))
                html_out.append(f"<pre class=\"code-block\"><code>{joined}</code></pre>")
                code_lines = []
            else:
                if in_table:
                    html_out.append(flush_table())
                if in_list:
                    html_out.append(flush_list())
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        # Handle Tables (| col | col |)
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                if in_list:
                    html_out.append(flush_list())
                in_table = True
                table_header_done = False
                table_rows = []

            # Check if this is a divider line like |---|---|
            if re.match(r"^\|(\s*:?-+:?\s*\|)+$", stripped):
                table_header_done = True
                continue

            cells = [c.strip() for c in stripped.strip("|").split("|")]
            tag = "th" if not table_header_done else "td"
            row_cells = []
            for c in cells:
                formatted_cell = format_inline_markdown(c)
                row_cells.append(f"<{tag}>{formatted_cell}</{tag}>")
            
            row_str = f"<tr>{''.join(row_cells)}</tr>"
            if not table_header_done:
                table_rows.append(f"<thead>{row_str}</thead><tbody>")
            else:
                table_rows.append(row_str)
            continue
        elif in_table:
            # End of table
            table_rows.append("</tbody>")
            html_out.append(flush_table())

        # Empty line
        if not stripped:
            if in_list:
                html_out.append(flush_list())
            continue

        # Headings
        if stripped.startswith("#### "):
            if in_list:
                html_out.append(flush_list())
            content = format_inline_markdown(stripped[5:])
            html_out.append(f"<h4 class=\"legal-h4\">{content}</h4>")
            continue
        elif stripped.startswith("### "):
            if in_list:
                html_out.append(flush_list())
            content = format_inline_markdown(stripped[4:])
            html_out.append(f"<h3 class=\"legal-h3\">{content}</h3>")
            continue
        elif stripped.startswith("## "):
            if in_list:
                html_out.append(flush_list())
            content = format_inline_markdown(stripped[3:])
            html_out.append(f"<h2 class=\"legal-h2\"><span class=\"legal-h2-bar\"></span>{content}</h2>")
            continue
        elif stripped.startswith("# "):
            if in_list:
                html_out.append(flush_list())
            content = format_inline_markdown(stripped[2:])
            html_out.append(f"<h1 class=\"legal-h1\">{content}</h1>")
            continue

        # Horizontal Rule
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            if in_list:
                html_out.append(flush_list())
            html_out.append("<hr class=\"legal-divider\" />")
            continue

        # Blockquote (> text)
        if stripped.startswith("> "):
            if in_list:
                html_out.append(flush_list())
            content = format_inline_markdown(stripped[2:])
            html_out.append(f"<blockquote class=\"legal-quote\">{content}</blockquote>")
            continue

        # Unordered list items (- item, * item)
        if stripped.startswith(("- ", "* ", "• ")) and not stripped.startswith("**"):
            if not in_list:
                in_list = True
                html_out.append("<ul class=\"legal-list\">")
            item_text = stripped[2:].strip()
            formatted = format_inline_markdown(item_text)
            html_out.append(f"<li>{formatted}</li>")
            continue
        elif in_list and not re.match(r"^\d+\.\s", stripped):
            html_out.append(flush_list())

        # Numbered list items (1. item)
        num_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if num_match:
            if in_list:
                html_out.append(flush_list())
            num = num_match.group(1)
            content = format_inline_markdown(num_match.group(2))
            html_out.append(f"<div class=\"legal-numbered-item\"><span class=\"num-badge\">{num}</span><div class=\"num-content\">{content}</div></div>")
            continue

        # Regular Paragraph
        formatted_p = format_inline_markdown(stripped)
        html_out.append(f"<p class=\"legal-p\">{formatted_p}</p>")

    if in_table:
        table_rows.append("</tbody>")
        html_out.append(flush_table())
    if in_list:
        html_out.append(flush_list())
    if in_code:
        joined = html.escape("\n".join(code_lines))
        html_out.append(f"<pre class=\"code-block\"><code>{joined}</code></pre>")

    return "\n".join(html_out)


def format_inline_markdown(text: str) -> str:
    """Formats inline bold, italics, code, and citations."""
    if not text:
        return ""

    # Escape raw HTML entities first to prevent injection
    text = html.escape(text)

    # Bold: **bold** or __bold__
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)

    # Italics: *italic* or _italic_
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_([^_]+?)_(?!_)", r"<em>\1</em>", text)

    # Inline Code: `code`
    text = re.sub(r"`([^`]+?)`", r"<code class=\"inline-code\">\1</code>", text)

    # Citations e.g. [CALIP: Book 1, Page 213] or [Source 1] or [IPC Section 409]
    def cite_replacer(match):
        raw = match.group(1)
        # Distinguish CALIP internal vs external citations
        if "calip" in raw.lower() or "source" in raw.lower() or "page" in raw.lower():
            return f"<span class=\"citation-badge citation-internal\" title=\"Internal CALIP Evidence Record\">{raw}</span>"
        return f"<span class=\"citation-badge citation-external\" title=\"Statutory & Legal Citation\">{raw}</span>"

    text = re.sub(r"\[([A-Za-z0-9_\-\s\.:,/§#]+)\]", cite_replacer, text)

    return text
