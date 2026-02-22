# docs/

This directory contains human-facing documentation for project management.

For agent-facing documentation, see:
- `developmentGuide.md` (project root)
- `memory-bank/` (project root)

## Structure

```
docs/
├── README.md           # This file
├── epic/               # Active epics
├── backlog/            # Planned work
├── templates/          # Document templates
└── archive/            # Completed work
```

## Epic Management

### Creating an Epic
1. Create initial document in `backlog/epics/`
2. Review and prioritize
3. Move to `epic/[epic-name]/` when starting

### Epic Structure
```
epic/[epic-name]/
├── EPIC.md              # Epic definition
├── phase-1/
│   ├── design.md
│   └── tasks.md
└── phase-2/
    └── ...
```

### Completing an Epic
1. Write retrospective
2. Move to `archive/completed-epics/`
3. Update `backlog/README.md`

## Backlog

### Priority Levels
| Level | Description |
|-------|-------------|
| P0 | Immediate, blocker |
| P1 | High priority |
| P2 | Medium priority |
| P3 | Low priority |

### Status
- Idea
- Under Review
- Planned
- In Progress
- On Hold
- Cancelled

## Templates

Copy from `templates/` when creating new documents:
- `epic.md` - Epic definition
- `feature.md` - Feature specification
- `bug_report.md` - Bug report
- `retrospective.md` - Retrospective

## Naming Conventions

- Files: lowercase with hyphens (`my-feature.md`)
- With date: `YYYYMMDD-description.md`
- Archive: `YYYYMMDD-YYYYMMDD-epic-name/`

---
Last Updated: 2026-02-20
