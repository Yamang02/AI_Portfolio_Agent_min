# CLAUDE.md

This file is the entry point for Claude Code agents working on this project.

## Required Reading

Before starting any task, read these files in order:

1. `developmentGuide.md` - Development principles and coding standards
2. `memory-bank/activeContext.md` - Current work state and recent changes
3. `memory-bank/systemPatterns.md` - Architecture decisions (when relevant)

## Memory Bank

The `memory-bank/` directory contains persistent context:

| File | Purpose | When to Read |
|------|---------|--------------|
| projectBrief.md | Project goals and scope | Initial onboarding |
| productContext.md | User personas, problem definition | Feature work |
| systemPatterns.md | Architecture decisions | Structural changes |
| activeContext.md | Current focus, recent changes | Every session |
| progress.md | Completed work, pending tasks, issues | Status check |

## Session End Protocol

When completing a work session, propose updates to:
- `memory-bank/activeContext.md` - What was done, what's next
- `memory-bank/progress.md` - Completed items, new issues discovered

## Key Principles

- Follow coding standards in `developmentGuide.md`
- No emojis in code or documentation
- Check existing patterns before creating new ones
- Document architectural decisions in `systemPatterns.md`
