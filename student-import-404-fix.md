# 学生导入API调用404错误修复

## 🐛 问题描述

```
POST http://localhost:5173/api/v1/import 404 (Not Found)
SyntaxError: Failed to execute 'json' on 'Response': Unexpected end of JSON input
```

**原因**: 前端访问了前端服务器的5173端口，而不是后端的8000端口。

---

## ✅ 修复方案

在 `StudentManagementTab.vue` 的 `startImport` 函数中添加了正确的API基础URL检测逻辑。

### 修复前

```typescript
const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/import`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
})
```

**问题**:
- 环境变量 `VITE_API_BASE_URL` 为空
- 默认值 `/api/v1` 会访问前端服务器（5173端口）
- 导致404错误

### 修复后

```typescript
// 获取正确的API基础URL
const hostname = window.location.hostname
const protocol = window.location.protocol
let apiBaseUrl = '/api/v1'

// 检测 CloudStudio 环境
if (hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) {
  if (hostname.includes('--')) {
    const backendHostname = hostname.replace(/--\d+/, '--8000')
    apiBaseUrl = `https://${backendHostname}/api/v1`
  } else {
    apiBaseUrl = `${protocol}//${hostname}:8000/api/v1`
  }
} else if (import.meta.env.VITE_API_BASE_URL) {
  // 使用环境变量（如果配置了）
  apiBaseUrl = import.meta.env.VITE_API_BASE_URL
} else {
  // 本地开发环境
  apiBaseUrl = `${protocol}//${hostname}:8000/api/v1`
}

console.log('🚀 [学生导入] API基础地址:', apiBaseUrl)

const response = await fetch(`${apiBaseUrl}/import`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
})
```

**改进**:
1. ✅ 自动检测 CloudStudio 环境
2. ✅ 自动检测本地开发环境
3. ✅ 支持环境变量配置
4. ✅ 添加详细的日志输出
5. ✅ 改进错误处理

---

## 🔍 URL检测逻辑

### 1. CloudStudio 环境

**格式**: `{workspace-id}--{port}.{region}.cloudstudio.club`

| 环境 | 前端URL | 后端URL |
|------|---------|---------|
| 前端 | `xxx--5173.ap-shanghai2.cloudstudio.club` | - |
| 后端 | - | `xxx--8000.ap-shanghai2.cloudstudio.club` |

**转换**: 将 `--5173` 替换为 `--8000`

### 2. 本地开发环境

| 环境 | 访问地址 | 后端API |
|------|---------|---------|
| 本地 | `localhost:5173` 或 `127.0.0.1:5173` | `http://localhost:8000/api/v1` |
| 局域网 | `192.168.1.100:5173` | `http://192.168.1.100:8000/api/v1` |

### 3. 环境变量

如果设置了 `VITE_API_BASE_URL`，则优先使用环境变量。

---

## 📊 测试验证

### 本地开发环境

```bash
# 1. 启动后端（8000端口）
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. 启动前端（5173端口）
cd frontend && pnpm dev

# 3. 访问前端
open https://localhost:5173

# 4. 测试导入
# → 学生管理 → 批量导入 → 选择文件 → 开始导入
# → 应该访问: http://localhost:8000/api/v1/import
```

### API调用日志

修复后，在浏览器控制台可以看到：

```
🚀 [学生导入] API基础地址: http://localhost:8000/api/v1
📥 [学生导入] 响应状态: 200
✅ [学生导入] 导入结果: {total: 3, success: 3, ...}
```

---

## 🛠️ 错误处理改进

### 修复前

```typescript
if (!response.ok) {
  const error = await response.json()  // ❌ 404页面不是JSON，会报错
  throw new Error(error.detail || '导入失败')
}
```

### 修复后

```typescript
if (!response.ok) {
  let errorMessage = '导入失败'
  try {
    const error = await response.json()
    errorMessage = error.detail || error.message || errorMessage
  } catch (e) {
    // ✅ 如果响应不是JSON（如404 HTML页面），使用状态码
    errorMessage = `HTTP ${response.status}: ${response.statusText}`
  }
  throw new Error(errorMessage)
}
```

---

## 📁 修改文件

**文件**: `frontend/src/pages/Admin/OrganizationManagement/StudentManagementTab.vue`

**修改位置**: 第683-765行

**变更**:
- ✅ 添加API基础URL检测逻辑
- ✅ 添加详细日志输出
- ✅ 改进错误处理
- ✅ 支持多种环境（本地、CloudStudio、生产）

---

## 🎯 现在可以正常使用

### 完整流程

```
1. 下载模板
   → 组织架构管理 → 人员管理 → 学生管理 → 批量导入 → 下载导入模板

2. 填写数据
   → 使用新格式：学号*、姓名*、学籍号*、年级级别*、班级编号*

3. 上传导入
   → 选择Excel文件 → 预览数据 → 开始导入

4. 查看结果
   → 成功导入X位学生 ✅
```

---

## ✅ 验证清单

- [x] 本地开发环境API调用正常
- [x] CloudStudio环境API调用正常
- [x] 环境变量配置支持
- [x] 错误提示友好
- [x] 日志输出完整
- [x] 模板格式正确

---

**修复时间**: 2026-01-17
**状态**: ✅ 已修复并可用
