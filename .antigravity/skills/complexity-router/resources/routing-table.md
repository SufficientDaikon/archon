# Routing Decision Matrix

This table maps complexity classifications to optimal execution paths.

## Classification: TRIVIAL

**Characteristics**:

- Token count: <50
- Single-turn response
- No tools needed
- Factual or definitional
- <10 second response time

**Routing Decision**:

- **Model tier**: Fast (Haiku, GPT-5-mini, Gemini-Flash)
- **Execution mode**: Direct response
- **Handler**: None (no skill/agent needed)
- **Estimated cost**: $0.0001 - $0.001 per request
- **Estimated time**: <10 seconds

**Example requests**:

- "What is X?"
- "Define Y"
- "List the HTTP methods"
- "What does CLI stand for?"

**Quality checklist**:

- ✅ Answer is factually correct
- ✅ Response is concise (1-3 sentences)
- ❌ Don't need to execute code/tools
- ❌ Don't need external sources

---

## Classification: SIMPLE

**Characteristics**:

- Token count: 50-200
- Single skill invocation
- Straightforward task
- Clear success criteria
- <30 second response time

**Routing Decision**:

- **Model tier**: Fast (Haiku, GPT-5-mini)
- **Execution mode**: Single skill
- **Handler**: Route to best-matching skill from registry
- **Estimated cost**: $0.001 - $0.01 per request
- **Estimated time**: <30 seconds

**Example requests**:

- "Format this code block"
- "Check spelling in this doc"
- "Run the test suite"
- "List all files matching \*.py"

**Skill selection logic**:

1. Match request keywords to skill `triggers.keywords`
2. Match patterns to skill `triggers.patterns`
3. Select highest-priority match (P0 > P1 > P2 > P3)
4. If multiple matches at same priority, select most recently used

**Quality checklist**:

- ✅ Single skill can handle entire task
- ✅ No multi-step reasoning needed
- ✅ No ambiguity in requirements
- ❌ Don't need multiple skills or synthesis

---

## Classification: MODERATE

**Characteristics**:

- Token count: 200-1000
- Skill + supporting resources
- Some analysis required
- Multiple tool calls
- <2 minute response time

**Routing Decision**:

- **Model tier**: Standard (Sonnet 4.6, GPT-5.1, Gemini-Pro)
- **Execution mode**: Skill with resources loaded
- **Handler**: Skill + resource files from `resources/` directory
- **Estimated cost**: $0.01 - $0.10 per request
- **Estimated time**: <2 minutes

**Example requests**:

- "Review this UI design for accessibility"
- "Debug this error with stack trace"
- "Optimize this database query"
- "Explain how this code works"

**Resource loading strategy**:

1. Load skill's SKILL.md
2. Load all resources marked `load: always`
3. Load on-demand resources if keywords match
4. Include relevant bundle resources if applicable

**Quality checklist**:

- ✅ Skill benefits from reference materials
- ✅ Some domain knowledge required
- ✅ Analysis or synthesis needed
- ❌ Don't need multiple unrelated skills
- ❌ Don't need multi-phase execution

---

## Classification: COMPLEX

**Characteristics**:

- Token count: 1000-3000
- Multi-skill coordination
- Agent-level reasoning
- Synthesis across domains
- <10 minute response time

**Routing Decision**:

- **Model tier**: Premium (Opus 4.6, GPT-5.3) OR Standard (if cost-sensitive)
- **Execution mode**: Agent with multiple skills
- **Handler**: Invoke agent with relevant skill bundle
- **Estimated cost**: $0.10 - $1.00 per request
- **Estimated time**: <10 minutes

**Example requests**:

- "Design and implement this feature"
- "Refactor this module for performance and maintainability"
- "Analyze this security vulnerability and propose fixes"
- "Migrate this component from Vue to React"

**Agent selection logic**:

1. Check for domain-specific agents (e.g., `ui-design-agent`, `debugger-agent`)
2. Fall back to `general-purpose` agent with appropriate bundle
3. Bind relevant skills from matching bundles
4. Load shared resources from bundle

**Skill composition**:

- Load entire bundle (e.g., `web-dev-kit`, `godot-kit`)
- Agent orchestrates which skills to invoke when
- Agent handles handoffs between skills
- Agent synthesizes final result

**Quality checklist**:

- ✅ Task spans multiple skills/domains
- ✅ Requires strategic planning
- ✅ Needs synthesis across steps
- ❌ Don't need full pipeline orchestration

---

## Classification: EXPERT

**Characteristics**:

- Token count: 3000+
- Full pipeline orchestration
- Deep multi-phase analysis
- Research or architecture work
- 10+ minute response time

**Routing Decision**:

- **Model tier**: Premium (Opus 4.6, GPT-5.3, Gemini-Ultra)
- **Execution mode**: Pipeline with multiple agents
- **Handler**: Invoke named pipeline (e.g., `sdd-pipeline`, `ux-pipeline`, `full-product`)
- **Estimated cost**: $1.00 - $10.00+ per request
- **Estimated time**: 10 minutes to hours

**Example requests**:

- "Build a complete authentication system with OAuth2, JWT, and RBAC"
- "Design and implement a real-time multiplayer game feature"
- "Architect a microservices platform with full observability"
- "Research and write a comprehensive technical specification for X"

**Pipeline selection logic**:

1. Match request to registered pipeline triggers
   - `sdd-pipeline`: "build feature \* from scratch"
   - `ux-pipeline`: "design feature \*"
   - `debug-pipeline`: "fix bug \*"
   - `full-product`: "build product \* end-to-end"
2. If no trigger match, route to `general-purpose` agent with expert instructions
3. Pipeline orchestrates agent handoffs automatically

**Pipeline execution**:

- Each phase uses dedicated agent with specialized skills
- Artifacts pass between phases (spec → implementation → review)
- Quality gates between phases
- User can intervene at phase boundaries

**Quality checklist**:

- ✅ Requires comprehensive planning
- ✅ Multiple distinct phases needed
- ✅ Deliverable is substantial (full feature, system, or document)
- ✅ Quality gates and validation required
- ✅ Worth the premium cost

---

## Fallback & Error Handling

### If classification is uncertain:

1. Default to one level higher (err on side of quality)
2. Start execution and monitor for signs of under-provisioning:
   - Vague/incomplete responses
   - Tool errors due to missing capabilities
   - Agent requesting more context
3. If under-provisioned, upgrade and retry

### If selected route fails:

1. Log failure reason
2. Upgrade one classification level
3. Retry with higher-tier route
4. If fails again at Expert level, return error to user

### If user overrides routing:

- Honor explicit model requests (e.g., "use Claude Opus for this")
- Honor explicit agent requests (e.g., "use the debugger agent")
- Honor explicit skill requests (e.g., "apply the react-best-practices skill")
- Log override for analytics but proceed

---

## Cost Tracking

Log every routing decision with:

- Request hash (for deduplication)
- Classification
- Selected model tier
- Estimated cost
- Actual execution time
- Success/failure

Aggregate weekly to identify:

- Over-provisioning opportunities (Complex tasks succeeding on Standard models)
- Under-provisioning patterns (Moderate tasks failing, upgrading to Complex)
- High-cost queries (optimize with caching, better skills, or specialized agents)

**Cost optimization targets**:

- 60% of requests → Fast models (Trivial/Simple)
- 30% of requests → Standard models (Moderate)
- 10% of requests → Premium models (Complex/Expert)
