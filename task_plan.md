# 任务计划：检查 dev 和 production-deploy 分支教案内容显示差异

## 目标
找出为什么本地 dev 分支教案有具体内容，而 remotes/origin/production-deploy 分支无法显示具体内容。

## 阶段

### Phase 1: 代码差异分析 [complete]
- [x] 查看两个分支的总体差异统计
- [x] 比较关键文件差异：
  - frontend/src/store/lesson.ts ✅
  - frontend/src/services/lesson.ts ✅ (无差异)
  - frontend/src/services/api.ts ✅ **关键差异**
  - frontend/src/utils/lessonContent.ts ✅ (无差异)
  - backend/app/api/v1/lessons.py ✅ (无差异)
  - backend/app/schemas/lesson.py ✅ (无差异)

### Phase 2: 数据格式检查 [complete]
- [x] 检查后端返回的数据格式 ✅ 后端支持两种格式
- [x] 检查前端处理 content 的逻辑差异 ✅ 前端支持两种格式
- [x] 检查 sections 格式转换逻辑 ✅ 转换逻辑正常

### Phase 3: API 调用检查 [complete]
- [x] 检查 API 基础路径配置 ✅ **发现关键差异**
- [x] 检查请求/响应拦截器 ✅ 无差异
- [x] 检查错误处理逻辑 ✅ 无差异

### Phase 4: 问题定位与修复 [complete]
- [x] 确定根本原因 ✅ **已定位**
- [x] 提出修复方案 ✅ **已提出**
- [x] 实施修复 ✅ **已应用修复**
- [ ] 验证修复效果 ⏳ **待验证**

## 错误记录
| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| - | - | - |

## 当前状态
✅ Phase 1-3 已完成，已定位根本原因
🔧 Phase 4：提出修复方案

## 根本原因总结

**问题根源**：`frontend/src/services/api.ts` 中 API 地址检测逻辑的优先级差异

- **dev 分支**：优先动态检测环境，然后才检查环境变量（更灵活，适合开发环境）
- **production-deploy 分支**：优先使用环境变量，如果没有环境变量才动态检测（适合生产环境，但需要正确配置）

**可能的问题场景**：
1. 生产环境构建时，`VITE_API_BASE_URL` 环境变量为空或未设置
2. 导致前端使用了错误的 API 地址（可能是默认的 `http://localhost:8000/api/v1`）
3. 无法正确连接到后端，或连接到了错误的后端实例
4. 教案内容无法正确加载或显示
