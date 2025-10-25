"""
Cell单元Schemas
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.models.cell import CellType


class CellBase(BaseModel):
    """Cell基础Schema"""
    cell_type: CellType = Field(..., description="Cell类型")
    title: Optional[str] = Field(None, max_length=200, description="Cell标题")
    content: Dict[str, Any] = Field(default_factory=dict, description="Cell内容")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Cell配置")
    order: int = Field(0, description="显示顺序")
    editable: bool = Field(False, description="是否可编辑")


class CellCreate(CellBase):
    """创建Cell Schema"""
    lesson_id: int = Field(..., description="所属教案ID")


class CellUpdate(BaseModel):
    """更新Cell Schema"""
    title: Optional[str] = Field(None, max_length=200, description="Cell标题")
    content: Optional[Dict[str, Any]] = Field(None, description="Cell内容")
    config: Optional[Dict[str, Any]] = Field(None, description="Cell配置")
    order: Optional[int] = Field(None, description="显示顺序")
    editable: Optional[bool] = Field(None, description="是否可编辑")


class CellResponse(CellBase):
    """Cell响应Schema"""
    id: int
    lesson_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CellListResponse(BaseModel):
    """Cell列表响应Schema"""
    items: List[CellResponse]
    total: int
    page: int
    page_size: int


# ==================== Cell执行相关Schemas ====================

class CodeExecutionRequest(BaseModel):
    """代码执行请求Schema"""
    code: str = Field(..., description="代码内容")
    language: str = Field(..., description="编程语言")
    timeout: Optional[int] = Field(30, description="执行超时时间（秒）")
    max_memory: Optional[int] = Field(100, description="最大内存使用（MB）")


class CodeExecutionResponse(BaseModel):
    """代码执行响应Schema"""
    output: str = Field(..., description="执行输出")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., description="执行时间（毫秒）")
    memory_used: Optional[int] = Field(None, description="内存使用量（MB）")


class CellExecutionRequest(BaseModel):
    """Cell执行请求Schema"""
    cell_id: int = Field(..., description="Cell ID")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="执行参数")


class CellExecutionResponse(BaseModel):
    """Cell执行响应Schema"""
    success: bool = Field(..., description="执行是否成功")
    output: Optional[str] = Field(None, description="执行输出")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., description="执行时间（毫秒）")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")


# ==================== QA Cell相关Schemas ====================

class QAQuestionRequest(BaseModel):
    """QA问题请求Schema"""
    question: str = Field(..., min_length=1, max_length=1000, description="问题内容")
    ask_ai: bool = Field(True, description="是否向AI提问")


class QAAnswerResponse(BaseModel):
    """QA回答响应Schema"""
    answer: str = Field(..., description="回答内容")
    is_ai_answer: bool = Field(..., description="是否为AI回答")
    confidence: Optional[float] = Field(None, description="AI回答置信度")
    response_time: float = Field(..., description="响应时间（毫秒）")


class QACellUpdate(BaseModel):
    """QA Cell更新Schema"""
    question: Optional[str] = Field(None, description="问题内容")
    answer: Optional[str] = Field(None, description="回答内容")
    is_ai_answer: Optional[bool] = Field(None, description="是否为AI回答")


# ==================== 其他Cell类型Schemas ====================

class ChartDataRequest(BaseModel):
    """图表数据请求Schema"""
    chart_type: str = Field(..., description="图表类型")
    data: Dict[str, Any] = Field(..., description="图表数据")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="图表选项")


class SimConfigRequest(BaseModel):
    """仿真配置请求Schema"""
    sim_type: str = Field(..., description="仿真类型")
    config: Dict[str, Any] = Field(..., description="仿真配置")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="仿真参数")


class ContestSubmissionRequest(BaseModel):
    """竞赛提交请求Schema"""
    submission_data: Dict[str, Any] = Field(..., description="提交数据")
    user_id: int = Field(..., description="用户ID")


class ContestSubmissionResponse(BaseModel):
    """竞赛提交响应Schema"""
    score: float = Field(..., description="得分")
    rank: int = Field(..., description="排名")
    feedback: Optional[str] = Field(None, description="反馈信息")
    leaderboard: List[Dict[str, Any]] = Field(default_factory=list, description="排行榜")
