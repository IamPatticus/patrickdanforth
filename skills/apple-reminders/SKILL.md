---
name: "apple-reminders"
description: "Control Apple Reminders via remindctl."
---

```markdown
openclaw:
  emoji: ⏰
  install:
    - bins:
        - remindctl
      formula: steipete/tap/remindctl
      id: brew
      kind: brew
      label: Install remindctl via Homebrew
  os:
    - darwin
  requires:
    bins:
      - remindctl
```
