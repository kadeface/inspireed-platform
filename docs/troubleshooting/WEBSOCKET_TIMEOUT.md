# WebSocket 连接超时排查

## 现象

- 控制台报错：`WebSocket连接超时（10000ms）` 或 `WebSocket is closed before the connection is established`
- 学生端/教师端会降级到轮询模式，功能可用但实时性变差

## 可能原因

1. **后端未在超时内响应**
   - 后端冷启动、数据库慢、或首次请求较慢，超过默认 20 秒未完成 WebSocket 握手。
   - 前端默认超时已改为 20 秒（原 10 秒），若仍超时，可检查后端日志与数据库。

2. **后端未监听外网/局域网**
   - 学生或教师通过 `192.168.x.x` 访问时，后端必须监听 `0.0.0.0`，不能只监听 `127.0.0.1`。
   - 本机脚本启动：`uvicorn ... --host 0.0.0.0 --port 8000` 已正确。
   - Docker：容器内服务监听 8000，宿主机端口映射 `8000:8000` 即可从局域网访问。

3. **防火墙或网络**
   - 本机或路由器防火墙拦截 8000 端口的 TCP 连接或 WebSocket 升级请求。
   - 跨网段、VPN、代理等导致连接变慢或中断。

4. **反向代理未配置 WebSocket**
   - 若前端/API 前有 Nginx 等反向代理，需对 WebSocket 做升级配置，例如：
   ```nginx
   location /api/v1/classroom-sessions/ {
       proxy_pass http://backend;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_read_timeout 86400;
   }
   ```

5. **Origin 校验失败**
   - 后端会校验 WebSocket 请求的 `Origin`。若前端页面来源（如 `http://192.168.2.57:80`）未在后端允许列表中，连接会在服务端被关闭。
   - 当前后端允许：localhost、127.0.0.1、192.168.x.x、10.x、172.16–31.x、CloudStudio 域名。确保实际访问的 Origin 符合规则。

## 前端已做调整

- 默认连接超时由 **10 秒** 改为 **20 秒**（`frontend/src/services/websocket.ts`）。
- 超时仅在对端仍处于 `CONNECTING` 时触发关闭，并提示「请检查网络或后端是否可访问」。
- 超时或连接失败后会**自动降级到轮询**，学生端/教师端仍可正常使用，仅实时性依赖轮询间隔。

## 建议排查步骤

1. 浏览器直接访问：`http://<后端IP>:8000/health`，确认后端 HTTP 可访问。
2. 查看后端日志：学生/教师连接时是否有 `学生WebSocket连接请求` 或教师端对应日志；若有则看后续是否报错或关闭原因。
3. 确认前端访问地址的 Origin（协议+主机+端口）在后端 CORS/WebSocket Origin 允许范围内。
4. 若走 Nginx/代理，按上文增加 WebSocket 的 `Upgrade`/`Connection` 与 `proxy_read_timeout`。
5. 仍超时时，可在 `websocket.ts` 中临时将 `connect(..., 20000)` 的第三个参数改为更大值（如 30000）做测试。

---

文档日期：2026-02-03
