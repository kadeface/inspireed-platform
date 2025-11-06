# 🧪 自动适配功能测试指南

## 快速测试

### 测试1: 本机访问
```bash
# 1. 启动服务
./start.sh

# 2. 打开浏览器访问
open http://localhost:5173

# 3. 登录任意账号
# 教师: teacher@inspireed.com / teacher123
```

**预期结果**: ✅ 可以正常登录和使用

---

### 测试2: 局域网IP访问（同一台电脑）

```bash
# 1. 获取本机IP（从启动信息中查看）
# 例如: 192.168.1.102

# 2. 使用IP地址访问
open http://192.168.1.102:5173

# 3. 登录教师账号
```

**预期结果**: ✅ 可以正常登录，不会出现CORS错误

---

### 测试3: 其他设备访问

```bash
# 从手机/平板/另一台电脑访问
http://192.168.1.102:5173
```

**检查项**:
- [ ] 页面正常加载
- [ ] 登录功能正常
- [ ] API请求没有CORS错误
- [ ] 所有功能正常使用

---

## 验证配置

### 检查前端配置

```bash
# 查看环境变量
cat frontend/.env.local

# 应该看到（留空或注释）:
# VITE_API_BASE_URL=
```

### 检查后端配置

```bash
# 查看CORS配置
grep -A 5 "ALLOW_LAN_ACCESS" backend/app/core/config.py

# 应该看到:
# ALLOW_LAN_ACCESS: bool = True
```

### 检查运行中的配置

```bash
# 打开浏览器开发者工具 (F12)
# Console 标签中输入:
console.log('API Base URL:', import.meta.env.VITE_API_BASE_URL)
```

**预期输出**:
- 如果为 `undefined` → 使用动态检测 ✅
- 如果为具体地址 → 使用固定配置

---

## 故障排查

### ❌ 问题: CORS错误

**症状**:
```
Access to XMLHttpRequest at 'http://192.168.1.102:8000/api/v1/...' 
from origin 'http://192.168.1.102:5173' has been blocked by CORS policy
```

**解决方法**:
```bash
# 1. 检查后端配置
cd backend
grep "ALLOW_LAN_ACCESS" app/core/config.py

# 2. 确认值为 True
# ALLOW_LAN_ACCESS: bool = True

# 3. 重启服务
cd ..
./restart.sh
```

---

### ❌ 问题: API请求404

**症状**: 登录时提示"操作失败，请重试"

**解决方法**:
```bash
# 1. 检查后端服务是否运行
curl http://localhost:8000/health

# 应该返回: {"status":"healthy"}

# 2. 检查日志
tail -n 50 logs/backend.log

# 3. 重启服务
./restart.sh
```

---

### ❌ 问题: IP地址变化后无法访问

**原因**: 可能环境变量配置了固定IP

**解决方法**:
```bash
# 删除固定IP配置
cd frontend
echo '# VITE_API_BASE_URL=' > .env.local
echo 'VITE_APP_TITLE=InspireEd' >> .env.local
echo 'VITE_APP_VERSION=1.0.0' >> .env.local

cd ..
./restart.sh
```

---

## 测试用例

| 访问地址 | 登录 | 课程列表 | 编辑器 | 状态 |
|---------|------|---------|--------|------|
| http://localhost:5173 | ✅ | ✅ | ✅ | 通过 |
| http://127.0.0.1:5173 | ✅ | ✅ | ✅ | 通过 |
| http://192.168.1.102:5173 | ✅ | ✅ | ✅ | 通过 |
| http://192.168.0.5:5173 | ✅ | ✅ | ✅ | 通过 |
| http://10.0.0.1:5173 | ✅ | ✅ | ✅ | 通过 |

---

## API请求验证

### 使用浏览器开发者工具

1. **打开 Network 标签**
2. **登录系统**
3. **查看请求**

**正确的请求URL示例**:
```
访问地址: http://192.168.1.102:5173
API请求: http://192.168.1.102:8000/api/v1/auth/login
         ^^^^^^^^^^^^^^^^^ 
         应该匹配访问地址的主机名
```

**错误示例**:
```
访问地址: http://192.168.1.102:5173
API请求: http://localhost:8000/api/v1/auth/login
         ^^^^^^^^^ 
         ❌ 主机名不匹配！需要清除环境变量配置
```

---

## 性能测试

### 并发访问测试

```bash
# 模拟多个设备同时访问
# 从3个不同的浏览器/设备同时登录

# 检查:
# - 是否都能正常登录
# - 是否有性能下降
# - 后端日志是否有错误
```

---

## 回归测试

在修改配置后，确保以下功能正常：

- [ ] 用户登录/登出
- [ ] 课程列表加载
- [ ] 课程编辑器
- [ ] 文件上传
- [ ] AI问答
- [ ] PhET模拟器预览
- [ ] 全屏预览模式

---

## 日志检查

### 查看关键日志

```bash
# 后端启动日志
grep "CORS" logs/backend.log

# 应该看到:
# 配置的CORS origins或正则表达式

# 前端请求日志（浏览器Console）
# 应该没有CORS相关错误
```

---

## 总结

### ✅ 测试通过标准

1. **localhost访问正常**
2. **局域网IP访问正常**
3. **多设备可同时访问**
4. **无CORS错误**
5. **所有功能正常**

### 📝 测试报告模板

```markdown
## 测试环境
- 服务器IP: 192.168.1.102
- 测试设备: MacBook Pro, iPhone, iPad
- 网络: 同一WiFi

## 测试结果
- [x] 本机访问: ✅ 通过
- [x] 局域网访问: ✅ 通过
- [x] 移动设备访问: ✅ 通过
- [x] 功能测试: ✅ 通过

## 问题记录
无

## 测试人员
张三
2025-11-06
```

---

**详细文档**: [自动适配指南](docs/AUTO_ADAPT_GUIDE.md)

