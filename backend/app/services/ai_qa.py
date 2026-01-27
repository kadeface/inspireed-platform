"""
AI问答服务
提供智能问答功能，支持多种AI模型
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import httpx
from app.core.config import settings


@dataclass
class AIResponse:
    """AI回答结果"""

    answer: str
    confidence: float
    response_time: float
    model_used: str
    tokens_used: Optional[int] = None


class AIQAService:
    """AI问答服务类"""

    def __init__(self):
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", None)
        self.openai_base_url = getattr(
            settings, "OPENAI_BASE_URL", "https://api.openai.com/v1"
        )
        self.default_model = getattr(settings, "DEFAULT_AI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = getattr(settings, "AI_MAX_TOKENS", 1000)
        self.temperature = getattr(settings, "AI_TEMPERATURE", 0.7)

    async def ask_question(
        self,
        question: str,
        context: Optional[str] = None,
        lesson_title: Optional[str] = None,
        cell_content: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        agent_prompt: Optional[str] = None,
    ) -> AIResponse:
        """
        向AI提问

        Args:
            question: 问题内容
            context: 上下文信息
            lesson_title: 课程标题
            cell_content: Cell内容
            model: 使用的AI模型

        Returns:
            AIResponse: AI回答结果
        """
        start_time = time.time()
        model = model or self.default_model
        # 确保 model 是字符串类型
        if not isinstance(model, str):
            model = str(model) if model else self.default_model

        try:
            # 构建提示词（返回系统提示词和用户消息）
            system_prompt, user_message = self._build_prompt(question, context, lesson_title, cell_content, agent_prompt)

            # 调用AI API（确保 model 是字符串）
            final_model: str = str(model) if model else self.default_model
            response = await self._call_openai(system_prompt, user_message, final_model)

            response_time = (time.time() - start_time) * 1000

            return AIResponse(
                answer=response["answer"],
                confidence=response.get("confidence", 0.8),
                response_time=response_time,
                model_used=model or "unknown",
                tokens_used=response.get("tokens_used"),
            )

        except Exception as e:
            # 如果出现任何异常，回退到模拟回答
            import sys
            import datetime
            import traceback
            
            def _log_print(*args, **kwargs):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"[{timestamp}] " + " ".join(str(arg) for arg in args)
                print(message, **kwargs, flush=True)
                sys.stdout.flush()
                sys.stderr.flush()
            
            _log_print(f"❌ [ERROR] AI服务处理异常，使用模拟回答")
            _log_print(f"   异常类型: {type(e).__name__}")
            _log_print(f"   异常信息: {str(e)}")
            _log_print(f"   完整堆栈:\n{traceback.format_exc()}")
            _log_print(f"   诊断信息: API密钥已配置={bool(self.openai_api_key)}, Base URL={self.openai_base_url}, Model={model}")
            
            response_time = (time.time() - start_time) * 1000
            try:
                # 尝试生成模拟回答（传入系统提示词）
                system_prompt, user_message = self._build_prompt(question, context, lesson_title, cell_content, agent_prompt)
                mock_response = await self._get_mock_response(user_message, system_prompt)
                return AIResponse(
                    answer=mock_response["answer"],
                    confidence=mock_response.get("confidence", 0.75),
                    response_time=response_time,
                    model_used="mock",
                    tokens_used=mock_response.get("tokens_used"),
                )
            except Exception as fallback_error:
                # 如果连模拟回答都失败，返回错误消息
                _log_print(f"❌ [ERROR] 模拟回答生成也失败: {str(fallback_error)}")
                response_time = (time.time() - start_time) * 1000
                return AIResponse(
                    answer=f"抱歉，AI服务暂时不可用。请稍后重试或联系管理员。",
                    confidence=0.0,
                    response_time=response_time,
                    model_used=model or "unknown",
                )

    def _build_prompt(
        self,
        question: str,
        context: Optional[str] = None,
        lesson_title: Optional[str] = None,
        cell_content: Optional[Dict[str, Any]] = None,
        agent_prompt: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        构建AI提示词
        
        Returns:
            tuple: (system_prompt, user_message) 系统提示词和用户消息
        """
        # 统一的日志函数（避免重复定义）
        import sys
        import datetime
        
        def _log_print(*args, **kwargs):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"[{timestamp}] " + " ".join(str(arg) for arg in args)
            print(message, **kwargs, flush=True)
            sys.stdout.flush()
            sys.stderr.flush()
        
        # 系统角色设定
        # 如果提供了自定义智能体提示词，则使用它；否则使用默认提示词
        if agent_prompt:
            system_prompt = agent_prompt
            _log_print(f"✅ [AGENT] Using CUSTOM AGENT PROMPT")
            _log_print(f"   提示词长度: {len(agent_prompt)} 字符")
            _log_print(f"   提示词预览: {agent_prompt[:300]}...")
        else:
            _log_print("⚠️  [AGENT] Using DEFAULT system prompt (no agent selected)")
            # 默认系统角色设定（增强学习科学理论支持）
            system_prompt = """你是一个专业的教学助手，专门帮助教师进行教学设计和教学改进。

你擅长基于学习科学理论回答教育相关的问题。

你熟悉以下学习科学理论和教学方法：

1. **布鲁姆分类法（Bloom's Taxonomy）**：
   - 记忆（Remember）：回忆事实和基本概念
   - 理解（Understand）：解释概念和意义
   - 应用（Apply）：在新情境中使用信息
   - 分析（Analyze）：区分和组织信息
   - 评价（Evaluate）：做出判断和批判
   - 创造（Create）：产生新的或原创性的作品

2. **苏格拉底式提问法（Socratic Questioning）**：
   - 澄清性问题：帮助学生明确概念
   - 探索假设：挑战学生的前提假设
   - 证据和理由：要求学生提供支持证据
   - 观点和视角：考虑不同观点
   - 影响和后果：探索含义和后果
   - 关于问题的问题：元认知反思

3. **费曼学习法（Feynman Technique）**：
   - 选择概念并尝试解释
   - 识别知识缺口
   - 回到原始材料学习
   - 简化并类比

4. **5E教学模型**：
   - Engage（参与）：激发兴趣和动机
   - Explore（探索）：主动探索和发现
   - Explain（解释）：建构概念和解释
   - Elaborate（深化）：应用和迁移知识
   - Evaluate（评价）：评估理解和反思

5. **建构主义学习理论**：
   - 学生主动建构知识
   - 基于已有经验学习
   - 社会互动促进学习
   - 最近发展区（ZPD）和脚手架支持

6. **学习风格和差异化教学**：
   - 视觉型、听觉型、动觉型学习者
   - 多元智能理论
   - 为不同学习风格提供支持

7. **元认知和主动输出**：
   - 让学生解释自己的思维过程
   - 促进自我监控和反思
   - 通过输出促进深度学习

请用简洁、准确、易懂的语言回答问题，并在适当的时候应用这些学习科学理论。"""

        # 构建用户消息（包含上下文和问题）
        user_message_parts = []
        
        # 上下文信息
        if lesson_title:
            user_message_parts.append(f"当前课程：{lesson_title}")

        if context:
            user_message_parts.append(f"上下文信息：{context}")

        if cell_content:
            # 根据Cell类型提供特定上下文
            cell_type = cell_content.get("type", "unknown")
            if cell_type == "code":
                code = cell_content.get("code", "")
                language = cell_content.get("language", "")
                user_message_parts.append(f"代码内容（{language}）：\n{code}")
            elif cell_type == "video":
                video_title = cell_content.get("title", "")
                video_desc = cell_content.get("description", "")
                user_message_parts.append(f"视频内容：{video_title}\n{video_desc}")
            elif cell_type == "text":
                text_content = cell_content.get("html", "")
                user_message_parts.append(f"文本内容：{text_content}")

        # 问题
        user_message_parts.append(f"教师问题：{question}")

        # 回答要求（仅在不使用智能体时添加）
        if not agent_prompt:
            answer_guidance = """回答要求：
1. 如果问题涉及教学设计，请结合学习科学理论（如布鲁姆分类法、5E模型等）提供建议
2. 如果问题涉及提问技巧，请提供苏格拉底式提问的具体示例
3. 如果问题涉及学生理解，请考虑费曼学习法和主动输出策略
4. 如果问题涉及差异化教学，请考虑不同学习风格和多元智能
5. 提供具体、可操作的建议，避免空泛的理论描述"""
            user_message_parts.append(answer_guidance)

        user_message = "\n\n".join(user_message_parts) if user_message_parts else question
        
        # 调试：打印最终提示词（使用统一的日志函数）
        _log_print(f"[DEBUG] System prompt length: {len(system_prompt)}")
        _log_print(f"[DEBUG] User message length: {len(user_message)}")
        if agent_prompt:
            _log_print(f"[DEBUG] System prompt preview: {system_prompt[:200]}...")
        
        return system_prompt, user_message

    async def _call_openai(self, system_prompt: str, user_message: str, model: str) -> Dict[str, Any]:
        """调用OpenAI API，失败时自动回退到模拟回答"""
        import sys
        import datetime
        
        def log_print(*args, **kwargs):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"[{timestamp}] " + " ".join(str(arg) for arg in args)
            print(message, **kwargs, flush=True)
            sys.stdout.flush()
            sys.stderr.flush()
        
        if not self.openai_api_key or self.openai_api_key == "sk-your-openai-api-key" or not self.openai_api_key.strip():
            # 如果没有API密钥或使用默认密钥，返回模拟回答（传入系统提示词以便生成更合适的回答）
            log_print("⚠️  [WARNING] OpenAI API密钥未配置或无效，使用模拟回答")
            log_print("⚠️  [WARNING] 请配置有效的 OPENAI_API_KEY 环境变量以使用真实的AI服务")
            log_print(f"⚠️  [WARNING] 当前API密钥: {self.openai_api_key[:20] if self.openai_api_key else 'None'}...")
            return await self._get_mock_response(user_message, system_prompt)

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }

        # 构建消息列表：系统提示词 + 用户消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        data = {
            "model": model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        
        log_print(f"📡 [API CALL] System prompt length: {len(system_prompt)}, User message length: {len(user_message)}")
        log_print(f"📡 [API CALL] Model: {model}, Base URL: {self.openai_base_url}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.openai_base_url}/chat/completions", headers=headers, json=data
                )

                if response.status_code == 200:
                    result = response.json()
                    choice = result["choices"][0]
                    usage = result.get("usage", {})
                    
                    answer_content = choice["message"]["content"]
                    log_print(f"✅ [API SUCCESS] Response received")
                    log_print(f"   回答长度: {len(answer_content)} 字符")
                    log_print(f"   使用的tokens: {usage.get('total_tokens', 0)}")
                    log_print(f"   回答预览: {answer_content[:200]}...")
                    
                    # 检查回答是否被截断
                    finish_reason = choice.get("finish_reason", "unknown")
                    if finish_reason == "length":
                        log_print(f"⚠️  [WARNING] 回答可能被截断 (finish_reason: length)")
                        log_print(f"   建议增加 max_tokens 或缩短问题")

                    return {
                        "answer": answer_content,
                        "confidence": 0.9,
                        "tokens_used": usage.get("total_tokens", 0),
                    }
                else:
                    # API返回错误状态码，回退到模拟回答
                    try:
                        error_body = response.text
                    except:
                        error_body = "无法读取错误响应体"
                    
                    error_msg = f"OpenAI API错误: {response.status_code}"
                    log_print(f"❌ [ERROR] AI服务调用失败，使用模拟回答")
                    log_print(f"   错误状态码: {response.status_code}")
                    log_print(f"   错误响应: {error_body[:500]}")
                    log_print(f"   请求URL: {self.openai_base_url}/chat/completions")
                    log_print(f"   请求模型: {model}")
                    return await self._get_mock_response(user_message, system_prompt)
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError) as e:
            # 网络错误或超时，回退到模拟回答
            import traceback
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e) if str(e) else repr(e),
                "error_args": e.args if hasattr(e, 'args') else None,
            }
            # 尝试获取更多错误信息
            if hasattr(e, 'request') and e.request:
                error_details["request_url"] = str(e.request.url) if hasattr(e.request, 'url') else "N/A"
            # httpx 的某些异常类型（如 TimeoutException, ConnectError, RequestError）没有 response 属性
            # 只有 HTTPStatusError 等特定异常才有 response，使用 getattr 安全访问
            response_status = "N/A"
            try:
                response_obj = getattr(e, 'response', None)
                if response_obj is not None:
                    response_status = getattr(response_obj, 'status_code', "N/A")
            except (AttributeError, TypeError):
                pass
            error_details["response_status"] = response_status
            
            log_print(f"❌ [ERROR] AI服务连接失败，使用模拟回答")
            log_print(f"   错误类型: {error_details['error_type']}")
            log_print(f"   错误信息: {error_details['error_message']}")
            log_print(f"   错误参数: {error_details['error_args']}")
            if 'request_url' in error_details:
                log_print(f"   请求URL: {error_details['request_url']}")
            if 'response_status' in error_details:
                log_print(f"   响应状态: {error_details['response_status']}")
            log_print(f"   完整堆栈:\n{traceback.format_exc()}")
            log_print(f"   诊断信息: API密钥已配置={bool(self.openai_api_key)}, Base URL={self.openai_base_url}, Model={model}")
            return await self._get_mock_response(user_message, system_prompt)
        except Exception as e:
            # 其他异常，回退到模拟回答
            import traceback
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e) if str(e) else repr(e),
                "error_args": e.args if hasattr(e, 'args') else None,
            }
            log_print(f"❌ [ERROR] AI服务调用异常，使用模拟回答")
            log_print(f"   错误类型: {error_details['error_type']}")
            log_print(f"   错误信息: {error_details['error_message']}")
            log_print(f"   错误参数: {error_details['error_args']}")
            log_print(f"   完整堆栈:\n{traceback.format_exc()}")
            log_print(f"   诊断信息: API密钥已配置={bool(self.openai_api_key)}, Base URL={self.openai_base_url}, Model={model}")
            return await self._get_mock_response(user_message, system_prompt)

    async def _get_mock_response(self, user_message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """获取模拟回答（用于测试或API密钥不可用时）"""
        # 模拟AI思考时间
        await asyncio.sleep(1.0)

        # 调试日志
        import sys
        import datetime
        def _log_print(*args, **kwargs):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"[{timestamp}] " + " ".join(str(arg) for arg in args)
            print(message, **kwargs, flush=True)
            sys.stdout.flush()
        
        _log_print(f"[MOCK RESPONSE] System prompt provided: {system_prompt is not None}")
        _log_print(f"[MOCK RESPONSE] System prompt length: {len(system_prompt) if system_prompt else 0}")
        _log_print(f"[MOCK RESPONSE] User message: {user_message[:100]}...")

        # 如果提供了系统提示词（智能体），尝试根据提示词生成更合适的回答
        if system_prompt:
            # 检查是否是教学设计相关的智能体（扩展关键词匹配）
            teaching_keywords = ["教学设计", "教学设计师", "课程设计", "教案", "教学方案", "教学深度", "导航系统", "六维教学"]
            is_teaching_agent = any(keyword in system_prompt for keyword in teaching_keywords)
            _log_print(f"[MOCK RESPONSE] Is teaching agent: {is_teaching_agent}")
            
            if is_teaching_agent:
                # 检查用户问题是否关于教学设计
                teaching_user_keywords = ["设计", "教案", "教学", "课文", "课程", "雷雨", "文学", "文本"]
                is_teaching_question = any(keyword in user_message for keyword in teaching_user_keywords)
                _log_print(f"[MOCK RESPONSE] Is teaching question: {is_teaching_question}")
                
                if is_teaching_question:
                    answer = """这是一个很好的教学设计问题！让我来帮你设计教学方案：

## 教学设计方案

### 一、教学目标
- **知识与技能**：理解课文的核心内容和主题思想
- **过程与方法**：通过探究式学习，培养学生的分析能力和表达能力
- **情感态度与价值观**：引导学生深入思考，形成正确的价值观念

### 二、教学重点与难点
- **教学重点**：理解课文的主要内容和深层含义
- **教学难点**：引导学生进行深度思考和批判性分析

### 三、教学过程设计

**1. 导入环节（5分钟）**
- 通过情境导入，激发学生学习兴趣
- 提出问题，引导学生思考

**2. 探究环节（20分钟）**
- 学生自主阅读，理解课文内容
- 小组讨论，分享理解
- 教师引导，深入分析

**3. 深化环节（10分钟）**
- 拓展延伸，联系实际
- 总结提升，形成认知

**4. 评价环节（5分钟）**
- 学生自我评价
- 同伴互评
- 教师点评

### 四、教学评价
- 形成性评价：观察学生在课堂中的表现
- 总结性评价：通过作业和测试检验学习效果

### 五、教学反思
- 记录教学过程中的亮点和不足
- 为后续教学改进提供参考

**注意**：这是一个模拟回答。要获得更详细和个性化的教学设计方案，请配置有效的AI API密钥。"""
                else:
                    # 教学设计智能体但问题不相关
                    answer = """作为课程设计专家，我专注于帮助教师进行教学设计。

您的问题似乎不是关于教学设计的。如果您需要：
- **教学设计**：我可以帮您设计完整的教学方案
- **教案优化**：我可以分析现有教案并提供改进建议
- **教学活动设计**：我可以设计各种教学活动

请告诉我您具体需要什么帮助，我会为您提供专业的教学设计建议。

**注意**：这是一个模拟回答。要获得更详细和个性化的建议，请配置有效的AI API密钥。"""
            else:
                # 其他类型的智能体，使用通用回答
                answer = f"""根据您的智能体设定，我来为您提供建议：

**问题分析**：
您的问题需要从专业角度进行分析和解答。

**建议方案**：
1. 理解问题的核心要点
2. 提供专业的解决方案
3. 给出具体的实施建议

**注意事项**：
- 请根据实际情况调整方案
- 如有疑问，可以继续提问

**注意**：这是一个模拟回答。要获得更详细和个性化的建议，请配置有效的AI API密钥。"""
        else:
            # 没有智能体，使用通用回答（根据用户消息内容判断）
            # 注意：优先检查是否是教学相关问题，避免误判为编程问题
            _log_print("[MOCK RESPONSE] No system prompt, using generic response")
            if ("设计" in user_message and ("教学" in user_message or "教案" in user_message or "课文" in user_message)) or \
               "课文" in user_message or ("教案" in user_message and "设计" in user_message):
                _log_print("[MOCK RESPONSE] Detected teaching question, using teaching response")
                # 教学相关问题，使用教学设计回答
                answer = """这是一个很好的教学设计问题！让我来帮你设计教学方案：

## 教学设计方案

### 一、教学目标
- **知识与技能**：理解课文的核心内容和主题思想
- **过程与方法**：通过探究式学习，培养学生的分析能力和表达能力
- **情感态度与价值观**：引导学生深入思考，形成正确的价值观念

### 二、教学重点与难点
- **教学重点**：理解课文的主要内容和深层含义
- **教学难点**：引导学生进行深度思考和批判性分析

### 三、教学过程设计

**1. 导入环节（5分钟）**
- 通过情境导入，激发学生学习兴趣
- 提出问题，引导学生思考

**2. 探究环节（20分钟）**
- 学生自主阅读，理解课文内容
- 小组讨论，分享理解
- 教师引导，深入分析

**3. 深化环节（10分钟）**
- 拓展延伸，联系实际
- 总结提升，形成认知

**4. 评价环节（5分钟）**
- 学生自我评价
- 同伴互评
- 教师点评

### 四、教学评价
- 形成性评价：观察学生在课堂中的表现
- 总结性评价：通过作业和测试检验学习效果

### 五、教学反思
- 记录教学过程中的亮点和不足
- 为后续教学改进提供参考

**注意**：这是一个模拟回答。要获得更详细和个性化的教学设计方案，请配置有效的AI API密钥。"""
            elif "代码" in user_message or "code" in user_message.lower():
                answer = """这是一个很好的编程问题！让我来帮你分析一下：

1. **问题分析**：从你的描述来看，这涉及到代码逻辑的实现。

2. **解决方案**：
```python
# 示例代码
def solve_problem():
    # 在这里实现你的逻辑
    pass
```

3. **注意事项**：
   - 确保代码的可读性和可维护性
   - 添加适当的注释
   - 考虑边界情况

如果你需要更具体的帮助，请提供更多细节！

**注意**：这是一个模拟回答。要获得更详细的编程帮助，请配置有效的AI API密钥。"""
            elif "视频" in user_message or "video" in user_message.lower():
                answer = """关于视频内容的问题，我来为你解答：

**主要内容**：
- 视频涵盖了重要的教学概念
- 通过实例演示帮助理解

**学习建议**：
1. 仔细观看视频内容
2. 做好笔记记录重点
3. 结合实际练习加深理解

**注意**：这是一个模拟回答。要获得更详细的帮助，请配置有效的AI API密钥。"""
            else:
                answer = """这是一个很好的问题！让我来为你详细解答：

**核心概念**：
这个问题涉及到重要的知识点，需要从多个角度来理解。

**详细解释**：
1. 首先，我们需要理解基础概念
2. 然后，通过实例来加深理解
3. 最后，通过练习来巩固知识

**学习建议**：
- 建议你多做一些相关练习
- 如果还有疑问，可以继续提问
- 也可以参考相关的学习资料

**注意**：这是一个模拟回答。要获得更详细的帮助，请配置有效的AI API密钥。"""

        return {
            "answer": answer,
            "confidence": 0.75,
            "tokens_used": len(answer.split()),
        }

    async def get_related_questions(
        self, question: str, lesson_title: Optional[str] = None, limit: int = 3
    ) -> List[str]:
        """获取相关问题建议"""
        # 这里可以实现相关问题推荐逻辑
        # 暂时返回一些通用建议
        suggestions = ["能否详细解释一下这个概念？", "有什么实际应用场景吗？", "如何避免常见错误？"]

        return suggestions[:limit]

    async def evaluate_answer_quality(
        self, question: str, answer: str
    ) -> Dict[str, Any]:
        """评估回答质量"""
        # 这里可以实现回答质量评估逻辑
        return {
            "relevance_score": 0.8,
            "completeness_score": 0.7,
            "clarity_score": 0.9,
            "overall_score": 0.8,
        }


# 创建全局实例
ai_qa_service = AIQAService()
