# 发现记录

## 初步发现

### 1. 分支差异统计
- 65 个文件有差异
- 主要差异文件：
  - frontend/src/services/api.ts (67 行变化) ⚠️ **关键差异**
  - frontend/src/store/lesson.ts (9 行变化)
  - docker/docker-compose.prod.yml (39 行变化)
  - backend/app/api/v1/semesters.py (42 行变化)

### 2. 教案内容处理逻辑
- 前端支持两种格式：
  - 旧格式：`Cell[]` 平铺数组
  - 新格式：`{ sections: [...] }` 分节格式
- 转换函数在 `frontend/src/utils/lessonContent.ts`
- Store 中有处理两种格式的逻辑

### 3. 关键差异：API 服务配置 ⚠️

#### frontend/src/services/api.ts 的差异

**dev 分支**：
```typescript
function getApiBaseUrl(): string {
  // 动态获取当前主机名（优先于环境变量，确保 CloudStudio 环境能正确检测）
  const hostname = window.location.hostname
  // ... 动态检测逻辑 ...
  // 如果环境变量中配置了API地址，检查并处理
  if (import.meta.env.VITE_API_BASE_URL) {
    // ... 处理环境变量 ...
  }
}
```

**production-deploy 分支**：
```typescript
function getApiBaseUrl(): string {
  // 优先使用环境变量中的 API 地址（如果已配置）
  if (import.meta.env.VITE_API_BASE_URL) {
    // ... 直接返回环境变量 ...
    return envApiUrl
  }
  // 如果没有配置环境变量，使用动态检测
  // ... 动态检测逻辑 ...
}
```

**关键问题**：
- production-deploy 分支**优先使用环境变量**，如果环境变量配置错误或指向了错误的后端地址，会导致：
  1. API 请求失败
  2. 返回错误的数据
  3. 内容无法正确加载

### 4. Store 差异
- production-deploy 分支在创建新教案时有额外的格式转换逻辑（将 sections 转为 Cell[]）
- 但这只影响创建，不影响读取

### 5. 后端代码
- 后端代码在两个分支中**没有差异**
- `_lesson_to_response` 函数正常处理 content
- `_validate_content_cells` 函数支持两种格式

## 根本原因分析 ✅

### 问题根源

**API 地址检测逻辑的优先级差异**导致 production-deploy 分支在生产环境中可能使用了错误的 API 地址。

### 详细分析

1. **代码差异**：
   - **dev 分支**：先动态检测环境（CloudStudio、生产环境等），然后才检查环境变量
   - **production-deploy 分支**：优先使用环境变量 `VITE_API_BASE_URL`，如果没有环境变量才动态检测

2. **Docker 构建配置**：
   ```yaml
   # docker-compose.prod.yml
   frontend:
     build:
       args:
         VITE_API_BASE_URL: ${VITE_API_BASE_URL:-}  # 如果未设置，传入空字符串
   ```
   
   ```dockerfile
   # frontend/Dockerfile
   ARG VITE_API_BASE_URL=http://localhost:8000/api/v1  # 默认值
   ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
   ```

3. **问题场景**：
   - 如果生产环境构建时 `VITE_API_BASE_URL` 未设置或为空
   - Dockerfile 会使用默认值 `http://localhost:8000/api/v1`
   - production-deploy 分支会优先使用这个环境变量
   - 导致前端尝试连接到 `localhost:8000`，而不是实际的后端地址
   - 结果：无法获取教案内容或获取到错误的数据

4. **为什么 dev 分支正常**：
   - dev 分支优先动态检测，即使环境变量配置错误，也能通过动态检测找到正确的后端地址
   - 更适合开发和测试环境

### 解决方案建议

1. **方案一（推荐）**：修改 production-deploy 分支的 API 检测逻辑，使其与 dev 分支一致
   - 优先动态检测，环境变量作为备选
   - 确保在生产环境中也能正确检测后端地址

2. **方案二**：确保生产环境构建时正确设置 `VITE_API_BASE_URL`
   - 在构建脚本或 CI/CD 中设置正确的环境变量
   - 确保环境变量指向正确的后端地址

3. **方案三**：改进 Dockerfile 默认值处理
   - 如果环境变量为空，不设置默认值，让前端代码使用动态检测
