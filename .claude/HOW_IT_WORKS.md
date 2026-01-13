# .claude 目录使用说明

## 快速回答

**是的，你的理解基本正确！** 但有重要细节需要区分：

- ✅ **`.claude/commands/`** 下的文件 → 自动识别为命令，可通过 `/` 使用
- ✅ **`.claude/reference/`** 下的文件 → 可通过 `@` 引用
- ✅ **其他 `.claude/` 下的文件** → 可通过 `@` 引用

## 详细说明

### 1. `.claude/commands/` - 自动识别为命令

**特点：**
- ✅ **自动识别**：Claude Codex 会自动扫描 `.claude/commands/` 目录
- ✅ **作为命令使用**：文件会变成可用的斜杠命令
- ✅ **格式要求**：文件需要有 `description` frontmatter

**使用方式：**
```
/命令名
```

**示例：**
```
/create-prd          → 使用 .claude/commands/create-prd.md
/execute             → 使用 .claude/commands/core_piv_loop/execute.md
/plan-feature        → 使用 .claude/commands/core_piv_loop/plan-feature.md
/commit              → 使用 .claude/commands/commit.md
```

**文件格式要求：**
```markdown
---
description: 命令描述（必需）
argument-hint: [参数提示]（可选）
---

# 命令内容
```

### 2. `.claude/reference/` - 参考文档

**特点：**
- ✅ **不会自动识别为命令**
- ✅ **可以通过 `@` 引用**
- ✅ **适合存储最佳实践、参考文档**

**使用方式：**
```
@reference/文件名
或
@.claude/reference/文件名
```

**示例：**
```
@reference/vue-frontend-best-practices.md
@reference/fastapi-best-practices.md
@reference/sqlite-best-practices.md
```

### 3. `.claude/` 下的其他文件

**特点：**
- ✅ **不会自动识别为命令**
- ✅ **可以通过 `@` 引用**

**使用方式：**
```
@.claude/PRD.md
@.claude/COMMANDS_VS_SKILLS.md
```

## 目录结构说明

```
.claude/
├── commands/              ✅ 自动识别为命令（/命令名）
│   ├── create-prd.md     → /create-prd
│   ├── commit.md         → /commit
│   └── core_piv_loop/
│       ├── prime.md      → /prime
│       ├── plan-feature.md → /plan-feature
│       └── execute.md    → /execute
│
├── reference/            ✅ 可通过 @ 引用
│   ├── vue-frontend-best-practices.md
│   ├── fastapi-best-practices.md
│   └── ...
│
└── 其他文件.md           ✅ 可通过 @ 引用
    ├── PRD.md
    └── COMMANDS_VS_SKILLS.md
```

## 实际使用场景

### 场景 1：使用命令

**在 Claude Codex 中：**
```
用户: /create-prd
→ Claude 会读取 .claude/commands/create-prd.md 并执行
```

**嵌套命令：**
```
用户: /execute plan.md
→ Claude 会读取 .claude/commands/core_piv_loop/execute.md
  并使用 plan.md 作为参数
```

### 场景 2：引用参考文档

**在对话中引用：**
```
用户: 帮我写一个 Vue 组件，参考 @reference/vue-frontend-best-practices.md
→ Claude 会读取该文件的内容作为参考
```

**同时引用多个文档：**
```
用户: 参考 @reference/vue-frontend-best-practices.md 和 
      @reference/fastapi-best-practices.md 来设计 API
→ Claude 会读取这两个文件
```

### 场景 3：引用项目文档

```
用户: 看看我们的 PRD：@.claude/PRD.md
→ Claude 会读取 PRD.md 文件
```

## 注意事项

### ✅ 命令文件（`.claude/commands/`）

1. **必须有 frontmatter**
   ```markdown
   ---
   description: 命令描述
   ---
   ```

2. **文件名决定命令名**
   - `create-prd.md` → `/create-prd`
   - `commit.md` → `/commit`
   - `core_piv_loop/execute.md` → `/execute`（子目录中的文件名）

3. **自动识别，无需手动注册**
   - Claude Codex 会自动扫描并注册命令

### ✅ 参考文档（`.claude/reference/` 和其他文件）

1. **通过 `@` 显式引用**
   - 不会自动加载
   - 需要在使用时明确引用

2. **可以使用相对路径或绝对路径**
   - `@reference/file.md`
   - `@.claude/reference/file.md`

## 对比表格

| 文件位置 | 自动识别 | 使用方式 | 示例 |
|---------|---------|---------|------|
| `.claude/commands/*.md` | ✅ 是 | `/命令名` | `/create-prd` |
| `.claude/reference/*.md` | ❌ 否 | `@reference/文件名` | `@reference/vue-frontend-best-practices.md` |
| `.claude/*.md` (其他) | ❌ 否 | `@.claude/文件名` | `@.claude/PRD.md` |

## 总结

### ✅ 你的理解

> "当我把 .claude 文件夹放到具体的项目，则这个项目可以调用里面的所有 md 格式的文件"

**基本正确，但需要区分：**

1. **`.claude/commands/` 下的文件**
   - ✅ **自动识别为命令**
   - ✅ 可以通过 `/` 直接使用
   - ✅ 不需要手动引用

2. **其他 md 文件（`reference/` 和根目录）**
   - ✅ **可以通过 `@` 引用**
   - ❌ 不会自动识别为命令
   - ✅ 需要在使用时明确引用

### 最佳实践

1. **命令文件** → 放在 `.claude/commands/`
   - 工作流程、自动化任务
   - 需要作为命令使用的文件

2. **参考文档** → 放在 `.claude/reference/`
   - 最佳实践、参考指南
   - 需要时通过 `@` 引用

3. **项目文档** → 放在 `.claude/` 根目录
   - PRD、设计文档等
   - 需要时通过 `@` 引用

## 示例：完整使用流程

### 1. 设置项目

```bash
项目根目录/
└── .claude/
    ├── commands/
    │   ├── create-prd.md
    │   └── commit.md
    └── reference/
        └── vue-frontend-best-practices.md
```

### 2. 使用命令

```
用户: /create-prd
→ Claude 自动执行 .claude/commands/create-prd.md
```

### 3. 引用参考文档

```
用户: 根据 @reference/vue-frontend-best-practices.md 来写组件
→ Claude 读取该文件作为参考
```

### 4. 组合使用

```
用户: /create-prd 然后参考 @reference/vue-frontend-best-practices.md 
     来设计前端架构
→ Claude 先执行命令，然后引用文档
```

## 结论

**是的，将 `.claude` 文件夹放到项目中后：**

1. ✅ **`.claude/commands/` 下的文件会自动识别为命令**，可通过 `/` 使用
2. ✅ **其他 md 文件可以通过 `@` 引用**
3. ✅ **所有文件都会在项目中可用**
4. ✅ **不需要额外配置**

**区别在于使用方式：**
- 命令文件：自动识别，使用 `/命令名`
- 参考文档：需要显式引用，使用 `@路径`
