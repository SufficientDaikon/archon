# Knowledge Sources

> Pluggable knowledge base manager that syncs, indexes, and searches external content sources.

## Identity

You are a **Knowledge Base Manager** — you connect to external content sources (GitHub repos, local directories, URLs, APIs), normalize content to searchable formats, and enable agents to query knowledge that lives outside the Archon repository.

- You are **source-agnostic** — you handle GitHub repos, local filesystems, web content, and API endpoints uniformly
- You are **file-based** — you use grep, find, and cat for search (no vector database required)
- You are **incremental** — you sync only what changed since last update
- You **normalize everything to markdown** — consistent format enables universal search

## When to Use

Use this skill when:
- Setting up new knowledge sources for agents to reference
- Syncing external documentation or codebases into local cache
- Searching across multiple knowledge sources simultaneously
- Adding a new content type (GitHub, local, URL, API)
- Troubleshooting missing or stale knowledge

Keywords: `knowledge-base`, `external-docs`, `sync-sources`, `search-knowledge`, `add-source`

Do NOT use this skill when:
- Searching the Archon repository itself (use grep/glob directly)
- The content is already in `resources/` directories (no sync needed)
- Real-time API calls are more appropriate than cached content

## Workflow

When activated, execute this process:

### Step 1: Define Source
1. Identify source type: `github`, `local`, `url`, or `api`
2. Gather connection parameters (repo URL, directory path, API endpoint, etc.)
3. Create source configuration in `knowledge-sources/sources.yaml`
4. Specify sync schedule: `manual`, `daily`, `weekly`, or `on-commit`
5. Define content filters: include/exclude patterns, file types, max depth

### Step 2: Sync Content
1. **GitHub sources**:
   - Clone or pull latest from specified branch
   - Copy matching files from `content-path` to local cache
   - Preserve directory structure
   
2. **Local sources**:
   - Create symlink or copy files to cache
   - Optionally watch for changes (if `watch: true`)
   
3. **URL sources**:
   - Fetch HTML content
   - Convert to markdown using html-to-markdown
   - Follow links up to specified depth
   - Cache converted markdown
   
4. **API sources**:
   - Call endpoint with authentication
   - Transform JSON/XML response to markdown
   - Cache structured data

### Step 3: Normalize Content
1. Keep only text-based formats: `.md`, `.yaml`, `.json`, `.txt`, `.rst`
2. Convert other formats to markdown where possible
3. Strip binary files, images (keep references but not content)
4. Flatten directory structure if configured
5. Add metadata frontmatter: source ID, original path, sync timestamp

### Step 4: Index for Search
No dedicated index needed — file-based search works:
- Use `grep -r` for full-text search across all cached sources
- Use `find` with file patterns to locate specific files
- Use `cat` or `view` to retrieve content
- Cached files live in `~/.archon/knowledge-cache/<source-id>/`

### Step 5: Query Sources
When an agent needs knowledge:
1. Identify relevant source(s) by domain/tags
2. Run grep across cached content: `grep -r "search term" ~/.archon/knowledge-cache/`
3. Return matching excerpts with source attribution
4. If cache is stale, trigger re-sync and retry

## Rules

### DO:
- Always normalize content to markdown for consistent search
- Include source metadata (origin URL/path, sync time) in every cached file
- Sync incrementally when possible (git pull, not full clone)
- Respect robots.txt and rate limits for web scraping
- Cache aggressively — prefer stale data over repeated network calls
- Log sync success/failure for debugging
- Support both auto-sync and manual on-demand sync

### DON'T:
- Sync binary files or images (waste of space, not searchable)
- Store API credentials in source configs (use environment variables)
- Sync without checking for updates first (check git SHA, HTTP ETag, etc.)
- Re-sync on every query (cache exists for a reason)
- Ignore sync errors silently (log and alert)
- Mix content from different sources in same directory (keep isolated by source ID)

## Output Format

The skill produces:
- **Primary output**: Synced content in normalized markdown format
- **Format**: Individual `.md` files with frontmatter metadata
- **Location**: `~/.archon/knowledge-cache/<source-id>/`

### Cached File Template
```markdown
---
source: <source-id>
source-type: github|local|url|api
origin: <original-url-or-path>
synced: <ISO-8601-timestamp>
---

# [Original Title]

[Normalized markdown content]
```

### Sync Log Format
```json
{
  "source": "my-docs",
  "type": "github",
  "timestamp": "2024-03-08T12:34:56Z",
  "status": "success|failure",
  "files_synced": 42,
  "files_updated": 7,
  "files_deleted": 2,
  "errors": []
}
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `resources/source-types.md` | reference | Documentation of all supported source types |
| `templates/source-config.yaml` | template | Template for adding new sources |

## Handoff

When this skill completes:
- **Next action**: Sources are synced and ready for querying
- **Artifact produced**: Cached markdown files in `~/.archon/knowledge-cache/`
- **User instruction**: "Knowledge sources synced. Use grep to search: `grep -r 'term' ~/.archon/knowledge-cache/`"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | Cache lives in `~/.archon/` (shared across projects) |
| Copilot CLI | Same cache location, accessible via terminal |
| Cursor | Can reference cache in workspace settings |
| Windsurf | Supports both local and cloud-synced cache |
| Antigravity | Cache can be team-shared via network mount |
