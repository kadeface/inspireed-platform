# Findings: 教师端登录后闪退

## 现象
教师端登录成功后，短暂显示教师工作台，随即跳回登录页（“闪退”）。

## 根因分析

### 1. API 401 拦截器导致强制跳转（最可能原因）

**位置**：`frontend/src/services/api.ts` 第 265-272 行

```typescript
if (error.response?.status === 401) {
  const requestUrl = error.config?.url ?? ''
  const isAuthRequest = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')

  if (!isAuthRequest) {
    localStorage.removeItem('access_token')
    window.location.href = '/login'
  }
}
```

**逻辑**：任意非登录/注册接口返回 401 时，会清除 `access_token` 并直接重定向到 `/login`，表现为“刚进入工作台就回到登录页”。

### 2. Teacher Dashboard 加载时的 API 调用

**位置**：`frontend/src/pages/Teacher/Dashboard.vue` 第 1524-1541 行 `onMounted`

| 调用 | 接口 | 可能 401 场景 |
|------|------|---------------|
| `authService.getCurrentUser()` | `/auth/me` | token 无效/过期 |
| `loadLessons()` | lessonService | 教案列表接口 |
| `loadAvailableChapters()` | curriculumService | 课程/章节接口 |
| `refreshPdcaOverview()` | 多个接口 | 教研组统计、问答统计、教案状态等 |

任一接口返回 401，都会触发上述拦截器逻辑，导致闪退。

### 3. 可能触发 401 的具体场景

1. **Token 校验失败**：token 格式错误、签名不匹配、后端与前端 secret 不一致
2. **Token 过期**：登录时下发短期 token，进入 Dashboard 前已过期
3. **API 地址错误**：`api.ts` 中 baseURL 计算有误，请求发到错误地址，返回 401
4. **CORS / 代理问题**：开发/生产环境代理配置错误，预检或实际请求被拒绝
5. **后端权限逻辑**：教师角色在部分接口上被拒绝访问，返回 401（应为 403 更合理）

### 4. 相关代码路径

| 文件 | 相关逻辑 |
|------|----------|
| `frontend/src/services/api.ts` | 401 拦截、baseURL 计算、请求/响应拦截 |
| `frontend/src/pages/Login.vue` | 登录流程、setToken/setUser、router.push |
| `frontend/src/pages/Teacher/Dashboard.vue` | onMounted 数据加载 |
| `frontend/src/router/index.ts` | 路由守卫、角色校验 |
| `frontend/src/store/user.ts` | token/user 持久化 |

### 5. 登录时序（理论上无问题）

```
Login.vue handleSubmit:
  authService.login() → token
  userStore.setToken(token)  // 同步写 localStorage
  authService.getCurrentUser() → user
  userStore.setUser(user)    // 同步写 localStorage
  router.push('/teacher')
```

token 和 user 在跳转前已写入 localStorage，路由守卫与 API 拦截器都能读取到。因此，闪退更可能是进入 Dashboard 后**某个接口返回 401** 导致。

## 建议排查步骤

1. **打开浏览器开发者工具**
   - 在 Network 面板勾选 “Preserve log”
   - 登录教师账号，观察进入 `/teacher` 后的请求
   - 找出第一个返回 401 的请求及其 URL

2. **检查 Console**
   - 是否有与 401、CORS、网络错误相关的报错

3. **检查 API baseURL**
   - 在 Console 中执行：`localStorage.getItem('access_token')` 确认 token 存在
   - 查看请求的完整 URL 是否指向正确的后端

4. **临时关闭 401 自动跳转**
   - 在 `api.ts` 的 401 分支中注释 `window.location.href = '/login'`
   - 再次登录，观察具体 401 请求与错误信息

## 建议修复方向

1. **优化 401 处理**  
   - 在清除 token 并跳转前，先提示用户（如 toast）“登录已过期，请重新登录”
   - 可考虑在部分接口（如 `/auth/me`）返回 401 时做特殊处理，避免误判

2. **确认 token 与后端配置**  
   - 检查后端 JWT secret、过期时间、签发者等与前端是否匹配
   - 确认教师角色在相关接口上的权限配置

3. **增强错误日志**  
   - 在 401 分支中 `console.warn` 记录请求 URL、status、response，便于线上排查
