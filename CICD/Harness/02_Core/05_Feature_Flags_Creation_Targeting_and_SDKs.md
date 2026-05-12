---
tags: [harness, core, feature-flags, flag, targeting, segmentation, sdk, flag-pipeline, variation, A/B-test]
aliases: ["Harness Feature Flags", "Flag Management", "Feature Flag SDK", "Flag Targeting", "Segment", "Flag Pipeline"]
status: stable
updated: 2026-05-11
---

# Feature Flags — Flag Management, Targeting, and SDKs

> [!summary] Goal
> Master Harness Feature Flags (FF): flag types (boolean, multivariate), targeting rules (segments, users, percentages, custom attributes), flag pipeline (approval flow before flag activation), SDK integration (server-side: Go/Java/Node/Python; client-side: JS/React/Flutter), and flag architecture (proxy, stream vs poll).

## Table of Contents

1. [Flag Types and Creation](#flag-types-and-creation)
2. [Targeting Rules and Segments](#targeting-rules-and-segments)
3. [SDKs and Flag Architecture](#sdks-and-flag-architecture)

---

## Flag Types and Creation

> [!info] Feature flag
> A feature flag is a toggle that controls whether a feature is ON or OFF (or a specific variation) for a given target (user, IP, account). Flags exist in environments (dev/staging/prod) independently. Each flag has a name, identifier, type, permanent flag or temporary flag flag, and tags.

### Flag types

| Type | Variations | Use case |
|:-----|:-----------|:---------|
| **Boolean** | `true` / `false` | Simple on/off kill switch |
| **Multivariate — String** | Custom strings (`"blue"`, `"green"`, `"red"`) | A/B experiments, UI variants |
| **Multivariate — Number** | Custom numbers (`10`, `50`, `100`) | Percentage rollouts, throttling |
| **Multivariate — JSON** | Custom JSON (`{"feature": "new-ui", "variant": "v2"}`) | Complex feature configuration |

```yaml
# Flag configuration (within Harness UI):
name: "new-checkout-flow"
identifier: new_checkout_flow
type: boolean
permanent: false                   # NOT permanent — schedule cleanup date
environments:
  - dev:
      state: "on"
      defaultServe: "false"
      targetingRules:
        - serves: "true"
          segments:
            - "qa-team"
  - prod:
      state: "on"
      defaultServe: "false"
```

### Flag pipeline (change approval)

```text
[Image: Harness UI → Feature Flags → new-checkout-flow → Change Management]

Flag changes can require approval before activating in production:
  1. Developer changes flag state (true for all traffic).
  2. Pipeline triggers: → Approval step (requiring QA sign-off).
  3. Flag change is deployed AFTER approval.
  4. Users see the new feature.

This decouples feature flag activation from code deployment.
```

---

## Targeting Rules and Segments

> [!info] Targeting
> Targeting rules determine WHICH users see a flag variation. Rules are evaluated in order: first match wins. Default fallback serves the `defaultServe` value.

```yaml
# Targeting rule structure (evaluation order matters):
targetingRules:
  - priority: 1                    # Highest priority — evaluated first
    serves:
      - variation: "true"
    segments:
      - "beta-users"               # All beta users get "true"
  - priority: 2
    serves:
      - variation: "true"
    targets:
      - identifier: "user@company.com"   # Individual user override
  - priority: 3
    serves:
      - variation: "true"
      - variation: "false"               # Percentage rollout
        weight: "50"                      # 50% get "true", 50% get "false"
  - defaultServe:                         # Everyone else (no matching rule)
      variation: "false"
```

### Segments

```text
[Image: Harness UI → Feature Flags → Segments → + New Segment]

A segment groups targets (users) by identifiers or custom attributes:
  - "Employee" segment → emails ending with @mycompany.com.
  - "Beta" segment → all users with `account_tier: "beta"`.
  - "Internal" segment → all users with `internal: true`.

Custom attributes in targeting rules:
  - `country` → "US" → US based users get "false" rule.
  - `device` → "mobile" → Mobile users get "true".

Flag change workflow:
  Developer→Edit Flag→Change targeting→Save→Approval (if required)→Promote to Prod.
```

---

## SDKs and Flag Architecture

### SDK integration

```go
// Server-side SDK example (Go):
import (
    "github.com/harness/harness-go-sdk"
)

func main() {
    client, _ := harness.NewClient(&harness.Config{
        ApiKey:     os.Getenv("HARNESS_SDK_KEY"),     // Environment-specific SDK key
        FeatureFlagHost: "https://app.harness.io/ff",  // SaaS endpoint
    })

    // Synchronous evaluation (server-side — fast, always evaluated locally):
    enabled, _ := client.BoolVariation("new-checkout-flow", user, false)
    if enabled {
        // Show new checkout
    } else {
        // Show old checkout
    }
}
```

```javascript
// Client-side SDK (React):
import { useFeatureFlag } from '@harnessio/ff-react-client-sdk';

function CheckoutButton() {
    const enabled = useFeatureFlag('new-checkout-flow');
    return enabled ? <NewCheckout /> : <OldCheckout />;
}
```

### Flag architecture

```text
Architecture overview:
[User Device] → SDK → [Harness SaaS or Proxy] → Flag Evaluation

  - Client-side SDKs: browser/mobile evaluate locally (polling or streaming).
  - Server-side SDKs: evaluate locally on server (cached rules — fast, ~1ms).
  - Flag Proxy: deploy a proxy between SDKs and Harness SaaS for:
    * Reduced latency (proxy in your region).
    * Offline mode (proxy caches flag rules — flags still resolve if proxy goes down).
    * Enterprise security (proxy handles SDK keys, not the client).

Poll interval: client-side SDKs poll for flag changes every 60 seconds by default.
  (Can be reduced for faster flag updates — at cost of more proxy/SaaS requests.)

Flag Relay Proxy: open-source by Harness.
  Features: active-active, Redis-backed cache, local evaluation, health-check endpoints.
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/05_Services_Environments_and_Overrides]] for flag environments
- [[CICD/Harness/01_Foundations/07_Input_Sets_Overlays_and_Triggers]] for flag pipeline triggers
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for flag incorporation in CD
- [[CICD/Harness/02_Core/07_CCM_Cloud_Cost_Management]] for cost analysis of flag experiments
