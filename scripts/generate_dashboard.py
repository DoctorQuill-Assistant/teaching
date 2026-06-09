#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT = ROOT / "index.html"
EXCLUDE_DIRS = {".git", ".github", ".idea", "scripts"}


CSS = """
:root {
  color-scheme: light;
  --bg: #f6f1e8;
  --paper: #fffdf9;
  --paper-2: #fff8ee;
  --ink: #1f2937;
  --muted: #6b7280;
  --accent: #0f766e;
  --accent-2: #b45309;
  --line: #e7dccb;
  --shadow: 0 12px 30px rgba(0,0,0,.06);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  background: linear-gradient(180deg, #efe7d7 0%, var(--bg) 240px);
  color: var(--ink);
}
main { max-width: 1120px; margin: 0 auto; padding: 28px 18px 64px; }
a { color: var(--accent); }
code { background:#f3efe7; padding:2px 6px; border-radius:6px; }
h1, h2, h3 { line-height: 1.12; margin-top: 0; }
p, li { font-size: 1.02rem; line-height: 1.6; }
.hero, .panel, .card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: var(--shadow);
}
.hero { padding: 30px; margin-bottom: 22px; }
.panel { padding: 22px; }
.grid { display: grid; gap: 18px; }
.topic-grid { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
.columns { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.eyebrow {
  color: var(--accent);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  font-size: .8rem;
  margin: 0 0 8px;
}
.muted { color: var(--muted); }
.stats, .actions, .chips { display: flex; gap: 10px; flex-wrap: wrap; }
.pill, .chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 8px 12px;
  background: var(--paper-2);
  white-space: nowrap;
}
.action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  border: 1px solid var(--line);
  background: var(--paper-2);
}
.action.primary {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}
.card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.section-title { margin-bottom: 10px; }
ul.link-list { margin: 0; padding-left: 20px; }
ul.link-list li + li { margin-top: 8px; }
.empty {
  margin: 0;
  color: var(--muted);
  padding: 14px 16px;
  background: #fcfaf5;
  border: 1px dashed var(--line);
  border-radius: 14px;
}
footer { margin-top: 20px; color: var(--muted); font-size: .95rem; }
.breadcrumbs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 14px;
  color: var(--muted);
}
.breadcrumbs a { color: var(--muted); }
@media (max-width: 700px) {
  .card-head { flex-direction: column; }
}
"""


def slug_to_label(value: str) -> str:
    return value.replace("-", " ").replace("_", " ").strip().title()


def extract_text_between(tag: str, text: str) -> str:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"<.*?>", "", match.group(1)).strip()


def extract_title(file_path: Path, kind: str) -> str:
    text = file_path.read_text(encoding="utf-8")
    title = re.sub(r"\s+", " ", extract_text_between("title", text)).strip()
    h1 = re.sub(r"\s+", " ", extract_text_between("h1", text)).strip()
    number_match = re.match(r"(\d+)", file_path.name)
    number = str(int(number_match.group(1))) if number_match else None

    base = h1 or title or slug_to_label(file_path.stem)

    prefixes = [
        "Portuguese Lesson ",
        "French Lesson ",
        "Portuguese Reference ",
        "French Reference ",
        "Portuguese Reference: ",
        "French Reference: ",
    ]
    for prefix in prefixes:
        if base.startswith(prefix):
            base = base[len(prefix):].strip(" —:-")
            break

    if kind == "lesson" and number:
        return f"Lesson {number} — {base}"
    if kind == "reference" and number:
        return f"Reference {number} — {base}"
    return base


def extract_first_paragraph(markdown_path: Path) -> str:
    if not markdown_path.exists():
        return ""
    text = markdown_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-"):
            return line
    return ""


def collect_html_items(folder: Path, kind: str) -> list[dict]:
    items = []
    if folder.exists():
        for file_path in sorted(folder.glob("*.html")):
            items.append(
                {
                    "title": extract_title(file_path, kind),
                    "filename": file_path.name,
                    "path": file_path,
                }
            )
    return items


def find_topics() -> list[dict]:
    topics = []
    for path in sorted(ROOT.iterdir()):
        if not path.is_dir() or path.name in EXCLUDE_DIRS or path.name.startswith("."):
            continue

        mission_file = path / "MISSION.md"
        lessons = collect_html_items(path / "lessons", "lesson")
        references = collect_html_items(path / "reference", "reference")
        if not mission_file.exists() and not lessons and not references:
            continue

        topics.append(
            {
                "name": slug_to_label(path.name),
                "slug": path.name,
                "path": path,
                "mission": extract_first_paragraph(mission_file),
                "lessons": lessons,
                "references": references,
            }
        )
    return topics


def html_doc(title: str, body: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
'''


def render_links(items: list[dict], href_prefix: str = "") -> str:
    if not items:
        return ""
    rows = []
    for item in items:
        href = href_prefix + item["filename"]
        rows.append(f'<li><a href="{html.escape(href)}">{html.escape(item["title"])}</a></li>')
    return '<ul class="link-list">' + "".join(rows) + "</ul>"


def render_root(topics: list[dict]) -> str:
    total_lessons = sum(len(topic["lessons"]) for topic in topics)
    total_references = sum(len(topic["references"]) for topic in topics)

    cards = []
    for topic in topics:
        lesson_links = render_links(topic["lessons"], f'{topic["slug"]}/lessons/')
        reference_links = render_links(topic["references"], f'{topic["slug"]}/reference/')

        cards.append(
            f'''<section class="card">
  <div class="card-head">
    <div>
      <p class="eyebrow">{html.escape(topic["name"])}</p>
      <h2>{html.escape(topic["name"])} hub</h2>
      <p class="muted">{html.escape(topic["mission"] or 'Topic page for lessons and references.')}</p>
    </div>
    <div class="chips">
      <span class="chip">{len(topic["lessons"])} lesson{'s' if len(topic['lessons']) != 1 else ''}</span>
      <span class="chip">{len(topic["references"])} reference{'s' if len(topic['references']) != 1 else ''}</span>
    </div>
  </div>

  <div class="actions">
    <a class="action primary" href="{html.escape(topic["slug"] + '/index.html')}">Open {html.escape(topic["name"])} page</a>
  </div>

  <div class="grid columns">
    <section>
      <h3 class="section-title">Lessons</h3>
      {lesson_links or f'<p class="empty">No lessons yet in <code>{html.escape(topic["slug"] + '/lessons/')}</code>.</p>'}
    </section>
    <section>
      <h3 class="section-title">References</h3>
      {reference_links or f'<p class="empty">No references yet in <code>{html.escape(topic["slug"] + '/reference/')}</code>.</p>'}
    </section>
  </div>
</section>'''
        )

    body = f'''<main>
  <section class="hero">
    <p class="eyebrow">Teaching</p>
    <h1>Learning dashboard</h1>
    <p>One place to jump into every lesson, topic hub, and quick-reference sheet.</p>
    <p class="muted">Add a new <code>.html</code> file under <code>&lt;topic&gt;/lessons/</code> or <code>&lt;topic&gt;/reference/</code> and it will be picked up automatically on the next deploy.</p>
    <div class="stats">
      <span class="pill">{len(topics)} topic{'s' if len(topics) != 1 else ''}</span>
      <span class="pill">{total_lessons} lesson{'s' if total_lessons != 1 else ''}</span>
      <span class="pill">{total_references} reference{'s' if total_references != 1 else ''}</span>
    </div>
  </section>

  <div class="grid topic-grid">
    {''.join(cards)}
  </div>

  <footer>This dashboard is generated from topic folders at build time.</footer>
</main>'''
    return html_doc("Teaching Dashboard", body)


def render_topic(topic: dict) -> str:
    lessons = render_links(topic["lessons"], "lessons/")
    references = render_links(topic["references"], "reference/")

    body = f'''<main>
  <nav class="breadcrumbs">
    <a href="../index.html">Dashboard</a>
    <span>›</span>
    <span>{html.escape(topic["name"])}</span>
  </nav>

  <section class="hero">
    <p class="eyebrow">{html.escape(topic["name"])}</p>
    <h1>{html.escape(topic["name"])} learning hub</h1>
    <p>{html.escape(topic["mission"] or 'Topic hub for lessons and reference material.')}</p>
    <div class="stats">
      <span class="pill">{len(topic["lessons"])} lesson{'s' if len(topic['lessons']) != 1 else ''}</span>
      <span class="pill">{len(topic["references"])} reference{'s' if len(topic['references']) != 1 else ''}</span>
    </div>
    <div class="actions">
      <a class="action" href="../index.html">Back to dashboard</a>
    </div>
  </section>

  <div class="grid columns">
    <section class="panel">
      <h2>Lessons</h2>
      <p class="muted">Full lessons for this topic.</p>
      {lessons or f'<p class="empty">No lessons yet in <code>{html.escape(topic["slug"] + '/lessons/')}</code>.</p>'}
    </section>

    <section class="panel">
      <h2>References</h2>
      <p class="muted">Quick review sheets and phrase references.</p>
      {references or f'<p class="empty">No references yet in <code>{html.escape(topic["slug"] + '/reference/')}</code>.</p>'}
    </section>
  </div>
</main>'''
    return html_doc(f"{topic['name']} Learning Hub", body)


def main() -> None:
    topics = find_topics()
    ROOT_OUTPUT.write_text(render_root(topics), encoding="utf-8")
    for topic in topics:
        (topic["path"] / "index.html").write_text(render_topic(topic), encoding="utf-8")
    print(f"Wrote dashboard for {len(topics)} topics.")


if __name__ == "__main__":
    main()
