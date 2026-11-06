"""Refresh static navigation/breadcrumbs after editing navigation.json.
Run from any directory: python3 scripts/build_navigation.py
"""
import json
import os
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def flatten(nodes, ancestors=()):
    for node in nodes:
        yield node, ancestors
        yield from flatten(node.get('children', []), (*ancestors, node))


def relative(target, current):
    return escape(os.path.relpath(ROOT / target, (ROOT / current).parent), quote=True)


def navigation(nodes, current, ancestors):
    rows = []
    for node in nodes:
        title = escape(node['title'])
        active = ' aria-current="page"' if node['path'] == current else ''
        link = f'<a href="{relative(node["path"], current)}"{active}>{title}</a>'
        children = node.get('children', [])
        if children:
            opened = ' open' if node['path'] in ancestors else ''
            rows.append(
                f'<li class="nav-branch">{link}\n'
                f'<details data-page="{escape(node["path"], quote=True)}"{opened}>\n'
                f'<summary aria-label="Toggle {title} subpages"></summary>\n'
                f'{navigation(children, current, ancestors)}\n</details></li>'
            )
        else:
            rows.append(f'<li class="nav-leaf">{link}</li>')
    return '<ul class="nav-tree">\n' + '\n'.join(rows) + '\n</ul>'


def build():
    nodes = json.loads((ROOT / 'scripts/navigation.json').read_text())
    pages = list(flatten(nodes))
    for node, _ in pages:
        if not (ROOT / node['path']).is_file():
            raise FileNotFoundError(node['path'])
    for node, ancestors in pages:
        path = ROOT / node['path']
        source = path.read_text()
        nav = '<nav aria-label="Main navigation">\n' + navigation(
            nodes, node['path'], {a['path'] for a in ancestors}
        ) + '\n</nav>'
        source, count = re.subn(r'<nav(?:\s[^>]*)?>.*?</nav>', lambda _: nav, source, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Missing navigation in {path}')
        crumbs = [f'<li><a href="{relative(a["path"], node["path"])}">{escape(a["title"])}</a></li>' for a in ancestors]
        crumbs.append(f'<li><span>{escape(node["title"])}</span></li>')
        breadcrumb = '<!-- breadcrumbs:start -->\n'
        if ancestors:
            breadcrumb += '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>' + ''.join(crumbs) + '</ol></nav>\n'
        breadcrumb += '<!-- breadcrumbs:end -->'
        if '<!-- breadcrumbs:start -->' in source:
            source = re.sub(r'<!-- breadcrumbs:start -->.*?<!-- breadcrumbs:end -->', lambda _: breadcrumb, source, flags=re.S)
        else:
            source = source.replace('<main>', '<main>\n' + breadcrumb, 1)
        path.write_text(source)
    print(f'Updated navigation on {len(pages)} pages.')


if __name__ == '__main__':
    build()
