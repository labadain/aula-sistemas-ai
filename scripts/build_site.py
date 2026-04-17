from __future__ import annotations

import argparse
import html
import os
import shutil
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {'.git', '.github', '_site', '__pycache__'}
MARKDOWN_CSS = '''@import url("https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,600;6..72,700&family=Work+Sans:wght@400;500;600;700&display=swap");

:root {
  --bg: #eef3f8;
  --bg-strong: #dfe8f2;
  --surface: #ffffff;
  --surface-alt: #f8fafc;
  --ink: #102033;
  --muted: #5c6b7c;
  --line: #d8e0ea;
  --primary: #0b3b6e;
  --primary-soft: #e8f0fb;
  --accent: #b88917;
  --shadow: 0 20px 48px rgba(16, 32, 51, 0.08);
  --radius-lg: 24px;
  --radius-md: 18px;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: "Work Sans", "Segoe UI", sans-serif;
  color: var(--ink);
  background:
    linear-gradient(180deg, rgba(223, 232, 242, 0.9) 0, rgba(238, 243, 248, 0.92) 180px, var(--bg) 100%),
    linear-gradient(120deg, rgba(184, 137, 23, 0.08), rgba(11, 59, 110, 0.02));
}

a {
  color: inherit;
}

.shell {
  width: min(1140px, calc(100vw - 2rem));
  margin: 0 auto;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(14px);
  background: rgba(238, 243, 248, 0.82);
  border-bottom: 1px solid rgba(216, 224, 234, 0.85);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
}

.site-kicker {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--primary);
}

.site-title {
  display: inline-block;
  margin-top: 0.18rem;
  text-decoration: none;
  font-family: "Newsreader", Georgia, serif;
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.top-nav {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.top-nav a {
  text-decoration: none;
  padding: 0.72rem 1rem;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--primary);
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(11, 59, 110, 0.1);
}

.top-nav a:hover {
  background: var(--primary-soft);
}

.page-layout {
  padding: 2.2rem 0 4rem;
}

.content-flow {
  width: min(920px, 100%);
}

.content-flow > :first-child {
  margin-top: 0;
}

.content-flow > :last-child {
  margin-bottom: 0;
}

.content-flow h1,
.content-flow h2,
.content-flow h3 {
  margin: 0;
  font-family: "Newsreader", Georgia, serif;
  letter-spacing: -0.025em;
}

.content-flow h1 {
  margin-bottom: 1.25rem;
  padding-bottom: 0.6rem;
  font-size: clamp(2.4rem, 4.4vw, 4rem);
  line-height: 0.98;
  border-bottom: 1px solid var(--line);
}

.content-flow h2 {
  margin-top: 2rem;
  padding-top: 1.5rem;
  font-size: clamp(1.5rem, 2vw, 2rem);
  line-height: 1.05;
  border-top: 1px solid var(--line);
}

.content-flow h3 {
  margin-top: 1.5rem;
  font-size: 1.22rem;
}

.content-flow p,
.content-flow li,
.content-flow td,
.content-flow th {
  color: var(--ink);
  font-size: 1rem;
  line-height: 1.75;
}

.content-flow ul,
.content-flow ol {
  padding-left: 1.25rem;
}

.content-flow a {
  color: #006d77;
}

.content-flow pre {
  overflow-x: auto;
  padding: 1rem 1.1rem;
  border-radius: var(--radius-md);
  background: #102033;
  color: #f5f8fc;
  box-shadow: var(--shadow);
}

.content-flow code {
  background: rgba(11, 59, 110, 0.08);
  padding: 0.12rem 0.3rem;
  border-radius: 4px;
}

.content-flow pre code {
  background: transparent;
  padding: 0;
}

.content-flow table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  background: rgba(255, 255, 255, 0.72);
}

.content-flow th,
.content-flow td {
  padding: 0.65rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--line);
}

.content-flow th {
  font-size: 0.84rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary);
}

@media (max-width: 720px) {
  .header-inner {
    align-items: flex-start;
    flex-direction: column;
  }

  .page-layout {
    padding-top: 1.5rem;
  }

  .content-flow h1 {
    font-size: 2.2rem;
  }
}
'''


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def page_template(title: str, body_html: str, css_href: str, home_href: str, program_href: str) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{css_href}" />
</head>
<body>
  <header class="site-header">
    <div class="shell header-inner">
      <div>
        <p class="site-kicker">Unidade Kurikulár</p>
        <a class="site-title" href="{home_href}">Sistema Intelijénsia Artifisiál</a>
      </div>
      <nav class="top-nav" aria-label="Page navigation">
        <a href="{home_href}">Home</a>
        <a href="{program_href}">Program</a>
      </nav>
    </div>
  </header>
  <main class="shell page-layout">
    <div class="content-flow">
      {body_html}
    </div>
  </main>
</body>
</html>
'''


def write_markdown_css(output_root: Path) -> Path:
    css_target = output_root / 'assets/css/markdown.css'
    css_target.parent.mkdir(parents=True, exist_ok=True)
    css_target.write_text(MARKDOWN_CSS, encoding='utf-8')
    return css_target


def build_output(output_root: Path) -> None:
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / '.nojekyll').write_text('', encoding='utf-8')
    css_target = write_markdown_css(output_root)

    for path in ROOT.rglob('*'):
        if path.is_dir() or should_skip(path):
            continue

        relative = path.relative_to(ROOT)
        target = output_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix.lower() == '.md':
            md_text = path.read_text(encoding='utf-8')
            rendered = markdown.markdown(
                md_text,
                extensions=['tables', 'fenced_code', 'sane_lists', 'toc'],
                output_format='html5',
            )
            html_target = target.with_suffix('.html')
            css_href = os.path.relpath(css_target, html_target.parent).replace(os.sep, '/')
            home_href = os.path.relpath(output_root / 'index.html', html_target.parent).replace(os.sep, '/')
            program_href = os.path.relpath(output_root / 'modules.html', html_target.parent).replace(os.sep, '/')
            html_target.write_text(
                page_template(path.stem, rendered, css_href, home_href, program_href),
                encoding='utf-8',
            )
        elif path.suffix.lower() == '.html' and path.name != 'index.html':
            continue
        else:
            shutil.copy2(path, target)


def build_in_place() -> None:
    (ROOT / '.nojekyll').write_text('', encoding='utf-8')
    css_target = write_markdown_css(ROOT)

    for path in ROOT.rglob('*.md'):
        if should_skip(path):
            continue

        md_text = path.read_text(encoding='utf-8')
        rendered = markdown.markdown(
            md_text,
            extensions=['tables', 'fenced_code', 'sane_lists', 'toc'],
            output_format='html5',
        )
        html_target = path.with_suffix('.html')
        css_href = os.path.relpath(css_target, html_target.parent).replace(os.sep, '/')
        home_href = os.path.relpath(ROOT / 'index.html', html_target.parent).replace(os.sep, '/')
        program_href = os.path.relpath(ROOT / 'modules.html', html_target.parent).replace(os.sep, '/')
        html_target.write_text(
            page_template(path.stem, rendered, css_href, home_href, program_href),
            encoding='utf-8',
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', help='Write a full static site to this directory.')
    args = parser.parse_args()

    if args.output_dir:
        build_output((ROOT / args.output_dir).resolve())
    else:
        build_in_place()


if __name__ == '__main__':
    main()