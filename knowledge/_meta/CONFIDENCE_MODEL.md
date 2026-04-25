# Confidence Model

Every fact that could influence a security or architectural decision
must be tagged with one of these levels.

| Level | Meaning | Use When |
|-------|---------|----------|
| `confirmed` | Verified through code, config, observation, or capture | Direct technical evidence exists |
| `owner_confirmed` | Declared by the environment owner | Owner attests, no independent verification |
| `standard_default` | Industry-standard value accepted by the owner | Standard value the owner accepts as correct |
| `open_question` | Not yet resolved | Pending confirmation or a known gap |

## Rules

1. Every entry in a technical matrix MUST have a confidence tag.
2. Unconfirmed dependencies MUST be tagged or listed in uncertainty.
3. The domain YAML model MUST include a `metadata.confidence_model` section.
4. The AI agent must surface confidence levels in its answers.
5. Missing confidence tag = `open_question` by default.
