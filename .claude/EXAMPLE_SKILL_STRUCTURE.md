# Skills 转换示例

本文档展示如何将现有的 `.claude/commands/create-prd.md` 转换为符合 Skills 规范的格式。

## 原始结构

```
.claude/commands/create-prd.md  (单个文件，包含所有内容)
```

## 转换后的 Skill 结构

```
skill-create-prd/
├── SKILL.md                      (核心指令，添加 frontmatter)
└── references/
    └── prd-structure.md          (详细的 PRD 结构说明，从原文件提取)
```

## SKILL.md 示例

```markdown
---
name: create-prd
description: Create a Product Requirements Document from conversation. Use when the user wants to generate a comprehensive PRD based on current discussion context and requirements.
metadata:
  short-description: Generate Product Requirements Document
---

# Create PRD: Generate Product Requirements Document

## Overview

Generate a comprehensive Product Requirements Document (PRD) based on the current conversation context and requirements discussed.

## When to Use

Use this skill when:
- User asks to create a PRD
- User wants to document product requirements
- User needs a structured requirements document
- Generating product specifications from conversation

## Output File

Write the PRD to the specified file (default: `PRD.md` in current directory).

## Process

1. **Analyze Conversation Context**
   - Extract feature requirements from conversation
   - Identify user stories and use cases
   - Note technical constraints and preferences

2. **Structure the PRD**
   - Use the standard PRD structure (see [PRD Structure Guide](references/prd-structure.md))
   - Adapt sections based on available information
   - Mark MVP scope with ✅ (in scope) and ❌ (out of scope)

3. **Write the Document**
   - Be comprehensive but concise
   - Include concrete examples
   - Use checkboxes for actionable items
   - Link to related documentation when appropriate

## Quick Reference

### Core Sections (Required)

1. Executive Summary - Product overview and MVP goal
2. Mission - Mission statement and core principles
3. Target Users - User personas and needs
4. MVP Scope - In scope vs out of scope features
5. User Stories - Primary user stories in "As a [user]..." format
6. Core Architecture - Architecture and patterns
7. Technology Stack - Technologies with versions
8. Security & Configuration - Auth, config, deployment
9. Success Criteria - MVP success definition
10. Implementation Phases - Phased approach with deliverables

### Additional Sections (As Needed)

- API Specification
- Future Considerations
- Risks & Mitigations
- Appendix

## Detailed Reference

For comprehensive PRD structure, section templates, and examples, see [PRD Structure Guide](references/prd-structure.md).

## Output Format

- Use Markdown format
- Include frontmatter if needed (for project documentation)
- Use checkboxes (✅/❌) for scoping
- Structure with clear headings and subheadings
- Include code examples in appropriate language blocks
```

## references/prd-structure.md 示例

（这部分应该包含原 `create-prd.md` 中的详细内容，如完整的章节说明、示例等）

```markdown
# PRD Structure Guide

This reference contains detailed specifications for each PRD section.

## 1. Executive Summary

**Purpose:** Concise product overview (2-3 paragraphs)
**Contents:**
- Core value proposition
- MVP goal statement
- Key differentiators

**Example:**
[具体示例...]

## 2. Mission

**Purpose:** Product mission statement and core principles
**Contents:**
- Mission statement (1-2 sentences)
- Core principles (3-5 key principles)
- Product philosophy

[... 其他章节的详细说明 ...]
```

## 关键转换点

### 1. Frontmatter 添加

**原文件：**
```markdown
---
description: Create a Product Requirements Document from conversation
argument-hint: [output-filename]
---
```

**转换为：**
```markdown
---
name: create-prd
description: Create a Product Requirements Document from conversation. Use when the user wants to generate a comprehensive PRD based on current discussion context and requirements.
metadata:
  short-description: Generate Product Requirements Document
---
```

**关键变化：**
- ✅ 添加 `name` 字段（必需）
- ✅ 扩展 `description` 字段，明确使用场景（Codex 只读这个来决定是否使用）
- ✅ 添加 `metadata.short-description`（可选）

### 2. 内容简化

**原则：**
- SKILL.md 只包含核心流程和概述
- 详细内容移到 `references/`
- 在 SKILL.md 中明确引用 reference 文件

**示例：**
- SKILL.md: "Use the standard PRD structure (see [PRD Structure Guide](references/prd-structure.md))"
- references/prd-structure.md: 包含完整的章节说明、示例等

### 3. 文件组织

**原结构：**
- 单个文件包含所有内容

**新结构：**
- SKILL.md: 核心指令（简洁）
- references/: 详细参考文档（按需加载）

## 其他命令文档的转换建议

### core-piv-loop

**建议结构：**
```
skill-core-piv-loop/
├── SKILL.md
└── references/
    ├── prime.md
    ├── plan-feature.md
    └── execute.md
```

**SKILL.md 应该：**
- 概述 PIV 循环概念
- 说明三个阶段的关系
- 引用各个阶段的详细文档

### github-bug-fix

**建议结构：**
```
skill-github-bug-fix/
├── SKILL.md
└── references/
    ├── rca.md (Root Cause Analysis)
    └── implement-fix.md
```

### validation

**建议结构：**
```
skill-validation/
├── SKILL.md
└── references/
    ├── code-review.md
    ├── system-review.md
    ├── execution-report.md
    └── validate.md
```

## Reference 文档的转换建议

### vue-frontend-best-practices

**建议结构：**
```
skill-vue-practices/
├── SKILL.md (概述 + 快速参考)
└── references/
    └── vue-frontend-best-practices.md (现有完整文档)
```

**SKILL.md 示例：**
```markdown
---
name: vue-practices
description: Best practices and patterns for Vue 3 frontend development with Vite, TypeScript, and Tailwind CSS. Use when working on Vue frontend code, components, routing, state management, or styling.
metadata:
  short-description: Vue 3 frontend best practices
---

# Vue Frontend Best Practices

Guidance for building Vue 3 applications with modern tooling.

## Quick Reference

- **Framework**: Vue 3 with Composition API
- **Build Tool**: Vite
- **Type Safety**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Routing**: Vue Router

## Key Patterns

- Use `<script setup>` syntax
- Prefer Composition API over Options API
- Organize by features, not file types
- Use Pinia stores for shared state
- Tailwind utilities for styling

## Detailed Reference

For comprehensive patterns, examples, anti-patterns, and advanced techniques, see [vue-frontend-best-practices.md](references/vue-frontend-best-practices.md).
```

## 总结

转换的关键步骤：

1. ✅ **添加必需的 frontmatter**（name, description）
2. ✅ **简化 SKILL.md 内容**（核心流程，< 500 行）
3. ✅ **详细内容移到 references/**（按需加载）
4. ✅ **明确引用关系**（在 SKILL.md 中说明何时查看 reference）
5. ✅ **清晰描述使用场景**（description 字段很重要）
