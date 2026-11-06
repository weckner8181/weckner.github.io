# weckner.github.io
Personal webpage

## Style reference

Top-level page names appear only in the top header, not again at the start
of the main content. Home is the exception: keep the name and role in its
header and “Welcome!” in its content. Subpages retain their own title beneath
the breadcrumbs, with the top-level section name in the header.

For a future contextual back link, retain the former Physics notes style:
`<p><a href="index.html">« Back to homepage</a></p>` — a plain, underlined
text link using the existing link color, prefixed with `«`. Adjust the label
and relative destination as appropriate. Do not add this link to Physics notes;
the sidebar and breadcrumbs provide navigation there.

## Nested pages and navigation

Only Home and Publications are currently published. The Physics notes pages
and original navigation hierarchy are preserved in `_archive/`, which is
excluded from the GitHub Pages build by `_config.yml`. These files are source
examples; their relative links retain their original locations.

To restore Physics notes, move `_archive/physics-notes.html` and
`_archive/physics-notes/` back to the repository root, merge its branch from
`_archive/navigation.json` into `scripts/navigation.json`, and run the
navigation script. Update the live-page checks in `tests/test_navigation.py`
to reflect the restored section.

The site is static HTML. Arrows use native `details`/`summary` controls; page
links navigate independently. Only the current page's ancestors start open.

To add a page:

1. Copy a nearby HTML page and edit its title and main content. Adjust the
   stylesheet URL for its folder depth.
2. Add its title and repository-relative path beneath the appropriate parent
   in `scripts/navigation.json`. Topic and year/month/day branches work alike.
3. Add a link on the parent index page so its contents remain discoverable.
4. Run `python3 scripts/build_navigation.py` to refresh navigation and
   breadcrumbs on every page, then `python3 -m unittest discover -s tests`.
5. Commit the HTML files along with the hierarchy change. GitHub Pages serves
   the generated HTML directly; no build or JavaScript is needed for navigation.

Run the navigation script after changing `style.css` too. It versions each
page's stylesheet URL using the CSS content hash so browsers fetch updated
styles instead of reusing an older cached copy.

The sample topic and date pages are marked as examples and can be replaced or
removed. Keep large archives divided by year/month so each expanded branch
remains short. The full navigation is present in the HTML; for a very large
archive, a later build can limit it to the active branch to reduce page size.
