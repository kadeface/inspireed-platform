# 新项目命名脚手架

> **个人开新项目请用：** `~/.cursor/naming-scaffold/`（不依赖本仓库）  
> 本目录是仓库内同源副本，便于团队在 InspireEd 内查阅。

把本目录（或 `~/.cursor/naming-scaffold/`）复制到新仓库后，按下面步骤启用。目标：开写第一行业务代码之前，命名约定已可执行、可检查。

## 复制清单

```text
docs/templates/naming-scaffold/
├── README.md                          ← 本说明
├── NAMING_CONVENTIONS.md              → 复制为 docs/NAMING_CONVENTIONS.md
├── DECISION_DEFAULTS.md               → 复制为 docs/DECISION_DEFAULTS.md（决策表）
├── eslint.naming.snippet.cjs          → 合并进前端 ESLint 配置
├── scripts/check_naming.py            → 复制到 scripts/ 或 backend/scripts/
├── pull_request_checklist.md          → 合并进 .github/PULL_REQUEST_TEMPLATE.md
└── cursor-rules/naming-conventions.mdc → 复制到 .cursor/rules/
```

## Day 0 启用步骤

1. 复制 `NAMING_CONVENTIONS.md`、`DECISION_DEFAULTS.md` 到新项目 `docs/`。
2. 复制 Cursor 规则到 `.cursor/rules/naming-conventions.mdc`（`alwaysApply: true`）。
3. 前端：把 `eslint.naming.snippet.cjs` 中的 `overrides` 合并进 `.eslintrc.*`；安装（若尚未有）：
   ```bash
   pnpm add -D @typescript-eslint/eslint-plugin
   ```
4. 后端：把 `scripts/check_naming.py` 放进仓库，在 CI / pre-commit 中调用：
   ```bash
   python scripts/check_naming.py backend/app
   ```
5. 把 `pull_request_checklist.md` 里的「命名」小节并入 PR 模板。
6. 根 `README.md`「开发规范」增加一行指向 `docs/NAMING_CONVENTIONS.md`。
7. **用第一个业务模块当样板**（用户/会话即可），严格按规范写；后续模块照抄它，不要照抄旧项目的混用代码。

## 验收

- [ ] 新建一个带 camelCase 字段的 `types/*.ts` 接口，ESLint 报错
- [ ] 模型里写 `Index("foo_bar", ...)`（无 `ix_`/`idx_` 前缀），`check_naming.py` 失败
- [ ] Schema 里写 `serialization_alias="studentName"`，`check_naming.py` 失败
- [ ] PR 模板含命名勾选

## 与本仓库的关系

InspireEd 现行规范见 [`docs/NAMING_CONVENTIONS.md`](../NAMING_CONVENTIONS.md)（含存量债务说明）。  
本脚手架是**新项目精简版**：只有正向规则 + 检查手段，不含迁移债务章节。
