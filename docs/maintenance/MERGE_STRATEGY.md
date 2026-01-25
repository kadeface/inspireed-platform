# feature/cloudstudio-deploy → dev 合并策略

## 📊 差异分析

### 全局特性（✅ 应该合并到 dev）

#### 1. **业务功能修复**（必须合并）
- ✅ **教研员端课程导入和学科选择修复** (`952c986`)
  - 文件：`backend/app/api/v1/curriculum.py`, `backend/app/api/v1/researcher_curriculum.py`, `frontend/src/pages/Researcher/CourseFormModal.vue`
  - 原因：这是业务功能修复，与 CloudStudio 无关
  - 操作：直接合并

- ✅ **共享教案功能修复** (`6f1f738`, `4d2ffae`, `d63cf06`)
  - 文件：`frontend/src/pages/Teacher/Dashboard.vue`
  - 原因：修复共享教案的过滤、显示和状态筛选问题
  - 操作：直接合并

#### 2. **HTTPS 混合内容修复**（应该合并，但需要评估）
- ✅ **HTTPS 协议强制转换** (`c248da4`)
  - 文件：
    - `frontend/src/components/Cell/InteractiveCell.vue`
    - `frontend/src/components/Cell/ReferenceMaterialCell.vue`
    - `frontend/src/components/Library/AssetDetailModal.vue`
    - `frontend/src/components/Resource/PDFViewerModal.vue`
    - `frontend/src/pages/Teacher/ResourceLibrary.vue`
  - 原因：虽然由 CloudStudio 触发，但这是通用的 HTTPS 混合内容问题修复，适用于所有 HTTPS 环境
  - 操作：**直接合并**（这是通用修复）

#### 3. **数据库连接配置优化**（应该合并）
- ✅ **Docker 网络服务名支持** (`c248da4`)
  - 文件：`backend/app/core/config.py`
  - 变更：添加 `env_prefix=""` 配置，确保环境变量优先级正确
  - 原因：这是通用的配置改进，不仅适用于 CloudStudio，也适用于所有 Docker 环境
  - 操作：**直接合并**

### CloudStudio 特定特性（⚠️ 需要条件化或保留在分支）

#### 1. **CloudStudio 预览配置**（保留在分支）
- ⚠️ `.vscode/preview.yml`
  - 原因：这是 CloudStudio 特定的预览配置
  - 操作：**不合并到 dev**，保留在 `feature/cloudstudio-deploy` 分支

#### 2. **CloudStudio URL 检测逻辑**（已存在，无需额外处理）
- ℹ️ `frontend/src/services/api.ts` 和 `frontend/src/utils/url.ts`
  - 原因：这些文件中的 CloudStudio 检测逻辑已经存在，并且是条件性的（只在检测到 CloudStudio 域名时生效）
  - 操作：**无需额外处理**，代码已经兼容

## 🎯 推荐合并策略

### 方案一：选择性合并（推荐）⭐

**步骤：**

1. **创建临时分支进行合并**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b merge-cloudstudio-to-dev
   ```

2. **合并全局特性提交**
   ```bash
   # 合并业务功能修复
   git cherry-pick 952c986  # 教研员端课程修复
   git cherry-pick 6f1f738  # 共享教案过滤修复
   git cherry-pick 4d2ffae  # 共享教案显示修复
   git cherry-pick d63cf06  # 共享教案状态筛选修复
   
   # 合并 HTTPS 混合内容修复（整个提交）
   git cherry-pick c248da4  # HTTPS 修复和数据库配置
   ```

3. **排除 CloudStudio 特定文件**
   ```bash
   # 如果 preview.yml 被包含，需要恢复
   git checkout origin/dev -- .vscode/preview.yml
   ```

4. **测试验证**
   - 确保所有功能正常
   - 确保 HTTPS 环境正常工作
   - 确保 Docker 环境正常工作

5. **合并到 dev**
   ```bash
   git checkout dev
   git merge merge-cloudstudio-to-dev
   git push origin dev
   ```

### 方案二：完整合并 + 条件化处理

**适用场景**：如果希望 dev 分支也支持 CloudStudio 环境

**步骤：**

1. **直接合并整个分支**
   ```bash
   git checkout dev
   git merge feature/cloudstudio-deploy --no-ff
   ```

2. **保留所有更改**
   - `.vscode/preview.yml` 保留（不影响非 CloudStudio 环境）
   - 所有 HTTPS 修复保留（通用修复）
   - 所有业务功能修复保留

3. **验证**
   - 确保本地开发环境不受影响
   - 确保 CloudStudio 环境正常工作

## 📋 合并清单

### 必须合并的提交

- [x] `952c986` - 教研员端课程导入修复
- [x] `6f1f738` - 共享教案过滤修复
- [x] `4d2ffae` - 共享教案显示修复
- [x] `d63cf06` - 共享教案状态筛选修复
- [x] `c248da4` - HTTPS 混合内容修复 + 数据库配置优化

### 可选合并的提交

- [ ] `b27719b` - CloudStudio 自动预览功能（`.vscode/preview.yml`）
  - 建议：**不合并**，保留在 CloudStudio 分支

## 🔍 文件分类

### 全局文件（合并）
- `backend/app/api/v1/curriculum.py`
- `backend/app/api/v1/researcher_curriculum.py`
- `backend/app/core/config.py`
- `backend/app/schemas/curriculum.py`
- `frontend/src/components/Cell/InteractiveCell.vue`
- `frontend/src/components/Cell/ReferenceMaterialCell.vue`
- `frontend/src/components/Library/AssetDetailModal.vue`
- `frontend/src/components/Resource/PDFViewerModal.vue`
- `frontend/src/pages/Researcher/CourseFormModal.vue`
- `frontend/src/pages/Teacher/Dashboard.vue`
- `frontend/src/pages/Teacher/ResourceLibrary.vue`
- `frontend/src/types/curriculum.ts`

### CloudStudio 特定文件（不合并或条件化）
- `.vscode/preview.yml` - CloudStudio 预览配置

## ⚠️ 注意事项

1. **HTTPS 修复是通用的**：虽然由 CloudStudio 触发，但修复适用于所有 HTTPS 环境，应该合并

2. **数据库配置改进是通用的**：`env_prefix=""` 配置改进适用于所有 Docker 环境

3. **CloudStudio URL 检测已存在**：`api.ts` 和 `url.ts` 中的 CloudStudio 检测逻辑已经是条件性的，不会影响其他环境

4. **测试重点**：
   - 本地开发环境（HTTP）
   - HTTPS 生产环境
   - Docker 容器环境
   - CloudStudio 环境（如果合并了 preview.yml）

## 🚀 执行建议

**推荐使用方案一（选择性合并）**，因为：
- ✅ 更清晰：只合并通用特性
- ✅ 更安全：避免引入 CloudStudio 特定配置
- ✅ 更易维护：dev 分支保持通用性

**如果选择方案二（完整合并）**，需要：
- ✅ 确保 `.vscode/preview.yml` 不影响非 CloudStudio 环境
- ✅ 充分测试所有环境

