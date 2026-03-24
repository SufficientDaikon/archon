---
name: info-architecture
description: Information architecture patterns including sitemaps, navigation design, content strategy, user flows, and screen inventories. Use when organizing content structure, designing navigation, creating sitemaps, or mapping user flows.
---

# Information Architecture Skill

## Sitemap Patterns

### Hierarchical Tree Format (ASCII)

```
Home
├── About
│   ├── Our Story
│   ├── Team
│   └── Careers
├── Products
│   ├── Product Category A
│   │   ├── Product 1
│   │   └── Product 2
│   └── Product Category B
│       ├── Product 3
│       └── Product 4
├── Services
│   ├── Consulting
│   ├── Implementation
│   └── Support
├── Resources
│   ├── Blog
│   ├── Documentation
│   ├── Case Studies
│   └── Downloads
└── Contact
    ├── Get in Touch
    ├── Locations
    └── Support Portal
```

### Flat vs Deep Structures

**Flat Structure (Wide & Shallow)**:
- **When to Use**: Simple sites with <50 pages, diverse content types
- **Benefits**: Easy to navigate, fewer clicks, clear content overview
- **Drawbacks**: Can become overwhelming, harder to organize related content
- **Example**: Portfolio site with clear sections

**Deep Structure (Narrow & Deep)**:
- **When to Use**: Large sites with related content, hierarchical organizations
- **Benefits**: Logical grouping, scalable, easier to find specific content
- **Drawbacks**: More clicks required, potential for getting lost
- **Example**: Enterprise software documentation

### Common Site Structures by Type

**Landing Page Structure**:
```
Home
├── Product/Service Overview
├── Features/Benefits
├── Pricing
├── About/Company
├── Resources
│   ├── Blog
│   ├── Case Studies
│   └── Documentation
└── Contact/Get Started
```

**SaaS Product Structure**:
```
Home
├── Product
│   ├── Features
│   ├── Integrations
│   └── Security
├── Solutions
│   ├── By Industry
│   └── By Use Case
├── Pricing
├── Resources
│   ├── Blog
│   ├── Help Center
│   ├── API Docs
│   └── Templates
├── Company
│   ├── About
│   ├── Careers
│   └── Press
└── Contact/Demo
```

**E-commerce Structure**:
```
Home
├── Shop
│   ├── Category 1
│   │   ├── Subcategory A
│   │   └── Subcategory B
│   ├── Category 2
│   ├── Sale/Clearance
│   └── New Arrivals
├── About
├── Customer Service
│   ├── FAQ
│   ├── Returns
│   ├── Shipping
│   └── Contact
├── Account
│   ├── Login/Register
│   ├── Order History
│   └── Wishlist
└── Cart/Checkout
```

**Portfolio Structure**:
```
Home
├── Work/Portfolio
│   ├── Project Category 1
│   ├── Project Category 2
│   └── All Projects
├── About
│   ├── Bio
│   ├── Process
│   └── Resume
├── Services
├── Blog/Writing
└── Contact
```

## Navigation Patterns

### Primary Navigation

**Top Bar Navigation**:
- **When to Use**: Desktop-heavy sites, limited menu items (<7)
- **Best Practices**: Left-align logo, right-align CTAs, center main nav
- **Responsive**: Collapses to hamburger on mobile

**Sidebar Navigation**:
- **When to Use**: Dashboards, documentation, complex hierarchies
- **Best Practices**: Fixed position, collapsible, clear hierarchy
- **Responsive**: Overlay on mobile, toggle visibility

### Secondary Navigation

**Footer Navigation**:
- **Structure**: 3-5 columns, organized by topic
- **Content**: Less important pages, legal links, social media
- **Format**: Simple text links, grouped by category

**Contextual Navigation**:
- **Related Pages**: "You might also like" sections
- **Breadcrumbs**: Show current location in hierarchy
- **In-Page**: Table of contents, jump links for long content

### Utility Navigation

**Authentication**:
- **Logged Out**: Login/Register buttons
- **Logged In**: Profile dropdown with account options
- **Placement**: Top right corner, consistent across pages

**Search**:
- **Global Search**: Available from every page
- **Scoped Search**: Within specific sections (e.g., help center)
- **Auto-complete**: Suggested results as user types

**Settings/Preferences**:
- **User Settings**: Profile, notifications, privacy
- **App Settings**: Language, theme, accessibility
- **Admin Settings**: User management, system configuration

### Mobile Navigation Patterns

**Hamburger Menu**:
- **When to Use**: Many navigation items, space-constrained
- **Implementation**: Slide-in overlay, full-screen menu
- **Considerations**: Label with "Menu" text for clarity

**Tab Bar (Bottom Navigation)**:
- **When to Use**: App-like experiences, primary actions
- **Items**: 3-5 primary sections with icons
- **Active State**: Clear indication of current section

**Bottom Navigation**:
- **Fixed Position**: Always visible, easy thumb access
- **Primary Actions**: Most important user flows
- **Icon + Label**: Clear identification of each section

### Advanced Navigation

**Mega Menus**:
- **When to Use**: Large sites with many categories
- **Structure**: Multi-column dropdowns with rich content
- **Content**: Links, images, featured content, CTAs

**Breadcrumbs**:
- **Format**: Home > Category > Subcategory > Current Page
- **Separator**: Use > or / consistently
- **Interactive**: All levels except current should be clickable

## Content Strategy Principles

### Content Types

**Hero Content**:
- **Purpose**: Immediate value proposition communication
- **Length**: 1-2 sentences maximum
- **Tone**: Clear, compelling, action-oriented

**Feature Descriptions**:
- **Structure**: Benefit-focused headlines, supporting details
- **Length**: 2-3 sentences per feature
- **Format**: Scannable bullets or short paragraphs

**Social Proof**:
- **Types**: Customer testimonials, case studies, reviews, logos
- **Placement**: After value proposition, before conversion points
- **Authenticity**: Real names, photos, specific results

### Content Hierarchy (H1→H6 Semantic Meaning)

**H1**: Page title (one per page)
- Primary keyword focus
- Describes page purpose clearly
- 20-70 characters optimal

**H2**: Major section headers
- Break up main content areas
- Support the H1 topic
- Used for outline/TOC generation

**H3**: Subsection headers
- Detail within H2 sections
- Specific feature or benefit focus
- Most common heading level

**H4-H6**: Granular organization
- Use sparingly
- Technical documentation detail
- FAQ question headers

### CTA Strategy

**Primary CTAs**:
- **Purpose**: Main conversion goal
- **Placement**: Above fold, after value props, end of content
- **Styling**: High contrast, largest button size
- **Text**: Action-oriented ("Start Free Trial", "Get Demo")

**Secondary CTAs**:
- **Purpose**: Alternative conversion paths
- **Examples**: "Learn More", "Watch Demo", "Download Guide"
- **Styling**: Outline buttons, smaller than primary
- **Placement**: Near primary but visually distinct

**Tertiary CTAs**:
- **Purpose**: Supporting actions
- **Examples**: Social sharing, related content, newsletter signup
- **Styling**: Text links, minimal visual weight
- **Placement**: Sidebar, footer, end of articles

### Microcopy Approach

**Concise Principle**:
- Remove unnecessary words
- Use active voice
- Front-load important information
- Example: "Save your changes" not "Click here to save your changes"

**Action-Oriented Language**:
- Start with verbs
- Specific rather than generic
- Example: "Download free guide" not "Click here"

**User-Focused Perspective**:
- Use "you" and "your"
- Address user benefits
- Example: "Get your results" not "Generate results"

### Content Density Guidelines

**Scanning Patterns**:
- **F-Pattern**: Left-aligned headers and bullets
- **Z-Pattern**: For sparse content and landing pages
- **Gutenberg Diagram**: Natural reading flow

**White Space Usage**:
- **Line Height**: 1.4-1.6x font size for body text
- **Paragraphs**: 40-75 characters per line optimal
- **Sections**: Clear visual breaks between content blocks

## User Flow Diagramming

### ASCII Flowchart Format

```
[Start] → [Decision?] → [Action 1] → [End]
             ↓
          [Action 2] → [Subprocess] → [End]
```

**Standard Symbols**:
- `[ ]` = Process/Page (rectangle)
- `< >` = Decision (diamond)
- `( )` = Start/End (rounded rectangle)
- `→` = Flow direction
- `↓↑←` = Alternative directions

### Example User Flow: Sign-up Process

```
(User visits homepage) 
        ↓
[View pricing page]
        ↓
<Ready to sign up?>
   ↓         ↓
  No        Yes
   ↓         ↓
[Browse     [Click "Start Trial"]
features]      ↓
   ↓       [Enter email]
   ↓         ↓
   ↓    <Valid email?>
   ↓      ↓      ↓
   ↓     No     Yes
   ↓      ↓      ↓
   ↓   [Show    [Send verification]
   ↓   error]      ↓
   ↓      ↑    [Check email page]
   ↓      |       ↓
   └──────┴─→ [Click verify link]
              ↓
          [Complete profile]
              ↓
          [Dashboard onboarding]
              ↓
          (User activated)
```

### Deriving Flows from Personas + Goals

1. **Start with Persona Goals**: What does the user want to accomplish?
2. **Identify Entry Points**: How do they arrive at your product?
3. **Map Decision Points**: Where do they evaluate or choose?
4. **Include Error Paths**: What happens when things go wrong?
5. **Define Success States**: What does completion look like?

## Card Sorting Concepts

### Open Card Sorting
- **Process**: Users group content cards into categories they create
- **When to Use**: Understanding mental models, creating new navigation
- **Analysis**: Look for common groupings across participants
- **Output**: Natural category names and content organization

### Closed Card Sorting
- **Process**: Users sort cards into predefined categories
- **When to Use**: Validating existing navigation, optimizing current structure
- **Analysis**: Success rates per category, items that don't fit
- **Output**: Refinements to existing structure

### Deriving Navigation from Content Grouping

1. **Analyze Grouping Patterns**: Which items consistently group together?
2. **Identify Category Names**: What do users call these groups?
3. **Check Hierarchy Logic**: Do subcategories make sense within main categories?
4. **Validate with Task Testing**: Can users find specific items?
5. **Iterate Based on Results**: Refine groupings and labels

## Screen Inventory Format

| Screen Name | Purpose | Key Content Blocks | Primary Action | Secondary Actions |
|-------------|---------|-------------------|----------------|-------------------|
| Homepage | Convert visitors to trial users | Hero, Features, Social Proof, CTA | Start Free Trial | Learn More, View Pricing |
| Pricing | Present pricing options | Pricing Table, Feature Comparison | Choose Plan | Contact Sales, View Demo |
| Sign-up | Capture user information | Registration Form, Value Props | Create Account | Sign in, Back to Pricing |
| Dashboard | Show user overview and navigation | Metrics Cards, Quick Actions, Navigation | View Reports | Create New, Settings |
| User Profile | Manage account settings | Profile Form, Security Settings, Billing | Save Changes | Change Password, Cancel Account |
| Reports | Display user analytics | Data Tables, Charts, Filters | Export Data | Share Report, Schedule |
| Help Center | Provide user support | Search, Categories, Popular Articles | Search Help | Contact Support, Video Tutorials |
| Contact | Enable user communication | Contact Form, Office Info, Hours | Send Message | Call Us, Live Chat |

---

## IA Document Output Template

### Project Overview
- **Project Name**: [Product/Site Name]
- **Audience**: [Primary user segments]
- **Business Goals**: [Key objectives]
- **Content Scope**: [Types and volume of content]

### Site Architecture

#### Sitemap
```
[ASCII sitemap structure]
```

#### Navigation Design

**Primary Navigation**:
- [List main navigation items]
- **Rationale**: [Why this structure serves user goals]

**Secondary Navigation**:
- [Footer, contextual, utility navigation]
- **Placement**: [Where each type appears]

**Mobile Navigation**:
- **Pattern**: [Hamburger, tabs, etc.]
- **Responsive Behavior**: [How desktop nav transforms]

#### URL Structure
```
domain.com/
├── about/
├── products/
│   ├── category-a/
│   │   └── product-name/
│   └── category-b/
├── services/
└── contact/
```

### User Flows

#### Primary User Flow: [Most Important Task]
```
[ASCII flowchart of primary user journey]
```

#### Secondary User Flow: [Second Most Important Task]
```
[ASCII flowchart of secondary user journey]
```

### Content Strategy

#### Content Types
- **Hero Content**: [Purpose and requirements]
- **Product Content**: [Structure and tone]
- **Support Content**: [Organization and access]

#### Content Hierarchy
- **H1**: [Page title approach]
- **H2**: [Section organization]
- **H3**: [Subsection structure]

#### CTA Strategy
- **Primary CTA**: [Main conversion goal and placement]
- **Secondary CTAs**: [Alternative actions]
- **Tertiary CTAs**: [Supporting actions]

### Screen Inventory

[Complete screen inventory table with all screens]

### Technical Requirements

#### SEO Considerations
- URL structure optimized for search
- Proper heading hierarchy
- Breadcrumb implementation

#### Accessibility Requirements
- Skip navigation links
- Proper heading structure
- Keyboard navigation support
- Screen reader compatibility

#### Performance Considerations
- Lazy loading for images
- Minimal navigation complexity
- Mobile-first responsive design

### Implementation Notes
- **Phase 1**: [Core pages and navigation]
- **Phase 2**: [Additional features and content]
- **Phase 3**: [Advanced functionality]

### Success Metrics
- **Navigation Success**: Task completion rate
- **Content Findability**: Time to find information
- **User Satisfaction**: Post-navigation surveys
- **Search Success**: Internal search effectiveness