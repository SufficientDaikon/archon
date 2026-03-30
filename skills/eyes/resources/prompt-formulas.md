# Prompt Formulas for Image Generation

## The 5-Component Formula (Primary)

Every image generation prompt should contain these 5 components:

### 1. SUBJECT

Who or what is in the image. Include physical details, materials, scale.

**Weak:** "a robot"
**Strong:** "A humanoid robot with brushed titanium chassis, exposed servo joints at elbows and knees, a single cyan LED eye centered in a smooth featureless faceplate"

### 2. ACTION / STATE

What is happening. Motion, gesture, ambient behavior, process.

**Weak:** "standing"
**Strong:** "Crouching at the edge of a rooftop, one hand pressed to the concrete, head tilted analyzing the street below, rain beading on metallic surfaces"

### 3. ENVIRONMENT

Where the scene takes place. Background, setting, surrounding elements, atmosphere.

**Weak:** "in a city"
**Strong:** "On the rooftop of a brutalist concrete tower in a rain-soaked megacity, neon signs reflecting off wet surfaces below, distant skyscrapers disappearing into low cloud cover"

### 4. COMPOSITION

How the image is framed. Shot type, camera angle, lens choice, aspect ratio.

| Shot Type                | When to Use                                        |
| ------------------------ | -------------------------------------------------- |
| Extreme wide             | Establishing shots, environments, hero backgrounds |
| Wide                     | Full scene with context                            |
| Medium                   | Subject with some environment                      |
| Close-up                 | Detail, emotion, texture                           |
| Extreme close-up / Macro | Material detail, abstract                          |

| Camera Angle | Effect                  |
| ------------ | ----------------------- |
| Eye level    | Neutral, documentary    |
| Low angle    | Power, monumentality    |
| High angle   | Overview, vulnerability |
| Bird's eye   | Pattern, layout         |
| Dutch angle  | Tension, unease         |

**Example:** "Low-angle medium shot, 35mm lens, shallow depth of field, 16:9 cinematic frame"

### 5. STYLE

Visual treatment. Lighting, color palette, film reference, texture, mood.

**Lighting keywords:** Rembrandt, split lighting, rim light, backlit, volumetric, ambient occlusion, HDR, low-key, high-key, golden hour, blue hour, neon, fluorescent, bioluminescent

**Color palette keywords:** monochromatic, complementary, analogous, triadic, desaturated, crushed blacks, lifted shadows, teal-orange, cyan-magenta

**Film/camera references:** Shot on RED Monstro 8K, Kodak Portra 400, ARRI Alexa 65, Fujifilm Velvia, Sony Venice 2, Canon 5D Mark IV

**Texture keywords:** film grain, digital noise, CRT scanlines, halftone dots, paper texture, weathered, pristine, polished

---

## The 7-Component Formula (Extended)

Adds **Camera** and **Texture** as separate components from Style:

1. **Subject** — Who/what (same as above)
2. **Style** — Art movement or aesthetic (cyberpunk, Art Deco, minimalist, brutalist)
3. **Environment** — Setting details (same as above)
4. **Lighting** — Dedicated lighting description (direction, color, quality, shadows)
5. **Action** — What's happening (same as above)
6. **Camera** — Specific camera, lens, settings, film stock
7. **Texture** — Surface quality, grain, material feel

Use the 7-component formula when you need maximum control over the output.

---

## Quick Prompt Enhancers

Add these suffixes to any prompt for quality improvement:

**Realism:** ", photorealistic, 8K resolution, sharp focus, professional photography"
**Cinematic:** ", cinematic lighting, anamorphic lens, film grain, color graded"
**Dark/Moody:** ", low-key lighting, deep shadows, crushed blacks, dramatic contrast"
**Clean/Minimal:** ", clean white background, studio lighting, minimalist composition"
**Futuristic:** ", holographic elements, translucent materials, volumetric lighting, particle effects"

---

## Anti-Patterns (What Breaks Prompts)

❌ "A beautiful image of..." — "beautiful" means nothing to the model
❌ Contradictions — "bright sunny day with deep shadows and darkness"
❌ Too many subjects — one clear subject, everything else is environment
❌ Requesting text in images — AI renders text poorly. Use CSS/SVG instead.
❌ Negative prompts as positives — "not blurry" → instead specify "sharp focus, tack-sharp"
❌ Vague composition — "nice framing" → instead specify exact shot type and lens
