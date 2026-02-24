# AGENTS.md - OP_CMS Project Guide

## Project Overview

OP_CMS is a BMAD (Building Mental Models at the Speed of Thought) powered project using the opencode AI agent framework. This is a **database migration project** transitioning from PostgreSQL 16 to MySQL 8.0+.

**BMAD Version:** 6.0.3  
**Communication Language:** Chinese (中文)  
**User Name:** Sacrtap

---

## 交互要求

- Thinking 思考过程用中文表述
- Reply 回答也要用中文回复
- 所有生成的文档都要符合中文的语法规范
- Use context7 for all code generation and API documentation questions.

## Build/Run/Test Commands

### Package Management
```bash
# Using Bun (preferred - lock file present)
bun install          # Install dependencies
bun run <script>     # Run scripts

# Alternative: npm
npm install          # Install dependencies
npm run <script>     # Run scripts
```

### Testing Commands
```bash
# Run all tests
bun test

# Run single test file
bun test path/to/test.spec.ts

# Run tests matching pattern
bun test -t "pattern"

# Run tests with coverage
bun test --coverage
```

### BMAD-Specific Commands
```bash
# Load BMAD agent (activation required)
/bmad-help                    # Get advice on next steps
/bmad-help <your question>    # Contextual help

# Agent commands follow BMAD workflow system
```

---

## Code Style Guidelines

### Import Conventions
- **Absolute imports** from project root using `{project-root}` pattern
- **BMAD files** follow path convention: `{project-root}/_bmad/<module>/<type>/<name>.md`
- **Group imports:** BMAD configs → External libs → Internal modules → Local files
- **Markdown frontmatter** required for all agent/workflow files (YAML format)

### File Naming
- **Kebab-case** for all files: `workflow-config.md`, `agent-dev.md`
- **Agents:** `<module>-<role>.md` (e.g., `bmm-dev.md`, `gds-game-dev.md`)
- **Workflows:** `<action>-<target>.md` (e.g., `quick-dev.md`, `create-architecture.md`)
- **Configs:** `.customize.yaml` suffix for customizations

### Formatting Standards
- **Indentation:** 2 spaces (YAML/Markdown), consistent within code blocks
- **Line length:** Soft wrap at 120 characters
- **Code blocks:** Specify language (```xml, ```yaml, ```typescript)
- **Frontmatter:** YAML between `---` delimiters at file start

### Type Conventions (BMAD Files)
- **Agent definitions:** XML format within ```xml blocks
- **Workflow configs:** YAML with `name`, `description`, and workflow-specific fields
- **Customization files:** YAML with optional overrides (agent, persona, memories, menu)

### Naming Conventions
- **Agent names:** CamelCase internal (e.g., `dev.agent.yaml`), TitleCase display (e.g., "Developer Agent")
- **Workflow names:** kebab-case with action prefix (e.g., `quick-dev`, `create-architecture`)
- **Module prefixes:** 
  - `bmm` - Building Mental Models (core planning/implementation)
  - `bmb` - BMAD Builder (agent/module/workflow creation)
  - `cis` - Creative Intelligence Suite
  - `gds` - Game Development Studio
  - `tea` - Test Architecture Enterprise
  - `core` - BMAD core OS

### Error Handling
- **Agent activation:** MUST load `{project-root}/_bmad/bmm/config.yaml` on activation
- **Validation:** Verify config loaded before proceeding with any output
- **Error reporting:** Stop and report to user if critical files missing
- **Test failures:** NEVER proceed with failing tests - fix immediately

### Documentation Standards
- **Frontmatter required:** All agent/workflow files must have YAML frontmatter
- **Activation steps:** Numbered, sequential, with CRITICAL flags where needed
- **Menu items:** Consistent format: `cmd="trigger"` + description + workflow/exec path
- **Comments:** XML comments for section headers, inline comments for complex logic

---

## BMAD Workflow System

### Agent Activation Protocol (CRITICAL)
1. **Load** the complete agent file from `{project-root}/_bmad/<module>/agents/<role>.md`
2. **Read** `{project-root}/_bmad/bmm/config.yaml` - Store ALL fields as session variables
3. **Verify** config loaded - STOP if failed
4. **Display** greeting with `{user_name}` and menu in `{communication_language}`
5. **WAIT** for user input - NEVER auto-execute menu items
6. **Process** input: Number → menu[n] | Text → fuzzy match

### Workflow Execution
```bash
# Standard workflow pattern
1. LOAD {project-root}/_bmad/core/tasks/workflow.xml (CORE OS for workflows)
2. LOAD the specific workflow YAML/Markdown file
3. FOLLOW every step precisely - no skipping or reordering
4. SAVE outputs after EACH step (never batch)
5. VERIFY completion before next step
```

### Available Modules
- **core** (v6.0.3): BMAD master agent, party mode, editorial review
- **bmm** (v6.0.3): Analyst, Architect, Dev, PM, QA, SM, Tech Writer, UX Designer
- **bmb** (v0.1.6): Agent/Module/Workflow builder and validator
- **cis** (v0.1.8): Brainstorming, Creative Problem Solving, Design Thinking, Innovation Strategy
- **gds** (v0.1.9): Game architecture, design, dev, QA, scrum, solo dev
- **tea** (v1.2.3): Test architecture (ATDD, automation, CI, NFR, test design)

---

## Project Structure

```
OP_CMS/
├── .opencode/              # Opencode agent definitions
│   ├── agent/              # Agent configuration files
│   └── command/            # Command workflow definitions
├── _bmad/                  # BMAD framework
│   ├── _config/            # Installation manifests, customizations
│   ├── bmb/                # Builder module
│   ├── bmm/                # Core planning/implementation module
│   ├── cis/                # Creative intelligence
│   ├── gds/                # Game dev studio
│   └── tea/                # Test architecture
├── _bmad-output/           # Generated planning/implementation artifacts
├── docs/                   # Project documentation (output in Chinese)
└── AGENTS.md               # This file
```

---

## Communication Guidelines

### Language Protocol
- **Primary:** Chinese (中文) for all user communication
- **Exception:** Technical terms, commands, and file paths in English
- **Code comments:** English (industry standard)
- **Documentation output:** Chinese

### Agent Personas
Each agent has a specific persona and communication style:
- **Dev (Amelia):** Ultra-succinct, file paths + AC IDs, no fluff
- **Architect (Winston):** Calm, pragmatic, balances vision with reality
- **PM:** User-focused, business value driven
- **QA:** Detail-oriented, comprehensive, quality-focused

### Menu System
All agents present numbered menus. Users can:
- Type number: Execute menu item[n]
- Type command: Fuzzy match on trigger (e.g., "DS" or "dev-story")
- Type `/bmad-help`: Get contextual guidance

---

## Git Protocol (Critical)

### Commit Standards
- **Conventional Commits** format: `<type>(<scope>): <description>`
- **Commit types:** feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert
- **Auto-detection:** System analyzes changes to suggest type/scope
- **Breaking changes:** Flagged with `!` suffix and BREAKING CHANGE footer

### Security Protocols
- **NEVER** update git config
- **NEVER** run destructive commands (push --force, hard reset) unless explicitly requested
- **NEVER** skip hooks (--no-verify, --no-gpg-sign) unless requested
- **NEVER** force push to main/master - warn user if requested
- **NEVER** commit changes unless explicitly asked

### Commit Workflow
```bash
# Automatic conventional commit analysis
git-commit  # Uses installed git-commit skill
```

---

## Key BMAD Commands Reference

### Core Workflows
- **Dev Story:** Implement stories with TDD approach
- **Code Review:** Multi-faceted quality review
- **Create Architecture:** Document technical decisions
- **Implementation Readiness:** Validate PRD/UX/Architecture alignment

### Quick Flow (for small changes)
- **Quick Spec:** Rapid technical specification
- **Quick Dev:** Implement small features/changes

### Quality Assurance
- **E2E Test Generation:** Automated end-to-end test creation
- **Test Architecture:** ATDD, automation, CI/CD, NFR validation

---

## Best Practices

1. **Always load config first** - `{project-root}/_bmad/bmm/config.yaml` contains critical session variables
2. **Stay in character** - Agents maintain persona until explicit exit
3. **Sequential execution** - Never skip workflow steps or reorder tasks
4. **Test coverage** - All code must have comprehensive test coverage before marking complete
5. **Documentation** - Update changed files list after each task
6. **Language consistency** - Communicate in Chinese unless technical terms require English
7. **File organization** - Follow kebab-case naming and module prefixes
8. **Validation** - Always verify prerequisites before proceeding

---

## Troubleshooting

### Agent Not Loading
1. Check `{project-root}/_bmad/bmm/config.yaml` exists
2. Verify agent file path: `{project-root}/_bmad/<module>/agents/<role>.md`
3. Confirm frontmatter format (YAML between `---`)

### Workflow Not Executing
1. Load CORE OS: `{project-root}/_bmad/core/tasks/workflow.xml`
2. Verify workflow config path is correct
3. Check workflow has required fields (name, description, steps)

### Communication Issues
- Default to Chinese for user-facing text
- Keep technical terms in English
- Reference config.yaml for `{communication_language}` setting

---

**Last Updated:** 2026-02-24  
**BMAD Version:** 6.0.3  
**Project:** OP_CMS (PostgreSQL → MySQL Migration)
