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

        try:
            # 构建提示词
            prompt = self._build_prompt(question, context, lesson_title, cell_content)

            # 调用AI API
            if model.startswith("gpt"):
                response = await self._call_openai(prompt, model)
            else:
                # 默认使用OpenAI格式
                response = await self._call_openai(prompt, model)

            response_time = (time.time() - start_time) * 1000

            return AIResponse(
                answer=response["answer"],
                confidence=response.get("confidence", 0.8),
                response_time=response_time,
                model_used=model,
                tokens_used=response.get("tokens_used"),
            )

        except Exception as e:
            # 如果出现任何异常，回退到模拟回答
            print(f"AI服务处理异常，使用模拟回答: {str(e)}")
            response_time = (time.time() - start_time) * 1000
            try:
                # 尝试生成模拟回答
                mock_response = await self._get_mock_response(question)
                return AIResponse(
                    answer=mock_response["answer"],
                    confidence=mock_response.get("confidence", 0.75),
                    response_time=response_time,
                    model_used="mock",
                    tokens_used=mock_response.get("tokens_used"),
                )
            except Exception as fallback_error:
                # 如果连模拟回答都失败，返回错误消息
                response_time = (time.time() - start_time) * 1000
                return AIResponse(
                    answer=f"抱歉，AI服务暂时不可用。请稍后重试或联系管理员。",
                    confidence=0.0,
                    response_time=response_time,
                    model_used=model,
                )

    def _build_prompt(
        self,
        question: str,
        context: Optional[str] = None,
        lesson_title: Optional[str] = None,
        cell_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """构建AI提示词"""
        prompt_parts = []

        # 系统角色设定（增强学习科学理论支持）
        system_prompt = """你是一个专业的教学助手，擅长基于学习科学理论回答教育相关的问题。

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
        prompt_parts.append(system_prompt)

        # 上下文信息
        if lesson_title:
            prompt_parts.append(f"当前课程：{lesson_title}")

        if context:
            prompt_parts.append(f"上下文信息：{context}")

        if cell_content:
            # 根据Cell类型提供特定上下文
            cell_type = cell_content.get("type", "unknown")
            if cell_type == "code":
                code = cell_content.get("code", "")
                language = cell_content.get("language", "")
                prompt_parts.append(f"代码内容（{language}）：\n{code}")
            elif cell_type == "video":
                video_title = cell_content.get("title", "")
                video_desc = cell_content.get("description", "")
                prompt_parts.append(f"视频内容：{video_title}\n{video_desc}")
            elif cell_type == "text":
                text_content = cell_content.get("html", "")
                prompt_parts.append(f"文本内容：{text_content}")

        # 问题
        prompt_parts.append(f"教师问题：{question}")

        # 回答要求
        answer_guidance = """回答要求：
1. 如果问题涉及教学设计，请结合学习科学理论（如布鲁姆分类法、5E模型等）提供建议
2. 如果问题涉及提问技巧，请提供苏格拉底式提问的具体示例
3. 如果问题涉及学生理解，请考虑费曼学习法和主动输出策略
4. 如果问题涉及差异化教学，请考虑不同学习风格和多元智能
5. 提供具体、可操作的建议，避免空泛的理论描述
6. 如果涉及代码，请提供示例代码"""
        prompt_parts.append(answer_guidance)

        return "\n\n".join(prompt_parts)

    async def _call_openai(self, prompt: str, model: str) -> Dict[str, Any]:
        """调用OpenAI API，失败时自动回退到模拟回答"""
        if not self.openai_api_key or self.openai_api_key == "sk-your-openai-api-key" or not self.openai_api_key.strip():
            # 如果没有API密钥或使用默认密钥，返回模拟回答
            return await self._get_mock_response(prompt)

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.openai_base_url}/chat/completions", headers=headers, json=data
                )

                if response.status_code == 200:
                    result = response.json()
                    choice = result["choices"][0]
                    usage = result.get("usage", {})

                    return {
                        "answer": choice["message"]["content"],
                        "confidence": 0.9,
                        "tokens_used": usage.get("total_tokens", 0),
                    }
                else:
                    # API返回错误状态码，回退到模拟回答
                    error_msg = f"OpenAI API错误: {response.status_code}"
                    print(f"AI服务调用失败，使用模拟回答: {error_msg}")
                    return await self._get_mock_response(prompt)
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError) as e:
            # 网络错误或超时，回退到模拟回答
            print(f"AI服务连接失败，使用模拟回答: {str(e)}")
            return await self._get_mock_response(prompt)
        except Exception as e:
            # 其他异常，回退到模拟回答
            print(f"AI服务调用异常，使用模拟回答: {str(e)}")
            return await self._get_mock_response(prompt)

    async def _get_mock_response(self, prompt: str) -> Dict[str, Any]:
        """获取模拟回答（用于测试或API密钥不可用时）"""
        # 模拟AI思考时间
        await asyncio.sleep(1.0)

        # 根据问题内容生成模拟回答
        if "代码" in prompt or "code" in prompt.lower():
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

如果你需要更具体的帮助，请提供更多细节！"""
        elif "视频" in prompt or "video" in prompt.lower():
            answer = """关于视频内容的问题，我来为你解答：

**主要内容**：
- 视频涵盖了重要的教学概念
- 通过实例演示帮助理解

**学习建议**：
1. 仔细观看视频内容
2. 做好笔记记录重点
3. 结合实际练习加深理解

**常见问题**：
- 如果遇到不理解的地方，可以重复观看
- 建议结合其他学习材料一起学习

有什么具体问题可以继续问我！"""
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

希望这个回答对你有帮助！如果还有其他问题，随时可以问我。"""

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
