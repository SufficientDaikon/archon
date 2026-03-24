# Knowledge Source Types Reference

This document describes all supported knowledge source types and their configuration options.

## Source Type: GitHub

**Description**: Sync content from GitHub repositories (public or authenticated private).

**Use cases**:

- External documentation repositories
- Reference codebases
- Open-source library docs
- Team knowledge repos

**Configuration**:

```yaml
sources:
  - id: example-docs
    type: github
    repo: owner/repository # Required: GitHub repo in owner/repo format
    branch: main # Optional: branch to sync (default: main)
    content-path: docs # Optional: subdirectory to sync (default: entire repo)
    auth: $GITHUB_TOKEN # Optional: for private repos (env var)
    sync-schedule: daily # Optional: manual, daily, weekly, on-commit
    include: # Optional: file patterns to include
      - "*.md"
      - "*.yaml"
    exclude: # Optional: file patterns to exclude
      - "**/node_modules/**"
      - "**/.git/**"
```

**Sync behavior**:

1. On first sync: `git clone --depth 1 --branch <branch> <repo-url>`
2. On subsequent syncs: `git pull origin <branch>` (incremental)
3. Copy files matching `include` patterns from `content-path` to cache
4. Skip files matching `exclude` patterns

**Authentication**:

- Set `GITHUB_TOKEN` environment variable for private repos
- Token needs `repo` scope for private, `public_repo` for public
- Falls back to unauthenticated for public repos if no token

---

## Source Type: Local

**Description**: Sync content from local filesystem directories.

**Use cases**:

- Personal notes directories
- Local documentation
- Project-specific knowledge bases
- Workspace-specific resources

**Configuration**:

```yaml
sources:
  - id: my-notes
    type: local
    path: ~/notes # Required: absolute or ~-relative path
    watch: true # Optional: watch for file changes (default: false)
    sync-schedule: manual # Optional: for non-watched dirs
    include:
      - "*.md"
      - "*.txt"
    exclude:
      - "**/.DS_Store"
      - "**/drafts/**"
```

**Sync behavior**:

1. If `watch: true`: Create file watcher, sync on any file change
2. If `watch: false`: Copy files on manual sync or schedule
3. Symlink option: Set `symlink: true` to create symlink instead of copy (faster, but cache not portable)

**Notes**:

- Paths are resolved relative to home directory if using `~`
- Watch mode uses platform file watchers (inotify on Linux, FSEvents on macOS, etc.)
- Watch mode increases resource usage — use only for frequently updated dirs

---

## Source Type: URL

**Description**: Fetch and convert web content to markdown.

**Use cases**:

- Online documentation sites
- Blog posts or articles
- API references
- Tutorial sites

**Configuration**:

```yaml
sources:
  - id: some-docs
    type: url
    url: https://docs.example.com/ # Required: starting URL
    depth: 2 # Optional: how many levels of links to follow (default: 0)
    follow-external: false # Optional: follow links to other domains (default: false)
    sync-schedule: weekly # Optional: how often to re-fetch
    selectors: # Optional: CSS selectors to extract content
      include: ["main", "article", ".content"]
      exclude: ["nav", "footer", ".ad"]
```

**Sync behavior**:

1. Fetch HTML from URL
2. Convert to markdown using html-to-markdown (preserves headings, lists, code blocks, links)
3. If `depth > 0`, extract links from converted content
4. Follow links up to `depth` levels
5. If `selectors` provided, extract only matching elements before conversion
6. Cache each page as separate `.md` file with URL-based filename

**HTML to Markdown conversion**:

- Headings: `<h1>` → `#`, `<h2>` → `##`, etc.
- Lists: `<ul>/<ol>` → markdown lists
- Code: `<pre><code>` → fenced code blocks with language detection
- Links: `<a href>` → `[text](url)`
- Images: `<img>` → `![alt](url)` (reference only, image not downloaded)
- Tables: `<table>` → markdown tables

**Rate limiting**:

- Default: 1 request per second
- Respects `robots.txt`
- Honors `Retry-After` headers

---

## Source Type: API

**Description**: Fetch structured data from APIs and transform to markdown.

**Use cases**:

- REST API documentation from OpenAPI/Swagger
- GraphQL schema documentation
- Internal API catalogs
- Configuration data from APIs

**Configuration**:

```yaml
sources:
  - id: api-docs
    type: api
    endpoint: https://api.example.com/docs # Required: API endpoint
    method: GET # Optional: HTTP method (default: GET)
    headers: # Optional: request headers
      Authorization: Bearer $API_TOKEN
      Accept: application/json
    transform: openapi-to-markdown # Optional: transformation strategy
    sync-schedule: daily
```

**Sync behavior**:

1. Send HTTP request to endpoint with specified method and headers
2. Parse JSON or XML response
3. Apply transformation based on `transform` strategy:
   - `openapi-to-markdown`: Convert OpenAPI spec to markdown API docs
   - `json-to-markdown`: Pretty-print JSON as markdown code blocks with descriptions
   - `custom`: Use custom transformation script (must be in `scripts/transforms/`)
4. Cache transformed markdown

**Supported transformations**:

- **openapi-to-markdown**: Generates endpoint documentation from OpenAPI 3.x specs
- **json-to-markdown**: Wraps JSON in markdown with auto-generated descriptions
- **graphql-to-markdown**: Converts GraphQL schema to markdown documentation
- **custom**: Python script in `scripts/transforms/<name>.py` with `transform(data) -> markdown` function

**Authentication**:

- Use environment variables for tokens: `$API_TOKEN`, `$API_KEY`, etc.
- Supports Bearer, Basic, and custom auth headers
- Never hardcode credentials in config files

---

## Configuration File: sources.yaml

All sources are defined in `knowledge-sources/sources.yaml`:

```yaml
# Global settings
cache-dir: ~/.archon/knowledge-cache # Where synced content lives
max-cache-size: 1GB # Delete oldest content if exceeded
log-file: ~/.archon/logs/sync.log # Sync operation logs

# Source definitions
sources:
  - id: django-docs
    type: github
    repo: django/django
    branch: stable/5.0.x
    content-path: docs
    sync-schedule: weekly
    include: ["*.txt", "*.md"]

  - id: my-notes
    type: local
    path: ~/Dropbox/notes
    watch: false
    sync-schedule: daily

  - id: vercel-docs
    type: url
    url: https://vercel.com/docs
    depth: 1
    sync-schedule: weekly

  - id: internal-api
    type: api
    endpoint: https://api.internal.com/openapi.json
    headers:
      Authorization: Bearer $INTERNAL_API_TOKEN
    transform: openapi-to-markdown
    sync-schedule: daily
```

## Sync Commands

Via SDK:

```python
from archon import Archon
os = Archon()

# Sync all sources
os.sync_sources()

# Sync specific source
os.sync_sources(source_id="django-docs")

# Force re-sync (ignore cache)
os.sync_sources(force=True)
```

Via CLI:

```bash
# Sync all sources
python scripts/admin.py --sync

# Sync specific source
python scripts/admin.py --sync django-docs

# Force re-sync
python scripts/admin.py --sync --force
```

## Search Cached Content

Once synced, search with grep:

```bash
# Search all cached sources
grep -r "authentication" ~/.archon/knowledge-cache/

# Search specific source
grep -r "models" ~/.archon/knowledge-cache/django-docs/

# Case-insensitive with context
grep -ri -C 3 "middleware" ~/.archon/knowledge-cache/
```

Or via SDK:

```python
results = os.search_knowledge("authentication")
for result in results:
    print(f"{result.source}: {result.file} - {result.excerpt}")
```
