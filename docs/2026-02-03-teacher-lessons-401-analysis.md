# 教师登录后教案 401 问题：最近提交中的不当修改分析

**日期**: 2026-02-03  
**现象**: 教师账号登录后无法加载教案，请求 `/api/v1/lessons/` 返回 401 (Unauthorized)。

---

## 一、最近提交（HEAD）中的问题

对比当前**已提交**代码（`git show HEAD`），发现以下不当或缺失的修改会导致或加重 401：

### 1. `frontend/vite.config.ts`：代理被注释掉

**已提交内容**：`proxy` 整块被注释掉。

```ts
// 可选：配置代理以避免 CORS 问题
// proxy: {
//   '/api': { target: 'http://localhost:8000', changeOrigin: true, }
// }
```

**影响**：

- 若前端使用相对路径 `baseURL = '/api/v1'`，请求会发到 Vite（localhost:5173），**没有代理转发**，会得到 **404**，而不是到达后端 8000。
- 若前端使用绝对地址 `baseURL = 'http://localhost:8000/api/v1'`，请求会**跨域**（5173 → 8000），容易导致浏览器不发送或服务端收不到 `Authorization`，从而 **401**。

**结论**：本地开发必须启用 `/api` 代理，否则要么 404 要么跨域 401。

---

### 2. `frontend/src/services/api.ts`：本地未强制走代理

**已提交逻辑**：

- 当 `VITE_API_BASE_URL` 存在（例如 `http://localhost:8000/api/v1`）且 hostname 为 localhost 时，**没有**「本地开发强制使用 `/api/v1`」的逻辑。
- 因此会直接 `return envApiUrl`，即使用**绝对地址** `http://localhost:8000/api/v1`，请求直连 8000，形成跨域。

**影响**：即使后面启用了 Vite 代理，只要这里仍返回绝对地址，请求就不会走代理，依然跨域，容易 401。

**结论**：在本地开发（DEV + localhost/127.0.0.1）下应**一律**返回 `/api/v1`，与是否配置 `VITE_API_BASE_URL` 无关。

---

### 3. `frontend/src/services/api.ts`：401 时任意接口都清 token 并跳转登录

**已提交逻辑**：

```ts
if (error.response?.status === 401) {
  const isAuthRequest = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')
  if (!isAuthRequest) {
    localStorage.removeItem('access_token')
    window.location.href = '/login'
  }
}
```

**影响**：**只要是非登录/注册的接口 401（例如 `/lessons`），就会清空 token 并跳转登录页**。  
表现就是：教师登录成功 → 进入工作台 → 教案请求 401 → 立刻被清 token 并重定向到登录页（「一闪就回登录」）。

**结论**：应改为**仅当「会话校验」接口（如 `/auth/me`）401 时才清 token 并跳转登录**；数据接口（如 `/lessons`）401 时只报错，不自动清 token、不自动跳转，避免登录后闪退。

---

### 4. `frontend/src/pages/Teacher/Dashboard.vue`：初始化逻辑与 401 处理

**已提交逻辑**：

- 仅当 `!userStore.user` 时才请求 `getCurrentUser()`；登录后 `user` 已设置，因此**不会**再调 `getCurrentUser()`，直接执行 `loadLessons()` 等。
- 没有「先确认有 token、再请求 /auth/me、再请求教案」的明确顺序。
- 没有对 `getCurrentUser()` 或教案请求 401 的专门处理（例如 401 时登出并跳转登录）。

**影响**：  
若存在时序或跨域导致的首请求 401，Dashboard 会直接发教案请求，一旦 401 又触发上面第 3 点的全局逻辑，立刻清 token 并跳转，表现为「无法获得教案 + 需要重新登录」。

**结论**：  
应先检查 token 存在 → 再 `await getCurrentUser()` → 若 401 则登出并跳转登录、不再请求教案；只有会话正常后再调用 `loadLessons()` / `refreshPdcaOverview()` 等。

---

## 二、当前未提交修改（方案 C）在做什么

当前工作区相对 HEAD 的修改是在**纠正**上述问题：

| 文件 | 修改要点 |
|------|----------|
| `vite.config.ts` | **启用** `/api` 代理，指向 `http://localhost:8000`，并设置 `changeOrigin: true`、`ws: true`。 |
| `api.ts` | ① 本地开发（DEV + localhost/127.0.0.1）**一律**返回 `/api/v1`；② 请求拦截器增加从 `useUserStore().token` 的 fallback；③ 401 时**仅**在请求为 `/auth/me` 时清 token 并跳转登录。 |
| `Dashboard.vue` | 先检查 `hasToken` → `await getCurrentUser()` → 若 401 则 `userStore.logout()` 并 `window.location.href = '/login'`，避免在未认证时继续请求教案。 |

这些修改与「为何需要授权」「为何之前拿不到教案」的原因一致，方向正确，建议保留并提交。

---

## 三、若仍然 401，建议排查项

1. **确认未提交修改已生效**
   - 保存所有文件，重启 Vite 开发服务（`npm run dev` 或 `pnpm dev`）。
   - 浏览器硬刷新或无缓存打开教师工作台。

2. **确认请求是否走代理**
   - 打开控制台，看日志是否出现：`[API] 本地开发强制使用代理 /api/v1`。
   - 在 Network 里看教案请求的 URL：应为 `http://localhost:5173/api/v1/lessons/...`（同源），而不是 `http://localhost:8000/...`。

3. **确认后端与 token**
   - 后端服务已启动（例如 8000 端口）。
   - 登录后 localStorage 中有 `access_token`；若 401，可对比请求头是否带 `Authorization: Bearer <token>`。

4. **确认环境变量**
   - 本地开发可不依赖 `VITE_API_BASE_URL`（当前逻辑下会强制 `/api/v1`）；若仍配置了，不要配置成仅允许直连 8000 而绕过代理。

---

## 四、已实施的修复（方案 C）

1. **frontend/vite.config.ts**：启用 `/api` 代理，将请求转发到 `http://localhost:8000`，`changeOrigin: true`，`ws: true`。
2. **frontend/src/services/api.ts**：
   - 本地开发（DEV + localhost/127.0.0.1）**一律**返回 `/api/v1`，强制走代理。
   - 请求拦截器：优先 `localStorage.getItem('access_token')`，若无则从 `useUserStore().token` 取。
   - 401 响应：**仅当**请求为 `/auth/me` 时调用 `useUserStore().logout()` 并跳转 `/login`；移除调试用 agent log。
3. **frontend/src/pages/Teacher/Dashboard.vue**：先检查 `hasToken` → `await getCurrentUser()` → 若 401 则 `userStore.logout()` 并跳转登录，再调用 `loadLessons()` / `refreshPdcaOverview()`。

## 五、验证步骤

1. **重启前端**：保存所有文件后，停止并重新运行 `pnpm dev`（或 `npm run dev`）。
2. **清缓存**：浏览器硬刷新（Ctrl+Shift+R / Cmd+Shift+R）或无痕窗口打开 `http://localhost:5173`。
3. **教师登录**：用教师账号登录，进入教师工作台。
4. **看控制台**：应出现 `[API] 本地开发强制使用代理 /api/v1`；不应再出现教案接口 401。
5. **看 Network**：教案请求 URL 应为 `http://localhost:5173/api/v1/lessons/...`（同源），且请求头带 `Authorization: Bearer ...`。

## 六、总结

- **无法获得教案的直接原因**：请求教案时后端返回 401，前端拿不到数据；根因是**已提交代码**中：代理关闭、本地未强制走代理（跨域）、以及 401 时对任意接口清 token 并跳转登录。
- **为何需要授权**：教案接口设计为「必须登录且 token 有效」才返回数据，用于识别当前教师并做权限控制；401 表示「未带有效身份」，而不是「教师角色没权限」。
- **建议**：保留并提交当前方案 C 的修改；若仍 401，按第三节逐项排查。
