---
name: ux-test-suite
description: UX testing patterns including task completion testing, error recovery testing, usability scoring, cognitive load heuristics, and flow testing methodology. Use when testing user flows, evaluating usability, or creating UX test plans.
---

# UX Testing Patterns & Methodology

## Task Completion Testing

### Defining Tasks from User Flows

**Task Definition Framework**:
1. **Primary Tasks**: Core user goals (signup, purchase, content creation)
2. **Secondary Tasks**: Supporting actions (profile editing, settings, search)
3. **Edge Case Tasks**: Error recovery, unusual scenarios, boundary conditions

**Task Specification Template**:
```yaml
task_id: "T001"
name: "Complete user registration"
type: "primary"
description: "New user creates account and verifies email"
prerequisites: 
  - "User has valid email address"
  - "User is on homepage"
steps:
  - "Click 'Sign Up' button"
  - "Fill registration form"
  - "Submit form"
  - "Check email for verification"
  - "Click verification link"
success_criteria:
  - "User account is created"
  - "Email is verified"
  - "User is logged in"
  - "Welcome flow is triggered"
estimated_time: "3-5 minutes"
critical_path: true
```

### Success Criteria Per Task

**Completion Rate Metrics**:
- **Full Success**: Task completed without assistance or errors
- **Partial Success**: Task completed with minor issues or assistance  
- **Task Failure**: User unable to complete task or abandons attempt

**Quality Metrics**:
- **Time on Task**: Actual vs. expected completion time
- **Error Rate**: Number of mistakes per task attempt
- **Efficiency**: Steps taken vs. optimal path length
- **Satisfaction**: User-reported ease and satisfaction scores

**Measurement Collection**:
```javascript
// Task completion tracking
const taskMetrics = {
  taskId: 'T001',
  userId: 'user123',
  startTime: Date.now(),
  endTime: null,
  completionStatus: 'in_progress', // 'success', 'partial', 'failed', 'abandoned'
  errorCount: 0,
  stepsCompleted: [],
  optimalSteps: 5,
  actualSteps: 0,
  assistanceRequired: false,
  satisfactionScore: null // 1-5 scale
};
```

### Measuring Completion Rate

**Calculation Formula**:
```
Completion Rate = (Successful Completions / Total Attempts) × 100
Success Rate by Segment = Completions per User Type/Device/Flow Variant
```

**Benchmarks by Task Type**:
- **Primary Tasks**: ≥90% completion rate target
- **Secondary Tasks**: ≥75% completion rate target  
- **Complex Tasks**: ≥60% completion rate acceptable

### Identifying Blocking Issues

**Automatic Detection Patterns**:
- **High Abandonment Points**: >30% users exit at specific step
- **Extended Time on Step**: >3x expected time spent on single step
- **Repeated Error Patterns**: Same error occurs for >20% of users
- **Back/Forward Cycling**: Users repeatedly navigate back/forward

**Issue Classification**:
```yaml
blocking_issue:
  severity: "critical" | "high" | "medium" | "low"
  impact: "task_blocking" | "flow_disrupting" | "efficiency_reducing"
  frequency: percentage of users affected
  location: specific UI element or step
  user_segments: affected user types
  reproduction_steps: how to trigger the issue
  suggested_fix: recommended solution
```

## Error Recovery Testing

### Intentional Error Injection

**Error Injection Scenarios**:
1. **Network Errors**: Simulate connection loss during form submission
2. **Server Errors**: Trigger 500, 503, timeout responses  
3. **Validation Errors**: Submit forms with invalid data
4. **Authentication Errors**: Test expired sessions, invalid tokens
5. **Permission Errors**: Access restricted content without authorization
6. **Data Errors**: Corrupt or missing expected data

**Error Injection Framework**:
```javascript
// Error injection during testing
class ErrorInjector {
  static injectNetworkError(probability = 0.1) {
    if (Math.random() < probability) {
      throw new NetworkError('Connection failed');
    }
  }
  
  static injectValidationError(fieldName, errorType) {
    return {
      field: fieldName,
      error: errorType,
      message: this.getErrorMessage(fieldName, errorType)
    };
  }
  
  static injectServerError(statusCode = 500) {
    throw new ServerError(`Server error ${statusCode}`);
  }
}
```

### Recovery Path Validation

**Recovery Path Testing**:
- **Error Detection**: System recognizes error occurred
- **Error Communication**: User is informed of error clearly
- **Recovery Options**: User has clear path to resolve issue  
- **State Preservation**: User progress is maintained where possible
- **Retry Mechanisms**: User can retry failed actions

**Recovery Path Checklist**:
- [ ] Error message clearly explains what went wrong
- [ ] Specific instructions provided for resolving error
- [ ] User can retry action without losing progress
- [ ] Alternative paths available when primary path fails
- [ ] Contact/support information provided for complex errors
- [ ] Error doesn't break overall application state

### Error Message Quality Assessment

**Error Message Evaluation Criteria**:
```yaml
error_message_quality:
  clarity:
    score: 1-5
    criteria: "Message clearly explains what happened"
  actionability:
    score: 1-5  
    criteria: "Provides specific steps to resolve issue"
  tone:
    score: 1-5
    criteria: "Appropriate, helpful tone (not blaming user)"
  timing:
    score: 1-5
    criteria: "Appears at right time and place"
  visibility:
    score: 1-5
    criteria: "Sufficiently prominent to be noticed"
```

**Good Error Message Examples**:
```html
<!-- Good: Clear, actionable, helpful -->
<div class="error-message" role="alert">
  <h4>We couldn't create your account</h4>
  <p>The email address you entered is already registered.</p>
  <p><strong>What you can do:</strong></p>
  <ul>
    <li><a href="/login">Log in to your existing account</a></li>
    <li><a href="/reset-password">Reset your password</a></li>
    <li>Try a different email address</li>
  </ul>
</div>

<!-- Bad: Vague, unhelpful -->
<div class="error">Error 400: Bad Request</div>
```

### Dead-End Detection

**Dead-End Indicators**:
- No navigation options available
- No way to return to previous state  
- No clear next steps provided
- User cannot complete intended task
- No escape route from error state

**Dead-End Prevention**:
```javascript
// Dead-end detection system
class DeadEndDetector {
  static checkForDeadEnd(currentPage) {
    const hasNavigation = this.hasNavigationOptions(currentPage);
    const hasActions = this.hasAvailableActions(currentPage);
    const hasEscape = this.hasEscapeRoute(currentPage);
    
    return {
      isDeadEnd: !hasNavigation && !hasActions && !hasEscape,
      severity: this.calculateSeverity(hasNavigation, hasActions, hasEscape),
      recommendations: this.getRecommendations(currentPage)
    };
  }
}
```

## Flow Testing Methodology

### Step-by-Step Flow Validation

**Flow Testing Framework**:
1. **Flow Mapping**: Document each step and decision point
2. **State Validation**: Verify correct state at each step
3. **Transition Testing**: Test all possible step transitions
4. **Data Persistence**: Ensure data carries through flow correctly
5. **Exit Point Testing**: Validate behavior when flow is abandoned

**Flow Step Specification**:
```yaml
flow_step:
  step_id: "checkout_001"
  step_name: "Review Cart"
  preconditions:
    - "User has items in cart"
    - "User is logged in"
  actions_available:
    - "Edit quantities"
    - "Remove items"  
    - "Add promo code"
    - "Proceed to shipping"
  success_criteria:
    - "Cart totals are accurate"
    - "All items display correctly"
    - "Promo codes apply properly"
  failure_conditions:
    - "Cart is empty"
    - "Prices are incorrect"
    - "Items are out of stock"
  next_steps:
    - "shipping_info" (primary)
    - "continue_shopping" (secondary)
```

### Branch Coverage Testing

**Flow Branch Types**:
- **Happy Path**: Ideal user journey without errors
- **Alternative Paths**: Different but valid routes to completion  
- **Error Paths**: Recovery routes when errors occur
- **Edge Case Paths**: Unusual but possible scenarios

**Branch Coverage Checklist**:
- [ ] Primary happy path tested end-to-end
- [ ] All alternative completion paths tested
- [ ] Error recovery paths from each step tested
- [ ] Edge cases and boundary conditions tested
- [ ] User can navigate between different branches appropriately

**Branch Testing Matrix**:
```yaml
checkout_flow_branches:
  guest_checkout:
    path: "cart → shipping → payment → confirmation"
    coverage: "required"
  registered_user_checkout:
    path: "cart → (saved_addresses) → payment → confirmation"  
    coverage: "required"
  new_user_checkout:
    path: "cart → register → shipping → payment → confirmation"
    coverage: "required"
  error_recovery:
    path: "payment_failed → retry_payment → confirmation"
    coverage: "required"
  cart_modification:
    path: "cart → edit_items → recalculate → continue"
    coverage: "optional_but_recommended"
```

### Entry/Exit Point Testing

**Entry Point Validation**:
- Users can enter flow from multiple legitimate sources
- Flow state initializes correctly regardless of entry point
- Required data is available or collected appropriately
- User permissions are verified at entry

**Exit Point Validation**:  
- Users can exit flow gracefully at any step
- Progress is saved appropriately when flow is abandoned
- Users can re-enter flow and resume from correct point
- Exit points don't leave system in inconsistent state

**Entry/Exit Testing**:
```javascript
// Entry point testing
const entryPoints = [
  { source: 'homepage_cta', expectedState: 'flow_start' },
  { source: 'product_page', expectedState: 'product_selected' },
  { source: 'email_link', expectedState: 'authenticated_start' },
  { source: 'deep_link', expectedState: 'step_specific' }
];

// Exit point testing  
const exitPoints = [
  { step: 'any', action: 'browser_back', expectation: 'safe_exit' },
  { step: 'any', action: 'close_tab', expectation: 'progress_saved' },
  { step: 'payment', action: 'abandon', expectation: 'cart_preserved' },
  { step: 'final', action: 'complete', expectation: 'success_state' }
];
```

### Cross-Flow Navigation

**Cross-Flow Scenarios**:
- User switches between different task flows
- User accesses secondary features during primary flow  
- User navigates to help/support during flow
- User receives external interruption (notification, call, etc.)

**Navigation Testing**:
- Flow state is preserved when user navigates away
- User can return to previous flow step appropriately
- Context switching doesn't create confusion
- Multiple flows can run simultaneously if needed

## Usability Scoring Rubrics

### System Usability Scale (SUS) for Automated Evaluation

**Standard SUS Questions Adapted for Automated Testing**:
1. **Frequency of Use**: How often do users complete key tasks successfully?
2. **Complexity Assessment**: How many steps/errors occur in standard workflows?
3. **Ease of Use**: What percentage of users complete tasks without assistance?
4. **Technical Support**: How often do users need help documentation or support?
5. **Function Integration**: Do features work well together without conflicts?
6. **Consistency**: Are interaction patterns consistent across the interface?
7. **Learning Curve**: How quickly do new users achieve task completion?
8. **Confidence**: Do users complete tasks without hesitation or retry?
9. **Learning Requirement**: How much training/documentation is needed?
10. **System Preparedness**: Is the system ready for users before they attempt tasks?

**Automated SUS Scoring**:
```javascript
// Convert automated metrics to SUS scores
class AutomatedSUSCalculator {
  static calculateSUS(metrics) {
    const scores = {
      q1: this.mapCompletionRateToSUS(metrics.completionRate),
      q2: this.mapComplexityToSUS(metrics.avgSteps, metrics.optimalSteps),
      q3: this.mapAssistanceRateToSUS(metrics.assistanceRate),
      q4: this.mapSupportRequestRateToSUS(metrics.supportRate),
      q5: this.mapIntegrationScoreToSUS(metrics.integrationScore),
      q6: this.mapConsistencyScoreToSUS(metrics.consistencyScore),
      q7: this.mapLearningCurveToSUS(metrics.newUserSuccessRate),
      q8: this.mapConfidenceToSUS(metrics.retryRate),
      q9: this.mapDocumentationUsageToSUS(metrics.docUsageRate),
      q10: this.mapReadinessToSUS(metrics.errorRate)
    };
    
    // Calculate final SUS score (0-100)
    const susScore = Object.values(scores).reduce((sum, score) => sum + score, 0) * 2.5;
    return Math.round(susScore);
  }
}
```

**SUS Score Interpretation**:
- **≥80**: Excellent usability
- **70-79**: Good usability  
- **60-69**: Acceptable usability
- **50-59**: Below average usability
- **<50**: Poor usability requiring immediate attention

### UMUX-LITE (2-Question Variant)

**UMUX-LITE Questions**:
1. "This system's capabilities meet my requirements"
2. "This system is easy to use"

**Automated UMUX-LITE Scoring**:
```javascript
// Map automated metrics to UMUX-LITE responses
class UMUXLiteCalculator {
  static calculateUMUXLite(metrics) {
    // Question 1: Capabilities meet requirements
    const q1Score = this.mapFeatureCompletionRate(metrics.featureUsageSuccess);
    
    // Question 2: Easy to use  
    const q2Score = this.mapOverallEaseOfUse(metrics.avgTaskTime, metrics.errorRate);
    
    // UMUX-LITE score calculation
    const umuxScore = ((q1Score + q2Score - 2) / 5) * 100;
    return Math.round(umuxScore);
  }
}
```

### Inferring Scores from Automated Test Results

**Metric Mapping Framework**:
```yaml
usability_metrics_mapping:
  task_completion_rate:
    high: ">90% maps to SUS Q3 score 5"
    medium: "70-90% maps to SUS Q3 score 3-4"  
    low: "<70% maps to SUS Q3 score 1-2"
  
  error_rate:
    low: "<5% errors maps to SUS Q2 score 5"
    medium: "5-15% errors maps to SUS Q2 score 3-4"
    high: ">15% errors maps to SUS Q2 score 1-2"
    
  time_efficiency:
    high: "≤110% of optimal time maps to ease score 5"
    medium: "110-150% of optimal time maps to ease score 3-4"  
    low: ">150% of optimal time maps to ease score 1-2"
```

## Cognitive Load Heuristics

### Information Density Measurement

**Elements Per Viewport Calculation**:
```javascript
class CognitiveLoadAnalyzer {
  static measureInformationDensity(viewport) {
    const interactiveElements = viewport.querySelectorAll('button, a, input, select, textarea');
    const informationElements = viewport.querySelectorAll('h1, h2, h3, p, li, td');
    const visualElements = viewport.querySelectorAll('img, svg, canvas, video');
    
    const totalElements = interactiveElements.length + informationElements.length + visualElements.length;
    const viewportArea = viewport.clientWidth * viewport.clientHeight;
    
    return {
      totalElements,
      elementsPerViewport: totalElements,
      elementDensityRatio: totalElements / (viewportArea / 10000), // per 10k pixels
      interactiveElementCount: interactiveElements.length,
      informationElementCount: informationElements.length,
      visualElementCount: visualElements.length
    };
  }
}
```

**Density Thresholds**:
- **Mobile**: <15 interactive elements per viewport
- **Tablet**: <25 interactive elements per viewport
- **Desktop**: <35 interactive elements per viewport

### Choice Overload Detection

**Choice Overload Rules**:
- **7±2 Rule**: More than 9 options without grouping creates overload
- **Category Limits**: More than 5-7 items per category becomes overwhelming
- **Decision Points**: Multiple choice points in sequence increase cognitive burden

**Choice Analysis**:
```javascript
class ChoiceOverloadDetector {
  static analyzeChoices(container) {
    const choiceElements = container.querySelectorAll('[role="radio"], [role="checkbox"], option, .choice-item');
    const choiceCount = choiceElements.length;
    
    // Check for grouping/categorization
    const groups = container.querySelectorAll('[role="group"], .choice-group, fieldset');
    const hasGrouping = groups.length > 0;
    
    // Analyze choice complexity
    const complexity = this.calculateChoiceComplexity(choiceElements);
    
    return {
      choiceCount,
      hasOverload: choiceCount > 7 && !hasGrouping,
      overloadSeverity: this.calculateOverloadSeverity(choiceCount, hasGrouping),
      groupingPresent: hasGrouping,
      recommendations: this.getChoiceRecommendations(choiceCount, hasGrouping)
    };
  }
}
```

### Working Memory Assessment

**Working Memory Load Factors**:
1. **Information Retention**: How much info must user remember between steps
2. **Context Switching**: How often user must switch between different contexts  
3. **Concurrent Tasks**: Multiple tasks user must manage simultaneously
4. **Temporal Distance**: Time between related actions

**Memory Load Calculation**:
```javascript
class WorkingMemoryAnalyzer {
  static assessMemoryLoad(userFlow) {
    const memoryRequirements = {
      informationRetention: this.calculateRetentionLoad(userFlow),
      contextSwitching: this.calculateSwitchingLoad(userFlow),
      concurrentTasks: this.calculateConcurrencyLoad(userFlow),
      temporalDistance: this.calculateTemporalLoad(userFlow)
    };
    
    const totalLoad = Object.values(memoryRequirements).reduce((sum, load) => sum + load, 0);
    
    return {
      ...memoryRequirements,
      totalLoad,
      severity: this.assessLoadSeverity(totalLoad),
      recommendations: this.getMemoryRecommendations(memoryRequirements)
    };
  }
}
```

### Recognition vs Recall Scoring

**Recognition vs Recall Evaluation**:
- **Recognition**: User can identify correct option from visible choices
- **Recall**: User must remember information not currently visible
- **Scoring**: Higher recognition scores indicate better usability

**Recognition/Recall Analysis**:
```javascript
class RecognitionRecallAnalyzer {
  static analyzeInterface(interface) {
    const recognitionElements = interface.querySelectorAll('[role="menu"], [role="tab"], .button-group, .nav-links');
    const recallRequiredElements = interface.querySelectorAll('input[type="text"], textarea, [data-requires-recall]');
    
    const recognitionScore = this.calculateRecognitionSupport(recognitionElements);
    const recallBurden = this.calculateRecallBurden(recallRequiredElements);
    
    return {
      recognitionScore, // 0-100, higher is better
      recallBurden,     // 0-100, lower is better  
      overallScore: (recognitionScore - recallBurden + 100) / 2,
      recommendations: this.getRecognitionRecommendations(recognitionScore, recallBurden)
    };
  }
}
```

## Accessibility Testing Patterns

### axe-core Integration Patterns

**Automated Accessibility Testing Setup**:
```javascript
// axe-core integration for automated testing
import { AxePuppeteer } from '@axe-core/puppeteer';

class AccessibilityTester {
  static async runAxeTests(page, context = {}) {
    const axeBuilder = new AxePuppeteer(page);
    
    // Configure axe for WCAG 2.1 AA compliance
    const results = await axeBuilder
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    return {
      violations: results.violations,
      passes: results.passes,
      incomplete: results.incomplete,
      inapplicable: results.inapplicable,
      score: this.calculateAccessibilityScore(results),
      summary: this.generateAccessibilitySummary(results)
    };
  }
  
  static calculateAccessibilityScore(axeResults) {
    const { violations, passes } = axeResults;
    const totalTests = violations.length + passes.length;
    const passedTests = passes.length;
    
    return totalTests > 0 ? (passedTests / totalTests) * 100 : 100;
  }
}
```

### WCAG 2.1 AA Automated Checks

**Automated WCAG Compliance Testing**:
```yaml
wcag_automated_checks:
  perceivable:
    1.1.1_non_text_content:
      test: "Images have alt attributes"
      automation: "axe-core rule: image-alt"
    1.4.3_contrast_minimum:
      test: "Color contrast ratio 4.5:1 normal text, 3:1 large text"
      automation: "axe-core rule: color-contrast"
    1.4.11_non_text_contrast:
      test: "UI components contrast 3:1"
      automation: "axe-core rule: color-contrast-enhanced"
      
  operable:
    2.1.1_keyboard:
      test: "All functionality available via keyboard"
      automation: "Custom script: keyboard navigation test"
    2.4.3_focus_order:
      test: "Focus order is logical"
      automation: "axe-core rule: focus-order-semantics"
    2.5.5_target_size:
      test: "Touch targets at least 44x44px"  
      automation: "Custom script: touch target size check"
      
  understandable:
    3.1.1_language_of_page:
      test: "Page language identified"
      automation: "axe-core rule: html-has-lang"
    3.2.1_on_focus:
      test: "Focus doesn't trigger context changes"
      automation: "Custom script: focus change detection"
      
  robust:
    4.1.1_parsing:
      test: "HTML is valid"
      automation: "axe-core rule: valid-html"
    4.1.2_name_role_value:
      test: "Elements have accessible names and roles"
      automation: "axe-core rule: aria-roles, button-name, etc."
```

### Manual Check Items (Cannot be Automated)

**Manual Accessibility Testing Checklist**:
- [ ] **Keyboard Navigation Flow**: Tab order follows logical reading order
- [ ] **Focus Indicators**: All focusable elements have visible focus indicators
- [ ] **Screen Reader Testing**: Content is announced correctly and in logical order
- [ ] **Zoom Testing**: Interface works at 200% zoom without horizontal scrolling
- [ ] **Motion Sensitivity**: Animations can be paused or disabled
- [ ] **Cognitive Load**: Content is written at appropriate reading level
- [ ] **Error Recovery**: Users can understand and recover from errors independently

### Common Violations Ranked by Frequency

**Top 10 Most Common Accessibility Violations**:
1. **Missing Alt Text** (28% of sites): Images without descriptive alt attributes
2. **Low Color Contrast** (23% of sites): Text doesn't meet 4.5:1 contrast ratio
3. **Missing Form Labels** (19% of sites): Form inputs without associated labels
4. **Empty Links** (15% of sites): Links without descriptive text
5. **Missing Page Titles** (12% of sites): Pages without descriptive titles
6. **Improper Heading Structure** (11% of sites): Skipped heading levels or missing H1
7. **Missing Language Declaration** (10% of sites): HTML lang attribute missing
8. **Insufficient Touch Target Size** (8% of sites): Buttons/links smaller than 44px
9. **Missing Skip Links** (7% of sites): No way to skip navigation
10. **Improper ARIA Usage** (6% of sites): Incorrect or conflicting ARIA attributes

## Performance Testing Patterns

### Lighthouse Categories Integration

**Automated Lighthouse Testing**:
```javascript
import lighthouse from 'lighthouse';
import chromeLauncher from 'chrome-launcher';

class PerformanceTester {
  static async runLighthouseAudit(url, options = {}) {
    const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
    
    const lighthouseOptions = {
      logLevel: 'info',
      output: 'json',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      port: chrome.port,
      ...options
    };
    
    const runnerResult = await lighthouse(url, lighthouseOptions);
    await chrome.kill();
    
    const { lhr } = runnerResult;
    
    return {
      performance: lhr.categories.performance.score * 100,
      accessibility: lhr.categories.accessibility.score * 100,
      bestPractices: lhr.categories['best-practices'].score * 100,
      seo: lhr.categories.seo.score * 100,
      metrics: {
        firstContentfulPaint: lhr.audits['first-contentful-paint'].numericValue,
        largestContentfulPaint: lhr.audits['largest-contentful-paint'].numericValue,
        cumulativeLayoutShift: lhr.audits['cumulative-layout-shift'].numericValue,
        totalBlockingTime: lhr.audits['total-blocking-time'].numericValue
      },
      opportunities: lhr.audits,
      score: this.calculateOverallScore(lhr.categories)
    };
  }
}
```

### Core Web Vitals (LCP, FID/INP, CLS)

**Core Web Vitals Measurement**:
```javascript
class CoreWebVitalsAnalyzer {
  static measureCoreWebVitals() {
    const vitals = {
      lcp: null,  // Largest Contentful Paint
      fid: null,  // First Input Delay  
      inp: null,  // Interaction to Next Paint
      cls: null   // Cumulative Layout Shift
    };
    
    // LCP measurement
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      vitals.lcp = lastEntry.startTime;
    }).observe({ entryTypes: ['largest-contentful-paint'] });
    
    // FID measurement
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.processingStart && entry.startTime) {
          vitals.fid = entry.processingStart - entry.startTime;
        }
      });
    }).observe({ entryTypes: ['first-input'] });
    
    // CLS measurement
    new PerformanceObserver((list) => {
      let clsValue = 0;
      list.getEntries().forEach((entry) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });
      vitals.cls = clsValue;
    }).observe({ entryTypes: ['layout-shift'] });
    
    return vitals;
  }
  
  static assessVitalsPerformance(vitals) {
    return {
      lcp: {
        value: vitals.lcp,
        rating: vitals.lcp <= 2500 ? 'good' : vitals.lcp <= 4000 ? 'needs-improvement' : 'poor'
      },
      fid: {
        value: vitals.fid,
        rating: vitals.fid <= 100 ? 'good' : vitals.fid <= 300 ? 'needs-improvement' : 'poor'
      },
      cls: {
        value: vitals.cls,
        rating: vitals.cls <= 0.1 ? 'good' : vitals.cls <= 0.25 ? 'needs-improvement' : 'poor'
      }
    };
  }
}
```

**Core Web Vitals Thresholds**:
- **LCP (Largest Contentful Paint)**:
  - Good: ≤2.5 seconds
  - Needs Improvement: 2.5-4.0 seconds  
  - Poor: >4.0 seconds

- **FID (First Input Delay) / INP (Interaction to Next Paint)**:
  - Good: ≤100ms (FID) / ≤200ms (INP)
  - Needs Improvement: 100-300ms (FID) / 200-500ms (INP)
  - Poor: >300ms (FID) / >500ms (INP)

- **CLS (Cumulative Layout Shift)**:
  - Good: ≤0.1
  - Needs Improvement: 0.1-0.25
  - Poor: >0.25

### Asset Budget Guidelines

**Performance Budget Framework**:
```yaml
asset_budgets:
  total_page_size:
    mobile: "1.5MB max"
    desktop: "3MB max"
  
  javascript_bundle:
    critical: "150KB max (gzipped)"
    total: "500KB max (gzipped)"
  
  css_bundle:
    critical: "50KB max (gzipped)" 
    total: "150KB max (gzipped)"
  
  images:
    hero_image: "200KB max"
    content_images: "100KB max each"
    total_images: "1MB max per page"
  
  fonts:
    web_fonts: "300KB max total"
    font_families: "3 max per page"
  
  third_party:
    analytics: "50KB max"
    tracking: "100KB max total"
    widgets: "200KB max total"

loading_time_budgets:
  first_contentful_paint: "1.5s max"
  largest_contentful_paint: "2.5s max"  
  time_to_interactive: "3.5s max"
  first_input_delay: "100ms max"
```

## Test Report Format

### Comprehensive Test Report Template

```yaml
ux_test_report:
  metadata:
    project_name: "Project Name"
    test_date: "2025-01-15"
    test_version: "v1.2.0"
    tester: "UX Test Suite"
    environment: "staging" | "production"
    devices_tested: ["mobile", "tablet", "desktop"]
    browsers_tested: ["chrome", "firefox", "safari", "edge"]
  
  executive_summary:
    overall_score: "85/100"
    critical_issues: 3
    standard_issues: 12
    passed_tests: 47
    failed_tests: 8
    recommendation: "Approved with conditions"
  
  task_completion_analysis:
    primary_tasks:
      - task_id: "T001"
        name: "User Registration"
        completion_rate: "92%"
        avg_time: "4.2 minutes"
        error_rate: "8%"
        satisfaction: "4.1/5"
        status: "passed"
    
    secondary_tasks:
      - task_id: "T002"  
        name: "Profile Update"
        completion_rate: "76%"
        avg_time: "6.8 minutes"
        error_rate: "15%"
        satisfaction: "3.4/5"
        status: "needs_improvement"
  
  usability_scores:
    sus_score: "78/100"
    umux_lite_score: "72/100"
    cognitive_load_score: "83/100"
    accessibility_score: "89/100"
  
  performance_metrics:
    lighthouse_scores:
      performance: 85
      accessibility: 94
      best_practices: 91
      seo: 88
    core_web_vitals:
      lcp: "2.1s (good)"
      fid: "95ms (good)"
      cls: "0.08 (good)"
  
  detailed_findings:
    critical_issues:
      - finding_id: "UX-001"
        category: "Task Completion"
        description: "Registration flow blocks 8% of users at email verification step"
        impact: "High - prevents account creation"
        recommendation: "Add resend verification email button with clear instructions"
        
    accessibility_issues:
      - finding_id: "A11Y-003"
        category: "Keyboard Navigation"
        description: "Modal dialogs trap focus incorrectly"
        impact: "Critical for keyboard users"
        recommendation: "Implement proper focus management in modal components"
  
  flow_analysis:
    checkout_flow:
      completion_rate: "87%"
      abandonment_points:
        - step: "payment_info"
          abandonment_rate: "23%"
          reason: "Form validation errors unclear"
      recovery_rate: "65%"
  
  recommendations:
    immediate_fixes:
      - "Fix modal focus trapping (A11Y-003)"
      - "Add email verification resend button (UX-001)"
      - "Improve payment form validation messages"
    
    future_improvements:
      - "Optimize images for better LCP score"
      - "Implement progressive enhancement for form validation"
      - "Add micro-animations for better perceived performance"
  
  test_coverage:
    total_test_cases: 124
    executed_tests: 118
    passed_tests: 95
    failed_tests: 23
    coverage_percentage: "95%"
```

### Summary Dashboard Data

**Test Result Dashboard Metrics**:
```javascript
const dashboardData = {
  overallHealthScore: 85, // 0-100 composite score
  
  categoryScores: {
    taskCompletion: 89,
    usability: 78,
    accessibility: 94,
    performance: 85,
    errorRecovery: 72
  },
  
  trendData: {
    previousScore: 79,
    improvement: +6,
    trendDirection: 'improving'
  },
  
  criticalAlerts: [
    'Modal focus trapping fails accessibility standards',
    'Payment form causes 23% checkout abandonment',
    'Mobile performance below threshold on 3G networks'
  ],
  
  quickWins: [
    'Add loading spinners to async operations',
    'Improve error message clarity',
    'Optimize largest contentful paint image'
  ]
};
```