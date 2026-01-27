# AI Assistant 调用大模型工作流程

## 完整调用链路

### 1. 前端发起请求
- **文件**: `frontend/src/services/assistant.ts`
- **方法**: `askTeacherAssistant()`
- **路径**: `POST /teacher/assistant/query`
- **请求体**: `TeacherAssistantRequest` (包含 question, topic, context, agent_prompt 等)

```typescript
const response = await api.post<TeacherAssistantResponse>(
  `${this.teacherBasePath}/query`,
  payload
)
```

### 2. 后端路由接收请求
- **文件**: `backend/app/api/v1/teacher_ai_assistant.py`
- **路由函数**: `query_teacher_assistant()`
- **路由路径**: `/api/v1/teacher/assistant/query` (在 `backend/app/api/v1/__init__.py` 中注册)

```python
@router.post("/query", response_model=AssistantResponse)
async def query_teacher_assistant(
    payload: AssistantRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AssistantResponse:
```

### 3. 调用 AI 问答服务
- **服务类**: `AIQAService` (在 `backend/app/services/ai_qa.py`)
- **方法**: `ask_question()`
- **调用位置**: `teacher_ai_assistant.py:234`

```python
ai_result = await ai_qa_service.ask_question(
    question=payload.question,
    context=context_text,
    lesson_title=lesson_title,
    agent_prompt=agent_prompt,
)
```

### 4. 构建提示词
- **方法**: `_build_prompt()`
- **逻辑**:
  - 如果提供了 `agent_prompt`，使用自定义智能体提示词
  - 否则使用默认的系统提示词（教学助手角色）
  - 构建用户消息（包含问题、上下文、课程标题等）

### 5. 调用 OpenAI API
- **方法**: `_call_openai()`
- **流程**:

#### 5.1 API 密钥检查
```python
if not self.openai_api_key or self.openai_api_key == "sk-your-openai-api-key" or not self.openai_api_key.strip():
    # 返回模拟回答
    return await self._get_mock_response(user_message, system_prompt)
```

**检查条件**:
- API 密钥为空
- API 密钥等于默认值 `"sk-your-openai-api-key"`
- API 密钥只包含空白字符

#### 5.2 发送 HTTP 请求
```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(
        f"{self.openai_base_url}/chat/completions",
        headers=headers,
        json=data
    )
```

**请求参数**:
- URL: `{OPENAI_BASE_URL}/chat/completions` (默认: `https://api.openai.com/v1/chat/completions`)
- Headers: `Authorization: Bearer {OPENAI_API_KEY}`
- Body:
  - `model`: 模型名称 (默认: `gpt-3.5-turbo`)
  - `messages`: [系统提示词, 用户消息]
  - `max_tokens`: 最大令牌数 (默认: 20000)
  - `temperature`: 温度参数 (默认: 0.7)

#### 5.3 处理响应
- **成功** (status_code == 200): 提取回答内容
- **失败**: 回退到模拟回答

### 6. 返回响应
- **响应模型**: `AssistantResponse`
- **包含字段**:
  - `answer`: AI 回答内容
  - `insights`: 洞察列表
  - `suggested_actions`: 建议操作列表
  - `follow_up_questions`: 后续问题列表
  - `model_used`: 使用的模型
  - `confidence`: 置信度
  - `response_time_ms`: 响应时间（毫秒）

## 配置要求

### 环境变量
- **OPENAI_API_KEY**: OpenAI API 密钥（必需，用于调用真实 AI 服务）
- **OPENAI_BASE_URL**: API 基础 URL（可选，默认: `https://api.openai.com/v1`）
- **DEFAULT_AI_MODEL**: 默认模型（可选，默认: `gpt-3.5-turbo`）
- **AI_MAX_TOKENS**: 最大令牌数（可选，默认: 20000）
- **AI_TEMPERATURE**: 温度参数（可选，默认: 0.7）

### 配置文件位置
- `.env` 文件应在 `backend/` 目录下
- 参考 `backend/env.example` 查看配置格式

## 诊断步骤

### 1. 检查 API 密钥配置
```bash
# 检查环境变量
cd backend
grep OPENAI_API_KEY .env

# 或检查配置加载
python -c "from app.core.config import settings; print('API Key:', settings.OPENAI_API_KEY[:20] + '...' if settings.OPENAI_API_KEY else 'NOT SET')"
```

### 2. 查看后端日志
后端会输出详细的日志信息：
- `🤖 AI Assistant Request Received` - 请求接收
- `📡 [API CALL]` - API 调用信息
- `✅ [API SUCCESS]` - API 调用成功
- `❌ [ERROR]` - API 调用失败
- `⚠️  [WARNING]` - API 密钥未配置，使用模拟回答

### 3. 检查网络连接
- 确认服务器能够访问 `https://api.openai.com`
- 检查防火墙设置
- 确认 API 密钥有效且有足够配额

### 4. 验证路由注册
- 确认路由已在 `backend/app/api/v1/__init__.py` 中注册
- 路径: `/api/v1/teacher/assistant`

## 常见问题

### Q: 返回"Object"原型错误
**可能原因**:
1. API 密钥未配置，返回了模拟回答但前端解析出错
2. 响应序列化问题
3. 前端类型定义不匹配

**解决方法**:
1. 检查后端日志，确认是否使用了模拟回答
2. 检查 API 密钥配置
3. 检查前端响应处理代码

### Q: 没有调用大模型
**可能原因**:
1. API 密钥未配置或无效
2. API 调用失败（网络错误、超时等）
3. 返回了模拟回答

**解决方法**:
1. 检查后端日志中的警告信息
2. 确认 API 密钥有效
3. 检查网络连接

### Q: API 调用超时
**可能原因**:
1. 网络连接慢
2. OpenAI API 服务响应慢
3. 请求过大（提示词太长）

**解决方法**:
1. 增加超时时间（当前: 30秒）
2. 减少提示词长度
3. 检查网络连接质量

## 日志示例

### 成功调用
```
[2024-01-01 12:00:00] ================================================================================
[2024-01-01 12:00:00] 🤖 AI Assistant Request Received
[2024-01-01 12:00:00] User: teacher1 (ID: 1)
[2024-01-01 12:00:00] Question: 如何设计一个课程...
[2024-01-01 12:00:00] Topic: pdca
[2024-01-01 12:00:00] ✅ Using CUSTOM AGENT PROMPT
[2024-01-01 12:00:00]    Agent prompt length: 500
[2024-01-01 12:00:00] --------------------------------------------------------------------------------
[2024-01-01 12:00:00] 📡 [API CALL] System prompt length: 500, User message length: 200
[2024-01-01 12:00:00] 📡 [API CALL] Model: gpt-3.5-turbo, Base URL: https://api.openai.com/v1
[2024-01-01 12:00:00] ✅ [API SUCCESS] Response received
[2024-01-01 12:00:00]    回答长度: 500 字符
[2024-01-01 12:00:00]    使用的tokens: 800
[2024-01-01 12:00:00] ✅ AI Response received (model: gpt-3.5-turbo, confidence: 0.9)
[2024-01-01 12:00:00]    Answer length: 500
[2024-01-01 12:00:00] ================================================================================
```

### 使用模拟回答
```
[2024-01-01 12:00:00] ⚠️  [WARNING] OpenAI API密钥未配置或无效，使用模拟回答
[2024-01-01 12:00:00] ⚠️  [WARNING] 请配置有效的 OPENAI_API_KEY 环境变量以使用真实的AI服务
[2024-01-01 12:00:00] ⚠️  [WARNING] 当前API密钥: sk-your-openai-api-...
```

### API 调用失败
```
[2024-01-01 12:00:00] ❌ [ERROR] AI服务连接失败，使用模拟回答
[2024-01-01 12:00:00]    错误类型: ConnectError
[2024-01-01 12:00:00]    错误信息: Connection refused
```

