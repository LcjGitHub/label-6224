"""Pydantic 请求/响应模型。"""

from pydantic import BaseModel, Field


class RepairRecordBase(BaseModel):
    """维修记录公共字段。"""

    description: str = Field(..., min_length=1, description="问题描述")
    repair_date: str = Field(..., description="维修日期 YYYY-MM-DD")
    tools: str = Field(default="", description="使用工具")
    duration_minutes: int = Field(default=0, ge=0, description="耗时（分钟）")
    recurred: bool = Field(default=False, description="是否复发")


class RepairRecordCreate(RepairRecordBase):
    """创建维修记录。"""


class RepairRecordUpdate(RepairRecordBase):
    """更新维修记录。"""


class RepairRecord(RepairRecordBase):
    """维修记录响应。"""

    id: int
