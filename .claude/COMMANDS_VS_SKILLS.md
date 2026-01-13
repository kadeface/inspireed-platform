# Commands vs Skills：是否需要转换？

## 快速回答

**对于 `.claude/commands/` 目录下的文件：**

✅ **可以直接使用，不需要转换！**

你的 `.claude/commands/` 文件已经是一个功能性的命令系统，可以在项目中直接通过 `/` 命令使用。

## Commands 和 Skills 的区别

### `.claude/commands/` (项目特定命令)

**特点：**
- ✅ **项目特定**：只在本项目中可用
- ✅ **直接可用**：Claude Codex 会读取 `.claude/commands/` 下的文件
- ✅ **格式简单**：只需要 `description` 和 `argument-hint`
- ✅ **轻量级**：适合项目特定的工作流程

**你的文件格式：**
```markdown
---
description: Create a Product Requirements Document from conversation
argument-hint: [output-filename]
---

# 命令内容
```

**使用方式：**
- 在 Claude Codex 中直接使用 `/create-prd` 命令
- 系统会自动读取 `.claude/commands/create-prd.md`

### Skills (全局可重用技能)

**特点：**
- ✅ **全局可用**：安装在 `~/.codex/skills/` 后，所有项目可用
- ✅ **更结构化**：需要 `name` 和详细的 `description`
- ✅ **可分享**：可以分享给其他用户或团队
- ✅ **更复杂**：适合需要跨项目重用的复杂工作流程

**Skills 格式：**
```markdown
---
name: create-prd
description: Create a Product Requirements Document from conversation. Use when...
metadata:
  short-description: Generate PRD
---

# Skill 内容
```

## 是否需要转换？

### ❌ **不需要转换的情况**

如果你的文档：
- ✅ 只在这个项目中使用
- ✅ 已经作为 `.claude/commands/` 正常工作
- ✅ 是项目特定的工作流程
- ✅ 不打算在其他项目中重用

**建议：保持现状，直接使用 `/` 命令**

### ✅ **考虑转换为 Skills 的情况**

如果你的文档：
- ✅ 想要在多个项目中重用
- ✅ 想要分享给团队其他成员
- ✅ 是通用的最佳实践（如 Vue 最佳实践）
- ✅ 希望作为可安装的技能包分发

**建议：转换为 Skills，安装到 `~/.codex/skills/`**

## 实际建议

### 对于你的 `.claude/commands/` 文件

**保持原样，直接使用！**

你的命令文件已经：
- ✅ 格式正确（有 `description`）
- ✅ 结构清晰
- ✅ 可以在项目中直接使用

例如：
- `/create-prd` → 使用 `.claude/commands/create-prd.md`
- `/execute` → 使用 `.claude/commands/core_piv_loop/execute.md`
- `/plan-feature` → 使用 `.claude/commands/core_piv_loop/plan-feature.md`

### 对于你的 `.claude/reference/` 文件

**两种选择：**

**选项 1：保持作为项目参考文档**
- 直接在对话中引用：`@reference/vue-frontend-best-practices.md`
- 简单直接，适合项目特定文档

**选项 2：转换为 Skills（如果希望跨项目重用）**
- 如果是通用的最佳实践（如 Vue、FastAPI 最佳实践）
- 想要在其他项目中复用
- 建议转换为 Skills

## 最佳实践建议

### 项目特定 → 使用 Commands

```
.claude/commands/
├── create-prd.md          # 项目特定的 PRD 模板
├── core_piv_loop/         # 项目特定的工作流程
└── validation/            # 项目特定的验证流程
```

**优点：**
- 简单直接
- 项目特定配置
- 不需要安装

### 通用知识 → 考虑 Skills

```
~/.codex/skills/
├── skill-vue-practices/   # Vue 最佳实践（多个项目可用）
├── skill-fastapi-practices/  # FastAPI 最佳实践
└── skill-testing/         # 通用测试最佳实践
```

**优点：**
- 跨项目重用
- 可以分享
- 统一管理

## 总结

| 文档类型 | 当前位置 | 建议 |
|---------|---------|------|
| `.claude/commands/` | 项目特定命令 | ✅ **保持现状，直接使用 `/` 命令** |
| `.claude/reference/` | 项目参考文档 | ✅ **保持现状，通过 `@` 引用** |
| 通用最佳实践 | - | ✅ **考虑转换为 Skills** |
| 跨项目工作流 | - | ✅ **考虑转换为 Skills** |

## 行动建议

1. **继续使用现有命令**：你的 `.claude/commands/` 已经可以正常工作，直接使用即可

2. **保持 reference 文档**：`.claude/reference/` 作为项目文档，需要时引用即可

3. **可选：提取通用知识为 Skills**：
   - 如果某些最佳实践想在其他项目中使用
   - 可以单独转换那些通用的文档
   - 项目特定的命令和流程保持原样

**结论：不需要大规模转换，现有的 `.claude/commands/` 系统已经足够好用！**
