from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent


@dataclass
class State:
    in_ul: bool = False
    in_ol: bool = False
    in_table: bool = False
    in_code: bool = False
    paragraph: list[str] | None = None


def _render_inline(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("`") and part.endswith("`") and len(part) >= 2:
            out.append(f"<code>{escape(part[1:-1])}</code>")
            continue

        cursor = 0
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", part):
            if match.start() > cursor:
                out.append(escape(part[cursor : match.start()]))
            label = escape(match.group(1))
            raw_href = match.group(2)
            if raw_href.endswith(".md"):
                raw_href = raw_href[:-3] + ".html"
            href = escape(raw_href, quote=True)
            out.append(f'<a href="{href}">{label}</a>')
            cursor = match.end()
        if cursor < len(part):
            out.append(escape(part[cursor:]))

    return "".join(out)


def _flush_paragraph(buf: list[str], out: list[str], state: State) -> None:
    if state.paragraph:
        text = " ".join(state.paragraph).strip()
        if text:
            out.append(f"<p>{_render_inline(text)}</p>")
        state.paragraph = None


def _close_lists(out: list[str], state: State) -> None:
    if state.in_ul:
        out.append("</ul>")
        state.in_ul = False
    if state.in_ol:
        out.append("</ol>")
        state.in_ol = False


def _close_table(out: list[str], state: State) -> None:
    if state.in_table:
        out.append("</tbody></table>")
        state.in_table = False


def _parse_table_row(line: str) -> list[str]:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def markdown_to_html(md_text: str) -> str:
    lines = md_text.splitlines()
    out: list[str] = []
    state = State(paragraph=[])

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            _flush_paragraph(out, out, state)
            _close_lists(out, state)
            _close_table(out, state)
            if not state.in_code:
                out.append("<pre><code>")
                state.in_code = True
            else:
                out.append("</code></pre>")
                state.in_code = False
            i += 1
            continue

        if state.in_code:
            out.append(escape(line))
            i += 1
            continue

        if not stripped:
            _flush_paragraph(out, out, state)
            _close_lists(out, state)
            _close_table(out, state)
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            _flush_paragraph(out, out, state)
            _close_lists(out, state)
            _close_table(out, state)
            level = len(heading.group(1))
            out.append(
                f"<h{level}>{_render_inline(heading.group(2).strip())}</h{level}>"
            )
            i += 1
            continue

        if "|" in line and i + 1 < len(lines):
            separator = lines[i + 1].strip()
            if re.match(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$", separator):
                _flush_paragraph(out, out, state)
                _close_lists(out, state)
                _close_table(out, state)

                header_cells = _parse_table_row(line)
                out.append("<table><thead><tr>")
                for cell in header_cells:
                    out.append(f"<th>{_render_inline(cell)}</th>")
                out.append("</tr></thead><tbody>")
                state.in_table = True
                i += 2
                while i < len(lines):
                    row = lines[i].strip()
                    if not row or "|" not in row:
                        break
                    cells = _parse_table_row(lines[i])
                    out.append("<tr>")
                    for cell in cells:
                        out.append(f"<td>{_render_inline(cell)}</td>")
                    out.append("</tr>")
                    i += 1
                _close_table(out, state)
                continue

        ul = re.match(r"^[-*]\s+(.*)$", stripped)
        if ul:
            _flush_paragraph(out, out, state)
            _close_table(out, state)
            if state.in_ol:
                out.append("</ol>")
                state.in_ol = False
            if not state.in_ul:
                out.append("<ul>")
                state.in_ul = True
            out.append(f"<li>{_render_inline(ul.group(1).strip())}</li>")
            i += 1
            continue

        ol = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ol:
            _flush_paragraph(out, out, state)
            _close_table(out, state)
            if state.in_ul:
                out.append("</ul>")
                state.in_ul = False
            if not state.in_ol:
                out.append("<ol>")
                state.in_ol = True
            out.append(f"<li>{_render_inline(ol.group(1).strip())}</li>")
            i += 1
            continue

        if state.paragraph is None:
            state.paragraph = []
        state.paragraph.append(stripped)
        i += 1

    _flush_paragraph(out, out, state)
    _close_lists(out, state)
    _close_table(out, state)
    if state.in_code:
        out.append("</code></pre>")

    return "\n".join(out)


def _page_template(title: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f6f7f3;
      --panel: #ffffff;
      --text: #1f2430;
      --muted: #5e6777;
      --accent: #0f5ba8;
      --border: #d6ddea;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      color: var(--text);
      background: radial-gradient(circle at 20% 0%, #eaf2fb 0%, #f6f7f3 42%);
    }}
    .wrap {{ max-width: 980px; margin: 0 auto; padding: 18px; }}
    .top {{ background: linear-gradient(125deg, #0f5ba8, #247f96); color: #fff; border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; }}
    .top h1 {{ margin: 0 0 5px; font-size: 24px; }}
    .top a {{ color: #fff; text-decoration: underline; }}
    .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }}
    h1, h2, h3 {{ line-height: 1.3; }}
    p, li {{ line-height: 1.55; }}
    code {{ background: #f0f4f9; padding: 1px 4px; border-radius: 4px; }}
    pre {{ background: #f8fafc; border: 1px solid var(--border); border-radius: 6px; padding: 10px; overflow: auto; }}
    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
    th, td {{ border: 1px solid var(--border); padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f7fb; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"top\">
      <h1>{escape(title)}</h1>
      <div>
        <a href=\"../spx-combo-trading-curriculum.html\">Curriculum overview</a> |
        <a href=\"README.html\">Module index</a>
      </div>
    </div>
    <div class=\"panel\">{body_html}</div>
  </div>
</body>
</html>
"""


def build() -> None:
    files = sorted(p for p in ROOT.glob("*.md") if p.name != "README.md")
    files.insert(0, ROOT / "README.md")

    for md_file in files:
        md_text = md_file.read_text(encoding="utf-8")
        html_body = markdown_to_html(md_text)
        title = (
            md_text.splitlines()[0].lstrip("# ").strip()
            if md_text.strip()
            else md_file.stem
        )
        out_path = md_file.with_suffix(".html")
        out_path.write_text(_page_template(title, html_body), encoding="utf-8")
        print(f"wrote {out_path.name}")


if __name__ == "__main__":
    build()
