# 配置加载机制说明

## 📋 配置优先级

在 `backend/app/core/config.py` 中，`Settings` 类使用 Pydantic Settings 来管理配置。配置的加载优先级如下（从高到低）：

```
1. 🔝 系统环境变量（最高优先级）
   ↓
2. 📄 .env 文件
   ↓
3. 📝 config.py 中的默认值（最低优先级）
```

## 🔍 实际工作方式

### 配置类定义

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # 指定从 .env 文件读取配置
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""  # 这是默认值
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"
    # ... 其他配置
```

### 加载流程

1. **首先检查系统环境变量**
   - 如果系统环境变量中设置了 `OPENAI_API_KEY`，直接使用该值
   - 例如：`export OPENAI_API_KEY=sk-xxx`（Linux/Mac）或 `set OPENAI_API_KEY=sk-xxx`（Windows）

2. **如果系统环境变量未设置，读取 .env 文件**
   - 从 `backend/.env` 文件中读取配置
   - 如果 `.env` 文件中有 `OPENAI_API_KEY=sk-xxx`，使用该值

3. **如果 .env 文件也没有，使用 config.py 中的默认值**
   - 例如：`OPENAI_API_KEY: str = ""`（空字符串）

## ✅ 推荐做法

### 1. 在 .env 文件中配置（推荐）

```bash
# backend/.env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_MODEL=gpt-3.5-turbo
AI_MAX_TOKENS=20000
AI_TEMPERATURE=0.7
```

**优点**：
- ✅ 配置集中管理
- ✅ 不同环境可以使用不同的配置文件
- ✅ 不会将敏感信息提交到版本控制系统

### 2. config.py 中的默认值的作用

`config.py` 中的默认值主要作为：
- **后备值**：当 `.env` 文件不存在或缺少某些配置时使用
- **文档说明**：展示可用的配置项及其默认值
- **开发环境默认值**：方便开发时快速启动

**注意**：
- ⚠️ 不要将实际的 API 密钥写在 `config.py` 中（会提交到版本控制）
- ⚠️ `OPENAI_API_KEY` 的默认值保持为空字符串 `""`，强制在 `.env` 文件中配置

## 🔧 实际示例

### 场景 1: 只有 .env 文件配置

```bash
# .env 文件
OPENAI_API_KEY=sk-abc123...
```

**结果**：使用 `.env` 文件中的值 `sk-abc123...`

### 场景 2: 系统环境变量和 .env 文件都有

```bash
# 系统环境变量
export OPENAI_API_KEY=sk-env-var...

# .env 文件
OPENAI_API_KEY=sk-env-file...
```

**结果**：使用系统环境变量的值 `sk-env-var...`（系统环境变量优先级更高）

### 场景 3: 都没有配置

**结果**：使用 `config.py` 中的默认值 `""`（空字符串）

## 🐛 常见问题

### Q: 我在 .env 文件中配置了 OPENAI_API_KEY，但为什么没有生效？

**可能原因**：
1. 后端服务未重启（需要重新加载配置）
2. `.env` 文件路径不对（应该在 `backend/.env`）
3. `.env` 文件格式错误（应该是 `KEY=value` 格式，没有空格）

**解决方法**：
```bash
# 1. 确认 .env 文件位置
cd backend
ls -la .env

# 2. 确认格式正确
cat .env | grep OPENAI_API_KEY
# 应该显示：OPENAI_API_KEY=sk-xxx（没有引号，没有前后空格）

# 3. 重启后端服务
./stop.sh
./start.sh
```

### Q: config.py 中的默认值和 .env 文件的值有什么关系？

**回答**：
- `config.py` 中的值是**默认值/后备值**
- `.env` 文件中的值会**覆盖** `config.py` 中的默认值
- 如果 `.env` 文件中没有某个配置项，才会使用 `config.py` 中的默认值

### Q: 我应该修改 config.py 中的默认值吗？

**回答**：
- ✅ **可以修改**：对于非敏感的配置项（如 `OPENAI_BASE_URL`、`AI_MAX_TOKENS` 等）
- ❌ **不建议修改**：对于敏感配置（如 `OPENAI_API_KEY`），应该保持默认值为空，强制在 `.env` 文件中配置

## 📝 总结

| 配置方式 | 优先级 | 适用场景 | 是否提交到版本控制 |
|---------|--------|---------|------------------|
| 系统环境变量 | 最高 | 生产环境、CI/CD | 否 |
| .env 文件 | 中等 | 开发环境、本地配置 | 否（应在 .gitignore 中） |
| config.py 默认值 | 最低 | 后备值、文档说明 | 是 |

**最佳实践**：
1. 在 `.env` 文件中配置所有需要自定义的值
2. `config.py` 中只保留合理的默认值
3. 敏感信息（API 密钥等）只放在 `.env` 文件中，不在 `config.py` 中硬编码

