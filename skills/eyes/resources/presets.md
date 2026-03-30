# Eyes — Preset Prompt Library

Ready-to-use prompts organized by category. Each preset includes the full 5-component formula.

---

## Hero Backgrounds

### Dark Computational Void

```
A vast computational void stretching to infinity, pulsing with faint electromagnetic energy through a precise cyan (#00F0FF) grid matrix suspended in absolute darkness (#0e0e0e). Microscopic data particles drift through the space like luminous digital plankton, each trailing faint cyan filaments. No horizon, no ground — pure computational substrate. Scattered holographic glyphs float at varying depths, some sharp, some bokeh-blurred. A single concentrated beam of cold cyan light cuts diagonally through the void, illuminating suspended geometric fragments. Extreme wide shot, centered vanishing point, 16:9 cinematic frame. Shot on RED Monstro 8K, 14mm ultra-wide lens, f/1.4, ISO 800. Cold cyan-teal color grade with crushed blacks. Digital grain at 3% opacity. Inspired by Blade Runner 2049 cinematography and Ghost in the Shell data landscapes.
```

**Aspect:** 16:9 | **Mood:** Clinical, infinite | **Palette:** Cyan + black

### Abstract Data Flow

```
Thousands of thin luminous lines streaming in parallel curves through a dark void, each line carrying pulsing data packets visualized as brighter nodes traveling along the paths. Lines converge toward a central focal point that glows with concentrated white-cyan energy. Some lines break and reform, suggesting dynamic routing. The overall shape suggests a toroidal flow field. Wide shot, centered composition, 16:9 frame. Volumetric atmosphere with subtle dust motes. Shot on ARRI Alexa 65, 18mm lens. Monochromatic cyan (#00F0FF) against pure black (#0e0e0e). Subtle film grain.
```

**Aspect:** 16:9 | **Mood:** Dynamic, flowing | **Palette:** Cyan + black

### Cosmic Grid

```
An infinite perspective grid extending in all directions on a perfectly flat plane, rendered in ultra-thin cyan (#00F0FF) lines against absolute black (#0e0e0e). The grid squares are 40px equivalent, perfectly regular. Above the grid, a starfield of microscopic data points — some clustered, some isolated. Where grid lines intersect, tiny diamond-shaped nodes pulse with brighter light. A faint fog hugs the grid surface. Extreme wide shot, camera positioned 15 degrees above grid plane, looking toward the vanishing point, 16:9 frame. Shot on Phase One IQ4, 28mm tilt-shift lens. Zero color beyond cyan. No bloom, no flare — clean and clinical.
```

**Aspect:** 16:9 | **Mood:** Infinite, precise | **Palette:** Cyan + black

---

## Project Visuals

### Neural Network Monument (for AI/ML projects)

```
A towering crystalline neural network structure rendered as a physical monument — thousands of interconnected nodes made of translucent cyan glass, suspended in a dark void. Each node pulses with internal light, connected by hair-thin luminous filaments carrying visible data packets. The structure resembles both a brain scan and a constellation map. At its core, a brighter cluster suggests central intelligence. Volumetric fog drifts through the lower third. Medium-wide shot, slight low angle, 16:9. Cold clinical lighting from above, cyan rim lights. ARRI Alexa 65, 24mm lens. Desaturated with selective cyan, crushed shadows. Microscopic technical annotations float near nodes like AR overlays.
```

### Agent Orchestration (for multi-agent systems)

```
Multiple distinct geometric entities (polyhedra, toroids, icosahedra) orbiting a central command nexus in synchronized patterns. Each entity emits a unique spectral signature while maintaining formation through visible force-field connections rendered as thin cyan laser lines against deep black. The central nexus is a slowly rotating dodecahedron radiating structured light pulses. Data streams flow between entities as particle ribbons. Wide shot, top-down 30-degree angle, 16:9. Dramatic rim lighting in cold blue-white. Phantom Flex 4K, 35mm lens. Crushed blacks, selective cyan only.
```

### Systems Language (for programming language projects)

```
A macro close-up of a single neural axon rendered as an engineered structure — a translucent cylindrical conduit carrying visible electrical impulses as cyan light pulses. The axon's myelin sheath is precision-machined metallic segments with microscopic circuit traces etched into the surface. At synaptic terminals, sparks jump across infinitesimal gaps. Pure darkness background with faint hexagonal grid artifacts. Extreme macro, razor-thin DOF, 16:9. Backlit with cold white light creating translucency, cyan glow from within. Laowa Probe lens at 24:1 magnification. Monochromatic cyan-gray.
```

---

## World-Themed Backgrounds

### Creative / Design World (Purple Palette)

```
A surreal creative workspace dissolving into digital abstraction — a drafting table surface morphs into flowing liquid purple (#C084FC) light at its edges, shapes and typography fragments orbiting in zero gravity. Bezier curve handles float visibly. Color swatches materialize as holographic chips. A golden ratio spiral rendered in luminous wire overlays the composition. Environment transitions from physical (matte dark #1c1b1b) to ethereal (particle-based, translucent). Wide shot, slight overhead, 16:9. Soft purple key light from upper left. Phase One IQ4 150MP, 55mm lens, f/2.8. Warm shadows with selective purple highlights, gentle bloom.
```

### Business / Operator World (Amber Palette)

```
A command center data visualization room — curved wall of dark glass panels (#131313 to #201f1f) displaying real-time business metrics as amber (#F59E0B) holographic projections. Bar charts grow upward like luminous architecture. Network graphs show connection flows. Large central circular display shows a rotating globe with amber trade routes. Floor reflects displays faintly. No people — just the intelligence of data. Wide shot, centered, slight low angle, 16:9. Ambient darkness with amber display glow as primary light. Sony Venice 2, 18mm lens, T2. Deep contrast, amber-gold accent only, everything else near-monochrome dark.
```

---

## Textures & Overlays

### Digital Noise Texture

```
Pure abstract digital noise pattern — microscopic cyan (#00F0FF) and white particles scattered randomly across a pure black (#0e0e0e) field. No structure, no pattern — pure entropy. Some particles are sharp points, others are soft bokeh circles. Density: approximately 3-5% coverage. No objects, no shapes, no recognizable forms. Extreme macro shot, perfectly flat, 1:1 square format. Even lighting, no shadows. Maximum sharpness. This is a texture overlay, not a scene.
```

**Aspect:** 1:1 | **Usage:** CSS overlay at 3-5% opacity

### Grid Overlay

```
A perfectly regular grid of ultra-thin white lines on pure black background. Grid squares approximately 40px. Lines are 1px thickness, rendered at 10% opacity against black. Perfectly orthogonal, no perspective, no distortion. Flat, uniform, no depth. 1:1 square format. This is a UI overlay texture, not a scene.
```

**Aspect:** 1:1 | **Usage:** CSS overlay for grid texture effect

---

## Usage

```bash
# Use these prompts with the gemini-generate CLI:
npx tsx tools/gemini-generate.ts gen "paste prompt here" --name output-name --aspect landscape --raw

# Or use the built-in presets:
npx tsx tools/gemini-generate.ts preset hero
npx tsx tools/gemini-generate.ts preset archon
```
