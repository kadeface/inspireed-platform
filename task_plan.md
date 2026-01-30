# 任务计划：建立 Dev 到 Production-Deploy 选择性部署工作流程

## 问题描述

需要建立清晰的工作流程，确保：
- **dev 分支**：开发环境，可以自由开发
- **production-deploy 分支**：生产环境，只包含经过验证的稳定代码
- **需求**：从 dev 选择性推送修改到 production-deploy，而不是全部合并
- **避免**：合并冲突和意外引入未测试的代码

## 目标

1. ✅ 建立清晰的分支管理策略
2. ✅ 创建选择性部署工具和脚本
3. ✅ 编写详细的工作流程文档
4. ⏳ 验证工作流程的有效性

## 实施步骤

### 阶段 1：分析和规划 ✅

- [x] 分析当前分支状态
- [x] 识别问题和需求
- [x] 设计解决方案

**完成时间**: 2026-01-30

### 阶段 2：创建部署工具 ✅

- [x] 创建 `deployment_workflow_plan.md` 详细计划文档
- [x] 创建 `scripts/deploy-to-production.sh` Cherry-pick 部署脚本
- [x] 创建 `scripts/sync-files-to-production.sh` 文件同步脚本
- [x] 创建 `DEPLOYMENT_GUIDE.md` 快速参考指南
- [x] 设置脚本执行权限

**完成时间**: 2026-01-30

### 阶段 3：文档和培训 ⏳

- [ ] 团队培训新工作流程
- [ ] 建立部署清单模板
- [ ] 建立代码审查流程（可选）

### 阶段 4：验证和优化 ⏳

- [ ] 在实际项目中验证工作流程
- [ ] 收集反馈并优化
- [ ] 建立 CI/CD 自动化（长期目标）

## 解决方案总结

### 推荐方法：Cherry-pick 选择性提交

**优点**：
- 精确控制每个提交
- 不引入 dev 分支的其他历史
- 保持 production-deploy 历史清晰
- 可以按需选择多个提交

**基本流程**：
```bash
# 1. 在 dev 分支开发并提交
git checkout dev
git commit -m "feat: 新功能"
git push origin dev

# 2. 切换到 production-deploy
git checkout production-deploy
git pull origin production-deploy

# 3. Cherry-pick 需要的提交
git cherry-pick <commit-hash>

# 4. 推送到远程
git push origin production-deploy
```

### 备选方法：选择性文件合并

**适用场景**：只需要同步特定文件，不需要整个提交

**基本流程**：
```bash
git checkout production-deploy
git checkout dev -- path/to/file1 path/to/file2
git add .
git commit -m "fix: 同步文件到生产环境"
git push origin production-deploy
```

## 已创建的文件

1. **deployment_workflow_plan.md** - 详细的工作流程计划
2. **DEPLOYMENT_GUIDE.md** - 快速参考指南
3. **scripts/deploy-to-production.sh** - Cherry-pick 部署脚本
4. **scripts/sync-files-to-production.sh** - 文件同步脚本

## 下一步行动

1. ⏳ 在实际项目中测试新的工作流程
2. ⏳ 根据使用情况优化脚本和文档
3. ⏳ 考虑建立 CI/CD 自动化流程

## 注意事项

### ✅ 推荐操作
- 使用 cherry-pick 选择性部署
- 每次部署前在 dev 分支充分测试
- 保持提交信息清晰
- 记录每次部署的内容

### ❌ 避免操作
- 不要直接合并 dev 到 production-deploy
- 不要在 production-deploy 直接开发
- 不要强制推送 production-deploy（除非必要）

## 当前状态

- ✅ 工作流程文档已创建
- ✅ 部署脚本已创建
- ✅ 快速参考指南已创建
- ⏳ 等待实际使用验证
