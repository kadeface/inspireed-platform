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
        self.openai_base_url = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1")
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
            response_time = (time.time() - start_time) * 1000
            return AIResponse(
                answer=f"抱歉，AI服务暂时不可用：{str(e)}",
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

        # 系统角色设定
        prompt_parts.append(
            "你是一个专业的教学助手，擅长回答教育相关的问题。请用简洁、准确、易懂的语言回答问题。"
        )

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
        prompt_parts.append(f"学生问题：{question}")

        # 回答要求
        prompt_parts.append("请提供详细、准确的回答，如果涉及代码，请提供示例代码。")

        return "\n\n".join(prompt_parts)

    async def _call_openai(self, prompt: str, model: str) -> Dict[str, Any]:
        """调用OpenAI API"""
        if not self.openai_api_key or self.openai_api_key == "sk-your-openai-api-key":
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
                raise Exception(f"OpenAI API错误: {response.status_code} - {response.text}")

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

        return {"answer": answer, "confidence": 0.75, "tokens_used": len(answer.split())}

    async def get_related_questions(
        self, question: str, lesson_title: Optional[str] = None, limit: int = 3
    ) -> List[str]:
        """获取相关问题建议"""
        # 这里可以实现相关问题推荐逻辑
        # 暂时返回一些通用建议
        suggestions = ["能否详细解释一下这个概念？", "有什么实际应用场景吗？", "如何避免常见错误？"]

        return suggestions[:limit]

    async def evaluate_answer_quality(self, question: str, answer: str) -> Dict[str, Any]:
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
