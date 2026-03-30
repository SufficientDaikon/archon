# Shields.io Badges — Full Reference

## Static Badge URL Format

```
https://img.shields.io/badge/{LABEL}-{MESSAGE}-{COLOR}
https://img.shields.io/badge/{MESSAGE}-{COLOR}    ← no label
```

### URL Encoding

| In URL | Renders as |
|--------|-----------|
| `_` | Space |
| `%20` | Space |
| `__` | Literal underscore `_` |
| `--` | Literal dash `-` |
| `%25` | Literal `%` |

Hex colors go **without** `#` in the path: `ff69b4` not `#ff69b4`.

## All Query Parameters

| Parameter | Values | Example |
|-----------|--------|---------|
| `style` | `flat`, `flat-square`, `plastic`, `for-the-badge`, `social` | `?style=for-the-badge` |
| `logo` | Slug from [simpleicons.org](https://simpleicons.org) | `?logo=github` |
| `logoColor` | Any color format | `?logoColor=white` |
| `logoSize` | `auto` for wide logos | `?logoSize=auto` |
| `label` | Override left text | `?label=custom%20label` |
| `labelColor` | Left background color | `?labelColor=555` |
| `color` | Right background color | `?color=fe7d37` |
| `cacheSeconds` | Cache lifetime | `?cacheSeconds=3600` |

## Named Colors

| Name | Alias | Hex | Use for |
|------|-------|-----|---------|
| `brightgreen` | `success` | `#4c1` | Passing, success |
| `green` | -- | `#97ca00` | Good status |
| `yellowgreen` | -- | `#a4a61d` | Acceptable |
| `yellow` | -- | `#dfb317` | Warning |
| `orange` | `important` | `#fe7d37` | Attention needed |
| `red` | `critical` | `#e05d44` | Failing, critical |
| `blue` | `informational` | `#007ec6` | Informational |
| `grey`/`gray` | -- | `#555` | Neutral |
| `lightgrey` | `inactive` | `#9f9f9f` | Inactive/unknown |
| `blueviolet` | -- | `#7e59c2` | Special |

Also accepts: any hex (`ff69b4`), `rgb()`, `hsl()`, CSS named colors (`aqua`, `fuchsia`, etc.).

## Badge Styles Visual Reference

```markdown
![flat](https://img.shields.io/badge/style-flat-blue?style=flat)
![flat-square](https://img.shields.io/badge/style-flat--square-blue?style=flat-square)
![plastic](https://img.shields.io/badge/style-plastic-blue?style=plastic)
![for-the-badge](https://img.shields.io/badge/style-for--the--badge-blue?style=for-the-badge)
![social](https://img.shields.io/badge/style-social-blue?style=social)
```

## Common Static Badge Patterns

### Test Results
```markdown
![tests](https://img.shields.io/badge/tests-9%2F9_passing-brightgreen)
![tests](https://img.shields.io/badge/tests-3_failing-red)
![tests](https://img.shields.io/badge/tests-12%2F14_passing-yellow)
```

### Status Indicators
```markdown
![build](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)
![build](https://img.shields.io/badge/build-failing-red?style=flat-square)
![status](https://img.shields.io/badge/status-beta-orange)
![status](https://img.shields.io/badge/status-stable-brightgreen)
![status](https://img.shields.io/badge/status-deprecated-red)
```

### Technology Badges
```markdown
![PS](https://img.shields.io/badge/PowerShell-blue?logo=powershell&logoColor=white)
![TS](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![.NET](https://img.shields.io/badge/.NET_11-512BD4?logo=dotnet&logoColor=white)
![Node](https://img.shields.io/badge/Node.js-339933?logo=nodedotjs&logoColor=white)
```

### Labels
```markdown
![breaking](https://img.shields.io/badge/breaking_change-yes-red)
![breaking](https://img.shields.io/badge/breaking_change-no-green)
![WG](https://img.shields.io/badge/WG-approved-blue)
![RFC](https://img.shields.io/badge/RFC-required-orange)
![priority](https://img.shields.io/badge/priority-high-red)
```

### For-the-Badge Style (large, bold)
```markdown
![built](https://img.shields.io/badge/Built_With-TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![powered](https://img.shields.io/badge/Powered_By-.NET_11-512BD4?style=for-the-badge&logo=dotnet&logoColor=white)
![license](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
```

### Clickable Badges (linked)
```markdown
[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/user/repo/actions)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://docs.example.com)
```

## Dynamic Badge Endpoints

### GitHub Actions Workflow Status
```markdown
![CI](https://img.shields.io/github/actions/workflow/status/USER/REPO/WORKFLOW.yml?branch=main&logo=github&label=CI)
```

### GitHub License
```markdown
![License](https://img.shields.io/github/license/USER/REPO)
```

### GitHub Stars
```markdown
![Stars](https://img.shields.io/github/stars/USER/REPO?style=social)
```

### GitHub Release
```markdown
![Release](https://img.shields.io/github/v/release/USER/REPO?include_prereleases)
```

### GitHub Issues
```markdown
![Issues](https://img.shields.io/github/issues/USER/REPO)
![Open PRs](https://img.shields.io/github/issues-pr/USER/REPO)
```

### npm Version
```markdown
![npm](https://img.shields.io/npm/v/PACKAGE?logo=npm&color=red)
```

### Code Coverage (Codecov)
```markdown
![Coverage](https://img.shields.io/codecov/c/github/USER/REPO?logo=codecov)
```

### Custom JSON Endpoint
Your server returns:
```json
{
  "schemaVersion": 1,
  "label": "custom",
  "message": "value",
  "color": "blue"
}
```

```markdown
![Custom](https://img.shields.io/endpoint?url=https://your-server.com/badge.json)
```

## Logo Reference

Logos come from [Simple Icons](https://simpleicons.org/). Use the slug (lowercase, no spaces).

Common slugs: `github`, `powershell`, `typescript`, `javascript`, `python`, `dotnet`, `docker`, `npm`, `react`, `vue`, `angular`, `svelte`, `astro`, `cloudflare`, `vercel`, `amazonaws`, `microsoftazure`, `googlecloud`, `postgresql`, `mongodb`, `redis`, `git`, `visualstudiocode`, `neovim`

Find any slug: go to simpleicons.org, search for the icon, the slug is in the URL.
