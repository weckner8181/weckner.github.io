# Collapsible navigation implementation plan

Goal: Keep the existing static site style while adding independently expandable branches and linked page titles.

Architecture: A shared JSON hierarchy and Python script generate static navigation and breadcrumbs in each page. Native details/summary controls work without JavaScript. Only ancestors of the current page start open. Existing content remains static HTML.

- Add checks for collapsed Home navigation, expanded ancestor paths, current-page markers, and local links.
- Add sample topic and date pages, retaining the existing Zeeman text on its own page.
- Generate shared navigation and breadcrumbs; style narrow screens and keyboard focus.
- Run checks, inspect browser behavior if available, then commit, push, and verify synchronization.
