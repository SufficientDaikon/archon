# django-master

**Meta-Skill Coordinator for Django Development**

## Purpose

Routes Django development requests to the appropriate specialized skill based on whether the focus is ORM/database, REST API, general framework features, or expert-level architecture.

## Routing Logic

### 1. Database/ORM Focus → **django-orm-patterns**

**Trigger keywords:** model, QuerySet, database, filter, select_related, prefetch_related, annotate, aggregate, foreign key, many-to-many, migration, relationships, SQL, query optimization

**Use when:**
- Defining Django models
- Writing database queries with QuerySet API
- Optimizing query performance (N+1 queries)
- Using select_related or prefetch_related
- Defining relationships (ForeignKey, ManyToMany, OneToOne)
- Creating custom managers or QuerySets
- Working with aggregations or annotations
- Database migrations
- Complex filtering or Q objects

**Example requests:**
- "Create a User model with profile"
- "Optimize this query with select_related"
- "How do I filter with multiple conditions?"
- "Create a many-to-many relationship"
- "Write an aggregate query for statistics"
- "Fix N+1 query problem"

---

### 2. REST API Focus → **django-rest-framework**

**Trigger keywords:** DRF, REST, API, serializer, viewset, router, endpoint, APIView, ModelSerializer, pagination, authentication, permissions, JWT, token auth

**Use when:**
- Building REST APIs with Django REST Framework
- Creating serializers (ModelSerializer, custom serializers)
- Implementing viewsets (ModelViewSet, custom viewsets)
- Setting up routers and URL patterns
- API authentication (token, JWT, OAuth)
- API permissions and access control
- Pagination, filtering, searching
- Custom API endpoints
- Nested serializers
- API versioning

**Example requests:**
- "Create a REST API for a blog"
- "Build a ModelSerializer with nested relationships"
- "Implement JWT authentication"
- "Create custom API permissions"
- "Set up pagination for API endpoints"
- "Build a viewset with custom actions"

---

### 3. Django Framework Features → **django-framework**

**Trigger keywords:** admin, forms, templates, views, middleware, settings, static files, Django admin, ModelForm, class-based views, function-based views, URL routing

**Use when:**
- Using Django Admin customization
- Creating forms (ModelForm, custom forms)
- Working with Django templates
- Implementing views (CBV or FBV)
- Configuring settings and middleware
- Managing static files and media
- Using built-in authentication views
- Session management
- Django's batteries-included features
- URL routing and patterns

**Example requests:**
- "Customize the Django admin"
- "Create a ModelForm for user registration"
- "Build a class-based view"
- "Set up Django templates"
- "Configure static files for production"
- "Use Django's built-in authentication"

---

### 4. Expert Architecture/Consultation → **django-expert**

**Trigger keywords:** architecture, best practices, project structure, scalability, deployment, advanced patterns, design patterns, performance, security, Django project setup

**Use when:**
- Starting a new Django project
- Architectural decisions
- Django best practices and conventions
- Complex multi-app architecture
- Performance optimization strategies
- Security best practices
- Deployment and production setup
- Advanced Django patterns
- Project structure decisions
- Scaling Django applications

**Example requests:**
- "How should I structure my Django project?"
- "Design architecture for a multi-tenant SaaS"
- "Django best practices for production"
- "Optimize Django app performance"
- "Secure Django deployment checklist"
- "Design pattern for complex business logic"

---

## Multi-Skill Scenarios

### Building a Complete Django API
1. **django-expert** → Project structure and architecture
2. **django-orm-patterns** → Design models and relationships
3. **django-rest-framework** → Build REST API endpoints
4. **django-framework** → Admin customization (optional)

### Database-Heavy Feature
1. **django-orm-patterns** → Model design and queries
2. **django-framework** → Admin interface for models
3. **django-rest-framework** → API exposure (if needed)

### Full-Stack Django App
1. **django-expert** → Project setup and structure
2. **django-orm-patterns** → Database layer
3. **django-framework** → Views, forms, templates
4. **django-rest-framework** → Optional API layer

---

## Decision Tree

```
Is the request about...

├─ DATABASE, MODELS, QUERIES?
│  └─ django-orm-patterns
│
├─ REST API, SERIALIZERS, VIEWSETS?
│  └─ django-rest-framework
│
├─ ADMIN, FORMS, TEMPLATES, VIEWS?
│  └─ django-framework
│
└─ ARCHITECTURE, BEST PRACTICES, PROJECT SETUP?
   └─ django-expert
```

---

## Layer-Based Routing

### Database Layer
**django-orm-patterns** handles everything related to models, queries, and database

### API Layer
**django-rest-framework** handles REST API creation with DRF

### Framework Layer
**django-framework** handles Django's built-in features (admin, forms, auth, views)

### Architecture Layer
**django-expert** handles high-level design, best practices, and project structure

---

## Technology-Specific Routing

| Technology/Feature | Primary Skill | Secondary Skill |
|-------------------|---------------|-----------------|
| **Models & ORM** | django-orm-patterns | django-expert |
| **REST APIs** | django-rest-framework | django-orm-patterns |
| **Django Admin** | django-framework | django-orm-patterns |
| **Forms** | django-framework | - |
| **Templates** | django-framework | - |
| **Authentication** | django-framework | django-rest-framework |
| **Project Setup** | django-expert | django-framework |
| **Query Optimization** | django-orm-patterns | django-expert |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **New Project** | django-expert | django-framework | django-orm-patterns |
| **Model Design** | django-orm-patterns | django-expert | django-framework |
| **REST API** | django-rest-framework | django-orm-patterns | django-expert |
| **Admin Customization** | django-framework | django-orm-patterns | - |
| **Query Optimization** | django-orm-patterns | django-expert | - |
| **Authentication** | django-framework | django-rest-framework | - |

---

## Self-Evaluation Loop

Before routing, ask:

1. **Is this about PROJECT SETUP or ARCHITECTURE?**
   - Yes → django-expert
   - No → Continue

2. **Is this about DATABASE or MODELS?**
   - Yes → django-orm-patterns
   - No → Continue

3. **Is this about REST API with DRF?**
   - Yes → django-rest-framework
   - No → Continue

4. **Is this about ADMIN, FORMS, VIEWS, or TEMPLATES?**
   - Yes → django-framework
   - No → django-expert (default for unclear cases)

---

## Example Routing Decisions

| User Request | Routed To | Rationale |
|--------------|-----------|-----------|
| "Create a User model" | django-orm-patterns | Model definition |
| "Build a REST API for products" | django-rest-framework | DRF API creation |
| "Customize Django admin" | django-framework | Admin features |
| "Project structure for SaaS app" | django-expert | Architecture |
| "Optimize this QuerySet" | django-orm-patterns | Query optimization |
| "Implement JWT auth for API" | django-rest-framework | DRF authentication |
| "Create a ModelForm" | django-framework | Forms |
| "Design multi-tenant architecture" | django-expert | Advanced architecture |
| "Use select_related" | django-orm-patterns | ORM optimization |
| "Set up API permissions" | django-rest-framework | DRF permissions |

---

## File-Based Detection

Auto-detect focus from file context:

- **models.py** → django-orm-patterns
- **serializers.py** → django-rest-framework
- **views.py (DRF)** → django-rest-framework
- **views.py (Django)** → django-framework
- **admin.py** → django-framework
- **forms.py** → django-framework
- **settings.py** → django-expert
- **urls.py** → django-framework (or DRF if API-focused)

---

## Sequential Workflow Patterns

### Pattern 1: API-First Development
```
django-expert (setup)
    ↓
django-orm-patterns (models)
    ↓
django-rest-framework (API)
```

### Pattern 2: Traditional Django Web App
```
django-expert (setup)
    ↓
django-orm-patterns (models)
    ↓
django-framework (views, forms, admin)
```

### Pattern 3: Optimization Pass
```
django-orm-patterns (query optimization)
    ↓
django-expert (architecture review)
```

---

## Integration Points

### ORM + DRF
- **django-orm-patterns** designs the models
- **django-rest-framework** exposes them via API
- Coordinate: Pass model design to DRF for serializers

### Framework + ORM
- **django-orm-patterns** defines models
- **django-framework** builds admin/forms for those models
- Coordinate: Ensure ModelForm and Admin align with model design

### Expert + All Skills
- **django-expert** provides architectural guidance
- Other skills implement specific layers
- Coordinate: Expert sets conventions, others follow

---

## Quality Gates

Before marking Django work complete:

1. **Models designed?** → django-orm-patterns ✓
2. **API endpoints created?** → django-rest-framework ✓ (if needed)
3. **Admin/Forms configured?** → django-framework ✓ (if needed)
4. **Architecture sound?** → django-expert review ✓
5. **Queries optimized?** → django-orm-patterns ✓

---

## Common Anti-Patterns (Avoid)

- ❌ Using django-framework for ORM questions → Use django-orm-patterns
- ❌ Using django-orm-patterns for DRF serializers → Use django-rest-framework
- ❌ Using django-rest-framework for non-API views → Use django-framework
- ❌ Skipping django-expert for new projects → Always consult for architecture

---

## Notes for AI Assistants

- **Models/Queries** → Always django-orm-patterns
- **DRF/API** → Always django-rest-framework
- **Admin/Forms** → Always django-framework
- **New Project** → Always start with django-expert
- **Unclear** → Default to django-expert for consultation
- **Query performance issues** → django-orm-patterns with django-expert review
- **Consult each SKILL.md** before applying Django knowledge
- **Chain skills** for full-stack features (expert → ORM → DRF/framework)
