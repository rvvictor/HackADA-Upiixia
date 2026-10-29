# Shared-file owners

One writer per shared file. Others ask the owner with `uak msg ID --kind request`. Patterns are relative, with no spaces; directories end in `/`.
An owner is not a prerequisite for everyone: consumers work on published contracts and mocks. To transfer ownership, open a PR to main.

| Pattern | Owner task |
|---|---|
| pyproject.toml | PB-021 |
| uv.lock | PB-021 |
| web/package.json | PB-021 |
| web/package-lock.json | PB-021 |
| app/main.py | PB-021 |
| app/config.py | PB-021 |
| web/src/App.tsx | PB-021 |
| web/src/index.css | PB-021 |
| .env.example | PB-021 |
| .gitignore | PB-021 |
| .github/workflows/ | PB-001 |
| .uak/PROJECT.md | PB-001 |
| app/schemas/ | PB-002 |
| app/fixtures/ | PB-002 |
| web/src/lib/types.ts | PB-002 |
| web/DESIGN.md | PB-029 |
| web/src/lib/ui/ | PB-029 |
| web/src/lib/map/ | PB-029 |
| app/services/eventos.py | PB-007 |
