from __future__ import annotations

import argparse
import html
import os
import shutil
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {'.git', '.github', '_site', '__pycache__'}
MARKDOWN_CSS = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #f7f4ee;
  color: #13212f;
}
.page-shell {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1rem 3rem;
}
.page-nav {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
.page-nav a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem 1rem;
  border-radius: 999px;
  border: 1px solid #c7d3e0;
  background: #ffffff;
  color: #0b3b6e;
  text-decoration: none;
  font-weight: 600;
}
.page-nav a:hover {
  background: #eef4fb;
}
main {
  margin: 0;
}
article {
  background: #fffdf8;
  border: 1px solid #d6ccbc;
  border-radius: 12px;
  padding: 1.25rem;
}
a { color: #006d77; }
pre { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #d6ccbc; padding: 0.4rem 0.5rem; text-align: left; }
code { background: #f1ece0; padding: 0.12rem 0.3rem; border-radius: 4px; }
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
  <div class="page-shell">
    <nav class="page-nav" aria-label="Page navigation">
      <a href="{home_href}">Home</a>
      <a href="{program_href}">Program</a>
    </nav>
    <main>
      <article>
        {body_html}
      </article>
    </main>
  </div>
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