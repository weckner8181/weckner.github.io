from pathlib import Path
from html.parser import HTMLParser
import unittest
import json
import re
import hashlib

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links = []
        self.open_branches = []
        self.summaries = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.links.append(attrs)
        if tag == 'details' and 'open' in attrs:
            self.open_branches.append(attrs.get('data-page'))
        if tag == 'summary':
            self.summaries.append(attrs)

class NavigationTests(unittest.TestCase):
    def test_live_navigation_has_only_home_and_publications(self):
        nodes = json.loads((ROOT / 'scripts/navigation.json').read_text())
        self.assertEqual([n['path'] for n in nodes], ['index.html', 'publications.html'])
        for node in nodes:
            text = (ROOT / node['path']).read_text()
            self.assertNotIn('physics-notes', text)
            self.assertEqual(Page(ROOT / node['path']).summaries, [])

    def test_physics_notes_are_archived_and_excluded(self):
        self.assertFalse((ROOT / 'physics-notes.html').exists())
        self.assertFalse((ROOT / 'physics-notes').exists())
        self.assertTrue((ROOT / '_archive/physics-notes.html').is_file())
        self.assertEqual(len(list((ROOT / '_archive/physics-notes').rglob('*.html'))), 7)
        self.assertIn('  - _archive', (ROOT / '_config.yml').read_text())
        self.assertFalse((ROOT / '.nojekyll').exists())

    def test_deep_page_opens_only_ancestors(self):
        path = ROOT / '_archive/physics-notes/atomic-physics/zeeman-effect/example.html'
        self.assertTrue(path.is_file(), 'Deep example page must exist')
        page = Page(path)
        self.assertEqual(page.open_branches, [
            'physics-notes.html',
            'physics-notes/atomic-physics/index.html',
            'physics-notes/atomic-physics/zeeman-effect/index.html',
        ])
        self.assertEqual(len([a for a in page.links if a.get('aria-current') == 'page']), 1)
        self.assertIn('aria-label="Breadcrumb"', path.read_text())

    def test_all_pages_have_correct_ancestors_and_headers(self):
        def walk(nodes, ancestors=()):
            for node in nodes:
                path = ROOT / node['path']
                source = path.read_text()
                page = Page(path)
                self.assertEqual(page.open_branches, list(ancestors))
                self.assertEqual(len([a for a in page.links if a.get('aria-current') == 'page']), 1)
                header = re.search(r'<header>(.*?)</header>', source, re.S).group(1)
                if node['path'] == 'index.html':
                    self.assertIn('William Eckner', header)
                    self.assertIn('Postdoctoral researcher @ the PTB', header)
                else:
                    expected = 'Publications' if node['path'] == 'publications.html' else 'Physics notes'
                    self.assertIn(f'<h1>{expected}</h1>', header)
                    self.assertNotIn('<p>', header)
                walk(node.get('children', []), (*ancestors, node['path']))
        walk(json.loads((ROOT / 'scripts/navigation.json').read_text()))

    def test_pages_request_current_stylesheet(self):
        version = hashlib.sha256((ROOT / 'style.css').read_bytes()).hexdigest()[:12]
        for path in ROOT.rglob('*.html'):
            if '_archive' in path.relative_to(ROOT).parts:
                continue
            href = re.search(r'<link rel="stylesheet" href="([^"]+)"', path.read_text()).group(1)
            self.assertEqual(href.split('?')[-1], f'v={version}', str(path))
            self.assertEqual((path.parent / href.split('?')[0]).resolve(), ROOT / 'style.css')

    def test_local_links_resolve(self):
        for path in ROOT.rglob('*.html'):
            if '.git' in path.parts or '_archive' in path.relative_to(ROOT).parts:
                continue
            for link in Page(path).links:
                href = link.get('href', '')
                if href and not href.startswith(('https:', 'http:', 'mailto:', '#')):
                    self.assertTrue((path.parent / href.split('#')[0]).is_file(), f'{path}: {href}')

if __name__ == '__main__':
    unittest.main()
