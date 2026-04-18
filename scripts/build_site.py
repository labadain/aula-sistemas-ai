from __future__ import annotations

import argparse
import html
import os
import re
import shutil
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parent.parent
BRANCH_HTML_DIR = Path('generated-html')
SKIP_PARTS = {'.git', '.github', '_site', '__pycache__', '.venv', BRANCH_HTML_DIR.name}
CSS_SOURCE_REL = Path('assets/css/markdown.css')


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def extract_page_title_and_body(md_text: str, fallback_title: str) -> tuple[str, str]:
  body_text = md_text
  front_matter_title: str | None = None

  # Optional YAML front matter at the top of the file.
  if md_text.startswith('---\n'):
    end_idx = md_text.find('\n---\n', 4)
    if end_idx != -1:
      front_matter = md_text[4:end_idx]
      body_text = md_text[end_idx + 5 :]
      for line in front_matter.splitlines():
        if ':' not in line:
          continue
        key, value = line.split(':', 1)
        if key.strip().lower() == 'title':
          front_matter_title = value.strip().strip('"\'')
          break

  if front_matter_title:
    return front_matter_title, body_text

  # Fallback to first level-1 heading in Markdown body.
  heading_match = re.search(r'^\s*#\s+(.+?)\s*$', body_text, flags=re.MULTILINE)
  if heading_match:
    return heading_match.group(1).strip(), body_text

  return fallback_title, body_text


def page_template(
    title: str,
    body_html: str,
    css_href: str,
    home_href: str,
    nav2_label: str,
    nav2_href: str,
) -> str:
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
        <a href="{home_href}">Varanda</a>
        <a href="{nav2_href}">{nav2_label}</a>
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
    css_source = ROOT / CSS_SOURCE_REL
    if not css_source.exists():
        raise FileNotFoundError(f'Missing CSS source file: {css_source}')

    css_target = output_root / CSS_SOURCE_REL
    css_target.parent.mkdir(parents=True, exist_ok=True)
    if css_source != css_target:
        shutil.copy2(css_source, css_target)
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

    if path.suffix.lower() == '.md':
      md_text = path.read_text(encoding='utf-8')
      page_title, md_body = extract_page_title_and_body(md_text, path.stem)
      rendered = markdown.markdown(
        md_body,
        extensions=['tables', 'fenced_code', 'sane_lists', 'toc'],
        output_format='html5',
      )
      html_target = (output_root / BRANCH_HTML_DIR / relative).with_suffix('.html')
      html_target.parent.mkdir(parents=True, exist_ok=True)
      css_href = os.path.relpath(css_target, html_target.parent).replace(os.sep, '/')
      home_href = os.path.relpath(output_root / 'index.html', html_target.parent).replace(os.sep, '/')
      if path.stem == 'modules':
        nav2_label, nav2_href = 'Silabus', os.path.relpath(output_root / BRANCH_HTML_DIR / 'syllabus.html', html_target.parent).replace(os.sep, '/')
      else:
        nav2_label, nav2_href = 'Programa Semanál', os.path.relpath(output_root / BRANCH_HTML_DIR / 'modules.html', html_target.parent).replace(os.sep, '/')
      html_target.write_text(
        page_template(page_title, rendered, css_href, home_href, nav2_label, nav2_href),
        encoding='utf-8',
      )
    elif path.suffix.lower() == '.html' and path.name != 'index.html':
      continue
    else:
      target.parent.mkdir(parents=True, exist_ok=True)
      shutil.copy2(path, target)


def build_in_place() -> None:
    branch_root = ROOT / BRANCH_HTML_DIR

    # Remove previously generated HTML files that lived next to Markdown files.
    for path in ROOT.rglob('*.html'):
        if should_skip(path):
            continue
        if path == ROOT / 'index.html':
            continue
        path.unlink()

    if branch_root.exists():
        shutil.rmtree(branch_root)
    branch_root.mkdir(parents=True, exist_ok=True)

    (ROOT / '.nojekyll').write_text('', encoding='utf-8')
    css_target = write_markdown_css(branch_root)

    for path in ROOT.rglob('*.md'):
        if should_skip(path):
            continue

        md_text = path.read_text(encoding='utf-8')
        page_title, md_body = extract_page_title_and_body(md_text, path.stem)
        rendered = markdown.markdown(
            md_body,
            extensions=['tables', 'fenced_code', 'sane_lists', 'toc'],
            output_format='html5',
        )
        relative = path.relative_to(ROOT)
        html_target = (branch_root / relative).with_suffix('.html')
        html_target.parent.mkdir(parents=True, exist_ok=True)
        css_href = os.path.relpath(css_target, html_target.parent).replace(os.sep, '/')
        home_href = os.path.relpath(ROOT / 'index.html', html_target.parent).replace(os.sep, '/')
        if path.stem == 'modules':
            nav2_label, nav2_href = 'Silabus', os.path.relpath(branch_root / 'syllabus.html', html_target.parent).replace(os.sep, '/')
        else:
            nav2_label, nav2_href = 'Programa Semanál', os.path.relpath(branch_root / 'modules.html', html_target.parent).replace(os.sep, '/')
        html_target.write_text(
            page_template(page_title, rendered, css_href, home_href, nav2_label, nav2_href),
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