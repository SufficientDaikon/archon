---
name: wireframing
description: Wireframing patterns including layout grids, content blocks, responsive breakpoints, and page layout patterns for landing pages, dashboards, and forms. Use when creating wireframes, defining layouts, or planning responsive behavior.
---

# Wireframing Skill

## Layout Grid Systems

### 12-Column Grid Explanation

**Why 12 Columns?**
- Highly divisible (1, 2, 3, 4, 6, 12)
- Maximum flexibility for different layouts
- Industry standard across frameworks (Bootstrap, Foundation)
- Easy mental math for developers

**Grid Anatomy**:
```
[Container]
  [Row]
    [Col-1] [Col-2] [Col-3] [Col-4] [Col-5] [Col-6] [Col-7] [Col-8] [Col-9] [Col-10] [Col-11] [Col-12]
  [Row]
    [Col-6] [Col-6]
  [Row]
    [Col-4] [Col-4] [Col-4]
```

### CSS Grid vs Flexbox Guidance

**Use CSS Grid When**:
- 2-dimensional layout (rows AND columns)
- Complex, irregular layouts
- Items need to align to a grid structure
- Dashboard layouts with defined regions

**Use Flexbox When**:
- 1-dimensional layout (row OR column)
- Content-driven sizing
- Items need to grow/shrink dynamically
- Navigation bars, button groups

**Example CSS Grid**:
```css
.layout-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}
.col-6 { grid-column: span 6; }
.col-4 { grid-column: span 4; }
```

**Example Flexbox**:
```css
.flex-row {
  display: flex;
  gap: 24px;
}
.flex-item { flex: 1; }
.flex-item-2 { flex: 2; }
```

### Common Column Splits

**12 Columns (Full Width)**:
- Hero sections, single-column content
- Use for: Main content area, featured content

**6+6 Columns (Half Split)**:
- Image + text combinations
- Feature comparisons, before/after
- Use for: Two equal-weight content blocks

**4+4+4 Columns (Thirds)**:
- Three-feature layouts, team member grids
- Pricing tables (3-tier), testimonial cards
- Use for: Equal importance content blocks

**3+9 Columns (Sidebar + Main)**:
- Blog layouts, documentation
- Filter sidebar + product grid
- Use for: Primary content with supporting navigation

**8+4 Columns (Main + Sidebar)**:
- Article content + related links
- Form + help text, checkout + order summary
- Use for: Primary content with secondary information

**2+8+2 Columns (Centered)**:
- Focused content with breathing room
- Reading-optimized layouts
- Use for: Long-form content, legal pages

### Gutter Sizing Guidelines

**Mobile (≤480px)**: 16px gutters
- **Reasoning**: Limited space, finger-friendly touch targets
- **Side margins**: 16px from screen edge

**Tablet (481-1024px)**: 24px gutters
- **Reasoning**: More space, comfortable reading
- **Side margins**: 24px from screen edge

**Desktop (≥1025px)**: 32px gutters
- **Reasoning**: Ample space, clear content separation
- **Side margins**: Auto-centering with max-width container

## Content Block Patterns

### Hero Blocks

**Centered Hero**:
```
┌─────────────────────────────────────────┐
│                                         │
│            [Logo/Nav]                   │
│                                         │
│         [Headline Text]                 │
│       [Supporting Text]                 │
│                                         │
│         [Primary CTA]                   │
│                                         │
└─────────────────────────────────────────┘
```
- **When to Use**: SaaS products, service businesses
- **Content**: Value proposition, single CTA

**Split Hero (50/50)**:
```
┌─────────────────┬─────────────────┐
│ [Headline]      │                 │
│ [Supporting]    │   [Hero Image]  │
│ [CTA Button]    │   or [Video]    │
│                 │                 │
└─────────────────┴─────────────────┘
```
- **When to Use**: Product demos, app showcases
- **Content**: Text left, visual right (or reverse)

**Background Image Hero**:
```
┌─────────────────────────────────────────┐
│ [Background Image/Video]                │
│                                         │
│    [White/Yellow Text Overlay]         │
│    [Contrasting CTA Button]            │
│                                         │
└─────────────────────────────────────────┘
```
- **When to Use**: Lifestyle brands, travel, hospitality
- **Requirements**: High contrast, readable text

### Feature Grids

**2-Column Features**:
```
┌─────────────────┬─────────────────┐
│ [Icon/Image]    │ [Icon/Image]    │
│ [Feature Name]  │ [Feature Name]  │
│ [Description]   │ [Description]   │
└─────────────────┴─────────────────┘
┌─────────────────┬─────────────────┐
│ [Icon/Image]    │ [Icon/Image]    │
│ [Feature Name]  │ [Feature Name]  │
│ [Description]   │ [Description]   │
└─────────────────┴─────────────────┘
```
- **When to Use**: 4-6 key features
- **Mobile**: Stacks to single column

**3-Column Features**:
```
┌─────────┬─────────┬─────────┐
│ [Icon]  │ [Icon]  │ [Icon]  │
│ [Title] │ [Title] │ [Title] │
│ [Text]  │ [Text]  │ [Text]  │
└─────────┴─────────┴─────────┘
```
- **When to Use**: 3, 6, or 9 features
- **Mobile**: Stacks to single column

**Alternating Features**:
```
┌─────────────────┬─────────────────┐
│ [Feature Text]  │ [Feature Image] │
└─────────────────┴─────────────────┘
┌─────────────────┬─────────────────┐
│ [Feature Image] │ [Feature Text]  │
└─────────────────┴─────────────────┘
```
- **When to Use**: Detailed feature explanations
- **Visual Rhythm**: Prevents monotonous layout

### Testimonial Layouts

**Carousel/Slider**:
```
┌─────────────────────────────────────────┐
│  "Quote text here..."                   │
│                                         │
│  [Customer Photo] [Name, Company]       │
│                                         │
│  [● ○ ○] [< Previous | Next >]         │
└─────────────────────────────────────────┘
```
- **When to Use**: Many testimonials, limited space
- **Considerations**: Auto-advance, pause on hover

**Grid Layout**:
```
┌─────────┬─────────┬─────────┐
│ [Quote] │ [Quote] │ [Quote] │
│ [Photo] │ [Photo] │ [Photo] │
│ [Name]  │ [Name]  │ [Name]  │
└─────────┴─────────┴─────────┘
```
- **When to Use**: 3-6 strong testimonials
- **Mobile**: 2-column or single column

**Featured Testimonial**:
```
┌─────────────────────────────────────────┐
│                                         │
│     [Large Customer Photo]              │
│                                         │
│    "Extended testimonial quote text     │
│     that spans multiple lines..."       │
│                                         │
│    [Customer Name, Title, Company]      │
│                                         │
└─────────────────────────────────────────┘
```
- **When to Use**: One exceptional testimonial
- **Placement**: After features, before pricing

### Pricing Tables

**3-Tier Pricing**:
```
┌─────────┬─────────┬─────────┐
│ Basic   │ Pro ★   │ Enterprise │
│ $X/mo   │ $Y/mo   │ $Z/mo   │
│         │         │         │
│ Feature │ Feature │ Feature │
│ Feature │ Feature │ Feature │
│         │ Feature │ Feature │
│         │         │ Feature │
│         │         │         │
│ [CTA]   │ [CTA]   │ [CTA]   │
└─────────┴─────────┴─────────┘
```
- **Highlight**: Middle option (most popular)
- **Features**: Align vertically, use checkmarks/X

**Comparison Table**:
```
┌─────────────┬─────┬─────┬─────┐
│ Feature     │Basic│ Pro │ Ent │
├─────────────┼─────┼─────┼─────┤
│ Users       │  5  │ 25  │ ∞   │
│ Storage     │ 1GB │10GB │100GB│
│ Support     │ ✗   │ ✓   │ ✓   │
│ Analytics   │ ✗   │ ✓   │ ✓   │
│ API Access  │ ✗   │ ✗   │ ✓   │
└─────────────┴─────┴─────┴─────┘
```
- **When to Use**: Complex feature differences
- **Highlighting**: Color-code plan columns

### CTA Blocks

**Banner CTA**:
```
┌─────────────────────────────────────────┐
│ [Background Color/Gradient]             │
│                                         │
│       [Compelling Headline]             │
│     [Supporting Text (Optional)]        │
│                                         │
│         [Primary CTA Button]            │
│                                         │
└─────────────────────────────────────────┘
```
- **Placement**: End of page, between sections
- **Colors**: High contrast, brand colors

**Inline CTA**:
```
Text content continues here with natural
flow and then [Call-to-Action Link] that
appears within the paragraph context.
```
- **When to Use**: Within blog posts, articles
- **Styling**: Button or styled link

**Floating CTA**:
```
                                    ┌─────────┐
                                    │ [CTA]   │
                                    │ Button  │
                                    │ Fixed   │
                                    └─────────┘
```
- **Position**: Fixed bottom-right or top bar
- **Behavior**: Sticky, follows scroll
- **Mobile**: Full-width bottom bar

### Footer Layouts

**4-Column Footer**:
```
┌─────────┬─────────┬─────────┬─────────┐
│ Company │ Product │ Support │ Legal   │
│ About   │ Features│ Help    │ Privacy │
│ Careers │ Pricing │ Contact │ Terms   │
│ Press   │ Updates │ FAQ     │ Cookies │
└─────────┴─────────┴─────────┴─────────┘
┌─────────────────────────────────────────┐
│ © 2024 Company | [Social Icons]         │
└─────────────────────────────────────────┘
```

**Simple Footer**:
```
┌─────────────────────────────────────────┐
│ [Company Logo]                          │
│                                         │
│ [About] [Contact] [Privacy] [Terms]     │
│                                         │
│ © 2024 Company | [Social Icons]         │
└─────────────────────────────────────────┘
```

**Mega Footer**:
```
┌─────────┬─────────┬─────────┬─────────┐
│ Products│ Solutions│ Resources│ Company │
│ ┌─────┐ │ By Industry│ Blog    │ About   │
│ │Image│ │ By Size  │ Guides   │ Careers │
│ └─────┘ │ By Role  │ Webinars │ News    │
│ Product │          │ Templates│ Contact │
│ Name    │          │          │         │
└─────────┴─────────┴─────────┴─────────┘
```

### Navigation Layouts

**Top Bar Navigation**:
```
┌─────────────────────────────────────────┐
│ [Logo] [Nav] [Nav] [Nav]    [CTA] [User]│
└─────────────────────────────────────────┘
```
- **Structure**: Logo left, nav center, actions right
- **Responsive**: Collapses to hamburger menu

**Sticky Navigation**:
```
┌─────────────────────────────────────────┐ ← Scrolls with page
│ [Reduced Logo] [Key Nav]    [CTA]      │ ← Appears on scroll
└─────────────────────────────────────────┘ ← Fixed position
```
- **Behavior**: Appears after scroll threshold
- **Content**: Simplified navigation items

**Transparent Navigation**:
```
┌─────────────────────────────────────────┐
│ [Hero Background Image/Video]           │
│                                         │
│ [White Logo] [White Nav] [White CTA]    │
│                                         │
└─────────────────────────────────────────┘
```
- **Requirements**: High contrast background
- **Transition**: Becomes solid on scroll

## Responsive Breakpoint Strategy

### 3 Breakpoints System

**Mobile (≤480px)**:
- **Single column layouts**
- **Touch-first interactions**
- **Simplified navigation (hamburger)**
- **Font sizes**: 14-16px body, 24-32px headers
- **Image sizing**: Full width, optimized for retina
- **Forms**: Stacked labels, large input fields

**Tablet (481-1024px)**:
- **2-3 column layouts**
- **Hybrid touch/mouse interactions**
- **Condensed navigation**
- **Font sizes**: 15-16px body, 28-36px headers
- **Image sizing**: 50% widths common
- **Forms**: Side-by-side shorter fields

**Desktop (≥1025px)**:
- **Multi-column layouts (up to 4)**
- **Mouse-optimized interactions**
- **Full navigation menu**
- **Font sizes**: 16-18px body, 32-48px headers
- **Image sizing**: Varied, decorative elements
- **Forms**: Efficient horizontal layouts

### Content Changes by Breakpoint

**Navigation Transformation**:
```
Desktop: [Logo] [Home] [About] [Services] [Contact] [CTA]
Tablet:  [Logo] [Home] [About] [Services] [☰]
Mobile:  [☰] [Logo] [CTA]
```

**Column Collapsing**:
```
Desktop: [4 columns across]
Tablet:  [2 columns] [2 columns]
Mobile:  [1 column]
         [1 column]  
         [1 column]
         [1 column]
```

**Font Size Scaling**:
```
Desktop: H1(48px) H2(36px) Body(18px)
Tablet:  H1(36px) H2(28px) Body(16px)
Mobile:  H1(32px) H2(24px) Body(16px)
```

**Image Resizing Strategy**:
```
Desktop: Hero images full width, decorative images varied sizes
Tablet:  Hero images full width, content images 50% max
Mobile:  All images full width, optimized loading
```

### Mobile-First vs Desktop-First Approach

**Mobile-First Benefits**:
- Progressive enhancement philosophy
- Better performance on mobile devices
- Forces content prioritization
- Easier to add features than remove them

**Mobile-First CSS Structure**:
```css
/* Base styles (mobile) */
.feature-grid { display: block; }

/* Tablet up */
@media (min-width: 481px) {
  .feature-grid { display: grid; grid-template-columns: 1fr 1fr; }
}

/* Desktop up */
@media (min-width: 1025px) {
  .feature-grid { grid-template-columns: repeat(3, 1fr); }
}
```

**Desktop-First (When to Use)**:
- Complex desktop applications
- Dashboard/admin interfaces
- Content-heavy websites with secondary mobile usage

## Common Page Layout Patterns

### Landing Page Pattern
```
[Navigation Bar]
[Hero Section - Value Prop + CTA]
[Features Section - 3 columns]
[Social Proof - Testimonials/Logos]
[Secondary CTA Section]
[Footer]
```
**Content Flow**: Awareness → Interest → Consideration → Action

### Dashboard Pattern
```
┌─────────┬─────────────────────────────┐
│ [Logo]  │ [Top Navigation/User Menu]  │
├─────────┼─────────────────────────────┤
│ Main    │ [Key Metrics Cards]         │
│ Nav     ├─────────┬─────────┬─────────┤
│ Menu    │ [Chart] │ [Chart] │ [List]  │
│         ├─────────┴─────────┴─────────┤
│ [User]  │ [Recent Activity Table]     │
└─────────┴─────────────────────────────┘
```
**Layout**: Fixed sidebar + scrollable main content area

### Form Page Pattern
```
[Header/Navigation]
┌─────────────────┐
│ [Progress Bar]  │ ← For multi-step
├─────────────────┤
│ [Form Title]    │
│                 │
│ [Field Group 1] │
│ [Field Group 2] │
│ [Field Group 3] │
│                 │
│ [CTA] [Secondary]│
└─────────────────┘
[Footer - Minimal]
```
**Single Column**: 600px max width, centered
**Multi-Step**: Progress indicator, save/continue pattern

### Content Page Pattern
```
┌─────────┬─────────────────────────────┐
│ Table   │ [Breadcrumbs]               │
│ of      │ [Article Title]             │
│ Contents│ [Author/Date]               │
│         │                             │
│ [Links] │ [Article Content]           │
│ [Tags]  │ [Images/Media]              │
│ [Share] │ [Subheadings]              │
│         │                             │
│         │ [Related Articles]          │
└─────────┴─────────────────────────────┘
```
**Sidebar**: 25% width, sticky positioning
**Main**: 75% width, optimal reading measure

### Product Page Pattern
```
┌─────────────────┬─────────────────┐
│ [Image Gallery] │ [Product Name]  │
│ [Main Image]    │ [Rating/Reviews]│
│ [Thumbnails]    │ [Price]         │
│                 │ [Variants]      │
│                 │ [Add to Cart]   │
│                 │ [Description]   │
└─────────────────┴─────────────────┘
┌─────────────────────────────────────┐
│ [Detailed Specs/Features]           │
│ [Customer Reviews]                  │
│ [Related Products]                  │
└─────────────────────────────────────┘
```
**Above Fold**: Gallery + key product info
**Below Fold**: Supporting information, social proof

## Wireframe Conventions

### Visual Design Rules

**Colors**: Grayscale only
- `#FFFFFF` - Background/negative space
- `#F5F5F5` - Light gray blocks/containers  
- `#CCCCCC` - Medium gray for borders/dividers
- `#666666` - Dark gray for text representation
- `#000000` - High-emphasis text/headers

**Typography Representation**:
- Headers: `████████████` (thick black bars)
- Body text: `─────────────` (thin horizontal lines)
- Links: `─────────────` (underlined thin lines)
- Captions: `───────` (shorter thin lines)

**Images and Media**:
- Static images: Box with large "X" diagonal lines
- Video: Box with triangle play button in center
- Icons: Small squares with descriptive labels
- Avatars: Circles with person icon or initials

**Interactive Elements**:
- Primary buttons: `[Primary CTA]` (filled rectangle with label)
- Secondary buttons: `[Secondary]` (outline rectangle)
- Form fields: `[___________]` (underlined or boxed)
- Dropdowns: `[Select Option ▼]`

### Annotation Format

**Spacing Annotations**:
```
│←── 24px ──→│
[Content Block]
│←── 32px ──→│
[Content Block]
```

**Behavior Notes**:
```
[Image Gallery] ← Swipeable on mobile
                  Click to enlarge on desktop
```

**Content Specifications**:
```
[Headline] ← H1, ~8 words max
[Description] ← 2-3 sentences, benefit-focused
```

## Above-the-Fold Strategy

### Priority Content (Must be visible without scrolling)

**Primary Elements**:
1. **Value Proposition** - What you do, for whom
2. **Primary CTA** - Main conversion goal  
3. **Navigation** - How to explore further
4. **Trust Signal** - Logo, credentials, or social proof

**Supporting Elements**:
- **Hero visual** - Relevant image or video
- **Secondary CTA** - Alternative action
- **Key benefit** - One compelling reason to stay

### Prioritization Framework

**Tier 1 (Critical)**:
- Must communicate core value instantly
- Enables primary user action
- Required for basic site function

**Tier 2 (Important)**:
- Supports primary message
- Provides alternative paths
- Builds credibility/trust

**Tier 3 (Nice to Have)**:
- Decorative/atmospheric
- Secondary information
- Advanced functionality

### Viewport Considerations

**Mobile Viewport (~375x667px)**:
- Logo + hamburger menu
- Headline (1-2 lines)
- Primary CTA button
- Minimal hero visual

**Desktop Viewport (~1440x900px)**:
- Full navigation menu
- Complete hero section
- Supporting text/benefits
- Larger hero visual/video

---

## Wireframe HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wireframe Template</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: #ffffff;
            color: #666666;
            line-height: 1.5;
        }
        
        /* Grid System */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 16px;
        }
        
        .row {
            display: flex;
            flex-wrap: wrap;
            margin: 0 -12px;
        }
        
        .col {
            padding: 0 12px;
        }
        
        .col-1 { flex: 0 0 8.333%; }
        .col-2 { flex: 0 0 16.666%; }
        .col-3 { flex: 0 0 25%; }
        .col-4 { flex: 0 0 33.333%; }
        .col-6 { flex: 0 0 50%; }
        .col-8 { flex: 0 0 66.666%; }
        .col-9 { flex: 0 0 75%; }
        .col-12 { flex: 0 0 100%; }
        
        /* Wireframe Components */
        .wf-block {
            background: #f5f5f5;
            border: 2px dashed #cccccc;
            padding: 20px;
            margin: 10px 0;
            text-align: center;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .wf-header {
            font-weight: bold;
            font-size: 18px;
            color: #000000;
            background: repeating-linear-gradient(90deg, #000 0px, #000 8px, transparent 8px, transparent 12px);
            height: 20px;
            margin: 10px 0;
        }
        
        .wf-text {
            background: repeating-linear-gradient(90deg, #666 0px, #666 6px, transparent 6px, transparent 8px);
            height: 12px;
            margin: 5px 0;
        }
        
        .wf-image {
            background: #f5f5f5;
            border: 2px solid #cccccc;
            position: relative;
            min-height: 200px;
        }
        
        .wf-image::before,
        .wf-image::after {
            content: '';
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            border: 2px solid #cccccc;
        }
        
        .wf-image::before {
            transform: rotate(45deg);
        }
        
        .wf-image::after {
            transform: rotate(-45deg);
        }
        
        .wf-button {
            background: #000000;
            color: #ffffff;
            padding: 12px 24px;
            border: none;
            display: inline-block;
            margin: 10px 5px;
            text-decoration: none;
        }
        
        .wf-button-secondary {
            background: transparent;
            color: #000000;
            border: 2px solid #000000;
        }
        
        .wf-input {
            background: #ffffff;
            border: 2px solid #cccccc;
            padding: 12px;
            width: 100%;
            margin: 5px 0;
        }
        
        /* Responsive Breakpoints */
        @media (max-width: 1024px) {
            .container { padding: 0 24px; }
            .row { margin: 0 -12px; }
        }
        
        @media (max-width: 480px) {
            .container { padding: 0 16px; }
            .col { flex: 0 0 100%; }
            .row { margin: 0 -8px; }
            .col { padding: 0 8px; }
        }
        
        /* Utility Classes */
        .text-center { text-align: center; }
        .mb-20 { margin-bottom: 20px; }
        .mt-20 { margin-top: 20px; }
        .p-20 { padding: 20px; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="wf-block">
        [LOGO] [HOME] [ABOUT] [SERVICES] [CONTACT] [CTA BUTTON]
    </nav>
    
    <!-- Hero Section -->
    <section class="container">
        <div class="row">
            <div class="col-6">
                <div class="wf-header"></div>
                <div class="wf-text"></div>
                <div class="wf-text" style="width: 80%;"></div>
                <a href="#" class="wf-button">Primary CTA</a>
                <a href="#" class="wf-button-secondary">Secondary</a>
            </div>
            <div class="col-6">
                <div class="wf-image"></div>
            </div>
        </div>
    </section>
    
    <!-- Features Section -->
    <section class="container mt-20">
        <div class="wf-header text-center"></div>
        <div class="row">
            <div class="col-4">
                <div class="wf-block">[ICON]</div>
                <div class="wf-header" style="height: 16px;"></div>
                <div class="wf-text"></div>
                <div class="wf-text" style="width: 90%;"></div>
            </div>
            <div class="col-4">
                <div class="wf-block">[ICON]</div>
                <div class="wf-header" style="height: 16px;"></div>
                <div class="wf-text"></div>
                <div class="wf-text" style="width: 90%;"></div>
            </div>
            <div class="col-4">
                <div class="wf-block">[ICON]</div>
                <div class="wf-header" style="height: 16px;"></div>
                <div class="wf-text"></div>
                <div class="wf-text" style="width: 90%;"></div>
            </div>
        </div>
    </section>
    
    <!-- Form Section -->
    <section class="container mt-20">
        <div class="row">
            <div class="col-6">
                <div class="wf-header"></div>
                <input type="text" class="wf-input" placeholder="Name">
                <input type="email" class="wf-input" placeholder="Email">
                <input type="text" class="wf-input" placeholder="Company">
                <a href="#" class="wf-button">Submit Form</a>
            </div>
            <div class="col-6">
                <div class="wf-block" style="min-height: 300px;">
                    [CONTACT INFO / MAP / IMAGE]
                </div>
            </div>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="mt-20">
        <div class="container">
            <div class="wf-block">
                [FOOTER LINKS] | [SOCIAL ICONS] | [COPYRIGHT]
            </div>
        </div>
    </footer>
</body>
</html>
```

This wireframe template provides:
- **Responsive grid system** with breakpoints
- **Grayscale color scheme** for focus on structure
- **Wireframe-style components** (boxes, lines, placeholders)
- **Semantic HTML structure** for accessibility
- **Flexible layout patterns** that can be customized
- **Mobile-first responsive behavior**