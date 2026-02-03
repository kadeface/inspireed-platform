# Task Plan: 教师端登录后闪退问题排查

## Goal
找出教师端登录进入后闪退（闪一下教师工作台后回到登录页）的根本原因并修复。

## Current Phase
Phase 1（根因分析）已完成，待确认修复方案

## Phases

### Phase 1: 根因分析与发现
- [x] 梳理登录流程与路由守卫
- [x] 检查 API 401 拦截器行为
- [x] 分析 Teacher Dashboard 加载时的 API 调用
- [x] 整理发现到 findings.md
- **Status:** complete

### Phase 2: 修复方案设计与实施
- [ ] 确定修复方案（401 处理优化 / token 时序 / 其他）
- [ ] 实施代码修改
- [ ] 本地验证
- **Status:** pending

### Phase 3: 验证与交付
- [ ] 回归验证教师端登录
- [ ] 更新 findings.md 与 progress
- **Status:** pending

## Key Findings（简要）

1. **401 拦截器导致重定向到登录**：`api.ts` 中任何非登录/注册的 401 响应会清除 token 并 `window.location.href = '/login'`，导致“闪退”。
2. **Dashboard 挂载时有多处 API 调用**：getCurrentUser、loadLessons、loadSubjectGroupStats、loadQuestionStats 等，任一返回 401 都会触发闪退。
3. **可能触发 401 的场景**：token 失效/过期、后端校验失败、API 地址错误、CORS 等。

详见 `findings_teacher_flash.md`。

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| 优先排查 401 拦截逻辑 | 闪退表现为“进入后立刻回到登录页”，与 401 处理逻辑高度一致 |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| （待补充） | 1       |            |

## Notes
- 若为网络/环境问题（API 不可达），需结合具体部署环境（CloudStudio / 生产）进一步排查
- 可考虑在 401 拦截时增加用户提示，而非直接重定向
