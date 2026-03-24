#!/usr/bin/env python3
"""
Archon v2.0 — Documentation Builder
Converts Markdown docs to beautiful HTML with Mermaid diagram rendering.
ASCII art diagrams are automatically detected and replaced with Mermaid.js diagrams.
"""

import re
import os
import sys
from pathlib import Path

try:
    import markdown
    from markdown.extensions.toc import TocExtension
except ImportError:
    print("Installing markdown library...")
    os.system(f"{sys.executable} -m pip install markdown --quiet")
    import markdown
    from markdown.extensions.toc import TocExtension

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
HTML_DIR = DOCS_DIR / "html"
ROOT_FILES = ["README.md", "CHANGELOG.md", "CONTRIBUTING.md"]

# ─── Mermaid Diagram Mappings ────────────────────────────────────────────────
# Each key is (filename, diagram_index) → mermaid code
# diagram_index is the 0-based index of ASCII-art code blocks in that file

MERMAID_MAPS = {
    # architecture.md — 5 diagrams
    ("architecture.md", 0): """block-beta
    columns 1
    block:L4["Layer 4: ARTIFACT LAYER\\nPipeline outputs, validated JSON, audit trails"]:1
    end
    block:L3["Layer 3: PIPELINE LAYER\\nsdd | ux | debug | skill-factory | full-product"]:1
    end
    block:L2["Layer 2: SKILL LAYER\\n48+ skills, each with manifest.yaml"]:1
    end
    block:L1["Layer 1: AGENT LAYER\\n9 agents with guardrails & manifests"]:1
    end
    block:L0["Layer 0: BOOTSTRAP & DISCIPLINE\\nHooks, synapses, anti-rationalization"]:1
    end

    style L4 fill:#4CAF50,color:#fff,stroke:#388E3C
    style L3 fill:#2196F3,color:#fff,stroke:#1565C0
    style L2 fill:#FF9800,color:#fff,stroke:#E65100
    style L1 fill:#9C27B0,color:#fff,stroke:#6A1B9A
    style L0 fill:#F44336,color:#fff,stroke:#C62828""",

    ("architecture.md", 1): """flowchart TD
    A["🚀 session_start hook"] --> B["Load core synapses"]
    B --> B1["anti-rationalization.md"]
    B --> B2["sequential-thinking.md"]
    B --> B3["metacognition.md"]
    A --> C["Inject anti-rationalization rules"]
    C --> C1["10 Iron Laws activated"]
    A --> D["Inject sequential thinking protocol"]
    D --> D1["[THINKING] blocks required"]
    A --> E["Inject metacognition synapse"]
    E --> E1["Complexity scaling activated"]

    style A fill:#F44336,color:#fff
    style B fill:#FF9800,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#FF9800,color:#fff
    style E fill:#FF9800,color:#fff""",

    ("architecture.md", 2): """flowchart TD
    U["👤 User Request"] --> AG["🤖 Agent\\n(guardrails active)"]
    AG --> S1["Skill A\\n(focused capability)"]
    AG --> S2["Skill B\\n(focused capability)"]
    AG --> S3["Skill C\\n(focused capability)"]
    S1 --> O["✅ Validated Output"]
    S2 --> O
    S3 --> O

    style U fill:#607D8B,color:#fff
    style AG fill:#9C27B0,color:#fff
    style S1 fill:#FF9800,color:#fff
    style S2 fill:#FF9800,color:#fff
    style S3 fill:#FF9800,color:#fff
    style O fill:#4CAF50,color:#fff""",

    ("architecture.md", 3): """stateDiagram-v2
    [*] --> pending
    pending --> validating : validate
    validating --> executing : execute
    executing --> paused : pause/deviation
    paused --> executing : resume
    executing --> completed : all steps done
    executing --> failed : unrecoverable error
    executing --> cancelled : user cancel

    state executing {
        [*] --> step_loop
        step_loop --> step_loop : next step
    }""",

    ("architecture.md", 4): """flowchart TD
    U["👤 User: build feature X"] --> L0["Layer 0: Bootstrap fires"]
    L0 --> L3["Layer 3: Pipeline selects sdd-pipeline"]
    L3 --> SW["Layer 1: spec-writer agent"]
    SW --> SWS["Layer 2: spec-writer skill"]
    SWS --> SWA["Layer 4: spec artifact"]
    L3 --> CC1["Layer 1: context-curator curates"]
    L3 --> IM["Layer 1: implementer agent"]
    IM --> IMS["Layer 2: implementer skill"]
    IMS --> IMA["Layer 4: code artifact"]
    L3 --> CC2["Layer 1: context-curator curates"]
    L3 --> RV["Layer 1: reviewer agent"]
    RV --> RVS["Layer 2: reviewer skill"]
    RVS --> RVA["Layer 4: review report"]

    style U fill:#607D8B,color:#fff
    style L0 fill:#F44336,color:#fff
    style L3 fill:#2196F3,color:#fff
    style SW fill:#9C27B0,color:#fff
    style IM fill:#9C27B0,color:#fff
    style RV fill:#9C27B0,color:#fff
    style CC1 fill:#00BCD4,color:#fff
    style CC2 fill:#00BCD4,color:#fff
    style SWS fill:#FF9800,color:#fff
    style IMS fill:#FF9800,color:#fff
    style RVS fill:#FF9800,color:#fff
    style SWA fill:#4CAF50,color:#fff
    style IMA fill:#4CAF50,color:#fff
    style RVA fill:#4CAF50,color:#fff""",

    # pipeline-orchestration.md — 1 diagram (the curation flow)
    ("pipeline-orchestration.md", 0): """flowchart TD
    SW["📝 spec-writer"] -->|"full spec ~3000 words"| CC1["🔄 context-curator"]
    CC1 -->|"curated ~800 words"| IM["⚙️ implementer"]
    IM -->|"full impl ~5000 words"| CC2["🔄 context-curator"]
    CC2 -->|"curated ~1200 words"| RV["✅ reviewer"]
    RV --> RP["📊 review report"]

    style SW fill:#9C27B0,color:#fff
    style CC1 fill:#00BCD4,color:#fff
    style IM fill:#FF9800,color:#fff
    style CC2 fill:#00BCD4,color:#fff
    style RV fill:#4CAF50,color:#fff
    style RP fill:#607D8B,color:#fff""",

    # sequential-thinking.md — 2 diagrams
    ("sequential-thinking.md", 0): """flowchart LR
    D["🔍 DECOMPOSE"] --> R["🧠 REASON"]
    R --> V["✓ VALIDATE"]
    V --> S["📋 SYNTHESIZE"]

    style D fill:#2196F3,color:#fff
    style R fill:#FF9800,color:#fff
    style V fill:#4CAF50,color:#fff
    style S fill:#9C27B0,color:#fff""",

    ("sequential-thinking.md", 1): """flowchart LR
    DT["🔎 DETECT"] --> HY["💡 HYPOTHESIZE"]
    HY --> EN["📋 ENUMERATE"]
    EN --> VR["✅ VERIFY"]
    VR --> CO["🔄 CONTINUE"]
    CO -.->|"questions remain"| DT

    style DT fill:#F44336,color:#fff
    style HY fill:#FF9800,color:#fff
    style EN fill:#2196F3,color:#fff
    style VR fill:#4CAF50,color:#fff
    style CO fill:#9C27B0,color:#fff""",

    # guardrails.md — 1 diagram (quick reference hierarchy)
    ("guardrails.md", 0): """flowchart TD
    SYS["🛡️ System Level\\n10 Iron Laws (always on)"] --> AGT["🤖 Agent Level\\nagent-manifest.yaml guardrails"]
    AGT --> STP["⚙️ Step Level\\nPipeline YAML constraints"]
    STP --> DET["🔍 Detection\\npre_step.py + post_step.py"]
    DET --> RSP["🚨 Response\\nSTOP → DOCUMENT → ASK → LOG"]

    style SYS fill:#F44336,color:#fff
    style AGT fill:#9C27B0,color:#fff
    style STP fill:#2196F3,color:#fff
    style DET fill:#FF9800,color:#fff
    style RSP fill:#4CAF50,color:#fff""",
}

# Characters that indicate ASCII art in a code block
ASCII_ART_CHARS = set("┌┐└┘├┤┬┴─│▼▲►◄═╔╗╚╝╠╣╦╩")


def is_ascii_art_block(code_content: str) -> bool:
    """Detect if a code block contains ASCII art diagrams."""
    # Check for box-drawing characters
    if any(ch in code_content for ch in ASCII_ART_CHARS):
        return True
    # Check for arrow-based flow diagrams (→, ►, ->, -->)
    if "→" in code_content and code_content.count("→") >= 2:
        return True
    if ("──►" in code_content or "──>" in code_content):
        return True
    if "│" in code_content and ("├" in code_content or "└" in code_content):
        return True
    return False


def preprocess_markdown(content: str, filename: str) -> str:
    """Replace ASCII art code blocks with Mermaid div blocks."""
    lines = content.split("\n")
    result = []
    in_code_block = False
    code_block_lines = []
    code_block_lang = ""
    ascii_diagram_index = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```") and not in_code_block:
            in_code_block = True
            code_block_lang = line.strip()[3:].strip()
            code_block_lines = []
            i += 1
            continue

        if line.strip() == "```" and in_code_block:
            in_code_block = False
            block_content = "\n".join(code_block_lines)

            # Check if this is an ASCII art block
            if not code_block_lang and is_ascii_art_block(block_content):
                key = (filename, ascii_diagram_index)
                if key in MERMAID_MAPS:
                    mermaid_code = MERMAID_MAPS[key]
                    result.append(f'<div class="mermaid">\n{mermaid_code}\n</div>\n')
                    # Also keep original as collapsed detail
                    escaped = block_content.replace("<", "&lt;").replace(">", "&gt;")
                    result.append(f'<details class="ascii-original"><summary>View original ASCII</summary><pre><code>{escaped}</code></pre></details>')
                else:
                    # No mermaid mapping, keep as styled pre block
                    escaped = block_content.replace("<", "&lt;").replace(">", "&gt;")
                    result.append(f'<pre class="ascii-diagram"><code>{escaped}</code></pre>')
                ascii_diagram_index += 1
            else:
                # Regular code block — keep as-is for markdown to handle
                if code_block_lang:
                    result.append(f"```{code_block_lang}")
                else:
                    result.append("```")
                result.extend(code_block_lines)
                result.append("```")
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
        else:
            result.append(line)
        i += 1

    return "\n".join(result)


def get_nav_items(doc_files: list) -> str:
    """Generate navigation HTML."""
    items = []
    for f in sorted(doc_files):
        name = f.stem
        title = name.replace("-", " ").replace("_", " ").title()
        # Special case titles
        title_map = {
            "README": "Overview",
            "CHANGELOG": "Changelog",
            "CONTRIBUTING": "Contributing",
            "faq": "FAQ",
            "cli-guide": "CLI Guide",
            "llms-txt": "LLMs.txt",
        }
        title = title_map.get(name, title)
        items.append(f'<a href="{name}.html" class="nav-link">{title}</a>')
    return "\n".join(items)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Archon v2.0</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --bg-card: #1c2128;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;
            --accent: #58a6ff;
            --accent-hover: #79c0ff;
            --accent-subtle: #388bfd26;
            --border: #30363d;
            --border-muted: #21262d;
            --green: #3fb950;
            --red: #f85149;
            --orange: #d29922;
            --purple: #bc8cff;
            --pink: #f778ba;
            --cyan: #39d2c0;
            --nav-width: 280px;
            --header-height: 60px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.7;
            font-size: 16px;
        }}

        /* Header */
        .header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--header-height);
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            padding: 0 24px;
            z-index: 100;
            backdrop-filter: blur(12px);
        }}
        .header-brand {{
            font-size: 20px;
            font-weight: 700;
            color: var(--accent);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header-brand span {{ color: var(--text-secondary); font-weight: 400; font-size: 14px; }}
        .header-nav {{
            margin-left: auto;
            display: flex;
            gap: 16px;
        }}
        .header-nav a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.2s;
        }}
        .header-nav a:hover {{ color: var(--accent); }}
        .menu-toggle {{
            display: none;
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 24px;
            cursor: pointer;
            margin-right: 16px;
        }}

        /* Sidebar */
        .sidebar {{
            position: fixed;
            top: var(--header-height);
            left: 0;
            bottom: 0;
            width: var(--nav-width);
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            overflow-y: auto;
            padding: 20px 0;
            z-index: 50;
            transition: transform 0.3s;
        }}
        .sidebar-section {{
            padding: 8px 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-top: 12px;
        }}
        .nav-link {{
            display: block;
            padding: 8px 20px 8px 28px;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 14px;
            border-left: 3px solid transparent;
            transition: all 0.15s;
        }}
        .nav-link:hover {{
            color: var(--text-primary);
            background: var(--accent-subtle);
            border-left-color: var(--accent);
        }}
        .nav-link.active {{
            color: var(--accent);
            background: var(--accent-subtle);
            border-left-color: var(--accent);
            font-weight: 600;
        }}

        /* Main content */
        .main {{
            margin-left: var(--nav-width);
            margin-top: var(--header-height);
            padding: 40px 48px 80px;
            max-width: 920px;
        }}

        /* Typography */
        h1 {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
        }}
        h2 {{
            font-size: 24px;
            font-weight: 600;
            margin-top: 48px;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-muted);
            color: var(--text-primary);
        }}
        h3 {{
            font-size: 20px;
            font-weight: 600;
            margin-top: 32px;
            margin-bottom: 12px;
            color: var(--text-primary);
        }}
        h4 {{
            font-size: 16px;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 8px;
            color: var(--text-primary);
        }}
        p {{
            margin-bottom: 16px;
            color: var(--text-primary);
        }}
        a {{
            color: var(--accent);
            text-decoration: none;
        }}
        a:hover {{ text-decoration: underline; }}

        strong {{ color: var(--text-primary); font-weight: 600; }}

        /* Lists */
        ul, ol {{
            margin: 0 0 16px 24px;
            color: var(--text-primary);
        }}
        li {{ margin-bottom: 6px; }}
        li > ul, li > ol {{ margin-top: 6px; margin-bottom: 0; }}

        /* Code */
        code {{
            font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
            font-size: 85%;
            background: var(--bg-tertiary);
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--orange);
        }}
        pre {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px 20px;
            overflow-x: auto;
            margin: 16px 0;
            line-height: 1.5;
        }}
        pre code {{
            background: none;
            padding: 0;
            color: var(--text-primary);
            font-size: 14px;
        }}

        /* ASCII diagram styling */
        pre.ascii-diagram {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px 24px;
            font-size: 14px;
            line-height: 1.4;
            color: var(--cyan);
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
        }}
        thead {{
            background: var(--bg-tertiary);
        }}
        th {{
            text-align: left;
            padding: 12px 16px;
            font-weight: 600;
            color: var(--text-primary);
            border-bottom: 2px solid var(--border);
        }}
        td {{
            padding: 10px 16px;
            border-bottom: 1px solid var(--border-muted);
            color: var(--text-secondary);
        }}
        tr:hover td {{
            background: var(--accent-subtle);
        }}

        /* Blockquotes */
        blockquote {{
            border-left: 4px solid var(--accent);
            padding: 12px 20px;
            margin: 16px 0;
            background: var(--accent-subtle);
            border-radius: 0 8px 8px 0;
            color: var(--text-secondary);
        }}

        /* Horizontal rule */
        hr {{
            border: none;
            border-top: 1px solid var(--border);
            margin: 32px 0;
        }}

        /* Mermaid diagrams */
        .mermaid {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin: 24px 0;
            text-align: center;
            overflow-x: auto;
        }}

        /* ASCII original toggle */
        details.ascii-original {{
            margin: -16px 0 24px;
            font-size: 13px;
        }}
        details.ascii-original summary {{
            cursor: pointer;
            color: var(--text-muted);
            padding: 4px 0;
            user-select: none;
        }}
        details.ascii-original summary:hover {{
            color: var(--text-secondary);
        }}
        details.ascii-original pre {{
            background: var(--bg-card);
            border: 1px dashed var(--border);
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 8px;
        }}

        /* Badge pills */
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-green {{ background: #238636; color: #fff; }}
        .badge-blue {{ background: #1f6feb; color: #fff; }}
        .badge-purple {{ background: #8957e5; color: #fff; }}
        .badge-red {{ background: #da3633; color: #fff; }}

        /* Footer */
        .footer {{
            margin-top: 64px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
            font-size: 13px;
            color: var(--text-muted);
            text-align: center;
        }}

        /* Responsive */
        @media (max-width: 900px) {{
            .sidebar {{ transform: translateX(-100%); }}
            .sidebar.open {{ transform: translateX(0); }}
            .main {{ margin-left: 0; padding: 24px 20px 60px; }}
            .menu-toggle {{ display: block; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <button class="menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>
        <a href="index.html" class="header-brand">
            ⚡ Archon <span>v2.0 Documentation</span>
        </a>
        <nav class="header-nav">
            <a href="https://github.com/SufficientDaikon/archon" target="_blank">GitHub</a>
            <a href="index.html">Home</a>
        </nav>
    </header>

    <nav class="sidebar">
        <div class="sidebar-section">Getting Started</div>
        {nav_getting_started}
        <div class="sidebar-section">Architecture</div>
        {nav_architecture}
        <div class="sidebar-section">Guides</div>
        {nav_guides}
        <div class="sidebar-section">Reference</div>
        {nav_reference}
    </nav>

    <main class="main">
        {content}
        <div class="footer">
            Archon v2.0 — Enforced Intelligence Framework<br>
            <a href="https://github.com/SufficientDaikon/archon">GitHub</a> ·
            <a href="index.html">Documentation Home</a>
        </div>
    </main>

    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#1f6feb',
                primaryTextColor: '#e6edf3',
                primaryBorderColor: '#30363d',
                lineColor: '#8b949e',
                secondaryColor: '#21262d',
                tertiaryColor: '#161b22',
                fontSize: '14px'
            }},
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            stateDiagram: {{
                useMaxWidth: true
            }}
        }});

        // Highlight active nav link
        const currentPage = location.pathname.split('/').pop() || 'index.html';
        document.querySelectorAll('.nav-link').forEach(link => {{
            if (link.getAttribute('href') === currentPage) {{
                link.classList.add('active');
            }}
        }});
    </script>
</body>
</html>"""


# Navigation structure
NAV_GETTING_STARTED = [
    ("index.html", "📚 Documentation Home"),
    ("Getting-Started.html", "🚀 Getting Started"),
    ("Cli-Guide.html", "💻 CLI Guide"),
    ("Migration-V2.html", "📦 Migration to v2.0"),
]

NAV_ARCHITECTURE = [
    ("Architecture.html", "🏗️ 5-Layer Architecture"),
    ("Pipeline-Orchestration.html", "🔧 Pipeline Orchestration"),
    ("Guardrails.html", "🛡️ Guardrails Engine"),
    ("Sequential-Thinking.html", "🧠 Sequential Thinking"),
]

NAV_GUIDES = [
    ("Creating-Skills.html", "✨ Creating Skills"),
    ("Creating-Agents.html", "🤖 Creating Agents"),
    ("Creating-Pipelines.html", "🔄 Creating Pipelines"),
    ("Creating-Bundles.html", "📦 Creating Bundles"),
    ("Creating-Synapses.html", "🧬 Creating Synapses"),
    ("Platform-Guide.html", "🌐 Platform Guide"),
]

NAV_REFERENCE = [
    ("Agent-Cards.html", "🃏 Agent Cards"),
    ("Integration-Catalog.html", "🔌 Integration Catalog"),
    ("Faq.html", "❓ FAQ"),
    ("Llms-Txt.html", "📄 LLMs.txt"),
    ("Changelog.html", "📋 Changelog"),
    ("Contributing.html", "🤝 Contributing"),
    ("Readme.html", "📖 README"),
]


def build_nav_section(items, active_page=""):
    lines = []
    for href, label in items:
        cls = ' class="nav-link active"' if href == active_page else ' class="nav-link"'
        lines.append(f'<a href="{href}"{cls}>{label}</a>')
    return "\n        ".join(lines)


def md_to_html(md_content: str, filename: str) -> str:
    """Convert markdown to HTML with Mermaid preprocessing."""
    # Preprocess: replace ASCII diagrams with Mermaid
    processed = preprocess_markdown(md_content, filename)

    # Convert MD → HTML
    extensions = [
        'tables',
        'fenced_code',
        'codehilite',
        TocExtension(permalink=False, toc_depth=3),
        'attr_list',
        'md_in_html',
    ]
    extension_configs = {
        'codehilite': {'css_class': 'highlight', 'guess_lang': False},
    }
    html = markdown.markdown(
        processed,
        extensions=extensions,
        extension_configs=extension_configs,
        output_format='html5',
    )
    return html


def get_title(md_content: str, filename: str) -> str:
    """Extract title from first H1."""
    for line in md_content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return filename.replace(".md", "").replace("-", " ").title()


def build_page(md_content: str, filename: str) -> str:
    """Build complete HTML page from markdown content."""
    title = get_title(md_content, filename)
    content = md_to_html(md_content, filename)

    # Determine active page
    page_name = Path(filename).stem.replace("_", "-").title() + ".html"

    page = HTML_TEMPLATE.format(
        title=title,
        content=content,
        nav_getting_started=build_nav_section(NAV_GETTING_STARTED, page_name),
        nav_architecture=build_nav_section(NAV_ARCHITECTURE, page_name),
        nav_guides=build_nav_section(NAV_GUIDES, page_name),
        nav_reference=build_nav_section(NAV_REFERENCE, page_name),
    )
    return page


INDEX_CONTENT = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archon v2.0 — Documentation</title>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --bg-card: #1c2128;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;
            --accent: #58a6ff;
            --accent-hover: #79c0ff;
            --accent-subtle: #388bfd26;
            --border: #30363d;
            --green: #3fb950;
            --red: #f85149;
            --orange: #d29922;
            --purple: #bc8cff;
            --cyan: #39d2c0;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }

        .hero {
            text-align: center;
            padding: 80px 24px 48px;
            background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
            border-bottom: 1px solid var(--border);
        }
        .hero-icon { font-size: 64px; margin-bottom: 16px; }
        .hero h1 {
            font-size: 48px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent), var(--purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 12px;
        }
        .hero p {
            font-size: 20px;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 24px;
            line-height: 1.6;
        }
        .hero-badges {
            display: flex;
            gap: 8px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .badge {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 600;
        }
        .badge-green { background: #238636; color: #fff; }
        .badge-blue { background: #1f6feb; color: #fff; }
        .badge-purple { background: #8957e5; color: #fff; }
        .badge-orange { background: #9e6a03; color: #fff; }

        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 48px 24px 80px;
        }

        .section-title {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 48px;
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.2s;
            display: block;
        }
        .card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 4px 24px rgba(0,0,0,0.3);
            text-decoration: none;
        }
        .card-icon { font-size: 28px; margin-bottom: 12px; }
        .card h3 { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
        .card p { font-size: 14px; color: var(--text-secondary); line-height: 1.5; margin: 0; }
        .card .tag {
            display: inline-block;
            margin-top: 12px;
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 600;
            background: var(--accent-subtle);
            color: var(--accent);
        }
        .card .tag.new {
            background: #23863622;
            color: var(--green);
        }

        .footer {
            text-align: center;
            padding: 32px;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 14px;
        }
        .footer a { color: var(--accent); text-decoration: none; }
    </style>
</head>
<body>
    <div class="hero">
        <div class="hero-icon">⚡</div>
        <h1>Archon v2.0</h1>
        <p>Enforced Intelligence Framework — 61 skills, 9 agents, 6 pipelines, all with runtime guardrails</p>
        <div class="hero-badges">
            <span class="badge badge-green">v2.0.0</span>
            <span class="badge badge-blue">61 Skills</span>
            <span class="badge badge-purple">9 Agents</span>
            <span class="badge badge-orange">5 Pipelines</span>
        </div>
    </div>

    <div class="container">
        <div class="section-title">🚀 Getting Started</div>
        <div class="grid">
            <a href="Getting-Started.html" class="card">
                <div class="card-icon">🚀</div>
                <h3>Getting Started</h3>
                <p>Install Archon, configure your platform, and start using skills and agents.</p>
            </a>
            <a href="Cli-Guide.html" class="card">
                <div class="card-icon">💻</div>
                <h3>CLI Guide</h3>
                <p>Command-line interface reference for managing skills, agents, pipelines, and bundles.</p>
            </a>
            <a href="Migration-V2.html" class="card">
                <div class="card-icon">📦</div>
                <h3>Migration to v2.0</h3>
                <p>Upgrade guide from v0.2.0 — fully backward compatible, zero breaking changes.</p>
                <span class="tag new">NEW</span>
            </a>
        </div>

        <div class="section-title">🏗️ Architecture & Core Systems</div>
        <div class="grid">
            <a href="Architecture.html" class="card">
                <div class="card-icon">🏗️</div>
                <h3>5-Layer Architecture</h3>
                <p>Bootstrap → Agents → Skills → Pipelines → Artifacts. The full architectural blueprint.</p>
                <span class="tag new">NEW</span>
            </a>
            <a href="Pipeline-Orchestration.html" class="card">
                <div class="card-icon">🔧</div>
                <h3>Pipeline Orchestration</h3>
                <p>Real execution engine with state machines, artifact validation, and failure recovery.</p>
                <span class="tag new">NEW</span>
            </a>
            <a href="Guardrails.html" class="card">
                <div class="card-icon">🛡️</div>
                <h3>Guardrails Engine</h3>
                <p>10 Iron Laws, anti-rationalization, forbidden phrases, and the deviation protocol.</p>
                <span class="tag new">NEW</span>
            </a>
            <a href="Sequential-Thinking.html" class="card">
                <div class="card-icon">🧠</div>
                <h3>Sequential Thinking</h3>
                <p>DECOMPOSE → REASON → VALIDATE → SYNTHESIZE chain-of-thought protocol.</p>
                <span class="tag new">NEW</span>
            </a>
        </div>

        <div class="section-title">📖 Guides</div>
        <div class="grid">
            <a href="Creating-Skills.html" class="card">
                <div class="card-icon">✨</div>
                <h3>Creating Skills</h3>
                <p>Write SKILL.md + manifest.yaml to add new capabilities to the framework.</p>
            </a>
            <a href="Creating-Agents.html" class="card">
                <div class="card-icon">🤖</div>
                <h3>Creating Agents</h3>
                <p>Define specialized agents with guardrails, triggers, and skill dependencies.</p>
            </a>
            <a href="Creating-Pipelines.html" class="card">
                <div class="card-icon">🔄</div>
                <h3>Creating Pipelines</h3>
                <p>Build multi-step workflows that chain agents with validation gates.</p>
            </a>
            <a href="Creating-Bundles.html" class="card">
                <div class="card-icon">📦</div>
                <h3>Creating Bundles</h3>
                <p>Package related skills into installable bundles for different workflows.</p>
            </a>
            <a href="Creating-Synapses.html" class="card">
                <div class="card-icon">🧬</div>
                <h3>Creating Synapses</h3>
                <p>Build cognitive protocols that shape how agents think and reason.</p>
            </a>
            <a href="Platform-Guide.html" class="card">
                <div class="card-icon">🌐</div>
                <h3>Platform Guide</h3>
                <p>Configure Archon for Claude Code, Copilot CLI, Cursor, Windsurf, and more.</p>
            </a>
        </div>

        <div class="section-title">📋 Reference</div>
        <div class="grid">
            <a href="Agent-Cards.html" class="card">
                <div class="card-icon">🃏</div>
                <h3>Agent Cards</h3>
                <p>Detailed profiles of all 9 specialized agents and their capabilities.</p>
            </a>
            <a href="Integration-Catalog.html" class="card">
                <div class="card-icon">🔌</div>
                <h3>Integration Catalog</h3>
                <p>Full catalog of platform integrations and adapter configurations.</p>
            </a>
            <a href="Faq.html" class="card">
                <div class="card-icon">❓</div>
                <h3>FAQ</h3>
                <p>Frequently asked questions about Archon usage and troubleshooting.</p>
            </a>
            <a href="Changelog.html" class="card">
                <div class="card-icon">📋</div>
                <h3>Changelog</h3>
                <p>Version history and release notes for all Archon releases.</p>
            </a>
            <a href="Readme.html" class="card">
                <div class="card-icon">📖</div>
                <h3>README</h3>
                <p>Project overview, quick start, and feature summary.</p>
            </a>
            <a href="Contributing.html" class="card">
                <div class="card-icon">🤝</div>
                <h3>Contributing</h3>
                <p>How to contribute skills, agents, bug fixes, and documentation.</p>
            </a>
        </div>
    </div>

    <div class="footer">
        Archon v2.0 — Enforced Intelligence Framework<br>
        <a href="https://github.com/SufficientDaikon/archon">GitHub</a> · Built with ⚡
    </div>
</body>
</html>"""


def build_all():
    """Build all HTML documentation."""
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all doc files
    doc_files = []

    # docs/ directory
    for md_file in sorted(DOCS_DIR.glob("*.md")):
        if md_file.name == "README.md":
            continue  # Handle separately
        doc_files.append(md_file)

    # Root files
    for name in ROOT_FILES:
        root_file = ROOT / name
        if root_file.exists():
            doc_files.append(root_file)

    # docs/README.md if it exists
    docs_readme = DOCS_DIR / "README.md"
    if docs_readme.exists():
        doc_files.append(docs_readme)

    print(f"📚 Building {len(doc_files)} documentation pages...")

    for md_file in doc_files:
        filename = md_file.name
        content = md_file.read_text(encoding="utf-8")
        title = get_title(content, filename)

        # Generate output filename
        out_name = md_file.stem.replace("_", "-").title() + ".html"
        out_path = HTML_DIR / out_name

        try:
            html = build_page(content, filename)
            out_path.write_text(html, encoding="utf-8")
            print(f"  ✅ {filename} → {out_name}")
        except Exception as e:
            print(f"  ❌ {filename} → Error: {e}")

    # Write index page
    index_path = HTML_DIR / "index.html"
    index_path.write_text(INDEX_CONTENT, encoding="utf-8")
    print(f"  ✅ index.html (documentation home)")

    # Also copy to root for GitHub Pages compatibility
    root_index = ROOT / "index.html"
    if root_index.exists():
        # Don't overwrite existing root index.html
        pass

    print(f"\n🎉 Built {len(doc_files) + 1} HTML files in {HTML_DIR}")
    print(f"   Open: {HTML_DIR / 'index.html'}")


if __name__ == "__main__":
    build_all()
