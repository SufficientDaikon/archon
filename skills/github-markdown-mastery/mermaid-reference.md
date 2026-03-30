# Mermaid Diagrams — Full Reference for GitHub

## Check GitHub's Mermaid Version

````markdown
```mermaid
info
```
````

This renders the version number. GitHub lags behind upstream Mermaid releases.

## Compatibility Tiers

| Tier | Diagram Types | Notes |
|------|--------------|-------|
| **Confirmed working** | Flowchart, Sequence, Class, State, ER, Gantt, Pie, Git Graph, User Journey, Mindmap, Timeline, Requirement | Pre-v10, long-established |
| **Very likely working** | Quadrant, Sankey (`sankey-beta`), XY Chart (`xychart-beta`), Block (`block-beta`), C4 | v10.2-10.8 |
| **Uncertain** | Packet (`packet-beta`), Architecture (`architecture-beta`) | Requires v11.0+ |
| **Unlikely on GitHub** | Kanban, Radar, Treemap, Venn, Ishikawa | Requires v11.4+ |
| **Confirmed broken** | ZenUML | Does not render at all |

**Always use `-beta` suffixes** for Sankey, XY Chart, Block, Packet, Architecture on GitHub.

## What Does NOT Work on GitHub's Mermaid

- `click` directives — blocked by iframe sandbox ("This content is blocked")
- Font Awesome icons — not loaded in GitHub's renderer
- ELK layout engine — not enabled
- External links in nodes — same sandbox restriction
- ZenUML — does not render
- `%%{init: ...}%%` directives — partial/inconsistent support

---

## All Diagram Types with Examples

### 1. Flowchart

**Keyword:** `flowchart` or `graph`

````markdown
```mermaid
flowchart TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great]
    B -->|No| D[Debug]
    D --> B
```
````

**Directions:** `TD`/`TB` (top-down), `LR` (left-right), `BT` (bottom-top), `RL` (right-left)

**Node shapes:**
- `[text]` — rectangle
- `(text)` — rounded
- `{text}` — diamond (decision)
- `([text])` — stadium
- `[[text]]` — subroutine
- `[(text)]` — cylinder
- `((text))` — circle
- `>text]` — asymmetric
- `{{text}}` — hexagon
- `[/text/]` — parallelogram
- `[\text\]` — reverse parallelogram
- `[/text\]` — trapezoid
- `[\text/]` — reverse trapezoid

**Arrow types:**
- `-->` — solid arrow
- `---` — solid line (no arrow)
- `-.->` — dotted arrow
- `==>` — thick arrow
- `--text-->` — labeled arrow
- `-->|text|` — labeled arrow (alt)

**Subgraphs:**
```
subgraph title
    A --> B
end
```

### 2. Sequence Diagram

**Keyword:** `sequenceDiagram`

````markdown
```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob
    B-->>A: Hi Alice
    A->>B: How are you?
    Note right of B: Bob thinks
    B-->>A: Great!
```
````

**Arrow types:**
- `->` — solid line (no arrowhead)
- `-->` — dotted line (no arrowhead)
- `->>` — solid line with arrowhead
- `-->>` — dotted line with arrowhead
- `-x` — solid line with cross
- `--x` — dotted line with cross
- `-)` — solid line with open arrow (async)
- `--)` — dotted line with open arrow (async)

**Features:**
- `activate`/`deactivate` or `+`/`-` suffixes on arrows
- `Note left of`/`right of`/`over` for notes
- `loop`/`alt`/`opt`/`par`/`critical`/`break`/`rect` blocks
- `autonumber` for automatic numbering
- `actor` instead of `participant` for stick figures

### 3. Class Diagram

**Keyword:** `classDiagram`

````markdown
```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
    class Dog {
        +fetch() void
    }
    Animal <|-- Dog
```
````

**Relationships:**
- `<|--` — inheritance
- `*--` — composition
- `o--` — aggregation
- `-->` — association
- `..>` — dependency
- `..|>` — realization

**Visibility:** `+` public, `-` private, `#` protected, `~` package

### 4. State Diagram

**Keyword:** `stateDiagram-v2`

````markdown
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: start()
    Processing --> Done: complete()
    Processing --> Error: fail()
    Error --> Idle: retry()
    Done --> [*]
```
````

**Features:**
- `[*]` — start/end state
- `state "Description" as s1` — aliased states
- `--` — notes
- Composite states via nested `state Name { ... }`
- `<<fork>>` and `<<join>>` for concurrent states
- `<<choice>>` for conditional branching

### 5. Entity Relationship Diagram

**Keyword:** `erDiagram`

````markdown
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
```
````

**Cardinality notation:**
- `||` — exactly one
- `o|` — zero or one
- `}|` — one or more
- `o{` — zero or more

**Line types:** `--` solid (identifying), `..` dashed (non-identifying)

**Attributes:**
```
CUSTOMER {
    string name PK
    string email
    int age
}
```

### 6. Gantt Chart

**Keyword:** `gantt`

````markdown
```mermaid
gantt
    title Project Schedule
    dateFormat YYYY-MM-DD
    section Design
    Mockups     :a1, 2024-01-01, 14d
    Review      :a2, after a1, 7d
    section Build
    Backend     :b1, after a2, 21d
    Frontend    :b2, after a2, 28d
    section Test
    QA          :after b1, 14d
```
````

**Task modifiers:** `done`, `active`, `crit` (critical path), `milestone`

### 7. Pie Chart

**Keyword:** `pie`

````markdown
```mermaid
pie title Language Distribution
    "TypeScript" : 45
    "Python" : 30
    "Shell" : 15
    "Other" : 10
```
````

Values are relative — automatically computed as percentages.

### 8. Git Graph

**Keyword:** `gitGraph`

````markdown
```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "feature-a"
    commit id: "feature-b"
    checkout main
    merge develop id: "merge" tag: "v1.0"
    commit id: "hotfix"
```
````

**Commands:** `commit`, `branch`, `checkout`, `merge`, `cherry-pick`

### 9. User Journey

**Keyword:** `journey`

````markdown
```mermaid
journey
    title User Login Flow
    section Authentication
      Open app: 5: User
      Enter credentials: 3: User
      Wait for 2FA: 2: User, System
    section Dashboard
      View dashboard: 4: User
      Check notifications: 3: User
```
````

Score is 1-5 (1 = frustrating, 5 = great). Actors listed after score.

### 10. Mindmap

**Keyword:** `mindmap`

````markdown
```mermaid
mindmap
    root((Project))
        Frontend
            React
            CSS Modules
        Backend
            Node.js
            PostgreSQL
        Infrastructure
            Docker
            AWS
```
````

Hierarchy is indentation-based. Root can use shapes: `((circle))`, `[square]`, `(rounded)`.

### 11. Timeline

**Keyword:** `timeline`

````markdown
```mermaid
timeline
    title Release History
    2023 : v1.0 Initial release
         : v1.1 Bug fixes
    2024 : v2.0 Major rewrite
         : v2.1 Performance improvements
    2025 : v3.0 API overhaul
```
````

### 12. Quadrant Chart

**Keyword:** `quadrantChart`

````markdown
```mermaid
quadrantChart
    title Effort vs Impact
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Do First
    quadrant-2 Schedule
    quadrant-3 Delegate
    quadrant-4 Eliminate
    Feature A: [0.2, 0.8]
    Feature B: [0.7, 0.9]
    Feature C: [0.8, 0.2]
```
````

Coordinates are [0,1] range for both axes.

### 13. Sankey Diagram

**Keyword:** `sankey-beta` (use `-beta` on GitHub)

````markdown
```mermaid
sankey-beta

Source A,Target X,30
Source A,Target Y,20
Source B,Target X,15
Source B,Target Y,35
```
````

CSV format: source, target, value. Blank lines between rows are fine.

### 14. XY Chart

**Keyword:** `xychart-beta` (use `-beta` on GitHub)

````markdown
```mermaid
xychart-beta
    title "Monthly Revenue"
    x-axis [Jan, Feb, Mar, Apr, May]
    y-axis "Revenue ($K)" 0 --> 100
    bar [52, 78, 61, 89, 95]
    line [52, 78, 61, 89, 95]
```
````

Supports `bar` and `line` series. Use `xychart-beta horizontal` for horizontal.

### 15. Block Diagram

**Keyword:** `block-beta` (use `-beta` on GitHub)

````markdown
```mermaid
block-beta
    columns 3
    Frontend blockArrowId<["  "]>(right) Backend
    space:2 Database
```
````

Grid-based layout with `columns N`. `space` creates empty cells. `space:2` spans two.

### 16. C4 Context Diagram

**Keyword:** `C4Context` / `C4Container` / `C4Component` / `C4Dynamic` / `C4Deployment`

````markdown
```mermaid
C4Context
    title System Context
    Person(user, "User", "End user of the system")
    System(app, "Application", "Main application")
    System_Ext(email, "Email System", "Sends emails")
    Rel(user, app, "Uses")
    Rel(app, email, "Sends via")
```
````

### 17. Requirement Diagram

**Keyword:** `requirementDiagram`

````markdown
```mermaid
requirementDiagram
    requirement test_req {
        id: REQ-01
        text: System shall respond in <100ms
        risk: high
        verifymethod: test
    }
    element test_entity {
        type: simulation
    }
    test_entity - satisfies -> test_req
```
````

### 18. Packet Diagram (v11+, uncertain on GitHub)

**Keyword:** `packet-beta`

````markdown
```mermaid
packet-beta
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
```
````

### 19. Architecture Diagram (v11.1+, uncertain on GitHub)

**Keyword:** `architecture-beta`

````markdown
```mermaid
architecture-beta
    group api(cloud)[API Layer]
    service db(database)[PostgreSQL] in api
    service server(server)[Node.js] in api
    db:R -- L:server
```
````

Built-in icons: `cloud`, `database`, `server`, `disk`, `internet`.
