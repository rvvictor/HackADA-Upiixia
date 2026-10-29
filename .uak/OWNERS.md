# Shared-file owners

One writer per shared file. Others ask the owner with `uak msg ID --kind request`. Patterns are relative, with no spaces; directories end in `/`.
An owner is not a prerequisite for everyone: consumers work on published contracts and mocks. To transfer ownership, open a PR to main.

| Pattern | Owner task |
|---|---|
| app/schemas/ | CO-001 |
| app/config.py | CO-001 |
| web/src/lib/types.ts | CO-001 |
| web/src/index.css | CO-002 |
| web/src/lib/ui/ | CO-002 |
| web/src/App.tsx | CO-018 |
| web/src/lib/map/hex.ts | CO-006 |
