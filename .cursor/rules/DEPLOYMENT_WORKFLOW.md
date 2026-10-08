# 部署工作流程规则

## 分支管理策略

### 分支定义

- **`dev` 分支**：开发环境分支
  - 用于日常开发和实验性功能
  - 可以自由提交和推送
  - 包含所有开发中的代码，可能不稳定

- **`production-deploy` 分支**：生产环境分支
  - 只包含经过测试、稳定的代码
  - 必须通过选择性部署从 dev 分支获取代码
  - 禁止直接在此分支开发

### 核心原则

1. **禁止直接合并**：❌ 不要使用 `git merge dev` 将整个 dev 分支合并到 production-deploy
2. **选择性部署**：✅ 使用 cherry-pick 或文件同步的方式选择性部署
3. **测试优先**：✅ 所有代码必须在 dev 分支充分测试后才能部署
4. **记录部署**：✅ 每次部署都要记录部署内容和原因

## 部署方法

### 方法 1：Cherry-pick 提交（推荐）

**适用场景**：部署完整的提交（包含多个文件的修改）

```bash
# 1. 在 dev 分支开发并提交
git checkout dev
git add .
git commit -m "fix: 修复XXX问题"
git push origin dev

# 2. 记录提交哈希
COMMIT_HASH=<commit-hash>

# 3. 切换到 production-deploy
git checkout production-deploy
git pull origin production-deploy

# 4. Cherry-pick 提交
git cherry-pick $COMMIT_HASH

# 5. 解决冲突（如果有）
# 编辑冲突文件，然后：
git add <resolved-file>
git cherry-pick --continue

# 6. 推送到远程
git push origin production-deploy
```

**使用脚本**：
```bash
./scripts/deploy-to-production.sh <commit-hash>
```

### 方法 2：选择性文件同步

**适用场景**：只需要同步特定文件，不需要整个提交

```bash
# 1. 切换到 production-deploy
git checkout production-deploy
git pull origin production-deploy

# 2. 从 dev 分支检出特定文件
git checkout dev -- path/to/file1 path/to/file2

# 3. 提交更改
git add path/to/file1 path/to/file2
git commit -m "fix: 同步文件到生产环境"

# 4. 推送到远程
git push origin production-deploy
```

**使用脚本**：
```bash
./scripts/sync-files-to-production.sh path/to/file1 path/to/file2
```

## 提交信息规范

### 在 dev 分支

使用清晰的提交信息，便于识别需要部署的提交：

```bash
# ✅ 好的提交信息
git commit -m "fix: 修复学生端内容显示问题 [DEPLOY]"
git commit -m "feat: 优化班级匹配机制 [DEPLOY]"

# ❌ 避免模糊的提交信息
git commit -m "更新"
git commit -m "修复bug"
```

### 在 production-deploy 分支

部署提交应该清晰说明来源：

```bash
# Cherry-pick 方式
git commit -m "fix: 从 dev 同步修复 (cherry-pick: 614eb33)"

# 文件同步方式
git commit -m "fix: 同步关键文件到生产环境
- backend/app/api/v1/classroom_sessions.py
- frontend/src/pages/Student/LessonView.vue"
```

## 部署前检查清单

在部署到 production-deploy 之前，必须完成：

- [ ] 代码已在 dev 分支测试通过
- [ ] 没有已知的 bug
- [ ] 已检查依赖关系
- [ ] 已检查数据库迁移（如果有）
- [ ] 已检查配置文件兼容性
- [ ] 已记录部署内容

## 冲突处理

### Cherry-pick 冲突

```bash
# 1. 查看冲突
git status

# 2. 解决冲突
# 编辑冲突文件，选择正确的代码
# 优先保留 production-deploy 的配置，应用 dev 的功能修改

# 3. 标记已解决
git add <resolved-file>

# 4. 继续 cherry-pick
git cherry-pick --continue

# 或放弃
git cherry-pick --abort
```

### 文件同步冲突

如果文件在 production-deploy 有不同版本：

```bash
# 1. 查看差异
git diff dev production-deploy -- <file>

# 2. 手动合并或选择版本
# 选择 dev 版本（功能更新）
git checkout dev -- <file>

# 或手动编辑合并
```

## 禁止的操作

以下操作**严格禁止**：

1. ❌ **不要直接合并 dev 到 production-deploy**
   ```bash
   # 错误示例
   git checkout production-deploy
   git merge dev  # ❌ 禁止
   ```

2. ❌ **不要在 production-deploy 直接开发**
   ```bash
   # 错误示例
   git checkout production-deploy
   # ... 直接修改代码 ...  # ❌ 禁止
   ```

3. ❌ **不要强制推送 production-deploy（除非必要）**
   ```bash
   # 只有在修复错误提交时才使用
   git push origin production-deploy --force  # ⚠️ 谨慎使用
   ```

## 推荐的操作

以下操作**强烈推荐**：

1. ✅ **使用 cherry-pick 选择性部署**
   ```bash
   git cherry-pick <commit-hash>
   ```

2. ✅ **每次部署前在 dev 分支充分测试**
   ```bash
   # 在 dev 分支测试
   git checkout dev
   # ... 测试功能 ...
   ```

3. ✅ **保持提交信息清晰**
   ```bash
   git commit -m "fix: 清晰描述修复内容 [DEPLOY]"
   ```

4. ✅ **记录每次部署的内容**
   ```markdown
   ## 部署记录 - 2026-01-30
   - 提交: 614eb33
   - 内容: 优化班级匹配机制并修复学生端内容显示问题
   - 文件: 11 个文件
   ```

## 紧急修复流程

如果生产环境需要紧急修复：

```bash
# 1. 在 dev 分支创建修复
git checkout dev
# ... 快速修复 ...
git commit -m "hotfix: 紧急修复XXX问题"
git push origin dev

# 2. 立即部署到 production-deploy
git checkout production-deploy
git cherry-pick <hotfix-commit-hash>
git push origin production-deploy

# 3. 后续在 dev 分支完善修复
git checkout dev
# ... 完善修复 ...
```

## 自动化工具

项目提供了以下自动化脚本：

1. **`scripts/deploy-to-production.sh`**
   - Cherry-pick 部署脚本
   - 支持单个或多个提交
   - 自动处理冲突提示

2. **`scripts/sync-files-to-production.sh`**
   - 文件同步脚本
   - 支持同步特定文件
   - 自动检查文件存在性

## 相关文档

- `deployment_workflow_plan.md` - 详细的工作流程计划
- `DEPLOYMENT_GUIDE.md` - 快速参考指南

## 违反规则的后果

违反上述规则可能导致：
- 生产环境不稳定
- 引入未测试的代码
- 合并冲突难以解决
- 部署历史混乱

**请严格遵守以上规则！**
