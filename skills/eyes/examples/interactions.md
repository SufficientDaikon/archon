# Eyes Skill — Example Interactions

## Example 1: Generate a Hero Background

**User:** "Generate a hero background for my dark-themed portfolio"

**Agent (with Eyes):**

```
EYES — IMAGE GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Model:    gemini-2.0-flash-preview-image-generation
Aspect:   16:9 (landscape)
File:     public/generated/hero-bg.png
Size:     1.2 MB
Alt-text: "Dark computational void with cyan grid lines and floating data particles"

Prompt used:
  Subject: A vast computational void with an infinite cyan grid matrix
  Action: Electromagnetic energy pulsing through grid nodes, data particles drifting
  Environment: Pure darkness, no horizon, suspended geometric fragments
  Composition: Extreme wide shot, centered vanishing point, 16:9 cinematic frame
  Style: Shot on RED Monstro 8K, cold cyan-teal color grade, crushed blacks, 3% grain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Example 2: Visual QA on a Screenshot

**User:** "Check this screenshot for visual bugs"

**Agent (with Eyes):**

```
EYES — VISUAL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Image:    screenshots/tech-1440x900.png
Question: "Identify visual bugs, alignment issues, and design problems"

Findings:
  [CRITICAL] Hero heading "SYSTEM_ARCHITECT" clips behind the fixed header
             at scroll position ~200px — z-index conflict
  [WARNING]  CaseStudy card grid: third card has 8px less bottom padding
             than cards 1 and 2 (24px vs 32px)
  [WARNING]  Footer social icons lack hover state — contrast too low
             against surface-dim background (2.8:1 ratio)
  [INFO]     Timeline section: DNA helix SVG has a 1px gap at the
             4th milestone connection point

Score: 6/10
Recommendation: Fix the header z-index issue first, then padding consistency.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Example 3: Edit an Existing Image

**User:** "Make the archon-hero image darker and add more contrast"

**Agent (with Eyes):**

```
EYES — IMAGE EDITED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source:   public/generated/archon-hero.webp
Edit:     "Increase contrast significantly, crush the blacks deeper, make the
           bright cyan nodes pop more against the darkness"
Result:   public/generated/archon-hero-v2.png
Size:     956 KB
Changes:  Black point lowered to #050505, cyan highlights boosted +15%,
          midtone contrast curve steepened, overall brightness reduced 20%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Example 4: Generate Alt Text

**User:** "Create accessibility alt-text for all images in public/generated/"

**Agent (with Eyes):**

```
EYES — ALT TEXT GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
hero-bg.png:
  "Dark void with cyan electromagnetic grid matrix and floating data particles"

archon-hero.webp:
  "Crystalline neural network monument with cyan glass nodes and luminous filaments"

aether-hero.webp:
  "Geometric entities orbiting a central nexus connected by cyan laser lines"

axon-hero.png:
  "Macro view of an engineered neural axon carrying cyan light impulses"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4 images captioned. Use these as alt="" attributes in <img> tags.
```

## Example 5: Compare Two Images

**User:** "Compare the old hero-bg with the new one — what changed?"

**Agent (with Eyes):**

```
EYES — VISUAL COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Image A: public/generated/hero-bg-old.png
Image B: public/generated/hero-bg.png

Differences:
  1. Grid density: B has ~2x more grid lines, creating finer mesh
  2. Color temperature: B is cooler (more blue-cyan vs A's warmer cyan)
  3. Particle count: B has more particles with longer trailing filaments
  4. Depth: B has stronger depth-of-field effect — foreground particles
     are sharp, background grid blurs naturally
  5. Brightness: B is ~15% darker overall — better crushed blacks
  6. Grain: B has visible 3% digital noise that A lacks

Verdict: B is significantly better for the Forensic Monolith aesthetic.
         The deeper blacks and finer grid create a more clinical, precise feel.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
