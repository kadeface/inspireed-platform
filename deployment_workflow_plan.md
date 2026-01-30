# Dev 到 Production-Deploy 选择性部署工作流程

## 问题描述

- **dev 分支**：开发环境，包含所有开发中的功能和实验性代码
- **production-deploy 分支**：生产环境，只应包含经过测试、稳定的代码
- **需求**：从 dev 选择性推送修改到 production-deploy，而不是全部合并

## 目标

建立清晰的工作流程，确保：
1. dev 分支可以自由开发，不受限制
2. production-deploy 只包含经过验证的、稳定的修改
3. 可以精确控制哪些修改进入生产环境
4. 避免合并冲突和意外引入未测试的代码

## 解决方案

### 方案 1：Cherry-pick 选择性提交（推荐）

**优点**：
- 精确控制每个提交
- 不引入 dev 分支的其他历史
- 保持 production-deploy 历史清晰
- 可以按需选择多个提交

**工作流程**：

```bash
# 1. 在 dev 分支开发并提交
git checkout dev
# ... 开发工作 ...
git add .
git commit -m "feat: 新功能"

# 2. 切换到 production-deploy
git checkout production-deploy
git pull origin production-deploy

# 3. Cherry-pick 需要的提交（使用提交哈希）
git cherry-pick <commit-hash>

# 4. 解决可能的冲突（如果有）
# ... 解决冲突 ...
git add .
git cherry-pick --continue

# 5. 推送到远程
git push origin production-deploy
```

### 方案 2：选择性文件合并

**优点**：
- 可以只选择特定文件
- 适合大范围修改但只需要部分文件的情况

**工作流程**：

```bash
# 1. 切换到 production-deploy
git checkout production-deploy
git pull origin production-deploy

# 2. 从 dev 分支检出特定文件
git checkout dev -- path/to/file1 path/to/file2

# 3. 提交更改
git add path/to/file1 path/to/file2
git commit -m "fix: 从 dev 同步特定文件的修复"

# 4. 推送到远程
git push origin production-deploy
```

### 方案 3：创建部署脚本自动化

**优点**：
- 自动化流程，减少人为错误
- 可以添加验证步骤
- 可以记录部署历史

## 推荐工作流程（详细）

### 日常开发流程

1. **在 dev 分支开发**
   ```bash
   git checkout dev
   git pull origin dev
   # ... 开发工作 ...
   git add .
   git commit -m "feat: 描述你的修改"
   git push origin dev
   ```

2. **测试和验证**
   - 在开发环境测试新功能
   - 确保功能稳定、无 bug
   - 记录需要部署的提交哈希

3. **部署到生产环境**

   **方法 A：Cherry-pick 单个提交**
   ```bash
   git checkout production-deploy
   git pull origin production-deploy
   git cherry-pick <commit-hash>
   # 解决冲突（如果有）
   git push origin production-deploy
   ```

   **方法 B：Cherry-pick 多个提交**
   ```bash
   git checkout production-deploy
   git pull origin production-deploy
   git cherry-pick <commit-hash-1> <commit-hash-2> <commit-hash-3>
   # 解决冲突（如果有）
   git push origin production-deploy
   ```

   **方法 C：选择性文件**
   ```bash
   git checkout production-deploy
   git pull origin production-deploy
   git checkout dev -- path/to/file1 path/to/file2
   git add .
   git commit -m "fix: 同步特定修复到生产环境"
   git push origin production-deploy
   ```

### 冲突处理

如果 cherry-pick 或文件合并时出现冲突：

```bash
# 1. 查看冲突文件
git status

# 2. 手动解决冲突
# 编辑冲突文件，选择正确的代码

# 3. 标记冲突已解决
git add <resolved-file>

# 4. 继续 cherry-pick
git cherry-pick --continue

# 或者放弃 cherry-pick
git cherry-pick --abort
```

## 最佳实践

### 1. 提交信息规范

在 dev 分支使用清晰的提交信息，便于识别需要部署的提交：

```bash
# 好的提交信息
git commit -m "fix: 修复学生端内容显示问题 [DEPLOY]"
git commit -m "feat: 优化班级匹配机制 [DEPLOY]"

# 实验性功能不标记
git commit -m "experiment: 尝试新的UI设计"
```

### 2. 使用标签标记可部署的提交

```bash
# 在 dev 分支标记可部署的提交
git tag deploy/v1.0.1 <commit-hash>
git push origin deploy/v1.0.1

# 在 production-deploy 分支 cherry-pick 标签
git checkout production-deploy
git cherry-pick deploy/v1.0.1
```

### 3. 创建部署清单

维护一个部署清单文件，记录每次部署的内容：

```markdown
# 部署清单

## 2026-01-30
- 提交: 614eb33
- 内容: 优化班级匹配机制并修复学生端内容显示问题
- 文件: 11 个文件
- 状态: ✅ 已部署
```

### 4. 部署前检查清单

在部署到 production-deploy 之前：

- [ ] 代码已在 dev 分支测试通过
- [ ] 没有已知的 bug
- [ ] 已检查依赖关系
- [ ] 已检查数据库迁移（如果有）
- [ ] 已检查配置文件兼容性
- [ ] 已记录部署内容

## 自动化脚本

### 创建部署脚本

创建 `scripts/deploy-to-production.sh`：

```bash
#!/bin/bash
# 部署脚本：从 dev 选择性部署到 production-deploy

set -e

COMMIT_HASH=$1

if [ -z "$COMMIT_HASH" ]; then
    echo "用法: ./scripts/deploy-to-production.sh <commit-hash>"
    exit 1
fi

echo "🔄 切换到 production-deploy 分支..."
git checkout production-deploy
git pull origin production-deploy

echo "🍒 Cherry-pick 提交 $COMMIT_HASH..."
git cherry-pick $COMMIT_HASH

echo "✅ Cherry-pick 成功！"
echo "📝 请检查更改，然后运行: git push origin production-deploy"
```

### 创建文件同步脚本

创建 `scripts/sync-files-to-production.sh`：

```bash
#!/bin/bash
# 文件同步脚本：从 dev 同步特定文件到 production-deploy

set -e

FILES="$@"

if [ -z "$FILES" ]; then
    echo "用法: ./scripts/sync-files-to-production.sh <file1> <file2> ..."
    exit 1
fi

echo "🔄 切换到 production-deploy 分支..."
git checkout production-deploy
git pull origin production-deploy

echo "📁 从 dev 分支检出文件..."
git checkout dev -- $FILES

echo "✅ 文件已同步！"
echo "📝 请检查更改，然后运行:"
echo "   git add $FILES"
echo "   git commit -m 'fix: 同步文件到生产环境'"
echo "   git push origin production-deploy"
```

## 注意事项

### 1. 避免的操作

- ❌ 不要直接合并 dev 到 production-deploy
- ❌ 不要在 production-deploy 直接开发
- ❌ 不要强制推送 production-deploy（除非必要）

### 2. 推荐的操作

- ✅ 使用 cherry-pick 选择性部署
- ✅ 每次部署前在 dev 分支充分测试
- ✅ 保持提交信息清晰
- ✅ 记录每次部署的内容

### 3. 紧急修复

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
```

## 实施步骤

1. **立即执行**：
   - [x] 已建立当前工作流程（cherry-pick 方式）
   - [ ] 创建部署脚本
   - [ ] 建立部署清单文档

2. **短期优化**：
   - [ ] 在 dev 分支使用 [DEPLOY] 标签标记可部署提交
   - [ ] 建立部署前检查清单
   - [ ] 培训团队成员使用新流程

3. **长期改进**：
   - [ ] 考虑使用 CI/CD 自动化部署
   - [ ] 建立代码审查流程
   - [ ] 建立回滚机制

## 总结

通过使用 **cherry-pick** 或 **选择性文件合并** 的方式，可以精确控制从 dev 到 production-deploy 的代码流动，避免不必要的合并冲突，保持生产环境的稳定性。
