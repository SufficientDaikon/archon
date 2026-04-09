# windows-expert

**Meta-Skill Coordinator for Windows System Administration**

## Purpose

Orchestrates Windows system administration tasks across three domains: crash investigation and error debugging, network performance optimization, and registry-level tuning. All operations use PowerShell and follow safety-first principles with mandatory backups before destructive changes.

## Administration Domains

The Windows toolkit routes based on symptom category:

```
1. CRASH DEBUGGING       -> windows-error-debugger
2. NETWORK OPTIMIZATION  -> windows-network-optimizer
3. REGISTRY MANAGEMENT   -> windows-registry-editor
```

---

## Routing Logic

### 1. Crash Investigation and Error Debugging -> **windows-error-debugger**

**Trigger keywords:** BSOD, crash, blue screen, system error, Event Log, minidump, stop code, system stability, crash investigation, error analysis, bugcheck

**Use when:**
- Investigating PC crashes or BSODs
- Analyzing Windows Event Log entries
- Reading minidump files for crash root cause
- Diagnosing system stability issues
- Troubleshooting application crashes
- Building crash investigation timelines
- Correlating stop codes with known issues

**Deliverable:** Crash investigation report with root cause analysis and remediation steps

**Example requests:**
- "My PC keeps crashing, help me investigate"
- "Analyze this BSOD stop code"
- "Check Event Logs for recent errors"
- "Investigate system stability issues"
- "Read the minidump from today's crash"

---

### 2. Network Performance Optimization -> **windows-network-optimizer**

**Trigger keywords:** slow internet, DNS, NIC, TCP/IP, network tuning, MMCSS, network adapter, latency, bandwidth, network optimization, Wi-Fi

**Use when:**
- Diagnosing slow internet or network performance
- Optimizing DNS configuration
- Tuning NIC (Network Interface Card) settings
- Adjusting TCP/IP parameters for performance
- Configuring MMCSS (Multimedia Class Scheduler Service)
- Optimizing network service priorities
- Fixing Wi-Fi connectivity or performance issues

**Deliverable:** Network optimization report with applied tuning changes

**Example requests:**
- "My internet is slow, optimize it"
- "Tune network settings for gaming"
- "Optimize DNS configuration"
- "Fix network adapter performance"
- "Apply network optimization for low latency"

---

### 3. Registry Management and Performance Tuning -> **windows-registry-editor**

**Trigger keywords:** registry, regedit, performance preset, registry tweak, system tuning, registry backup, optimization preset, Windows performance

**Use when:**
- Applying performance optimization presets
- Making targeted registry modifications
- Creating registry backups before changes
- Implementing curated performance tweaks
- Reverting registry changes
- Tuning Windows behavior via registry keys

**Deliverable:** Registry changes with mandatory backup and verification

**Example requests:**
- "Apply performance optimization preset"
- "Tweak registry for faster startup"
- "Back up registry before making changes"
- "Apply gaming optimization preset"
- "Revert last registry changes"
- "Tune Windows visual effects via registry"

---

## Core Administration Workflows

### Full System Optimization
```
windows-error-debugger (check for stability issues first)
    |
windows-network-optimizer (optimize network stack)
    |
windows-registry-editor (apply performance presets)
    |
DONE -- system optimized
```

### Crash Investigation Pipeline
```
windows-error-debugger (5-phase crash investigation)
    |
IF driver issue -> windows-registry-editor (disable or configure)
    |
IF network-related -> windows-network-optimizer (fix network stack)
    |
DONE -- root cause identified and resolved
```

### Performance Tuning Pipeline
```
windows-registry-editor (backup + apply presets)
    |
windows-network-optimizer (network layer tuning)
    |
DONE
```

---

## Decision Tree

```
What Windows issue are you dealing with?

+-- CRASH, BSOD, OR SYSTEM ERROR?
|   -> windows-error-debugger
|
+-- SLOW NETWORK OR INTERNET?
|   -> windows-network-optimizer
|
+-- PERFORMANCE TUNING OR REGISTRY TWEAKS?
|   -> windows-registry-editor
|
+-- GENERAL SYSTEM OPTIMIZATION?
    -> windows-error-debugger (stability check)
    THEN windows-network-optimizer
    THEN windows-registry-editor
```

---

## State-Based Routing

| Current State | Next Action | Routed To |
|---------------|-------------|-----------|
| **System Crashing** | Investigate crash | windows-error-debugger |
| **Crash Resolved** | Optimize system | windows-network-optimizer or windows-registry-editor |
| **Slow Network** | Network tuning | windows-network-optimizer |
| **Network Optimized** | Further tuning | windows-registry-editor |
| **Performance Request** | Apply presets | windows-registry-editor |
| **Driver Issue Found** | Registry fix | windows-registry-editor |
| **Unknown Instability** | Full investigation | windows-error-debugger |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **Crashes/BSODs** | windows-error-debugger | windows-registry-editor | - |
| **Network Issues** | windows-network-optimizer | windows-registry-editor | - |
| **Performance** | windows-registry-editor | windows-network-optimizer | - |
| **Full Optimization** | windows-error-debugger | windows-network-optimizer | windows-registry-editor |
| **Driver Problems** | windows-error-debugger | windows-registry-editor | - |

---

## Quality Gates

### Gate 1: Stability Baseline
- **Checked by:** windows-error-debugger
- **Criteria:** No recurring crashes, Event Log clean, no pending minidumps, system stable for optimization
- **Pass -> Safe to proceed with optimization**

### Gate 2: Network Health
- **Checked by:** windows-network-optimizer
- **Criteria:** DNS resolving correctly, NIC optimized, TCP/IP parameters tuned, latency within acceptable range
- **Pass -> Network stack healthy**

### Gate 3: Registry Safety
- **Checked by:** windows-registry-editor
- **Criteria:** Backup created before any changes, only curated presets applied, changes verified, rollback path documented
- **Pass -> Registry changes are safe and reversible**

---

## Safety Rules (CRITICAL)

1. **Always back up the registry** before any modification
2. **Never apply untested registry tweaks** -- only use the 6 curated presets
3. **Verify system stability** before applying performance optimizations
4. **Document all changes** for rollback capability
5. **Network changes should be incremental** -- test after each change
6. **Never disable security features** (Windows Defender, firewall) for performance

---

## Input/Output Contracts

### windows-error-debugger
- **Input:** Symptoms (crash frequency, stop codes, error messages), Event Log access
- **Output:** 5-phase investigation report with root cause and remediation

### windows-network-optimizer
- **Input:** Network symptoms, current configuration, optimization goals
- **Output:** Optimized network configuration with applied changes report

### windows-registry-editor
- **Input:** Optimization goal, preset selection
- **Output:** Registry backup, applied changes, verification report

---

## Notes for AI Assistants

- **Always check stability first** with windows-error-debugger before optimizing
- **Registry backups are mandatory** -- never skip this step
- **Only 6 curated presets exist** in windows-registry-editor -- do not invent new tweaks
- **Network optimization is incremental** -- apply one change, test, then proceed
- **PowerShell is the primary tool** -- avoid GUI instructions
- **Consult each SKILL.md** before applying skill knowledge
- **Safety is non-negotiable** -- document everything for rollback
